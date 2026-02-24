import httpx
import logging
from src.core.config import Z_API_CONFIG

logger = logging.getLogger("PostClinics.ZApi")

async def send_message(phone: str, message: str):
    instance_id = Z_API_CONFIG.get("instance_id")
    token = Z_API_CONFIG.get("token")
    client_token = Z_API_CONFIG.get("client_token")
    
    if not instance_id or not token or not client_token:
        logger.error("Z-API credentials incomplete. Missing instance_id, token or client_token.")
        return False
        
    url = f"https://api.z-api.io/instances/{instance_id}/token/{token}/send-text"
    
    headers = {
        "Client-Token": client_token,
        "Content-Type": "application/json"
    }
    
    payload = {
        "phone": phone,
        "message": message
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
        logger.info(f"Message sent to {phone}: {response.json()}")
        return True
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Error sending to Z-API: {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"Error sending to Z-API: {e}")
        return False
