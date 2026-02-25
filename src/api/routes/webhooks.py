import re
import json
import os
import logging
import asyncio
from collections import defaultdict
import time as _time
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from agents import Runner, SQLiteSession

from src.core.config import ANTISPAM_CONFIG, DATA_DIR
from src.core.security import verify_webhook_signature
from src.application.tools import (
    _check_availability, _schedule_appointment, _confirm_appointment,
    _cancel_appointment, _reschedule_appointment, _get_available_services,
    _find_patient_appointments
)
from src.infrastructure.vector_store import search_store
from src.application.agent import agent
from src.infrastructure.services.zapi import send_message

logger = logging.getLogger("PostClinics.Webhook")
router = APIRouter(prefix="/webhook", tags=["Webhooks"])

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

# State for rate limiting and dedup
_seen_messages = {}
_phone_timestamps = defaultdict(list)
_phone_locks = {}
_phone_out_of_scope_attempts = defaultdict(int)

SCOPE_PATTERN = re.compile(
    r"\b(agendar|agendamento|marcar|consulta|hor[aá]rio|servi[cç]o|reagendar|cancelar|confirmar|desmarcar)\b"
)
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
                prefs = get_patient_profile(phone)
            except Exception as e:
                prefs = ""
                logger.error(f"Failed to fetch profile: {e}")
                
            # Pre-process short messages/emojis into explicit intent phrases
            text_content = preprocess_intent(text_content)

            handoff_reason = detect_handoff_reason(text_content)
            if handoff_reason:
                logger.info(f"[HANDOFF] phone={phone} reason={handoff_reason}")
                await send_message(phone, HANDOFF_REPLY)
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
                    await send_message(phone, HANDOFF_REPLY)
                    _phone_out_of_scope_attempts[phone] = 0
                    return
            
            # Inject patient phone into context so agent can look up appointments
            agent_input = f"Telefone do paciente: {phone}\n{prefs}\n{text_content}"
            
            logger.info(f"[WPP:IN] phone={phone} msgId={message_id} text={text_content}")
            
            result = await Runner.run(agent, input=agent_input, session=session, max_turns=10)
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
                    
                tool_results = []
                for match in matches:
                    func_name = match.group(1)
                    args_str = match.group(2).strip()
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
                    tool_results.append(f"Tool '{func_name}' returned: {tool_output}")
                
                results_summary = "\n".join(tool_results)
                next_input = f"(SYSTEM: {results_summary}\nBased on these results, respond to the user in Portuguese.)"
                
                result = await Runner.run(agent, input=next_input, session=session)
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
            reply_text = reply_text.strip()
            
            if not reply_text:
                reply_text = "Desculpe, não entendi. Pode repetir?"
                
            send_success = await send_message(phone, reply_text)
            logger.info(f"[WPP:OUT] phone={phone} success={send_success} reply={reply_text[:100]}...")
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"CRITICAL Error in background task for {phone}: {e}\n{error_trace}")

@router.post("/zapi")
async def receiver(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint request from Z-API.
    Accepts arbitrary JSON and manually extracts fields to be robust against structure variations.
    Includes anti-spam protection: rate limiting per phone and message deduplication.
    """
    global _seen_messages, _phone_timestamps
    
    try:
        raw_body = await request.body()
        verify_webhook_signature(request.headers, raw_body)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        phone = payload.get("phone")
        
        # Extract text content
        text_content = ""
        text_data = payload.get("text")
        
        if isinstance(text_data, dict):
            text_content = text_data.get("message", "")
        elif isinstance(text_data, str):
            text_content = text_data
            
        message_id = payload.get("messageId", "unknown")
        logger.info(
            "[WPP:RAW] msgId=%s fromMe=%s isGroup=%s phoneSuffix=%s",
            message_id,
            payload.get("fromMe", False),
            payload.get("isGroup", False),
            (str(phone)[-4:] if phone else "none"),
        )
            
        if not phone or not text_content:
            logger.warning(f"Ignored payload (missing phone/text): {payload}")
            return {"status": "ignored", "reason": "missing_data"}

        if payload.get("fromMe", False) or payload.get("isGroup", False) or payload.get("isNewsletter", False):
             return {"status": "ignored", "reason": "filtered_source"}

        now = _time.time()
        
        # --- ANTI-SPAM: Message Deduplication ---
        dedup_window = ANTISPAM_CONFIG["dedup_window_seconds"]
        _seen_messages = {
            k: v for k, v in _seen_messages.items()
            if now - v < dedup_window
        }
        
        if message_id in _seen_messages:
            logger.info(f"[ANTISPAM] Duplicate message ignored: {message_id}")
            return {"status": "ignored", "reason": "duplicate_message"}
        
        _seen_messages[message_id] = now
        
        # --- ANTI-SPAM: Rate Limiting per Phone ---
        max_per_min = ANTISPAM_CONFIG["max_messages_per_minute"]
        cooldown = ANTISPAM_CONFIG["cooldown_seconds"]
        
        _phone_timestamps[phone] = [
            ts for ts in _phone_timestamps[phone]
            if now - ts < 60
        ]
        
        timestamps = _phone_timestamps[phone]
        
        if len(timestamps) >= max_per_min:
            logger.warning(f"[ANTISPAM] Rate limit exceeded for {phone}: {len(timestamps)} msgs/min")
            return {"status": "ignored", "reason": "rate_limited"}
        
        if timestamps and (now - timestamps[-1]) < cooldown:
            logger.info(f"[ANTISPAM] Cooldown active for {phone}: {now - timestamps[-1]:.1f}s < {cooldown}s")
            return {"status": "ignored", "reason": "cooldown"}
        
        _phone_timestamps[phone].append(now)

        # --- ENQUEUE PROCESS MESSAGE ---
        background_tasks.add_task(process_webhook_payload, phone, message_id, text_content)
        return {"status": "queued"}

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"CRITICAL Error processing webhook: {e}\n{error_trace}")
        raise HTTPException(status_code=500, detail=str(e))
