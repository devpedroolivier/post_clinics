import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, select
from src.infrastructure.database import engine
from src.domain.models import Appointment, Patient
from src.application.tools import _check_availability, _schedule_appointment, _reschedule_appointment
from sqlmodel import delete

@pytest.fixture(name="session", autouse=True)
def session_fixture():
    with Session(engine) as session:
        session.exec(delete(Appointment))
        session.exec(delete(Patient))
        session.commit()
        yield session

def test_grid_generation_45min():
    # Test availability for Ortodontia (08:00 start, 45min duration)
    # Expected slots: 08:00, 08:45, 09:30, 10:15, 11:00 (5 slots)
    # Afternoon slots: 13:00, 13:45, 14:30...
    result = _check_availability("2026-03-02", "Ortodontia")
    assert "08:00" in result
    assert "08:45" in result
    assert "13:00" in result
    assert "13:45" in result
    # It should return 5 slots total (2 morning + 3 afternoon as per our logic)
    slots = result.split(": ")[-1].split(", ")
    assert len(slots) == 5

def test_professional_separation(session):
    # Book a slot for Ortodontia
    _schedule_appointment("Test Orto", "5511999990001", "2026-03-02 09:00", "Ortodontia")
    
    # Check availability for Ortodontia at 09:00 - should be busy or not in grid
    # Grid for Orto: 08:00, 08:45, 09:30... 09:00 is not a grid start, but overlaps with 08:45 (08:45-09:30)
    result_orto = _check_availability("2026-03-02", "Ortodontia")
    assert "08:45" not in result_orto # Overlaps with 09:00-09:45
    
    # Check availability for Dra. Débora - should be FREE at 09:00 (different professional)
    result_debora = _check_availability("2026-03-02", "Clínica Geral")
    assert "09:00" in result_debora

def test_collision_detection():
    # Book Dr. Sidney at 10:00
    _schedule_appointment("P1", "55110001", "2026-03-03 10:00", "Clínica Geral")
    
    # Try to book same professional at 10:30 (overlaps since duration is 45min)
    res = _schedule_appointment("P2", "55110002", "2026-03-03 10:30", "Clínica Geral")
    assert "Conflito de horário" in res
    
    # Try to book same professional at 10:45 (exactly when first ends)
    res = _schedule_appointment("P3", "55110003", "2026-03-03 10:45", "Clínica Geral")
    assert "Agendamento confirmado" in res

def test_reschedule_with_professional_check():
    # P1 at 14:30
    _schedule_appointment("P1", "55110001", "2026-03-04 14:30", "Clínica Geral")
    # P2 at 15:30
    _schedule_appointment("P2", "55110002", "2026-03-04 15:30", "Clínica Geral")
    
    # Find P1 ID
    with Session(engine) as session:
        p1_appt = session.exec(select(Appointment).where(Appointment.service == "Clínica Geral", Appointment.datetime == datetime(2026, 3, 4, 14, 30))).first()
        p1_id = p1_appt.id
        
    # Reschedule P1 to 15:30 (collision with P2)
    res = _reschedule_appointment(p1_id, "2026-03-04 15:30")
    assert "Conflito de horário" in res
    
    # Reschedule P1 to 16:15 (free)
    res = _reschedule_appointment(p1_id, "2026-03-04 16:15")
    assert "reagendado" in res
