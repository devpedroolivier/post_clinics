from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime

from src.core.security import verify_token
from src.infrastructure.database import engine
from src.domain.models import Appointment, Patient
from src.domain.schemas import AppointmentCreate, AppointmentUpdate
from src.application.services.appointment_status import (
    build_status_legend_description,
    get_status_metadata,
    normalize_status,
)
from src.application.services.patient_identity import (
    get_contact_phone,
    resolve_patient_for_contact,
)
from src.application.services.service_catalog import canonicalize_service_name

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
            status_meta = get_status_metadata(appointment.status)
            appointments.append({
                "id": appointment.id,
                "patient_name": patient.name,
                "patient_phone": get_contact_phone(patient),
                "responsible_name": patient.responsible_name,
                "datetime": appointment.datetime.isoformat(),
                "service": canonicalize_service_name(appointment.service),
                "professional": appointment.professional,
                "status": status_meta["status"],
                "status_label": status_meta["label"],
                "status_color": status_meta["color"],
                "status_description": status_meta["description"],
                "calendar_description": build_status_legend_description(status_meta["status"]),
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
        patient = resolve_patient_for_contact(
            session,
            name=data.patient_name,
            phone=data.patient_phone,
            responsible_name=data.responsible_name,
        )
            
        appointment = Appointment(
            patient_id=patient.id,
            datetime=dt,
            service=canonicalize_service_name(data.service),
            professional=data.professional,
            status=normalize_status(data.status, default="scheduled")
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
            appointment.status = normalize_status(data.status, default=appointment.status)

        if data.service:
            appointment.service = canonicalize_service_name(data.service)

        if data.professional:
            appointment.professional = data.professional

        if data.patient_name or data.patient_phone or data.responsible_name is not None:
            current_patient = session.get(Patient, appointment.patient_id)
            if current_patient:
                resolved_patient = resolve_patient_for_contact(
                    session,
                    name=data.patient_name or current_patient.name,
                    phone=data.patient_phone or get_contact_phone(current_patient),
                    responsible_name=(
                        data.responsible_name
                        if data.responsible_name is not None
                        else current_patient.responsible_name
                    ),
                )
                appointment.patient_id = resolved_patient.id

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
