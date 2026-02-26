import re
import json
import os
import logging
import asyncio
from collections import defaultdict
import time as _time

from agents import Runner, SQLiteSession
from sqlmodel import Session, select

from src.core.config import DATA_DIR
from src.application.tools import (
    _check_availability, _schedule_appointment, _confirm_appointment,
    _cancel_appointment, _reschedule_appointment, _get_available_services,
    _find_patient_appointments
)
from src.application.services.patient_identity import find_patients_by_contact
from src.application.services.service_catalog import canonicalize_service_name
from src.domain.models import Appointment, Patient
from src.infrastructure.database import engine
from src.infrastructure.vector_store import search_store
from src.application.agent import agent
from src.infrastructure.services.zapi import send_message

logger = logging.getLogger("PostClinics.MessageHandler")

# --- INTENT PRE-PROCESSING ---
# Regex patterns for matching intents even within longer sentences
INTENT_PATTERNS = {
    "confirmar": r'\b(sim|confirmo|confirmar|confirmado|confirmei|confirma|ok)\b|✅',
    "reagendar": r'\b(reagendar|remarcar|mudar|trocar|reagenda|transferir|adiar)\b|🔄',
    "cancelar": r'\b(cancelar|cancela|desmarcar|cancelo|desmarco|nao vou|não vou)\b|❌|(?<![a-zA-Z])x(?![a-zA-Z])',
    "falar_atendente": r'\b(atendente|humano|pessoa|chata|ruim|falar com alguem|valor da consulta|preço)\b'
}

INTENT_PHRASES = {
    "confirmar": "Quero confirmar minha consulta",
    "reagendar": "Quero reagendar minha consulta",
    "cancelar": "Quero cancelar minha consulta",
    "falar_atendente": "Quero falar com um atendente",
}

def preprocess_intent(text: str) -> str:
    """Convert short emoji/text responses into explicit intent phrases for the agent."""
    normalized = text.strip().lower()
    # Remove variation selectors and zero-width joiners from emojis
    normalized = normalized.replace("\ufe0f", "").replace("\u200d", "")
    
    # Check if the text matches any intent pattern
    for intent, pattern in INTENT_PATTERNS.items():
        if re.search(pattern, normalized):
            phrase = INTENT_PHRASES[intent]
            logger.info(f"[INTENT] Mapped '{text}' -> '{phrase}'")
            return phrase
            
    return text

# Map of tool names to their undecorated implementations
TOOL_MAP = {
    "check_availability": _check_availability,
    "schedule_appointment": _schedule_appointment,
    "confirm_appointment": _confirm_appointment,
    "cancel_appointment": _cancel_appointment,
    "reschedule_appointment": _reschedule_appointment,
    "get_available_services": _get_available_services,
    "find_patient_appointments": _find_patient_appointments,
    "search_knowledge_base": lambda query="": (
        "\n\n".join(
            [f"Referência {i+1}: {r.page_content.strip()}" for i, r in enumerate(results)]
        ) if (results := search_store(query, k=2)) else "Nenhuma informação relevante encontrada."
    ),
}

_phone_locks = {}
_phone_out_of_scope_attempts = defaultdict(int)
_phone_handoff_until = {}

SCOPE_PATTERN = re.compile(
    r"\b(agendar|agendamento|marcar|consulta|hor[aá]rio|servi[cç]o|reagendar|cancelar|confirmar|desmarcar)\b"
)
DATE_SELECTION_PATTERN = re.compile(r"^(dia\s*)?\d{1,2}[/-]\d{1,2}([/-]\d{2,4})?\s*$", re.IGNORECASE)
TIME_SELECTION_PATTERN = re.compile(r"^(a[sà]s?\s*)?\d{1,2}(:|h)\d{2}\s*$", re.IGNORECASE)
GREETING_PATTERN = re.compile(r"^(oi|ol[áa]|bom dia|boa tarde|boa noite)\b")
HUMAN_REQUEST_PATTERN = re.compile(r"\b(atendente|humano|pessoa|recepcionista)\b")
FINANCIAL_PATTERN = re.compile(r"\b(valor|pre[cç]o|financeiro|pagamento|cobran[cç]a|or[cç]amento)\b")
COMPLAINT_PATTERN = re.compile(r"\b(reclama[cç][aã]o|reclamar|insatisfeit|ruim|péssimo|horr[ií]vel)\b")
URGENCY_PATTERN = re.compile(r"\b(urg[êe]ncia|urgente|emerg[êe]ncia|dor forte|sangramento)\b")

HANDOFF_REPLY = (
    "Encaminhei você para um atendente humano. "
    "Esse canal humano é indicado para: assuntos fora de agendamento/reagendamento/cancelamento, "
    "dúvidas financeiras ou preços, reclamações e urgências."
)
RATE_LIMIT_REPLY = (
    "Estamos com alto volume de atendimento no momento. "
    "Já encaminhei sua mensagem para um atendente humano para não atrasar seu suporte."
)
GENERIC_ERROR_REPLY = (
    "Tive uma instabilidade momentânea para processar sua mensagem. "
    "Encaminhei para um atendente humano e vamos te responder em seguida."
)

SMALL_TALK_PATTERN = re.compile(
    r"^(oi+|ol[áa]+|bom dia|boa tarde|boa noite|obrigad[oa]+|valeu+|perfeito+|beleza+|tudo bem\??)$",
    re.IGNORECASE
)

MAX_PROFILE_CHARS = 600
MAX_TEXT_CHARS = 1200
MAX_TOOL_OUTPUT_CHARS = 800
MAX_INLINE_TOOL_CALLS = int(os.environ.get("MAX_INLINE_TOOL_CALLS", "3"))
MAX_REPEATED_INLINE_SAME_CALL = int(os.environ.get("MAX_REPEATED_INLINE_SAME_CALL", "2"))
HANDOFF_TTL_SECONDS = int(os.environ.get("HANDOFF_TTL_SECONDS", "900"))


def _truncate_text(value: str, limit: int) -> str:
    if not value:
        return ""
    cleaned = value.strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit]


def _is_rate_limit_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return "rate_limit" in text or "error code: 429" in text or "too many requests" in text


def _is_request_too_large_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return "error code: 413" in text or "request too large" in text


def _activate_handoff(phone: str):
    _phone_handoff_until[phone] = _time.time() + HANDOFF_TTL_SECONDS


def _has_active_handoff(phone: str) -> bool:
    until = _phone_handoff_until.get(phone, 0)
    if until <= _time.time():
        _phone_handoff_until.pop(phone, None)
        return False
    return True


def _clear_handoff(phone: str):
    _phone_handoff_until.pop(phone, None)


async def _safe_send_message(phone: str, text: str):
    try:
        return await send_message(phone, text)
    except Exception as send_exc:
        logger.error("Failed to send fallback message to %s: %s", phone, send_exc)
        return {"success": False, "status_code": 500, "error_message": str(send_exc)}


def _format_appointment_summary(appointment: Appointment, patient: Patient) -> str:
    dt = appointment.datetime.strftime("%d/%m/%Y às %H:%M")
    service = canonicalize_service_name(appointment.service)
    return f"{patient.name} - {service} com {appointment.professional} em {dt}"


def _load_active_appointments_for_contact(phone: str) -> list[tuple[Appointment, Patient]]:
    with Session(engine) as session:
        patients = find_patients_by_contact(session, phone)
        patient_ids = [p.id for p in patients if p.id is not None]
        if not patient_ids:
            return []
        rows = session.exec(
            select(Appointment, Patient)
            .join(Patient)
            .where(
                Appointment.patient_id.in_(patient_ids),
                Appointment.status != "cancelled",
            )
            .order_by(Appointment.datetime)
        ).all()
        return rows


async def _try_fast_path(phone: str, text_content: str) -> bool:
    normalized = (text_content or "").strip().lower()
    normalized = re.sub(r"[.!?]+$", "", normalized).strip()

    if normalized == "quero confirmar minha consulta":
        rows = _load_active_appointments_for_contact(phone)
        if not rows:
            await _safe_send_message(phone, "Não encontrei consulta ativa para este contato. Deseja agendar uma nova?")
            return True
        if len(rows) > 1:
            options = "\n".join([f"- {_format_appointment_summary(appt, patient)}" for appt, patient in rows[:5]])
            await _safe_send_message(
                phone,
                "Encontrei mais de uma consulta vinculada ao seu contato. "
                "Me diga qual deseja confirmar (data/horário):\n" + options,
            )
            return True

        appt, _patient = rows[0]
        _confirm_appointment(appt.id)
        await _safe_send_message(phone, "Sua presença foi confirmada. Aguardamos você.")
        return True

    if SMALL_TALK_PATTERN.match(normalized):
        await _safe_send_message(
            phone,
            "Olá. Sou Cora da Espaço Interativo Reabilitare. "
            "Posso auxiliar com agendamentos, reagendamentos ou cancelamentos de consultas. "
            "Para outros assuntos, digite 'Falar com atendente'.",
        )
        return True

    return False


async def _run_agent_with_recovery(
    *,
    phone: str,
    conversation_db: str,
    base_session: SQLiteSession,
    agent_input: str,
    max_turns: int = 8,
):
    try:
        return await Runner.run(agent, input=agent_input, session=base_session, max_turns=max_turns)
    except Exception as exc:
        if _is_request_too_large_error(exc):
            logger.warning("[WPP] Oversized context for phone=%s. Retrying with reduced context.", phone)
            fallback_session = SQLiteSession(
                db_path=conversation_db,
                session_id=f"zapi:{phone}:recovery:{int(_time.time())}",
            )
            reduced_input = _truncate_text(agent_input, MAX_TEXT_CHARS)
            return await Runner.run(agent, input=reduced_input, session=fallback_session, max_turns=6)
        raise


def detect_handoff_reason(text: str) -> str | None:
    normalized = (text or "").strip().lower()
    if HUMAN_REQUEST_PATTERN.search(normalized):
        return "Pedido explícito de atendente."
    if URGENCY_PATTERN.search(normalized):
        return "Mensagem com indício de urgência."
    if FINANCIAL_PATTERN.search(normalized):
        return "Dúvida financeira ou de preço."
    if COMPLAINT_PATTERN.search(normalized):
        return "Reclamação/insatisfação."
    return None


def is_in_supported_scope(text: str) -> bool:
    normalized = (text or "").strip().lower()
    if GREETING_PATTERN.search(normalized):
        return True
    if DATE_SELECTION_PATTERN.match(normalized) or TIME_SELECTION_PATTERN.match(normalized):
        return True
    return bool(SCOPE_PATTERN.search(normalized))

def get_phone_lock(phone: str) -> asyncio.Lock:
    if phone not in _phone_locks:
        _phone_locks[phone] = asyncio.Lock()
    return _phone_locks[phone]

async def process_webhook_payload(phone: str, message_id: str, text_content: str):
    """
    Background worker that runs the LLM logic sequentially per-phone to prevent overlapping agent sessions.
    """
    lock = get_phone_lock(phone)
    async with lock:
        try:
            # --- PROCESS MESSAGE ---
            session_id = f"zapi:{phone}"
            conversation_db = os.path.join(DATA_DIR, "conversations.db")
            session = SQLiteSession(db_path=conversation_db, session_id=session_id)
            
            # Inject patient profile from Long-Term Memory
            try:
                from src.infrastructure.vector_store import get_patient_profile
                prefs = _truncate_text(get_patient_profile(phone), MAX_PROFILE_CHARS)
            except Exception as e:
                prefs = ""
                logger.error(f"Failed to fetch profile: {e}")
                
            # Pre-process short messages/emojis into explicit intent phrases
            text_content = preprocess_intent(_truncate_text(text_content, MAX_TEXT_CHARS))

            if _has_active_handoff(phone):
                if is_in_supported_scope(text_content) and not detect_handoff_reason(text_content):
                    _clear_handoff(phone)
                else:
                    await _safe_send_message(phone, HANDOFF_REPLY)
                    return

            handoff_reason = detect_handoff_reason(text_content)
            if handoff_reason:
                logger.info(f"[HANDOFF] phone={phone} reason={handoff_reason}")
                _activate_handoff(phone)
                await _safe_send_message(phone, HANDOFF_REPLY)
                _phone_out_of_scope_attempts[phone] = 0
                return

            if is_in_supported_scope(text_content):
                _phone_out_of_scope_attempts[phone] = 0
            else:
                _phone_out_of_scope_attempts[phone] += 1
                logger.info(
                    "[SCOPE] phone=%s out_of_scope_attempt=%s text=%s",
                    phone,
                    _phone_out_of_scope_attempts[phone],
                    text_content[:120],
                )
                if _phone_out_of_scope_attempts[phone] >= 2:
                    _activate_handoff(phone)
                    await _safe_send_message(phone, HANDOFF_REPLY)
                    _phone_out_of_scope_attempts[phone] = 0
                    return

            if await _try_fast_path(phone, text_content):
                logger.info("[FAST_PATH] phone=%s text=%s", phone, text_content[:80])
                return
            
            # Inject patient phone into context so agent can look up appointments
            agent_input = f"Telefone do paciente: {phone}\n{prefs}\n{text_content}"
            
            logger.info(f"[WPP:IN] phone={phone} msgId={message_id} text={text_content}")
            
            result = await _run_agent_with_recovery(
                phone=phone,
                conversation_db=conversation_db,
                base_session=session,
                agent_input=agent_input,
                max_turns=8,
            )
            logger.info(f"Agent response: {result}")
            
            # --- GROQ/LLAMA WORKAROUND ---
            final_text = result.final_output
            if not isinstance(final_text, str):
                final_text = str(final_text)
            
            tool_pattern = r'<function=(\w+)>(.*?)</function>'
            
            for attempt in range(3):
                matches = list(re.finditer(tool_pattern, final_text, re.DOTALL))
                if not matches:
                    break
                if len(matches) > MAX_INLINE_TOOL_CALLS:
                    logger.warning(
                        "[INLINE_TOOL_GUARD] phone=%s too_many_calls=%s",
                        phone,
                        len(matches),
                    )
                    _activate_handoff(phone)
                    await _safe_send_message(phone, GENERIC_ERROR_REPLY)
                    return
                    
                tool_results = []
                seen_inline_calls = defaultdict(int)
                for match in matches:
                    func_name = match.group(1)
                    args_str = match.group(2).strip()
                    call_key = f"{func_name}:{args_str}"
                    seen_inline_calls[call_key] += 1
                    if seen_inline_calls[call_key] > MAX_REPEATED_INLINE_SAME_CALL:
                        logger.warning(
                            "[INLINE_TOOL_GUARD] phone=%s skipped_repeated_call=%s",
                            phone,
                            call_key[:120],
                        )
                        continue
                    logger.info(f"Detected tool call #{attempt+1}: {func_name}({args_str})")
                    
                    if func_name in TOOL_MAP:
                        try:
                            kwargs = json.loads(args_str) if args_str else {}
                            tool_output = TOOL_MAP[func_name](**kwargs)
                        except json.JSONDecodeError:
                            tool_output = f"Error: Invalid JSON arguments: {args_str}"
                        except Exception as e:
                            tool_output = f"Error executing {func_name}: {e}"
                    else:
                        tool_output = f"Tool '{func_name}' not available."
                        
                    logger.info(f"Tool Output: {tool_output}")
                    tool_results.append(
                        f"Tool '{func_name}' returned: {_truncate_text(str(tool_output), MAX_TOOL_OUTPUT_CHARS)}"
                    )
                if not tool_results:
                    break
                
                results_summary = _truncate_text("\n".join(tool_results), MAX_TEXT_CHARS)
                next_input = f"(SYSTEM: {results_summary}\nBased on these results, respond to the user in Portuguese.)"
                inline_session = SQLiteSession(
                    db_path=conversation_db,
                    session_id=f"{session_id}:inline:{attempt}:{int(_time.time())}",
                )
                
                result = await _run_agent_with_recovery(
                    phone=phone,
                    conversation_db=conversation_db,
                    base_session=inline_session,
                    agent_input=next_input,
                    max_turns=6,
                )
                final_text = result.final_output
                if not isinstance(final_text, str):
                    final_text = str(final_text)
                logger.info(f"Agent follow-up response (attempt {attempt+1}): {final_text}")
            
            # --- RESPONSE CLEANUP ---
            reply_text = final_text
            if not isinstance(reply_text, str):
                reply_text = str(reply_text)
                
            reply_text = re.sub(r'<thought>.*?</thought>', '', reply_text, flags=re.DOTALL)
            reply_text = re.sub(r'\[TOOL_CALL\]|\[SYSTEM\]|\[FUNCTION\]', '', reply_text)
            reply_text = re.sub(r'Telefone do paciente:\s*\S+', '', reply_text)
            reply_text = re.sub(r'<function=.*?>.*?</function>', '', reply_text, flags=re.DOTALL)
            reply_text = re.sub(r'^\(SYSTEM:.*?\)$', '', reply_text, flags=re.DOTALL)
            reply_text = reply_text.strip()
            if "<function=" in reply_text:
                reply_text = "Desculpe, tive uma instabilidade para processar esta solicitação. Vou encaminhar para um atendente."
                _activate_handoff(phone)
            
            if not reply_text:
                reply_text = "Desculpe, não entendi. Pode repetir?"
            if "atendente humano" in reply_text.lower() or "encaminhada para um atendente" in reply_text.lower():
                _activate_handoff(phone)
                
            send_success = await _safe_send_message(phone, reply_text)
            logger.info(f"[WPP:OUT] phone={phone} success={send_success} reply={reply_text[:100]}...")
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"CRITICAL Error in background task for {phone}: {e}\n{error_trace}")
            fallback = RATE_LIMIT_REPLY if (_is_rate_limit_error(e) or _is_request_too_large_error(e)) else GENERIC_ERROR_REPLY
            _activate_handoff(phone)
            await _safe_send_message(phone, fallback)
