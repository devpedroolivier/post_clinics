import requests
import json
import sys

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
    
    try:
        print(f"Sending POST to {url}")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Response Code:", response.status_code)
        print("Response JSON:", response.json())
    except Exception as e:
        print(f"Error: {e}")
        # Dont exit 1 to allow logs to be read if server is down, just print

if __name__ == "__main__":
    verify()
