import json
import logging
from collections import defaultdict
import time as _time
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks

from src.core.config import ANTISPAM_CONFIG
from src.core.security import verify_webhook_signature
from src.application.services.message_handler import process_webhook_payload

logger = logging.getLogger("PostClinics.Webhook")
router = APIRouter(prefix="/webhook", tags=["Webhooks"])

# State for rate limiting and dedup
_seen_messages = {}
_phone_timestamps = defaultdict(list)


@router.post("/zapi")
async def receiver(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint request from Z-API.
    Accepts arbitrary JSON and manually extracts fields to be robust against structure variations.
    Includes anti-spam protection: rate limiting per phone and message deduplication.
    """
    global _seen_messages, _phone_timestamps
    
    try:
        raw_body = await request.body()
        verify_webhook_signature(request.headers, raw_body)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        phone = payload.get("phone")
        
        # Extract text content
        text_content = ""
        text_data = payload.get("text")
        
        if isinstance(text_data, dict):
            text_content = text_data.get("message", "")
        elif isinstance(text_data, str):
            text_content = text_data
            
        message_id = payload.get("messageId", "unknown")
        logger.info(
            "[WPP:RAW] msgId=%s fromMe=%s isGroup=%s phoneSuffix=%s",
            message_id,
            payload.get("fromMe", False),
            payload.get("isGroup", False),
            (str(phone)[-4:] if phone else "none"),
        )
            
        if not phone or not text_content:
            logger.warning(f"Ignored payload (missing phone/text): {payload}")
            return {"status": "ignored", "reason": "missing_data"}

        if payload.get("fromMe", False) or payload.get("isGroup", False) or payload.get("isNewsletter", False):
             return {"status": "ignored", "reason": "filtered_source"}

        now = _time.time()
        
        # --- ANTI-SPAM: Message Deduplication ---
        dedup_window = ANTISPAM_CONFIG["dedup_window_seconds"]
        _seen_messages = {
            k: v for k, v in _seen_messages.items()
            if now - v < dedup_window
        }
        
        if message_id in _seen_messages:
            logger.info(f"[ANTISPAM] Duplicate message ignored: {message_id}")
            return {"status": "ignored", "reason": "duplicate_message"}
        
        _seen_messages[message_id] = now
        
        # --- ANTI-SPAM: Rate Limiting per Phone ---
        max_per_min = ANTISPAM_CONFIG["max_messages_per_minute"]
        cooldown = ANTISPAM_CONFIG["cooldown_seconds"]
        
        _phone_timestamps[phone] = [
            ts for ts in _phone_timestamps[phone]
            if now - ts < 60
        ]
        
        timestamps = _phone_timestamps[phone]
        
        if len(timestamps) >= max_per_min:
            logger.warning(f"[ANTISPAM] Rate limit exceeded for {phone}: {len(timestamps)} msgs/min")
            return {"status": "ignored", "reason": "rate_limited"}
        
        if timestamps and (now - timestamps[-1]) < cooldown:
            logger.info(f"[ANTISPAM] Cooldown active for {phone}: {now - timestamps[-1]:.1f}s < {cooldown}s")
            return {"status": "ignored", "reason": "cooldown"}
        
        _phone_timestamps[phone].append(now)

        # --- ENQUEUE PROCESS MESSAGE ---
        background_tasks.add_task(process_webhook_payload, phone, message_id, text_content)
        return {"status": "queued"}

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"CRITICAL Error processing webhook: {e}\n{error_trace}")
        raise HTTPException(status_code=500, detail=str(e))
