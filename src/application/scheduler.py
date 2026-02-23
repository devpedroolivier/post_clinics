import time
import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()
BR_TZ = ZoneInfo("America/Sao_Paulo")

from sqlmodel import Session, select
from src.infrastructure.database import engine, create_db_and_tables
from src.domain.models import Appointment, Patient
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
        f"Olá {patient_name}! 😊\n\n"
        f"Aqui é a {ASSISTANT_NAME}, da {CLINIC_NAME}.\n\n"
        f"Passando para lembrar que você tem uma consulta *amanhã*:\n\n"
        f"📅 Data: {date_str}\n"
        f"⏰ Horário: {time_str}\n"
        f"🏥 Serviço: {service}\n\n"
        f"Poderia confirmar sua presença?\n"
        f"Responda com emoji OU texto:\n\n"
        f"✅ *Confirmo* (ou digite \"confirmo\")\n"
        f"🔄 *Reagendar* (ou digite \"reagendar\")\n"
        f"❌ *Cancelar* (ou digite \"cancelar\")\n\n"
        f"Caso precise de ajuda, estou aqui! 🙂"
    )

def get_reminder_message_3h(patient_name: str, appt_datetime: datetime, service: str) -> str:
    time_str = appt_datetime.strftime("%H:%M")
    return (
        f"Olá {patient_name}! 😊\n\n"
        f"Lembrete: sua consulta é *hoje* às *{time_str}*.\n\n"
        f"🏥 Serviço: {service}\n\n"
        f"Estamos te esperando! Até logo. 🙂"
    )

def check_and_send_reminders():
    now_aware = datetime.now(BR_TZ)
    now = now_aware.replace(tzinfo=None)
    logger.info(f"Checking reminders at {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    sent_count = 0
    
    with Session(engine) as session:
        statement = select(Appointment, Patient).join(Patient).where(
            Appointment.status.in_(["confirmed", "scheduled"]),
            Appointment.datetime > now,
        )
        results = session.exec(statement).all()
        
        for appointment, patient in results:
            time_until = appointment.datetime - now
            hours_until = time_until.total_seconds() / 3600
            
            # --- 24h Reminder ---
            if not appointment.notified_24h and 23 <= hours_until <= 25:
                message = get_reminder_message_24h(patient.name, appointment.datetime, appointment.service)
                logger.info(f"Sending 24h reminder to {patient.phone} for appt {appointment.id}")
                
                success = send_message(patient.phone, message)
                if success:
                    appointment.notified_24h = True
                    session.add(appointment)
                    session.commit()
                    sent_count += 1
                    logger.info(f"✅ 24h reminder sent to {patient.name} ({patient.phone})")
                else:
                    logger.warning(f"❌ Failed to send 24h reminder to {patient.phone}")
            
            # --- 3h Reminder ---
            if not appointment.notified_3h and 2.5 <= hours_until <= 3.5:
                message = get_reminder_message_3h(patient.name, appointment.datetime, appointment.service)
                logger.info(f"Sending 3h reminder to {patient.phone} for appt {appointment.id}")
                
                success = send_message(patient.phone, message)
                if success:
                    appointment.notified_3h = True
                    session.add(appointment)
                    session.commit()
                    sent_count += 1
                    logger.info(f"✅ 3h reminder sent to {patient.name} ({patient.phone})")
                else:
                    logger.warning(f"❌ Failed to send 3h reminder to {patient.phone}")
    
    logger.info(f"Check complete. {sent_count} reminder(s) sent.")

def run_scheduler():
    logger.info(f"🚀 Scheduler started. Checking every {CHECK_INTERVAL_SECONDS}s.")
    logger.info(f"Clinic: {CLINIC_NAME}")
    
    create_db_and_tables()
    
    while True:
        try:
            check_and_send_reminders()
        except Exception as e:
            logger.error(f"Error during reminder check: {e}")
        
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    run_scheduler()
