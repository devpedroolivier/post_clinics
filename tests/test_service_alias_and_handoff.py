import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from sqlmodel import Session, delete, select

from src.application.tools import _check_availability, _get_available_services, _schedule_appointment
from src.api.routes import webhooks
from src.domain.models import Appointment, NotificationLog, Patient
from src.infrastructure.database import engine


class _FakeRunnerResult:
    def __init__(self, final_output: str):
        self.final_output = final_output


@pytest.fixture(autouse=True)
def clean_db_and_webhook_state():
    with Session(engine) as session:
        session.exec(delete(NotificationLog))
        session.exec(delete(Appointment))
        session.exec(delete(Patient))
        session.commit()

    webhooks._phone_out_of_scope_attempts.clear()
    webhooks._phone_timestamps.clear()
    webhooks._seen_messages.clear()
    yield


def test_service_alias_keeps_compatibility_with_legacy_name():
    result = _schedule_appointment(
        name="Paciente Alias",
        phone="5511990000001",
        datetime_str="2026-06-10 09:00",
        service_name="Odontopediatria (Retorno)",
    )
    assert "Agendamento confirmado" in result

    with Session(engine) as session:
        appointment = session.exec(select(Appointment)).first()
        assert appointment is not None
        assert appointment.service == "Odontopediatria (Consulta)"

    availability = _check_availability("2026-06-10", "Odontopediatria (Retorno)")
    assert "Odontopediatria (Consulta)" in availability

    services = _get_available_services()
    assert "Odontopediatria (Consulta)" in services
    assert "Odontopediatria (Retorno)" not in services


def test_handoff_routes_financial_messages_without_llm():
    async def _run():
        with patch("src.api.routes.webhooks.send_message", new_callable=AsyncMock) as mock_send:
            with patch("src.api.routes.webhooks.Runner.run", new_callable=AsyncMock) as mock_runner:
                mock_send.return_value = {"success": True, "status_code": 200, "error_message": None}
                await webhooks.process_webhook_payload("5511990000002", "msg-handoff-fin", "Qual o preço da consulta?")
                mock_runner.assert_not_called()
                mock_send.assert_called_once()
                assert webhooks.HANDOFF_REPLY in mock_send.call_args.args[1]

    asyncio.run(_run())

def test_handoff_after_two_out_of_scope_attempts():
    async def _run():
        with patch("src.api.routes.webhooks.send_message", new_callable=AsyncMock) as mock_send:
            with patch("src.api.routes.webhooks.Runner.run", new_callable=AsyncMock) as mock_runner:
                mock_send.return_value = {"success": True, "status_code": 200, "error_message": None}
                mock_runner.return_value = _FakeRunnerResult("Posso ajudar com agendamentos.")

                phone = "5511990000003"
                await webhooks.process_webhook_payload(phone, "msg-scope-1", "Vocês vendem escova?")
                await webhooks.process_webhook_payload(phone, "msg-scope-2", "Também queria saber sobre produtos.")

                # First out-of-scope still goes to the agent, second escalates to human.
                assert mock_runner.call_count == 1
                assert mock_send.call_count == 2
                assert webhooks.HANDOFF_REPLY in mock_send.call_args.args[1]

    asyncio.run(_run())
