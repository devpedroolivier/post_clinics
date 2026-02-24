import asyncio
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta
from src.application.agent import agent
from agents import Runner, SQLiteSession

# --- Configuration ---
API_URL = "http://localhost:8000"
TEST_PHONE = "5511999999999"
TEST_NAME = "Full System Test"
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "clinica_espaco_interativo_reabilitare")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

def get_auth_headers():
    """Authenticate and return Authorization headers."""
    response = requests.post(
        f"{API_URL}/api/auth/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    token = data.get("access_token") or data.get("token")
    if not token:
        raise RuntimeError("Login succeeded but no token returned.")
    return {"Authorization": f"Bearer {token}"}

async def test_agent_scheduling():
    print(f"\n--- 1. Testing Agent Scheduling (Agendamento) ---")
    session_id = f"zapi:{TEST_PHONE}"
    session = SQLiteSession(db_path="conversations.db", session_id=session_id)
    
    # 1. User Intent
    input_text = f"Olá, gostaria de marcar uma consulta de Clínica Geral para amanhã às 14:00. Meu nome é {TEST_NAME}."
    print(f"User: {input_text}")
    
    result = await Runner.run(agent, input=input_text, session=session)
    print(f"Agent: {result.final_output}")
    
    # Verify via API (Simulating Dashboard View)
    print("\nVerifying via Dashboard API (GET /api/appointments)...")
    headers = get_auth_headers()
    response = requests.get(f"{API_URL}/api/appointments", headers=headers, timeout=30)
    if response.status_code == 200:
        appointments = response.json()["appointments"]
        found = False
        for apt in appointments:
            if apt["patient_phone"] == TEST_PHONE and "14:00" in apt["datetime"]:
                print(f"✅ SUCCESS: Found appointment for {apt['patient_name']} at {apt['datetime']}")
                found = True
                break
        if not found:
            print("❌ FAILURE: Appointment not found in API.")
    else:
        print(f"❌ FAILURE: API Error {response.status_code}")

    return session

async def test_dashboard_manual_entry():
    print(f"\n--- 2. Testing Dashboard Manual Entry (POST API) ---")
    headers = get_auth_headers()
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    payload = {
        "patient_name": "Manual Entry User",
        "patient_phone": "5511888888888",
        "datetime": f"{tomorrow}T16:00:00",
        "service": "Implante"
    }
    
    print(f"Sending POST to {API_URL}/api/appointments with: {json.dumps(payload)}")
    response = requests.post(f"{API_URL}/api/appointments", json=payload, headers=headers, timeout=30)
    
    if response.status_code == 200:
        print(f"✅ SUCCESS: API returned {response.json()}")
    else:
        print(f"❌ FAILURE: API Error {response.status_code} - {response.text}")

    # Verify persistence
    print("Verifying persistence via GET API...")
    response = requests.get(f"{API_URL}/api/appointments", headers=headers, timeout=30)
    appointments = response.json()["appointments"]
    found = any(apt["patient_phone"] == "5511888888888" for apt in appointments)
    if found:
         print("✅ SUCCESS: Manual entry persisted and visible.")
    else:
         print("❌ FAILURE: Manual entry not found.")

async def main():
    print("🚀 Starting Full System Verification...")
    
    # Run Agent Test
    await test_agent_scheduling()
    
    # Run Dashboard Manual Entry Test
    await test_dashboard_manual_entry()

if __name__ == "__main__":
    asyncio.run(main())
