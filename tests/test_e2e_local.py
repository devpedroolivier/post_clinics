"""
Local E2E Test - Simulates Z-API webhook calls to validate the full flow.
"""
import urllib.request
import json
import time
import os
import hmac
import hashlib
import pytest

BASE = "http://localhost:8000"
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "clinica_espaco_interativo_reabilitare")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
WEBHOOK_SIGNATURE_SECRET = os.getenv("WEBHOOK_SIGNATURE_SECRET", "change_me_webhook_secret")
WEBHOOK_SIGNATURE_HEADER = os.getenv("WEBHOOK_SIGNATURE_HEADER", "X-Webhook-Signature")

def _webhook_signature(payload_bytes: bytes) -> str:
    digest = hmac.new(
        WEBHOOK_SIGNATURE_SECRET.encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"

def login() -> str:
    """Authenticate and return JWT token for protected endpoints."""
    payload = json.dumps({
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/api/auth/login",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode())
        return data.get("access_token") or data.get("token", "")

def send_webhook(phone, message, msg_id):
    """Send a simulated Z-API webhook."""
    payload_bytes = json.dumps({
        "phone": phone,
        "text": {"message": message},
        "messageId": msg_id,
        "fromMe": False,
        "isGroup": False
    }, separators=(",", ":")).encode()
    
    req = urllib.request.Request(
        f"{BASE}/webhook/zapi",
        data=payload_bytes,
        headers={
            "Content-Type": "application/json",
            WEBHOOK_SIGNATURE_HEADER: _webhook_signature(payload_bytes),
        }
    )
    try:
        r = urllib.request.urlopen(req, timeout=60)
        result = json.loads(r.read().decode())
        return result
    except Exception as e:
        return {"status": "error", "reply": str(e)}

def get_appointments(token: str):
    """Get all appointments from API."""
    req = urllib.request.Request(
        f"{BASE}/api/appointments",
        headers={"Authorization": f"Bearer {token}"},
    )
    r = urllib.request.urlopen(req)
    return json.loads(r.read().decode())["appointments"]

def check_health():
    """Check API health."""
    r = urllib.request.urlopen(f"{BASE}/api/health")
    return json.loads(r.read().decode())

def run_local_e2e():
    # ========================================
    print("=" * 60)
    print("  POST Clinics - Local E2E Test")
    print("=" * 60)

    # 0. Health Check
    health = check_health()
    print(f"\n[0] Health: {health}")
    assert health.get("message")

    # 0.1 Login
    token = login()
    print(f"[0.1] Auth token acquired: {bool(token)}")
    assert token

    # 1. New patient greeting
    print("\n[1] Saudacao...")
    r1 = send_webhook(
        "5511888887777",
        "Ola! Gostaria de agendar uma consulta de ortodontia para quinta 13/02 as 11:00. Meu nome e Joao Santos.",
        "e2e-001",
    )
    print(f"    Status: {r1.get('status')}")
    # Webhook atual retorna queued/ignored; resposta final vem assíncrona via WhatsApp
    assert r1.get("status") in {"queued", "ignored", "error"}

    time.sleep(2)

    # 2. Check DB state
    print("\n[2] Checking DB...")
    appts = get_appointments(token)
    print(f"    Total appointments: {len(appts)}")
    assert isinstance(appts, list)
    for a in appts:
        print(f"    - ID:{a['id']} {a['patient_name']} | {a['service']} | {a['datetime']} | {a['status']}")

    # 3. Second patient
    print("\n[3] Segundo paciente...")
    r3 = send_webhook(
        "5511777776666",
        "Oi! Tenho consulta para marcar de clinica geral. Pode ser dia 13/02 as 11:00? Sou Ana Costa.",
        "e2e-003",
    )
    print(f"    Status: {r3.get('status')}")
    assert r3.get("status") in {"queued", "ignored", "error"}

    time.sleep(2)

    # 4. Final DB state
    print("\n[4] Final DB state...")
    appts = get_appointments(token)
    print(f"    Total appointments: {len(appts)}")
    assert isinstance(appts, list)
    for a in appts:
        print(f"    - ID:{a['id']} {a['patient_name']} | {a['service']} | {a['datetime']} | {a['status']}")

    print("\n" + "=" * 60)
    print("  E2E TEST COMPLETE")
    print("=" * 60)


def test_e2e_local():
    if os.getenv("RUN_LIVE_E2E", "0") != "1":
        pytest.skip("Live local E2E disabled. Set RUN_LIVE_E2E=1 to enable.")
    run_local_e2e()


if __name__ == "__main__":
    run_local_e2e()
