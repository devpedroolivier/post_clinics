from datetime import datetime, timedelta
from typing import Optional, List, Tuple

from sqlmodel import Session, select
from src.domain.models import Appointment, Patient
from src.core.config import CLINIC_CONFIG
from src.application.services.patient_identity import resolve_patient_for_contact
from src.application.services.service_catalog import canonicalize_service_name
from src.application.services.appointment_status import normalize_status
import difflib

def get_service_info(service_name: str) -> dict:
    """Helper to get service info (duration, professional) with fuzzy matching."""
    default_resp = {"duration": 45, "professional": "Clínica Geral"}
    if not service_name:
        return default_resp
    service_name = canonicalize_service_name(service_name)
        
    services = CLINIC_CONFIG.get("services", [])
    service_names = [canonicalize_service_name(s["name"]) for s in services]
    
    # 1. Exact or close match
    matches = difflib.get_close_matches(service_name, service_names, n=1, cutoff=0.6)
    if matches:
        best_match = matches[0]
        for s in services:
            if canonicalize_service_name(s["name"]) == best_match:
                return {
                    "duration": s.get("duration", 45),
                    "professional": s.get("professional", "Clínica Geral")
                }
                
    # 2. Substring fallback
    for s in services:
        canonical = canonicalize_service_name(s["name"])
        if service_name.lower() in canonical.lower() or canonical.lower() in service_name.lower():
            return {
                "duration": s.get("duration", 45),
                "professional": s.get("professional", "Clínica Geral")
            }
            
    return default_resp

def check_conflicts(
    session: Session,
    professional: str,
    start_dt: datetime,
    duration_minutes: int,
    exclude_id: Optional[int] = None
) -> Optional[Appointment]:
    """Returns the first conflicting appointment, or None."""
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    
    # Daily range for performance optimization
    day_start = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = start_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    statement = select(Appointment).where(
        Appointment.datetime >= day_start,
        Appointment.datetime <= day_end,
        Appointment.status != "cancelled",
        Appointment.professional == professional
    )
    if exclude_id:
        statement = statement.where(Appointment.id != exclude_id)
        
    existing_appointments = session.exec(statement).all()
    
    for appt in existing_appointments:
        appt_info = get_service_info(appt.service)
        appt_end = appt.datetime + timedelta(minutes=appt_info["duration"])
        
        # Overlap: (StartA < EndB) and (EndA > StartB)
        if start_dt < appt_end and end_dt > appt.datetime:
            return appt
            
    return None

def create_appointment(
    session: Session,
    patient_name: str,
    patient_phone: str,
    dt: datetime,
    service_name: str = "Clínica Geral",
    professional: Optional[str] = None,
    status: str = "scheduled",
    responsible_name: Optional[str] = None,
    force: bool = False
) -> Appointment:
    """Core logic to create an appointment."""
    canonical_service = canonicalize_service_name(service_name)
    info = get_service_info(canonical_service)
    
    # If professional not provided, use the one from service info
    if not professional:
        professional = info["professional"]
        
    patient = resolve_patient_for_contact(
        session,
        name=patient_name,
        phone=patient_phone,
        responsible_name=responsible_name,
    )
    
    if not force:
        conflict = check_conflicts(session, professional, dt, info["duration"])
        if conflict:
            raise ValueError(f"Horário ocupado pelo agendamento {conflict.id}")

    appt = Appointment(
        patient_id=patient.id,
        datetime=dt,
        service=canonical_service,
        professional=professional,
        status=normalize_status(status, default="scheduled")
    )
    session.add(appt)
    session.commit()
    session.refresh(appt)
    return appt

def update_appointment(
    session: Session,
    appointment_id: int,
    dt: Optional[datetime] = None,
    service_name: Optional[str] = None,
    professional: Optional[str] = None,
    status: Optional[str] = None,
    patient_name: Optional[str] = None,
    patient_phone: Optional[str] = None,
    responsible_name: Optional[str] = None,
    force: bool = False
) -> Appointment:
    """Core logic to update an appointment."""
    appt = session.get(Appointment, appointment_id)
    if not appt:
        raise KeyError("Appointment not found")
        
    # Update Patient if needed
    if patient_name or patient_phone or (responsible_name is not None):
        current_patient = session.get(Patient, appt.patient_id)
        # We need phone to resolve/update
        from src.application.services.patient_identity import get_contact_phone
        resolved_patient = resolve_patient_for_contact(
            session,
            name=patient_name or (current_patient.name if current_patient else ""),
            phone=patient_phone or (get_contact_phone(current_patient) if current_patient else ""),
            responsible_name=(
                responsible_name
                if responsible_name is not None
                else (current_patient.responsible_name if current_patient else None)
            ),
        )
        appt.patient_id = resolved_patient.id

    if service_name:
        appt.service = canonicalize_service_name(service_name)
        # If service changes and professional wasn't explicitly provided, update professional too?
        # Usually yes, unless the user provided a specific professional in this update.
        if not professional:
            info = get_service_info(appt.service)
            appt.professional = info["professional"]

    if professional:
        appt.professional = professional

    if status:
        appt.status = normalize_status(status, default=appt.status)

    if dt:
        appt.datetime = dt
        
    # Validation after all fields set
    if not force and (dt or service_name or professional) and appt.status != "cancelled":
        info = get_service_info(appt.service)
        conflict = check_conflicts(session, appt.professional, appt.datetime, info["duration"], exclude_id=appt.id)
        if conflict:
            raise ValueError(f"Horário ocupado pelo agendamento {conflict.id}")

    session.add(appt)
    session.commit()
    session.refresh(appt)
    return appt

def cancel_appointment(session: Session, appointment_id: int) -> Appointment:
    """Core logic to cancel an appointment."""
    appt = session.get(Appointment, appointment_id)
    if not appt:
        raise KeyError("Appointment not found")
        
    appt.status = "cancelled"
    session.add(appt)
    session.commit()
    session.refresh(appt)
    return appt
