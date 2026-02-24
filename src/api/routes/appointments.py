from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime

from src.core.security import verify_token
from src.infrastructure.database import engine
from src.domain.models import Appointment, Patient
from src.domain.schemas import AppointmentCreate, AppointmentUpdate

router = APIRouter(prefix="/api/appointments", tags=["Appointments"], dependencies=[Depends(verify_token)])

@router.get("")
async def get_appointments(include_cancelled: bool = False):
    """
    Fetch all scheduled appointments for the dashboard.
    Returns appointment data with patient information.
    """
    with Session(engine) as session:
        statement = select(Appointment, Patient).join(Patient)
        if not include_cancelled:
            statement = statement.where(Appointment.status != "cancelled")
        results = session.exec(statement).all()
        
        appointments = []
        for appointment, patient in results:
            appointments.append({
                "id": appointment.id,
                "patient_name": patient.name,
                "patient_phone": patient.phone,
                "datetime": appointment.datetime.isoformat(),
                "service": appointment.service,
                "professional": appointment.professional,
                "status": appointment.status,
                "created_at": appointment.created_at.isoformat()
            })
        
        return {"appointments": appointments}

@router.post("")
async def create_appointment(data: AppointmentCreate):
    """
    Manually create an appointment via Dashboard.
    """
    try:
        dt = datetime.fromisoformat(data.datetime)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")

    with Session(engine) as session:
        statement = select(Patient).where(Patient.phone == data.patient_phone)
        patient = session.exec(statement).first()
        
        if not patient:
            patient = Patient(name=data.patient_name, phone=data.patient_phone)
            session.add(patient)
            session.commit()
            session.refresh(patient)
            
        appointment = Appointment(
            patient_id=patient.id,
            datetime=dt,
            service=data.service,
            professional=data.professional,
            status="confirmed"
        )
        session.add(appointment)
        session.commit()
        session.refresh(appointment)
        
        return {"status": "success", "id": appointment.id}

@router.put("/{appointment_id}")
async def update_appointment(appointment_id: int, data: AppointmentUpdate):
    """
    Update an existing appointment.
    """
    with Session(engine) as session:
        appointment = session.get(Appointment, appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        if data.datetime:
            try:
                appointment.datetime = datetime.fromisoformat(data.datetime)
            except ValueError:
               raise HTTPException(status_code=400, detail="Invalid datetime format")
        
        if data.status:
            appointment.status = data.status

        if data.service:
            appointment.service = data.service

        if data.professional:
            appointment.professional = data.professional

        if data.patient_name or data.patient_phone:
            patient = session.get(Patient, appointment.patient_id)
            if patient:
                if data.patient_name:
                    patient.name = data.patient_name
                if data.patient_phone:
                    patient.phone = data.patient_phone
                session.add(patient)

        session.add(appointment)
        session.commit()
        session.refresh(appointment)
        
        return {"status": "success", "id": appointment.id}

@router.delete("/{appointment_id}")
async def delete_appointment(appointment_id: int):
    """
    Delete an appointment.
    """
    with Session(engine) as session:
        appointment = session.get(Appointment, appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
            
        session.delete(appointment)
        session.commit()
        
        return {"status": "success"}
