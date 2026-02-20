from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from agents import Runner, SQLiteSession
from src.agent import agent
from src.database import create_db_and_tables
from src.zapi import send_message
from src.config import DATA_DIR
from sqlmodel import SQLModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PostClinics")

app = FastAPI(title="POST Clinics MVP")

# Configure CORS for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow Ngrok and all origins for MVP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"message": "POST Clinics API is running"}

# --- Basic MVP Auth ---
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    expected_token = os.getenv("ADMIN_TOKEN", "post-clinics-mvp-secure-token")
    if credentials.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Token inválido")
    return credentials.credentials

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    expected_user = os.getenv("ADMIN_USERNAME", "clinica_espaco_interativo_reabilitare")
    expected_pass = os.getenv("ADMIN_PASSWORD", "admin")
    expected_token = os.getenv("ADMIN_TOKEN", "post-clinics-mvp-secure-token")
    
    if req.username == expected_user and req.password == expected_pass:
        return {"token": expected_token}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    logger.info("Database tables verified.")

@app.post("/webhook/zapi")
async def receiver(request: Request):
    """
    Endpoint request from Z-API.
    Accepts arbitrary JSON and manually extracts fields to be robust against structure variations.
    Includes anti-spam protection: rate limiting per phone and message deduplication.
    """
    import re
    import json
    from collections import defaultdict
    from src.tools import (
        _check_availability, _schedule_appointment, _confirm_appointment,
        _cancel_appointment, _reschedule_appointment, _get_available_services,
        _find_patient_appointments
    )
    from src.config import ANTISPAM_CONFIG

    # Map of tool names to their undecorated implementations
    TOOL_MAP = {
        "check_availability": _check_availability,
        "schedule_appointment": _schedule_appointment,
        "confirm_appointment": _confirm_appointment,
        "cancel_appointment": _cancel_appointment,
        "reschedule_appointment": _reschedule_appointment,
        "get_available_services": _get_available_services,
        "find_patient_appointments": _find_patient_appointments,
    }

    try:
        payload = await request.json()
        logger.info(f"Received payload: {payload}")
        
        phone = payload.get("phone")
        
        # Extract text content
        text_content = ""
        text_data = payload.get("text")
        
        if isinstance(text_data, dict):
            text_content = text_data.get("message", "")
        elif isinstance(text_data, str):
            text_content = text_data
            
        message_id = payload.get("messageId", "unknown")
            
        if not phone or not text_content:
            logger.warning(f"Ignored payload (missing phone/text): {payload}")
            return {"status": "ignored", "reason": "missing_data"}

        # Filter out own messages and group messages
        if payload.get("fromMe", False) or payload.get("isGroup", False):
             return {"status": "ignored", "reason": "filtered_source"}

        # --- ANTI-SPAM: Message Deduplication ---
        import time as _time
        now = _time.time()
        
        if not hasattr(app.state, "_seen_messages"):
            app.state._seen_messages = {}
        
        # Clean old entries (older than dedup window)
        dedup_window = ANTISPAM_CONFIG["dedup_window_seconds"]
        app.state._seen_messages = {
            k: v for k, v in app.state._seen_messages.items()
            if now - v < dedup_window
        }
        
        if message_id in app.state._seen_messages:
            logger.info(f"[ANTISPAM] Duplicate message ignored: {message_id}")
            return {"status": "ignored", "reason": "duplicate_message"}
        
        app.state._seen_messages[message_id] = now
        
        # --- ANTI-SPAM: Rate Limiting per Phone ---
        if not hasattr(app.state, "_phone_timestamps"):
            app.state._phone_timestamps = defaultdict(list)
        
        max_per_min = ANTISPAM_CONFIG["max_messages_per_minute"]
        cooldown = ANTISPAM_CONFIG["cooldown_seconds"]
        
        # Clean old timestamps (older than 60s)
        app.state._phone_timestamps[phone] = [
            ts for ts in app.state._phone_timestamps[phone]
            if now - ts < 60
        ]
        
        timestamps = app.state._phone_timestamps[phone]
        
        if len(timestamps) >= max_per_min:
            logger.warning(f"[ANTISPAM] Rate limit exceeded for {phone}: {len(timestamps)} msgs/min")
            return {"status": "ignored", "reason": "rate_limited"}
        
        if timestamps and (now - timestamps[-1]) < cooldown:
            logger.info(f"[ANTISPAM] Cooldown active for {phone}: {now - timestamps[-1]:.1f}s < {cooldown}s")
            return {"status": "ignored", "reason": "cooldown"}
        
        app.state._phone_timestamps[phone].append(now)

        # --- PROCESS MESSAGE ---
        session_id = f"zapi:{phone}"
        conversation_db = os.path.join(DATA_DIR, "conversations.db")
        session = SQLiteSession(db_path=conversation_db, session_id=session_id)
        
        # Inject patient phone into context so agent can look up appointments
        agent_input = f"[Telefone do paciente: {phone}]\n{text_content}"
        
        logger.info(f"[WPP:IN] phone={phone} msgId={message_id} text={text_content}")
        
        result = await Runner.run(agent, input=agent_input, session=session)
        logger.info(f"Agent response: {result}")
        
        # --- GROQ/LLAMA 3 WORKAROUND ---
        final_text = result.final_output
        if not isinstance(final_text, str):
            final_text = str(final_text)
        
        # Pattern matches <function=name>JSON_ARGS</function> (DOTALL for multiline JSON)
        tool_pattern = r'<function=(\w+)>(.*?)</function>'
        
        # Loop: handle up to 3 sequential tool calls (safety limit)
        for attempt in range(3):
            matches = list(re.finditer(tool_pattern, final_text, re.DOTALL))
            if not matches:
                break
                
            # Process each tool call found in the response
            tool_results = []
            for match in matches:
                func_name = match.group(1)
                args_str = match.group(2).strip()
                logger.info(f"Detected tool call #{attempt+1}: {func_name}({args_str})")
                
                if func_name in TOOL_MAP:
                    try:
                        kwargs = json.loads(args_str) if args_str else {}
                        tool_output = TOOL_MAP[func_name](**kwargs)
                    except json.JSONDecodeError:
                        tool_output = f"Error: Invalid JSON arguments: {args_str}"
                    except Exception as e:
                        tool_output = f"Error executing {func_name}: {e}"
                else:
                    tool_output = f"Tool '{func_name}' not available."
                    
                logger.info(f"Tool Output: {tool_output}")
                tool_results.append(f"Tool '{func_name}' returned: {tool_output}")
            
            # Feed all results back to the agent
            results_summary = "\n".join(tool_results)
            next_input = f"(SYSTEM: {results_summary}\nBased on these results, respond to the user in Portuguese.)"
            
            result = await Runner.run(agent, input=next_input, session=session)
            final_text = result.final_output
            if not isinstance(final_text, str):
                final_text = str(final_text)
            logger.info(f"Agent follow-up response (attempt {attempt+1}): {final_text}")
        
        # --- RESPONSE CLEANUP ---
        reply_text = final_text
        if not isinstance(reply_text, str):
            reply_text = str(reply_text)
            
        # Remove <thought> blocks
        reply_text = re.sub(r'<thought>.*?</thought>', '', reply_text, flags=re.DOTALL)
        
        # Remove [TOOL_CALL] identifiers if any
        reply_text = re.sub(r'\[.*?\]', '', reply_text)
        
        # Clean any residual <function> tags
        reply_text = re.sub(r'<function=.*?>.*?</function>', '', reply_text, flags=re.DOTALL)
        
        # Trim whitespace
        reply_text = reply_text.strip()
        
        # Fallback if empty
        if not reply_text:
            reply_text = "Desculpe, não entendi. Pode repetir?"
            
        send_success = send_message(phone, reply_text)
        
        logger.info(f"[WPP:OUT] phone={phone} success={send_success} reply={reply_text[:100]}...")
        
        status = "processed_and_sent" if send_success else "processed_send_failed"
        
        return {"status": status, "reply": reply_text}

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/appointments", dependencies=[Depends(verify_token)])
async def get_appointments():
    """
    Fetch all scheduled appointments for the dashboard.
    Returns appointment data with patient information.
    """
    from src.database import engine, Appointment, Patient
    from sqlmodel import Session, select
    
    with Session(engine) as session:
        statement = select(Appointment, Patient).join(Patient).where(Appointment.status != "cancelled")
        results = session.exec(statement).all()
        
        appointments = []
        for appointment, patient in results:
            appointments.append({
                "id": appointment.id,
                "patient_name": patient.name,
                "patient_phone": patient.phone,
                "datetime": appointment.datetime.isoformat(),
                "service": appointment.service,
                "status": appointment.status,
                "created_at": appointment.created_at.isoformat()
            })
        
        return {"appointments": appointments}

class AppointmentCreate(SQLModel):
    patient_name: str
    patient_phone: str
    datetime: str
    service: str = "Clínica Geral"

@app.post("/api/appointments", dependencies=[Depends(verify_token)])
async def create_appointment(data: AppointmentCreate):
    """
    Manually create an appointment via Dashboard.
    """
    from src.database import engine, Appointment, Patient
    from sqlmodel import Session, select
    from datetime import datetime
    
    try:
        dt = datetime.fromisoformat(data.datetime)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")

    with Session(engine) as session:
        # Find or create patient
        statement = select(Patient).where(Patient.phone == data.patient_phone)
        patient = session.exec(statement).first()
        
        if not patient:
            patient = Patient(name=data.patient_name, phone=data.patient_phone)
            session.add(patient)
            session.commit()
            session.refresh(patient)
            
        # Create appointment
        appointment = Appointment(
            patient_id=patient.id,
            datetime=dt,
            service=data.service,
            status="confirmed" # Manual entries are assumed confirmed
        )
        session.add(appointment)
        session.commit()
        session.refresh(appointment)
        
        return {"status": "success", "id": appointment.id}

class AppointmentUpdate(SQLModel):
    patient_name: str | None = None
    patient_phone: str | None = None
    datetime: str | None = None
    service: str | None = None
    status: str | None = None

@app.put("/api/appointments/{appointment_id}", dependencies=[Depends(verify_token)])
async def update_appointment(appointment_id: int, data: AppointmentUpdate):
    """
    Update an existing appointment.
    """
    from src.database import engine, Appointment, Patient
    from sqlmodel import Session, select
    from datetime import datetime

    with Session(engine) as session:
        appointment = session.get(Appointment, appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Update appointment fields
        if data.datetime:
            try:
                appointment.datetime = datetime.fromisoformat(data.datetime)
            except ValueError:
               raise HTTPException(status_code=400, detail="Invalid datetime format")
        
        if data.status:
            appointment.status = data.status

        if data.service:
            appointment.service = data.service

        # Update Patient info if provided
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

@app.delete("/api/appointments/{appointment_id}", dependencies=[Depends(verify_token)])
async def delete_appointment(appointment_id: int):
    """
    Delete an appointment.
    """
    from src.database import engine, Appointment
    from sqlmodel import Session

    with Session(engine) as session:
        appointment = session.get(Appointment, appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
            
        session.delete(appointment)
        session.commit()
        
        return {"status": "success"}

# Mount static files (Dashboard) - MUST BE LAST
# Check for 'static' dir (Production) or 'dashboard/dist' (Local)
static_dir = os.path.join(os.getcwd(), "static")
if not os.path.exists(static_dir):
    static_dir = os.path.join(os.getcwd(), "dashboard", "dist")

if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    logger.warning(f"Static directory not found at {static_dir}. Dashboard will not be served.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
