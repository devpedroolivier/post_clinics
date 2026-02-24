import httpx
import logging
import asyncio
from src.core.config import Z_API_CONFIG

logger = logging.getLogger("PostClinics.ZApi")

async def send_message(phone: str, message: str, max_retries: int = 3):
    """
    Sends a message via Z-API with automatic retry logic.
    Returns: dict with {success, status_code, error_message}
    """
    instance_id = Z_API_CONFIG.get("instance_id")
    token = Z_API_CONFIG.get("token")
    client_token = Z_API_CONFIG.get("client_token")
    
    if not instance_id or not token or not client_token:
        error = "Z-API credentials incomplete."
        logger.error(error)
        return {"success": False, "status_code": 0, "error_message": error}
        
    url = f"https://api.z-api.io/instances/{instance_id}/token/{token}/send-text"
    
    headers = {
        "Client-Token": client_token,
        "Content-Type": "application/json"
    }
    
    payload = {
        "phone": phone,
        "message": message
    }
    
    attempts = 0
    backoff = 2 # seconds
    
    while attempts < max_retries:
        attempts += 1
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=12)
                
            if response.status_code == 200:
                logger.info(f"Message sent to {phone} (Attempt {attempts}): {response.json()}")
                return {"success": True, "status_code": 200, "error_message": None}
            
            # If 4xx, it's a client error (invalid phone, etc.) - don't retry
            if 400 <= response.status_code < 500:
                error = f"Z-API Client Error {response.status_code}: {response.text}"
                logger.error(error)
                return {"success": False, "status_code": response.status_code, "error_message": error}
                
            # If 5xx, it's a server error - retry
            logger.warning(f"Z-API Server Error {response.status_code} (Attempt {attempts}/{max_retries}). Retrying in {backoff}s...")
            
        except (httpx.RequestError, asyncio.TimeoutError) as e:
            logger.warning(f"Z-API Connectivity Error (Attempt {attempts}/{max_retries}): {str(e)}. Retrying in {backoff}s...")
            
        if attempts < max_retries:
            await asyncio.sleep(backoff)
            backoff *= 2 # Exponential backoff
            
    error_msg = f"Failed to send message after {max_retries} attempts."
    logger.error(error_msg)
    return {"success": False, "status_code": 500, "error_message": error_msg}
