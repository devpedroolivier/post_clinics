import sys
import os
from datetime import datetime
from sqlmodel import Session, select

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.infrastructure.database import engine, create_db_and_tables
from src.domain.models import Appointment, Patient
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

def seed_appointment(date_str, time_str, patient_name="Test Patient", patient_phone="5511999999999", status="confirmed"):
    """
    Seeds an appointment into the database.
    """
    dt_str = f"{date_str} {time_str}"
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    
    with Session(engine) as session:
        # Check/Create Patient
        try:
            print(f"Engine URL: {engine.url}")
            patient = session.exec(select(Patient).where(Patient.phone == patient_phone)).first()
            if not patient:
                print("Creating Patient...")
                patient = Patient(name=patient_name, phone=patient_phone)
                session.add(patient)
                print("Committing Patient...")
                session.commit()
                session.refresh(patient)
                print(f"Created patient: {patient.name} ({patient.id})")
        
            # Create Appointment
            print("Creating Appointment...")
            appt = Appointment(patient_id=patient.id, datetime=dt, status=status)
            session.add(appt)
            print("Committing Appointment...")
            session.commit()
            print("Refresh Appointment...")
            session.refresh(appt)
            print(f"Seeded appointment: ID {appt.id} at {dt} [{status}]")
            return appt.id
        except Exception as e:
            print(f"ERROR SEEDING: {e}")
            import traceback
            traceback.print_exc()
            session.rollback()
            raise

def clear_test_data(phone="5511999999999"):
    """
    Removes test data associated with the test phone number.
    """
    with Session(engine) as session:
        patient = session.exec(select(Patient).where(Patient.phone == phone)).first()
        if patient:
            # Delete appointments
            appointments = session.exec(select(Appointment).where(Appointment.patient_id == patient.id)).all()
            for appt in appointments:
                session.delete(appt)
            
            # Delete patient
            session.delete(patient)
            session.commit()
            print(f"Cleared data for phone {phone}")

if __name__ == "__main__":
    print("Starting seeder...")
    import argparse
    parser = argparse.ArgumentParser(description="Seed test data")
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--time", required=True, help="HH:MM")
    parser.add_argument("--phone", default="5511999999999", help="Patient Phone")
    parser.add_argument("--clear", action="store_true", help="Clear data for this phone before seeding")
    
    args = parser.parse_args()
    
    print("Ensuring tables exist...")
    try:
        create_db_and_tables()
        print("Tables checked.")
    except Exception as e:
        print(f"ERROR CREATING TABLES: {e}")
        exit(1)
    
    if args.clear:
        print("Clearing data...")
        clear_test_data(args.phone)
        
    print("Seeding appointment...")
    seed_appointment(args.date, args.time, patient_phone=args.phone)
    print("Done.")
