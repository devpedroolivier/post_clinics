from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime
from typing import Optional

from src.core.security import verify_token
from src.infrastructure.database import engine
from src.domain.models import Appointment, Patient
from src.domain.schemas import AppointmentCreate, AppointmentUpdate
from src.application.services.appointment_status import (
    build_status_legend_description,
    get_status_metadata,
)
from src.application.services.patient_identity import (
    get_contact_phone,
)
from src.application.services.service_catalog import canonicalize_service_name
from src.application.services import appointment_manager

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
async def create_appointment(data: AppointmentCreate, force: bool = False):
    """
    Manually create an appointment via Dashboard.
    """
    try:
        dt = datetime.fromisoformat(data.datetime)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")

    with Session(engine) as session:
        try:
            appt = appointment_manager.create_appointment(
                session,
                patient_name=data.patient_name,
                patient_phone=data.patient_phone,
                dt=dt,
                service_name=data.service,
                professional=data.professional,
                status=data.status or "scheduled",
                responsible_name=data.responsible_name,
                force=force
            )
            return {"status": "success", "id": appt.id}
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e)) # Conflict

@router.put("/{appointment_id}")
async def update_appointment(appointment_id: int, data: AppointmentUpdate, force: bool = False):
    """
    Update an existing appointment.
    """
    try:
        dt = datetime.fromisoformat(data.datetime) if data.datetime else None
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")

    with Session(engine) as session:
        try:
            appt = appointment_manager.update_appointment(
                session,
                appointment_id=appointment_id,
                dt=dt,
                service_name=data.service,
                professional=data.professional,
                status=data.status,
                patient_name=data.patient_name,
                patient_phone=data.patient_phone,
                responsible_name=data.responsible_name,
                force=force
            )
            return {"status": "success", "id": appt.id}
        except KeyError:
            raise HTTPException(status_code=404, detail="Appointment not found")
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e)) # Conflict

@router.delete("/{appointment_id}")
async def delete_appointment(appointment_id: int):
    """
    Delete an appointment (hard delete).
    """
    with Session(engine) as session:
        appt = session.get(Appointment, appointment_id)
        if not appt:
            raise HTTPException(status_code=404, detail="Appointment not found")
            
        session.delete(appt)
        session.commit()
        
        return {"status": "success"}

