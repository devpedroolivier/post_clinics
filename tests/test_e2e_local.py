"""
Local E2E Test - Simulates Z-API webhook calls to validate the full flow.
"""
import urllib.request
import json
import time

BASE = "http://localhost:8000"

def send_webhook(phone, message, msg_id):
    """Send a simulated Z-API webhook."""
    payload = json.dumps({
        "phone": phone,
        "text": {"message": message},
        "messageId": msg_id,
        "fromMe": False,
        "isGroup": False
    }).encode()
    
    req = urllib.request.Request(
        f"{BASE}/webhook/zapi",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        r = urllib.request.urlopen(req, timeout=60)
        result = json.loads(r.read().decode())
        return result
    except Exception as e:
        return {"status": "error", "reply": str(e)}

def get_appointments():
    """Get all appointments from API."""
    r = urllib.request.urlopen(f"{BASE}/api/appointments")
    return json.loads(r.read().decode())["appointments"]

def check_health():
    """Check API health."""
    r = urllib.request.urlopen(f"{BASE}/api/health")
    return json.loads(r.read().decode())

# ========================================
print("=" * 60)
print("  POST Clinics - Local E2E Test")
print("=" * 60)

# 0. Health Check
health = check_health()
print(f"\n[0] Health: {health}")

# 1. New patient greeting
print("\n[1] Saudacao...")
r1 = send_webhook("5511888887777", "Ola! Gostaria de agendar uma consulta de ortodontia para quinta 13/02 as 11:00. Meu nome e Joao Santos.", "e2e-001")
print(f"    Status: {r1['status']}")
print(f"    Reply: {r1['reply'][:200]}")

time.sleep(2)

# 2. Check DB state 
print("\n[2] Checking DB...")
appts = get_appointments()
print(f"    Total appointments: {len(appts)}")
for a in appts:
    print(f"    - ID:{a['id']} {a['patient_name']} | {a['service']} | {a['datetime']} | {a['status']}")

# 3. Second patient
print("\n[3] Segundo paciente...")
r3 = send_webhook("5511777776666", "Oi! Tenho consulta para marcar de clinica geral. Pode ser dia 13/02 as 11:00? Sou Ana Costa.", "e2e-003")
print(f"    Status: {r3['status']}")
print(f"    Reply: {r3['reply'][:200]}")

time.sleep(2)

# 4. Final DB state
print("\n[4] Final DB state...")
appts = get_appointments()
print(f"    Total appointments: {len(appts)}")
for a in appts:
    print(f"    - ID:{a['id']} {a['patient_name']} | {a['service']} | {a['datetime']} | {a['status']}")

print("\n" + "=" * 60)
print("  E2E TEST COMPLETE")
print("=" * 60)
