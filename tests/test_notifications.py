import pytest
import asyncio
from datetime import datetime, timedelta
from sqlmodel import Session, select, delete
from src.infrastructure.database import engine
from src.domain.models import Appointment, Patient, NotificationLog
from src.application.scheduler import BR_TZ, check_and_send_reminders
from unittest.mock import patch, AsyncMock

@pytest.fixture(name="session", autouse=True)
def session_fixture():
    with Session(engine) as session:
        session.exec(delete(NotificationLog))
        session.exec(delete(Appointment))
        session.exec(delete(Patient))
        session.commit()
        yield session

def _now_br_naive() -> datetime:
    return datetime.now(BR_TZ).replace(tzinfo=None)


def test_scheduler_threshold_logic():
    """Test that reminders are sent within thresholds and flags are updated."""
    async def _run():
        with Session(engine) as session:
            patient = Patient(name="Test Patient", phone="5511999999999")
            session.add(patient)
            session.commit()
            session.refresh(patient)
            
            # Appt in 23 hours (should trigger 24h reminder)
            appt_24h = Appointment(
                patient_id=patient.id,
                datetime=_now_br_naive() + timedelta(hours=23),
                service="Clínica Geral",
                status="confirmed"
            )
            # Appt in 2 hours (should trigger 3h reminder)
            appt_3h = Appointment(
                patient_id=patient.id,
                datetime=_now_br_naive() + timedelta(hours=2),
                service="Clínica Geral",
                status="confirmed"
            )
            session.add(appt_24h)
            session.add(appt_3h)
            session.commit()
            session.refresh(appt_24h)
            session.refresh(appt_3h)

        # Mock send_message to return success
        mock_res = {"success": True, "status_code": 200, "error_message": None}
        with patch("src.application.scheduler.send_message", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_res
            
            await check_and_send_reminders()
            
            # Verify 2 calls were made
            assert mock_send.call_count == 2
            
        # Verify flags and logs
        with Session(engine) as session:
            a24 = session.get(Appointment, appt_24h.id)
            a3 = session.get(Appointment, appt_3h.id)
            
            assert a24.notified_24h is True
            assert a3.notified_3h is True
            
            logs = session.exec(select(NotificationLog)).all()
            assert len(logs) == 2
            assert any(l.notification_type == "24h" and l.status == "sent" for l in logs)
            assert any(l.notification_type == "3h" and l.status == "sent" for l in logs)

    asyncio.run(_run())

def test_late_booking_protection():
    """Test that 24h reminders are skipped for appointments booked on short notice."""
    async def _run():
        with Session(engine) as session:
            patient = Patient(name="Late Patient", phone="5511000000000")
            session.add(patient)
            session.commit()
            
            # Appt in 10 hours (less than 20h threshold)
            appt = Appointment(
                patient_id=patient.id,
                datetime=_now_br_naive() + timedelta(hours=10),
                service="Clínica Geral",
                status="confirmed"
            )
            session.add(appt)
            session.commit()
            session.refresh(appt)

        with patch("src.application.scheduler.send_message", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {"success": True, "status_code": 200, "error_message": None}
            
            await check_and_send_reminders()
            
            # Should only call once for 3h reminder (since 10h < 24.5h and > 0.5h)
            # Wait, actually check_and_send_reminders marks notified_24h = True for late bookings and continues.
            # If it's 10h away, it's NOT within 3h threshold (0.5-3.5h).
            # So it should only mark 24h as True and send NOTHING.
            assert mock_send.call_count == 0
            
        with Session(engine) as session:
            a = session.get(Appointment, appt.id)
            assert a.notified_24h is True # Marked as skipped
            assert a.notified_3h is False # Not yet time

    asyncio.run(_run())


def test_notification_failure_logging():
    """Test that Z-API failures are logged but flags are not set to True."""
    async def _run():
        with Session(engine) as session:
            patient = Patient(name="Fail Patient", phone="5511000000001")
            session.add(patient)
            session.commit()
            
            appt = Appointment(
                patient_id=patient.id,
                datetime=_now_br_naive() + timedelta(hours=24),
                service="Clínica Geral",
                status="confirmed"
            )
            session.add(appt)
            session.commit()
            session.refresh(appt)

        mock_fail = {"success": False, "status_code": 400, "error_message": "Invalid number"}
        with patch("src.application.scheduler.send_message", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_fail
            
            await check_and_send_reminders()
            
        with Session(engine) as session:
            a = session.get(Appointment, appt.id)
            assert a.notified_24h is False # Remains False to retry later if it was 5xx, or just stay False if 4xx
            
            log = session.exec(select(NotificationLog).where(NotificationLog.appointment_id == appt.id)).first()
            assert log.status == "failed"
            assert log.error_message == "Invalid number"

    asyncio.run(_run())
