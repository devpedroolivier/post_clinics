import sys
import os
from datetime import datetime
import re

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd()))

# Import UNDECORATED functions from tools (the core logic)
from src.application.tools import (
    _check_availability, 
    _schedule_appointment, 
    _get_available_services, 
    _reschedule_appointment, 
    _cancel_appointment,
    get_service_info
)
from src.infrastructure.database import create_db_and_tables, engine
from src.domain.models import Appointment, Patient
from sqlmodel import Session, delete

def test_logic():
    print("--- Testing Scheduling Logic ---")
    create_db_and_tables()
    
    # Clean DB for test
    with Session(engine) as session:
        session.exec(delete(Appointment))
        session.exec(delete(Patient))
        session.commit()

    # 1. Test Info Lookup
    info = get_service_info("Odontopediatria (1ª vez)")
    print(f"Duration 'Odontopediatria (1ª vez)': {info['duration']} (Expected 60)")
    assert info['duration'] == 60
    
    info = get_service_info("Clínica Geral")
    print(f"Duration 'Clínica Geral': {info['duration']} (Expected 45)")
    assert info['duration'] == 45

    # 2. Schedule Initial Appointment (09:00 - 09:45)
    print("\n--- Scheduling 'Clínica Geral' at 09:00 ---")
    res = _schedule_appointment(name="Test User", phone="123", datetime_str="2025-05-20 09:00", service_name="Clínica Geral")
    print(res)
    assert "Agendamento confirmado" in res
    
    # Extract ID for later tests
    match = re.search(r'ID: (\d+)', res)
    appt_id = int(match.group(1))
    print(f"Initial Appointment ID: {appt_id}")

    # 3. Check Availability for 60 min service
    print("\n--- Checking 60min Service Availability ---")
    slots_60 = _check_availability("2025-05-20", "Odontopediatria (1ª vez)") # 60 min
    print(slots_60)
    # The grid for 60min is 09:00, 10:00, 11:00...
    # Since there's an appt at 09:00, it's NOT free
    assert "09:00" not in slots_60
    assert "10:00" in slots_60
    
    # 4. Check Availability for 45 min service
    print("\n--- Checking 45min Service Availability ---")
    slots_45 = _check_availability("2025-05-20", "Clínica Geral") # 45 min
    print(slots_45)
    # Grid: 09:00, 09:45, 10:30...
    assert "09:00" not in slots_45
    assert "09:45" in slots_45

    # 5. Try to Schedule Overlap
    print("\n--- Trying to Schedule Overlap (09:30) ---")
    res_fail = _schedule_appointment(name="Fail User", phone="456", datetime_str="2025-05-20 09:30", service_name="Clínica Geral")
    print(res_fail)
    assert "Conflito de horário" in res_fail

    # 6. Test Reschedule
    print("\n--- Testing Reschedule (09:00 -> 14:30) ---")
    res_resched = _reschedule_appointment(appt_id, "2025-05-20 14:30")
    print(res_resched)
    assert "reagendado" in res_resched
    
    # Verify old slot (09:00) is free now
    print("Verifying old slot (09:00) is free...")
    slots_after_move = _check_availability("2025-05-20", "Clínica Geral")
    assert "09:00" in slots_after_move
    
    # Verify new slot (14:30) is taken
    assert "14:30" not in slots_after_move

    # 7. Test Cancel
    print("\n--- Testing Cancel ---")
    res_cancel = _cancel_appointment(appt_id)
    print(res_cancel)
    assert "cancelado com sucesso" in res_cancel
    
    # Verify it's free
    slots_after_cancel = _check_availability("2025-05-20", "Clínica Geral")
    assert "14:30" in slots_after_cancel

    # 8. Test Services List
    print("\n--- Testing Services List ---")
    svcs = _get_available_services()
    print(svcs)
    assert "Odontopediatria" in svcs

    print("\n[PASS] All Tests Passed")

if __name__ == "__main__":
    test_logic()
