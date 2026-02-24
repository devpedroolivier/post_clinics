import os
import requests
import time
import logging
import argparse
import sys
import hmac
import hashlib
import json
from sqlmodel import Session, select, create_engine, delete
from src.domain.models import Appointment, Patient
from src.infrastructure.database import DATABASE_URL
from datetime import datetime

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("verify_flows.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("VERIFY")

# Configuration
BASE_URL = "http://localhost:8000"
TEST_PHONE = "5511999998888" # Distinct from standard dev numbers
TEST_NAME = "Test AutoBot"
SESSION_ID = f"zapi:{TEST_PHONE}"
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "clinica_espaco_interativo_reabilitare")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
WEBHOOK_SIGNATURE_SECRET = os.getenv("WEBHOOK_SIGNATURE_SECRET", "change_me_webhook_secret")
WEBHOOK_SIGNATURE_HEADER = os.getenv("WEBHOOK_SIGNATURE_HEADER", "X-Webhook-Signature")

# Database setup
engine = create_engine(DATABASE_URL)

class WorkflowTester:
    def __init__(self):
        self.phone = TEST_PHONE
        self.patient_name = TEST_NAME
        self.results = {}
        self.auth_headers = self._authenticate()

    def _authenticate(self):
        login_url = f"{BASE_URL}/api/auth/login"
        response = requests.post(
            login_url,
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            timeout=30,
        )
        response.raise_for_status()
        token = response.json().get("access_token") or response.json().get("token")
        if not token:
            raise RuntimeError("Login succeeded but token is missing.")
        return {"Authorization": f"Bearer {token}"}

    def _log_step(self, step_name):
        logger.info(f"--- STEP: {step_name} ---")

    def reset_db(self):
        """Clears relevant tables for a clean slate for the test user."""
        self._log_step("Resetting Database for Test User")
        
        # 1. Clear Business Data
        with Session(engine) as session:
            # Find patient
            statement = select(Patient).where(Patient.phone == self.phone)
            patient = session.exec(statement).first()
            if patient:
                # Delete appointments
                appt_stmt = delete(Appointment).where(Appointment.patient_id == patient.id)
                session.exec(appt_stmt)
                # Delete patient
                session.delete(patient)
                session.commit()
                logger.info(f"Deleted business data for {self.phone}")
            else:
                logger.info(f"No business data found for {self.phone}")

        # 2. Clear Conversation Memory
        try:
            from src.core.config import DATA_DIR
            conv_db_path = os.path.join(DATA_DIR, "conversations.db")
            if os.path.exists(conv_db_path):
                conv_engine = create_engine(f"sqlite:///{conv_db_path}")
                try:
                    with conv_engine.connect() as conn:
                         # Attempt to delete messages for this session
                         conn.exec_driver_sql("DELETE FROM messages WHERE session_id = ?", (SESSION_ID,))
                         conn.commit()
                    logger.info(f"Cleared conversation memory for {SESSION_ID}")
                except Exception as e:
                    logger.warning(f"Could not clear table messages manually: {e}")
        except Exception as e:
            logger.warning(f"Failed to clear conversation memory: {e}")

    def send_message(self, text):
        """Sends a Z-API webhook payload."""
        logger.info(f"Sending User Message: '{text}'")
        payload = {
            "phone": self.phone,
            "text": {"message": text},
            "messageId": f"msg_{time.time_ns()}",
            "fromMe": False,
            "isGroup": False
        }
        payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        signature = hmac.new(
            WEBHOOK_SIGNATURE_SECRET.encode("utf-8"),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()
        try:
            response = requests.post(
                f"{BASE_URL}/webhook/zapi",
                data=payload_bytes,
                headers={
                    "Content-Type": "application/json",
                    WEBHOOK_SIGNATURE_HEADER: f"sha256={signature}",
                },
                timeout=60,
            )
            if response.status_code != 200:
                logger.error(f"HTTP Error: {response.text}")
                
            response.raise_for_status()
            data = response.json()
            reply = data.get('reply')
            logger.info(f"Agent Reply: {reply}")
            return reply
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise

    def verify_appointment_status(self, expected_status, note=""):
        """Checks DB for appointment status."""
        logger.info(f"Verifying DB Status (Expected: {expected_status}) {note}")
        with Session(engine) as session:
            statement = select(Appointment).join(Patient).where(Patient.phone == self.phone).order_by(Appointment.created_at.desc())
            appointment = session.exec(statement).first()
            
            if not appointment:
                logger.error("No appointment found in DB!")
                return False
            
            logger.info(f"Found Appointment ID {appointment.id} at {appointment.datetime}, Status: {appointment.status}")
            
            if appointment.status == expected_status:
                logger.info("✅ Status Matches")
                return True
            else:
                logger.error(f"❌ Status Mismatch. Got {appointment.status}")
                return False

    def test_dashboard_api(self):
        """Verifies if the appointment appears in the Dashboard API."""
        self._log_step("Checking Dashboard API")
        try:
            response = requests.get(f"{BASE_URL}/api/appointments", headers=self.auth_headers, timeout=30)
            if response.status_code == 401:
                self.auth_headers = self._authenticate()
                response = requests.get(f"{BASE_URL}/api/appointments", headers=self.auth_headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            logger.info(f"API Response: {data}")
            appointments = data.get("appointments", [])
            
            found = False
            for appt in appointments:
                if appt["patient_phone"] == self.phone:
                    found = True
                    logger.info(f"✅ Found appointment in Dashboard API: {appt}")
            
            if not found:
                logger.error("❌ Appointment NOT found in Dashboard API")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to query Dashboard API: {e}")
            return False

    def test_availability(self, date_str):
        self._log_step(f"TEST: Availability on {date_str}")
        reply = self.send_message(f"Tem horário livre para {date_str}?")
        if "Available slots" in reply or "livre" in reply.lower() or "vagas" in reply.lower():
            logger.info("✅ Agent checked availability")
            return True
        else:
             logger.warning(f"⚠️ Agent response unclear: {reply}")
             return False

    def test_collision(self, date, time_str):
        self._log_step(f"TEST: Collision on {date} {time_str}")
        # Prerequisite: Date/Time should be taken (use seeder)
        reply = self.send_message(f"Quero agendar para {date} às {time_str}")
        if "taken" in reply or "ocupado" in reply.lower() or "não" in reply.lower():
            logger.info("✅ Agent detected collision")
            return True
        else:
            logger.warning(f"⚠️ Agent might have double booked or error: {reply}")
            return False

    def test_invalid_date(self):
        self._log_step("TEST: Invalid Date Format")
        reply = self.send_message("Quero agendar para 30/02/2025") # Invalid date
        if "invalid" in reply.lower() or "correto" in reply.lower() or "não entendi" in reply.lower():
             logger.info("✅ Agent handled invalid date")
             return True
        else:
             logger.warning(f"⚠️ Agent response to invalid date: {reply}")
             return False

    def run_full_suite(self):
        try:
            # 1. Setup
            self.reset_db()
            
            # 2. Schedule Flow
            self._log_step("SCENARIO A: Scheduling")
            self.send_message("Olá, gostaria de agendar uma consulta.")
            time.sleep(2) # Wait for processing
            self.send_message("Clínica Geral, por favor.") # Assuming it asks for service
            time.sleep(2)
            self.send_message("Pode ser amanhã às 14h?")
            time.sleep(2)
            # Assuming agent asks for name or confirmation
            self.send_message(f"Meu nome é {self.patient_name}")
            time.sleep(2)
            self.send_message("Sim, confirmo.")
            time.sleep(2)
            
            if not self.verify_appointment_status("confirmed"): # Or 'scheduled' based on verify_flows
                 logger.error("Failed Scenario A")
            
            # 3. Dashboard Check
            self.test_dashboard_api()

            # 4. Reschedule Flow
            self._log_step("SCENARIO B: Rescheduling")
            self.send_message("Preciso remarcar para amanhã às 16h.")
            time.sleep(2)
            self.send_message("Sim, confirmo a mudança.")
            time.sleep(2)
            
            # Check if updated (logic depends on if it updates existing or creates new, usually updates)
            # Note: The logic in main.py might not support rescheduling directly yet, this tests IF the agent can do it.
            self.verify_appointment_status("confirmed", note="After Reschedule")

            # 5. Cancel Flow
            self._log_step("SCENARIO C: Cancellation")
            self.send_message("Quero cancelar minha consulta.")
            time.sleep(2)
            self.send_message("Sim, cancelar.")
            time.sleep(2)
            
            self.verify_appointment_status("cancelled")

            logger.info("🎉 FULL SUITE COMPLETED")

        except Exception as e:
            logger.error(f"Suite Aborted: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify Flows and Validation Scenarios")
    parser.add_argument("--test", choices=["all", "availability", "collision", "invalid", "api"], default="all")
    parser.add_argument("--date", help="Date for availability/collision check (YYYY-MM-DD)")
    parser.add_argument("--time", help="Time for collision check (HH:MM)")
    
    args = parser.parse_args()
    tester = WorkflowTester()
    
    if args.test == "all":
        tester.run_full_suite()
    elif args.test == "availability":
        date = args.date or "2024-12-25"
        tester.test_availability(date)
    elif args.test == "collision":
        date = args.date or "2024-12-25"
        time_str = args.time or "10:00"
        tester.test_collision(date, time_str)
    elif args.test == "invalid":
        tester.test_invalid_date()
    elif args.test == "api":
        tester.test_dashboard_api()
