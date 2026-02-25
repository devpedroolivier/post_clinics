import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from sqlmodel import Session, delete, select

from src.api.routes import webhooks
from src.domain.models import Appointment, NotificationLog, Patient
from src.infrastructure.database import create_db_and_tables, engine


class _FakeRunnerResult:
    def __init__(self, final_output: str):
        self.final_output = final_output


def _reset_webhook_runtime_state():
    webhooks._phone_out_of_scope_attempts.clear()
    webhooks._phone_timestamps.clear()
    webhooks._seen_messages.clear()
    webhooks._phone_locks.clear()
    webhooks._phone_handoff_until.clear()


def _clean_db():
    create_db_and_tables()
    with Session(engine) as session:
        session.exec(delete(NotificationLog))
        session.exec(delete(Appointment))
        session.exec(delete(Patient))
        session.commit()


def test_webhook_rate_limit_fallback_message():
    _clean_db()
    _reset_webhook_runtime_state()

    async def _run():
        with patch("src.api.routes.webhooks.Runner.run", new_callable=AsyncMock) as mock_runner:
            with patch("src.api.routes.webhooks.send_message", new_callable=AsyncMock) as mock_send:
                mock_runner.side_effect = Exception("Error code: 429 - rate_limit_exceeded")
                mock_send.return_value = {"success": True, "status_code": 200, "error_message": None}

                await webhooks.process_webhook_payload(
                    "5511981112222",
                    "msg-rate-limit",
                    "Quero agendar uma consulta",
                )

                mock_runner.assert_called_once()
                mock_send.assert_called_once()
                sent_text = mock_send.call_args.args[1]
                assert "alto volume de atendimento" in sent_text

    asyncio.run(_run())


def test_webhook_fast_path_confirm_without_llm():
    _clean_db()
    _reset_webhook_runtime_state()

    phone = "5511983334444"
    with Session(engine) as session:
        patient = Patient(name="Paciente Fast", phone=phone, contact_phone=phone)
        session.add(patient)
        session.commit()
        session.refresh(patient)

        appt = Appointment(
            patient_id=patient.id,
            datetime=datetime.now() + timedelta(days=1),
            service="Clínica Geral",
            professional="Dra. Débora / Dr. Sidney",
            status="scheduled",
        )
        session.add(appt)
        session.commit()
        session.refresh(appt)

    async def _run():
        with patch("src.api.routes.webhooks.Runner.run", new_callable=AsyncMock) as mock_runner:
            with patch("src.api.routes.webhooks.send_message", new_callable=AsyncMock) as mock_send:
                mock_send.return_value = {"success": True, "status_code": 200, "error_message": None}

                await webhooks.process_webhook_payload(phone, "msg-confirm", "Quero confirmar minha consulta")

                mock_runner.assert_not_called()
                mock_send.assert_called_once()
                assert "presença foi confirmada" in mock_send.call_args.args[1]

    asyncio.run(_run())

    with Session(engine) as session:
        updated = session.exec(select(Appointment)).first()
        assert updated is not None
        assert updated.status == "confirmed"


def test_webhook_small_talk_bypass_llm():
    _clean_db()
    _reset_webhook_runtime_state()

    async def _run():
        with patch("src.api.routes.webhooks.Runner.run", new_callable=AsyncMock) as mock_runner:
            with patch("src.api.routes.webhooks.send_message", new_callable=AsyncMock) as mock_send:
                mock_send.return_value = {"success": True, "status_code": 200, "error_message": None}

                await webhooks.process_webhook_payload("5511987778888", "msg-small-talk", "Boa tarde")

                mock_runner.assert_not_called()
                mock_send.assert_called_once()
                assert "Falar com atendente" in mock_send.call_args.args[1]

    asyncio.run(_run())


def test_handoff_sticky_blocks_non_scope_until_supported_scope_returns():
    _clean_db()
    _reset_webhook_runtime_state()

    async def _run():
        with patch("src.api.routes.webhooks.Runner.run", new_callable=AsyncMock) as mock_runner:
            with patch("src.api.routes.webhooks.send_message", new_callable=AsyncMock) as mock_send:
                mock_send.return_value = {"success": True, "status_code": 200, "error_message": None}
                mock_runner.return_value = _FakeRunnerResult("Posso ajudar com seu agendamento.")

                phone = "5511977700001"
                await webhooks.process_webhook_payload(phone, "msg-h1", "Qual o valor da consulta?")
                await webhooks.process_webhook_payload(phone, "msg-h2", "Me manda uma foto")
                await webhooks.process_webhook_payload(phone, "msg-h3", "Quero agendar uma consulta")

                assert mock_runner.call_count == 1
                assert mock_send.call_count == 3
                assert mock_send.call_args_list[0].args[1] == webhooks.HANDOFF_REPLY
                assert mock_send.call_args_list[1].args[1] == webhooks.HANDOFF_REPLY
                assert "agendamento" in mock_send.call_args_list[2].args[1].lower()

    asyncio.run(_run())


def test_inline_tool_guard_escalates_when_too_many_tags():
    _clean_db()
    _reset_webhook_runtime_state()

    inline_tags = (
        '<function=find_patient_appointments>{"phone":"5511999990000"}</function>\n'
        '<function=find_patient_appointments>{"phone":"5511999990000"}</function>\n'
        '<function=find_patient_appointments>{"phone":"5511999990000"}</function>\n'
        '<function=find_patient_appointments>{"phone":"5511999990000"}</function>'
    )

    async def _run():
        with patch("src.api.routes.webhooks.Runner.run", new_callable=AsyncMock) as mock_runner:
            with patch("src.api.routes.webhooks.send_message", new_callable=AsyncMock) as mock_send:
                mock_send.return_value = {"success": True, "status_code": 200, "error_message": None}
                mock_runner.return_value = _FakeRunnerResult(inline_tags)

                phone = "5511977700002"
                await webhooks.process_webhook_payload(phone, "msg-inline-guard", "Quero verificar minha consulta de amanhã")

                mock_runner.assert_called_once()
                mock_send.assert_called_once()
                assert "instabilidade momentânea" in mock_send.call_args.args[1]
                assert phone in webhooks._phone_handoff_until

    asyncio.run(_run())
