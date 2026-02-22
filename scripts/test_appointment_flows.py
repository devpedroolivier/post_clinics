import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.application.tools import _schedule_appointment, _reschedule_appointment, _cancel_appointment, _find_patient_appointments
from src.infrastructure.database import engine
from src.domain.models import Appointment, Patient
from sqlmodel import Session, select

def setup_dummy_appointment():
    # Schedule a dummy appointment for tomorrow at 10:00
    tomorrow = datetime.now() + timedelta(days=1)
    date_str = tomorrow.strftime("%Y-%m-%d 10:00")
    
    print(f"Scheduling initial appointment for {date_str}...")
    res = _schedule_appointment("Test Patient", "5511000000000", date_str, "Clínica Geral")
    print(res)
    
    # We need the ID
    with Session(engine) as session:
        patient = session.exec(select(Patient).where(Patient.phone == "5511000000000")).first()
        appt = session.exec(select(Appointment).where(Appointment.patient_id == patient.id).order_by(Appointment.id.desc())).first()
        return appt.id, tomorrow

def run_tests():
    print("--- STARTING TESTS ---")
    appt_id, tomorrow = setup_dummy_appointment()
    
    if not appt_id:
        print("Failed to setup appointment.")
        return

    # Test 1: Reschedule to a valid time
    new_time_1 = tomorrow.strftime("%Y-%m-%d 14:00")
    print(f"\n[Test 1] Reschedule to {new_time_1}")
    res1 = _reschedule_appointment(appt_id, new_time_1)
    print(res1)
    
    # Test 2: Double cancel
    print(f"\n[Test 2] First Cancel")
    res2 = _cancel_appointment(appt_id)
    print(res2)

    print(f"\n[Test 3] Second Cancel (Double Cancel)")
    res3 = _cancel_appointment(appt_id)
    print(res3)
    
    # Test 4: Reschedule a cancelled appointment
    new_time_2 = tomorrow.strftime("%Y-%m-%d 15:00")
    print(f"\n[Test 4] Reschedule cancelled appointment")
    res4 = _reschedule_appointment(appt_id, new_time_2)
    print(res4)
    
    # Cleanup
    with Session(engine) as session:
        appt = session.get(Appointment, appt_id)
        if appt:
            session.delete(appt)
            session.commit()
    print("\n--- TESTS FINISHED ---")

if __name__ == "__main__":
    run_tests()
