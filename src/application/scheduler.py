import time
import asyncio
import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()
BR_TZ = ZoneInfo("America/Sao_Paulo")

from sqlmodel import Session, select
from src.infrastructure.database import engine, create_db_and_tables
from src.domain.models import Appointment, Patient, NotificationLog
from src.infrastructure.services.zapi import send_message
from src.core.config import CLINIC_CONFIG

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [Scheduler] %(levelname)s: %(message)s"
)
logger = logging.getLogger("PostClinics.Scheduler")

CHECK_INTERVAL_SECONDS = int(os.environ.get("SCHEDULER_INTERVAL", 600))
CLINIC_NAME = CLINIC_CONFIG["name"]
ASSISTANT_NAME = CLINIC_CONFIG["assistant_name"]

def get_reminder_message_24h(patient_name: str, appt_datetime: datetime, service: str) -> str:
    date_str = appt_datetime.strftime("%d/%m/%Y")
    time_str = appt_datetime.strftime("%H:%M")
    return (
        f"Olá {patient_name}.\n\n"
        f"Aqui é a {ASSISTANT_NAME}, da {CLINIC_NAME}.\n\n"
        f"Lembramos que você possui uma consulta agendada para amanhã:\n\n"
        f"Data: {date_str}\n"
        f"Horário: {time_str}\n"
        f"Serviço: {service}\n\n"
        f"Por favor, confirme sua presença respondendo:\n"
        f"SIM - Para confirmar\n"
        f"REAGENDAR - Para solicitar nova data\n"
        f"CANCELAR - Para desmarcar\n\n"
        f"Agradecemos a atenção."
    )

def get_reminder_message_3h(patient_name: str, appt_datetime: datetime, service: str) -> str:
    time_str = appt_datetime.strftime("%H:%M")
    return (
        f"Olá {patient_name}.\n\n"
        f"Lembrete: sua consulta é hoje às {time_str}.\n"
        f"Serviço: {service}\n\n"
        f"Estamos aguardando você."
    )

async def check_and_send_reminders():
    # Use localized time for logic
    now_aware = datetime.now(BR_TZ)
    # Convert to naive for SQLite comparison (assuming DB stores in local naive time)
    now_naive = now_aware.replace(tzinfo=None)
    
    logger.info(f"Checking reminders at {now_aware.strftime('%Y-%m-%d %H:%M:%S')}")
    
    sent_count = 0
    
    with Session(engine) as session:
        # Fetch only active appointments that are in the future
        statement = select(Appointment, Patient).join(Patient).where(
            Appointment.status.in_(["confirmed", "scheduled"]),
            Appointment.datetime > now_naive,
        )
        results = session.exec(statement).all()
        
        for appointment, patient in results:
            time_until = appointment.datetime - now_naive
            hours_until = time_until.total_seconds() / 3600
            
            # --- 24h Reminder Logic ---
            if not appointment.notified_24h:
                if hours_until < 20:
                    # Late booking: too close to send "tomorrow" reminder
                    logger.info(f"Skipping 24h reminder for late booking: Appt {appointment.id} (booked with {hours_until:.1f}h remaining)")
                    appointment.notified_24h = True
                    session.add(appointment)
                    session.commit()
                elif 18 <= hours_until <= 25:
                    # Within normal 24h threshold
                    message = get_reminder_message_24h(patient.name, appointment.datetime, appointment.service)
                    logger.info(f"Attempting 24h reminder for {patient.name} ({patient.phone}) - Appt {appointment.id}")
                    
                    res = await send_message(patient.phone, message)
                    log = NotificationLog(
                        appointment_id=appointment.id,
                        notification_type="24h",
                        status="sent" if res["success"] else "failed",
                        error_message=res["error_message"]
                    )
                    session.add(log)
                    if res["success"]:
                        appointment.notified_24h = True
                        session.add(appointment)
                        sent_count += 1
                    session.commit()
            
            # --- 3h Reminder Logic ---
            if not appointment.notified_3h and 0.5 <= hours_until <= 3.5:
                message = get_reminder_message_3h(patient.name, appointment.datetime, appointment.service)
                logger.info(f"Attempting 3h reminder for {patient.name} ({patient.phone}) - Appt {appointment.id}")
                
                res = await send_message(patient.phone, message)
                log = NotificationLog(
                    appointment_id=appointment.id,
                    notification_type="3h",
                    status="sent" if res["success"] else "failed",
                    error_message=res["error_message"]
                )
                session.add(log)
                if res["success"]:
                    appointment.notified_3h = True
                    session.add(appointment)
                    sent_count += 1
                session.commit()
    
    logger.info(f"Check complete. {sent_count} reminder(s) sent successfully.")

def run_scheduler():
    logger.info(f"🚀 Scheduler started. Checking every {CHECK_INTERVAL_SECONDS}s.")
    logger.info(f"Clinic: {CLINIC_NAME}")
    
    create_db_and_tables()
    
    while True:
        try:
            asyncio.run(check_and_send_reminders())
        except Exception as e:
            logger.error(f"Error during reminder check: {e}")
        
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    run_scheduler()
