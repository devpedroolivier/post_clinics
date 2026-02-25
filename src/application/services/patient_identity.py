import re
from typing import Optional

from sqlmodel import Session, select

from src.domain.models import Patient


def normalize_phone(phone: str) -> str:
    return re.sub(r"\D+", "", phone or "")


def normalize_name(name: str) -> str:
    return re.sub(r"\s+", " ", (name or "").strip()).lower()


def get_contact_phone(patient: Patient) -> str:
    # Backward compatible with older rows that only had `phone`.
    return (patient.contact_phone or patient.phone or "").strip()


def find_patients_by_contact(session: Session, phone: str) -> list[Patient]:
    normalized = normalize_phone(phone)
    if not normalized:
        return []

    patients = session.exec(select(Patient)).all()
    return [
        p for p in patients
        if normalize_phone(get_contact_phone(p)) == normalized
    ]


def resolve_patient_for_contact(
    session: Session,
    *,
    name: str,
    phone: str,
    responsible_name: Optional[str] = None,
) -> Patient:
    normalized_name = normalize_name(name)
    for patient in find_patients_by_contact(session, phone):
        if normalize_name(patient.name) == normalized_name:
            changed = False
            if not patient.contact_phone:
                patient.contact_phone = (phone or "").strip()
                changed = True
            if responsible_name and patient.responsible_name != responsible_name:
                patient.responsible_name = responsible_name
                changed = True
            if changed:
                session.add(patient)
                session.commit()
                session.refresh(patient)
            return patient

    patient = Patient(
        name=(name or "").strip(),
        phone=(phone or "").strip(),
        contact_phone=(phone or "").strip(),
        responsible_name=(responsible_name or None),
    )
    session.add(patient)
    session.commit()
    session.refresh(patient)
    return patient
