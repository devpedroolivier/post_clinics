from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from agents import function_tool
from sqlmodel import Session, select
from src.database import engine, Appointment, Patient
from src.config import CLINIC_CONFIG

BR_TZ = ZoneInfo("America/Sao_Paulo")

def get_service_duration(service_name: str) -> int:
    """Helper to get duration in minutes for a service."""
    if not service_name:
        return 40 # Default
    for s in CLINIC_CONFIG["services"]:
        if s["name"].lower() == service_name.lower():
            return s["duration"]
    return 40 # Default fallback

# --- Core Logic Functions (Undecorated for Testing) ---

def _check_availability(date_str: str, service_name: str = "Clínica Geral") -> str:
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD."

    duration_minutes = get_service_duration(service_name)
    
    weekday = target_date.weekday() # 0=Mon, 6=Sun
    if weekday == 6: # Sunday
        return "Clínica fechada aos Domingos."
        
    start_hour = time(9, 0)
    if weekday == 5: # Saturday
        end_hour = time(13, 0)
    else:
        end_hour = time(17, 30)

    work_start = datetime.combine(target_date, start_hour)
    work_end = datetime.combine(target_date, end_hour)

    available_slots = []
    
    with Session(engine) as session:
        day_start = datetime.combine(target_date, time(0, 0))
        day_end = datetime.combine(target_date, time(23, 59))
        
        statement = select(Appointment).where(
            Appointment.datetime >= day_start,
            Appointment.datetime <= day_end,
            Appointment.status != "cancelled"
        )
        existing_appointments = session.exec(statement).all()
        
        busy_intervals = []
        for appt in existing_appointments:
            appt_duration = get_service_duration(appt.service)
            start = appt.datetime
            end = start + timedelta(minutes=appt_duration)
            busy_intervals.append((start, end))

        current_slot = work_start
        while current_slot + timedelta(minutes=duration_minutes) <= work_end:
            slot_end = current_slot + timedelta(minutes=duration_minutes)
            
            is_free = True
            for busy_start, busy_end in busy_intervals:
                if current_slot < busy_end and slot_end > busy_start:
                    is_free = False
                    break
            
            if is_free:
                available_slots.append(current_slot.strftime("%H:%M"))
            
            current_slot += timedelta(minutes=30)

    if not available_slots:
        return f"Não há horários disponíveis para {service_name} em {date_str}."
        
    return f"Horários disponíveis para {service_name} em {date_str}: {', '.join(available_slots)}"

def _schedule_appointment(name: str, phone: str, datetime_str: str, service_name: str = "Clínica Geral") -> str:
    try:
        appt_dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        return "Invalid format. Use YYYY-MM-DD HH:MM."
        
    with Session(engine) as session:
        patient = session.exec(select(Patient).where(Patient.phone == phone)).first()
        if not patient:
            patient = Patient(name=name, phone=phone)
            session.add(patient)
            session.commit()
            session.refresh(patient)
            
        new_duration = get_service_duration(service_name)
        new_end = appt_dt + timedelta(minutes=new_duration)
        
        day_start = appt_dt.replace(hour=0, minute=0)
        day_end = appt_dt.replace(hour=23, minute=59)
        
        statement = select(Appointment).where(
            Appointment.datetime >= day_start,
            Appointment.datetime <= day_end,
            Appointment.status != "cancelled"
        )
        existing_appointments = session.exec(statement).all()
        
        for appt in existing_appointments:
            existing_duration = get_service_duration(appt.service)
            existing_end = appt.datetime + timedelta(minutes=existing_duration)
            
            if appt_dt < existing_end and new_end > appt.datetime:
                return f"Desculpe, esse horário conflita com um agendamento existente ({appt.datetime.strftime('%H:%M')} - {existing_end.strftime('%H:%M')})."

        appt = Appointment(
            patient_id=patient.id, 
            datetime=appt_dt, 
            service=service_name,
            status="confirmed"
        )
        session.add(appt)
        session.commit()
        session.refresh(appt)
        
        return f"Agendamento confirmado! ID: {appt.id} para {name}, Serviço: {service_name} em {datetime_str}."

def _confirm_appointment(appointment_id: int) -> str:
    with Session(engine) as session:
        appt = session.get(Appointment, appointment_id)
        if not appt:
            return "Agendamento não encontrado."
        
        if appt.status == "confirmed":
            return f"Agendamento {appointment_id} já está confirmado."
        
        if appt.status in ("scheduled", "cancelled"):
            appt.status = "confirmed"
            session.add(appt)
            session.commit()
            return f"Agendamento {appointment_id} confirmado com sucesso!"
        
        return f"Agendamento {appointment_id} está com status '{appt.status}' e não pode ser confirmado."

def _cancel_appointment(appointment_id: int) -> str:
    with Session(engine) as session:
        appt = session.get(Appointment, appointment_id)
        if not appt:
            return "Agendamento não encontrado."
            
        if appt.status == "cancelled":
            return "Este agendamento já está cancelado."
            
        appt.status = "cancelled"
        session.add(appt)
        session.commit()
        
        return f"Agendamento {appointment_id} cancelado com sucesso."

def _reschedule_appointment(appointment_id: int, new_datetime_str: str) -> str:
    try:
        new_dt = datetime.strptime(new_datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        return "Formato inválido. Use YYYY-MM-DD HH:MM."

    with Session(engine) as session:
        appt = session.get(Appointment, appointment_id)
        if not appt:
            return "Agendamento não encontrado para reagendar."
            
        if appt.status == "cancelled":
            return "Não é possível reagendar um agendamento cancelado. Por favor, solicite um novo agendamento."

        service_name = appt.service
        duration = get_service_duration(service_name)
        new_end = new_dt + timedelta(minutes=duration)
        
        day_start = new_dt.replace(hour=0, minute=0)
        day_end = new_dt.replace(hour=23, minute=59)
        
        existing_collisions = session.exec(select(Appointment).where(
            Appointment.datetime >= day_start,
            Appointment.datetime <= day_end,
            Appointment.status != "cancelled",
            Appointment.id != appointment_id
        )).all()
        
        for coll in existing_collisions:
            coll_dur = get_service_duration(coll.service)
            coll_end = coll.datetime + timedelta(minutes=coll_dur)
            
            if new_dt < coll_end and new_end > coll.datetime:
                return f"Conflito de horário: Desculpe, o horário {new_datetime_str} já está ocupado."

        appt.datetime = new_dt
        session.add(appt)
        session.commit()
        session.refresh(appt)
        
        return f"Agendamento {appointment_id} reagendado para {new_datetime_str} com sucesso."

def _get_available_services() -> str:
    services_list = []
    for s in CLINIC_CONFIG["services"]:
        note = f" - {s['note']}" if "note" in s else ""
        services_list.append(f"{s['name']}{note}")
    return "Serviços disponíveis:\n" + "\n".join(services_list)

def _find_patient_appointments(phone: str) -> str:
    """Find all active appointments for a patient by phone number."""
    with Session(engine) as session:
        patient = session.exec(select(Patient).where(Patient.phone == phone)).first()
        if not patient:
            return "Nenhum paciente encontrado com esse telefone."
        
        statement = select(Appointment).where(
            Appointment.patient_id == patient.id,
            Appointment.status != "cancelled"
        ).order_by(Appointment.datetime)
        appointments = session.exec(statement).all()
        
        if not appointments:
            return f"Nenhum agendamento ativo encontrado para {patient.name}."
        
        lines = [f"Agendamentos de {patient.name}:"]
        for appt in appointments:
            date_str = appt.datetime.strftime("%d/%m/%Y às %H:%M")
            lines.append(f"- ID {appt.id}: {date_str} | {appt.service} | Status: {appt.status}")
        
        return "\n".join(lines)


# --- Decorated Tools Implementation (Using Core Logic) ---

@function_tool
def check_availability(date_str: str, service_name: str = "Clínica Geral") -> str:
    """Check available appointment slots for a given date."""
    return _check_availability(date_str, service_name)

@function_tool
def schedule_appointment(name: str, phone: str, datetime_str: str, service_name: str = "Clínica Geral") -> str:
    """Schedule a new appointment for a patient."""
    return _schedule_appointment(name, phone, datetime_str, service_name)

@function_tool
def confirm_appointment(appointment_id: int) -> str:
    """Confirm an existing appointment."""
    return _confirm_appointment(appointment_id)

@function_tool
def cancel_appointment(appointment_id: int) -> str:
    """Cancel an existing appointment."""
    return _cancel_appointment(appointment_id)

@function_tool
def reschedule_appointment(appointment_id: int, new_datetime_str: str) -> str:
    """Reschedule an appointment to a new date/time."""
    return _reschedule_appointment(appointment_id, new_datetime_str)

@function_tool
def get_available_services(query: str = "") -> str:
    """Get list of available services and their durations. Pass empty string for query."""
    return _get_available_services()

@function_tool
def find_patient_appointments(phone: str) -> str:
    """Find all active appointments for a patient by their phone number. Use this to look up appointment IDs before confirming, cancelling, or rescheduling."""
    return _find_patient_appointments(phone)
