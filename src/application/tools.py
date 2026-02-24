from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from agents import function_tool
from sqlmodel import Session, select
from src.infrastructure.database import engine
from src.domain.models import Appointment, Patient
from src.core.config import CLINIC_CONFIG
from src.infrastructure.vector_store import search_store

BR_TZ = ZoneInfo("America/Sao_Paulo")

import difflib

def get_service_info(service_name: str) -> dict:
    """Helper to get service info (duration, professional) with fuzzy matching."""
    default_resp = {"duration": 45, "professional": "Clínica Geral"}
    if not service_name:
        return default_resp
        
    services = CLINIC_CONFIG.get("services", [])
    service_names = [s["name"] for s in services]
    
    # 1. Exact or close match
    matches = difflib.get_close_matches(service_name, service_names, n=1, cutoff=0.6)
    if matches:
        best_match = matches[0]
        for s in services:
            if s["name"] == best_match:
                return {
                    "duration": s.get("duration", 45),
                    "professional": s.get("professional", "Clínica Geral")
                }
                
    # 2. Substring fallback
    for s in services:
        if service_name.lower() in s["name"].lower() or s["name"].lower() in service_name.lower():
            return {
                "duration": s.get("duration", 45),
                "professional": s.get("professional", "Clínica Geral")
            }
            
    return default_resp

# --- Core Logic Functions (Undecorated for Testing) ---

def _check_availability(date_str: str, service_name: str = "Clínica Geral") -> str:
    now = datetime.now(BR_TZ).date()
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        try:
            target_date = datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            try:
                target_date = datetime.strptime(date_str, "%d/%m").date()
                target_date = target_date.replace(year=now.year)
                if target_date < now:
                    target_date = target_date.replace(year=now.year + 1)
            except ValueError:
                return "Formato de data inválido. Use AAAA-MM-DD."

    info = get_service_info(service_name)
    duration_minutes = info["duration"]
    professional = info["professional"]
    
    weekday = target_date.weekday() # 0=Mon, 6=Sun
    if weekday == 6: # Sunday
        return "Clínica fechada aos Domingos."
    
    # Get schedule blocks for this professional/day
    schedules = CLINIC_CONFIG.get("schedules", {})
    
    if professional == "Dra. Débora / Dr. Sidney":
        if weekday == 5:  # Saturday
            blocks = schedules.get("Dra. Débora / Dr. Sidney", {}).get("sat", [])
        else:
            blocks = schedules.get("Dra. Débora / Dr. Sidney", {}).get("mon_fri", [])
    elif professional in schedules:
        blocks = schedules[professional]["blocks"]
    else:
        if weekday == 5:  # Saturday
            blocks = schedules.get("saturday", {"blocks": [("09:00", "13:00")]})["blocks"]
        else:
            blocks = schedules.get("default", {"blocks": [("09:00", "17:30")]})["blocks"]

    available_slots = []
    
    with Session(engine) as session:
        day_start = datetime.combine(target_date, time(0, 0))
        day_end = datetime.combine(target_date, time(23, 59))
        
        statement = select(Appointment).where(
            Appointment.datetime >= day_start,
            Appointment.datetime <= day_end,
            Appointment.status != "cancelled",
            Appointment.professional == professional
        )
        existing_appointments = session.exec(statement).all()
        
        busy_intervals = []
        for appt in existing_appointments:
            appt_info = get_service_info(appt.service)
            start = appt.datetime
            end = start + timedelta(minutes=appt_info["duration"])
            busy_intervals.append((start, end))

        # Generate slots from each time block
        for block_start_str, block_end_str in blocks:
            bh, bm = map(int, block_start_str.split(":"))
            eh, em = map(int, block_end_str.split(":"))
            
            work_start = datetime.combine(target_date, time(bh, bm))
            work_end = datetime.combine(target_date, time(eh, em))
            
            current_slot = work_start
            while current_slot + timedelta(minutes=duration_minutes) <= work_end:
                slot_end = current_slot + timedelta(minutes=duration_minutes)
                
                is_free = True
                for busy_start, busy_end in busy_intervals:
                    # Check for overlap: (StartA < EndB) and (EndA > StartB)
                    if current_slot < busy_end and slot_end > busy_start:
                        is_free = False
                        break
                
                if is_free:
                    available_slots.append(current_slot)
                
                # Use fixed 45-min grid for most, unless specified
                current_slot += timedelta(minutes=duration_minutes)

    if not available_slots:
        return f"Não há horários disponíveis para {service_name} em {date_str}."
    
    # Selection logic: return 5 options balanced (morning/afternoon)
    morning = [s for s in available_slots if s.hour < 12]
    afternoon = [s for s in available_slots if s.hour >= 12]
    
    selected = []
    if morning and afternoon:
        selected = morning[:2] + afternoon[:3]
    else:
        selected = available_slots[:5]
        
    formatted_slots = [s.strftime("%H:%M") for s in selected]
    return f"Horários disponíveis para {service_name} (Profissional: {professional}) em {date_str}: {', '.join(formatted_slots)}"

def _schedule_appointment(name: str, phone: str, datetime_str: str, service_name: str = "Clínica Geral") -> str:
    try:
        appt_dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        return "Formato inválido. Use AAAA-MM-DD HH:MM."
        
    info = get_service_info(service_name)
    duration_minutes = info["duration"]
    professional = info["professional"]

    with Session(engine) as session:
        patient = session.exec(select(Patient).where(Patient.phone == phone)).first()
        if not patient:
            patient = Patient(name=name, phone=phone)
            session.add(patient)
            session.commit()
            session.refresh(patient)
            
        new_end = appt_dt + timedelta(minutes=duration_minutes)
        
        # Check collisions for this professional
        day_start = appt_dt.replace(hour=0, minute=0)
        day_end = appt_dt.replace(hour=23, minute=59)
        
        statement = select(Appointment).where(
            Appointment.datetime >= day_start,
            Appointment.datetime <= day_end,
            Appointment.status != "cancelled",
            Appointment.professional == professional
        )
        existing_appointments = session.exec(statement).all()
        
        for appt in existing_appointments:
            appt_info = get_service_info(appt.service)
            existing_end = appt.datetime + timedelta(minutes=appt_info["duration"])
            
            if appt_dt < existing_end and new_end > appt.datetime:
                return f"Conflito de horário: Dr(a). {professional} já possui um agendamento das {appt.datetime.strftime('%H:%M')} às {existing_end.strftime('%H:%M')}."

        appt = Appointment(
            patient_id=patient.id, 
            datetime=appt_dt, 
            service=service_name,
            professional=professional,
            status="confirmed"
        )
        session.add(appt)
        session.commit()
        session.refresh(appt)
        
        return f"Agendamento confirmado [ID: {appt.id}] para {name}, Serviço: {service_name} com {professional} em {datetime_str}."

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
        return "Formato inválido. Use AAAA-MM-DD HH:MM."

    with Session(engine) as session:
        appt = session.get(Appointment, appointment_id)
        if not appt:
            return "Agendamento não encontrado para reagendar."
            
        if appt.status == "cancelled":
            return "Não é possível reagendar um agendamento cancelado. Por favor, solicite um novo agendamento."

        info = get_service_info(appt.service)
        professional = appt.professional
        duration = info["duration"]
        new_end = new_dt + timedelta(minutes=duration)
        
        day_start = new_dt.replace(hour=0, minute=0)
        day_end = new_dt.replace(hour=23, minute=59)
        
        existing_collisions = session.exec(select(Appointment).where(
            Appointment.datetime >= day_start,
            Appointment.datetime <= day_end,
            Appointment.status != "cancelled",
            Appointment.professional == professional,
            Appointment.id != appointment_id
        )).all()
        
        for coll in existing_collisions:
            coll_info = get_service_info(coll.service)
            coll_end = coll.datetime + timedelta(minutes=coll_info["duration"])
            
            if new_dt < coll_end and new_end > coll.datetime:
                return f"Conflito de horário: Dr(a). {professional} já possui um agendamento das {coll.datetime.strftime('%H:%M')} às {coll_end.strftime('%H:%M')}."

        appt.datetime = new_dt
        session.add(appt)
        session.commit()
        session.refresh(appt)
        
        return f"Agendamento {appointment_id} reagendado para {new_datetime_str} com sucesso."

def _get_available_services() -> str:
    services_list = []
    for s in CLINIC_CONFIG["services"]:
        duration = s["duration"]
        note = f" ({s['note']})" if "note" in s else ""
        services_list.append(f"- {s['name']}{note}")
    return "Serviços disponíveis na clínica:\n" + "\n".join(services_list)

WEEKDAYS_PT = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}

def _find_patient_appointments(phone: str) -> str:
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
            weekday = WEEKDAYS_PT.get(appt.datetime.weekday(), "")
            date_str = appt.datetime.strftime("%d/%m/%Y às %H:%M")
            lines.append(f"- [INTERNAL_ID:{appt.id}] {weekday}, {date_str} | {appt.service} | Status: {appt.status}")
        
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

@function_tool
def search_knowledge_base(query: str) -> str:
    """Search the clinic's knowledge base and FAQs for complex questions about rules, specific procedures, ou preços/valores. Use this IF and ONLY IF the answer is not already in your system prompt."""
    results = search_store(query, k=2)
    if not results:
        query_lower = query.lower()
        if "valor" in query_lower or "preç" in query_lower or "preco" in query_lower:
             return "(SYSTEM: Nenhuma informação de preço encontrada na base. Use a ferramenta request_human_attendant IMEDIATAMENTE.)"
        return "Nenhuma informação relevante encontrada na base de conhecimento. Se a dúvida persistir, encaminhe para um atendente utilizando request_human_attendant."
    
    docs = [f"Referência {i+1}: {res.page_content.strip()}" for i, res in enumerate(results)]
    return "\n\n".join(docs)

@function_tool
def request_human_attendant(reason: str = "") -> str:
    """Request a human attendant or receptionist to intervene in the conversation. Use this when the patient explicitly asks for a human, attendant or receptionist, or when the AI cannot resolve a complex issue."""
    return "Sua solicitação foi encaminhada para um atendente humano. Por favor, aguarde um momento que entraremos em contato em breve."
