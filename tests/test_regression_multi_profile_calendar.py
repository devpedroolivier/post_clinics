import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from sqlmodel import Session, delete, select

from src.application.scheduler import BR_TZ, check_and_send_reminders
from src.application.tools import _find_patient_appointments, _schedule_appointment
from src.domain.models import Appointment, NotificationLog, Patient
from src.infrastructure.database import engine


@pytest.fixture(autouse=True)
def clean_db():
    with Session(engine) as session:
        session.exec(delete(NotificationLog))
        session.exec(delete(Appointment))
        session.exec(delete(Patient))
        session.commit()
    yield


def test_michely_isis_same_phone_keeps_separate_patient_identity(client, auth_headers):
    phone = "5511912345678"
    payload_a = {
        "patient_name": "Michely",
        "patient_phone": phone,
        "responsible_name": "Michely",
        "datetime": "2026-03-24T08:00:00",
        "service": "Ortodontia",
        "professional": "Dr. Ewerton",
        "status": "confirmed",
    }
    payload_b = {
        "patient_name": "Isis",
        "patient_phone": phone,
        "responsible_name": "Michely",
        "datetime": "2026-03-24T08:30:00",
        "service": "Ortodontia",
        "professional": "Dr. Ewerton",
        "status": "confirmed",
    }

    resp_a = client.post("/api/appointments", headers=auth_headers, json=payload_a)
    resp_b = client.post("/api/appointments", headers=auth_headers, json=payload_b)
    assert resp_a.status_code == 200
    assert resp_b.status_code == 200

    with Session(engine) as session:
        patients = session.exec(select(Patient).where(Patient.contact_phone == phone)).all()
        assert sorted(p.name for p in patients) == ["Isis", "Michely"]
        assert len({p.id for p in patients}) == 2

        appts = session.exec(
            select(Appointment, Patient)
            .join(Patient)
            .order_by(Appointment.datetime)
        ).all()
        assert appts[0][1].name == "Michely"
        assert appts[1][1].name == "Isis"

    listed = client.get("/api/appointments?include_cancelled=true", headers=auth_headers)
    assert listed.status_code == 200
    names = [a["patient_name"] for a in listed.json()["appointments"]]
    assert "Michely" in names
    assert "Isis" in names

    found = _find_patient_appointments(phone)
    assert "Michely" in found
    assert "Isis" in found


def test_schedule_does_not_overwrite_patient_name_when_same_phone():
    phone = "5511988887777"
    first = _schedule_appointment("Michely", phone, "2026-03-24 08:00", "Ortodontia")
    second = _schedule_appointment("Isis", phone, "2026-03-24 08:45", "Ortodontia")
    assert "Agendamento confirmado" in first
    assert "Agendamento confirmado" in second

    with Session(engine) as session:
        patients = session.exec(select(Patient).where(Patient.contact_phone == phone)).all()
        assert sorted(p.name for p in patients) == ["Isis", "Michely"]


def test_update_appointment_relinks_patient_without_overwriting_shared_contact(client, auth_headers):
    phone = "5511977776666"
    first = client.post(
        "/api/appointments",
        headers=auth_headers,
        json={
            "patient_name": "Michely",
            "patient_phone": phone,
            "datetime": "2026-03-24T08:00:00",
            "service": "Ortodontia",
            "professional": "Dr. Ewerton",
        },
    )
    second = client.post(
        "/api/appointments",
        headers=auth_headers,
        json={
            "patient_name": "Isis",
            "patient_phone": phone,
            "datetime": "2026-03-24T08:30:00",
            "service": "Ortodontia",
            "professional": "Dr. Ewerton",
        },
    )
    assert first.status_code == 200
    assert second.status_code == 200
    second_id = second.json()["id"]

    updated = client.put(
        f"/api/appointments/{second_id}",
        headers=auth_headers,
        json={"patient_name": "Isis Ribeiro"},
    )
    assert updated.status_code == 200

    listed = client.get("/api/appointments?include_cancelled=true", headers=auth_headers).json()["appointments"]
    names = sorted(item["patient_name"] for item in listed)
    assert names == ["Isis Ribeiro", "Michely"]


def test_calendar_sync_is_idempotent_for_reminders():
    async def _run():
        with Session(engine) as session:
            patient = Patient(name="Paciente Teste", phone="5511999999999", contact_phone="5511999999999")
            session.add(patient)
            session.commit()
            session.refresh(patient)

            appt = Appointment(
                patient_id=patient.id,
                datetime=datetime.now(BR_TZ).replace(tzinfo=None) + timedelta(hours=23),
                service="Clínica Geral",
                professional="Dra. Débora / Dr. Sidney",
                status="confirmed",
            )
            session.add(appt)
            session.commit()
            session.refresh(appt)

        mock_res = {"success": True, "status_code": 200, "error_message": None}
        with patch("src.application.scheduler.send_message", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_res
            await check_and_send_reminders()
            await check_and_send_reminders()
            assert mock_send.call_count == 1

        with Session(engine) as session:
            appt_after = session.exec(select(Appointment)).first()
            assert appt_after is not None
            assert appt_after.status == "scheduled"
            assert appt_after.notified_24h is True
            logs = session.exec(select(NotificationLog)).all()
            assert len(logs) == 1

    asyncio.run(_run())


def test_calendar_status_metadata_and_colors_are_exposed(client, auth_headers):
    base_phone = "5511900000000"
    statuses = ["confirmed", "scheduled", "rescheduled", "cancelled"]
    for idx, status in enumerate(statuses):
        resp = client.post(
            "/api/appointments",
            headers=auth_headers,
            json={
                "patient_name": f"Paciente {idx}",
                "patient_phone": f"{base_phone}{idx}",
                "datetime": f"2026-05-0{idx + 1}T09:00:00",
                "service": "Clínica Geral",
                "professional": "Dra. Débora / Dr. Sidney",
                "status": status,
            },
        )
        assert resp.status_code == 200

    listed = client.get("/api/appointments?include_cancelled=true", headers=auth_headers)
    assert listed.status_code == 200
    appointments = listed.json()["appointments"]
    assert len(appointments) == 4
    for item in appointments:
        assert "status_color" in item
        assert "status_description" in item
        assert "calendar_description" in item
        assert "Legenda:" in item["calendar_description"]
