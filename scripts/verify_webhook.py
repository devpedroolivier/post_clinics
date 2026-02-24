import requests
import json
import sys
import os
import hmac
import hashlib

WEBHOOK_SIGNATURE_SECRET = os.getenv("WEBHOOK_SIGNATURE_SECRET", "change_me_webhook_secret")
WEBHOOK_SIGNATURE_HEADER = os.getenv("WEBHOOK_SIGNATURE_HEADER", "X-Webhook-Signature")

def build_signature(payload_bytes: bytes) -> str:
    digest = hmac.new(
        WEBHOOK_SIGNATURE_SECRET.encode("utf-8"),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"

def verify():
    url = "http://127.0.0.1:8000/webhook/zapi"
    # Z-API simulated payload
    payload = {
        "phone": "5511999999999",
        "text": {
            "message": "Quero agendar disponibilidade para 2025-12-01"
        },
        "messageId": "TEST-MSG-001",
        "fromMe": False,
        "isGroup": False
    }
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    
    try:
        print(f"Sending POST to {url}")
        response = requests.post(
            url,
            data=payload_bytes,
            headers={
                "Content-Type": "application/json",
                WEBHOOK_SIGNATURE_HEADER: build_signature(payload_bytes),
            },
            timeout=30,
        )
        response.raise_for_status()
        print("Response Code:", response.status_code)
        print("Response JSON:", response.json())
    except Exception as e:
        print(f"Error: {e}")
        # Dont exit 1 to allow logs to be read if server is down, just print

if __name__ == "__main__":
    verify()
