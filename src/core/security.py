import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from collections.abc import Mapping

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import ExpiredSignatureError, InvalidTokenError

from src.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    WEBHOOK_SIGNATURE_HEADER,
    WEBHOOK_SIGNATURE_SECRET,
    WEBHOOK_VALIDATE_SIGNATURE,
)

security = HTTPBearer(auto_error=False)

def _get_jwt_secret() -> str:
    if not JWT_SECRET_KEY:
        raise HTTPException(
            status_code=500,
            detail="JWT secret não configurado. Defina JWT_SECRET_KEY no ambiente.",
        )
    return JWT_SECRET_KEY

def create_access_token(subject: str, expires_minutes: int | None = None) -> tuple[str, int]:
    minutes = expires_minutes if expires_minutes is not None else ACCESS_TOKEN_EXPIRE_MINUTES
    now = datetime.now(timezone.utc)
    expire_at = now + timedelta(minutes=minutes)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": expire_at,
    }
    token = jwt.encode(payload, _get_jwt_secret(), algorithm=JWT_ALGORITHM)
    return token, int(minutes * 60)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(
            credentials.credentials,
            _get_jwt_secret(),
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp"]},
        )
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

    return payload["sub"]

def verify_webhook_signature(headers: Mapping[str, str], raw_body: bytes):
    if not WEBHOOK_VALIDATE_SIGNATURE:
        return

    if not WEBHOOK_SIGNATURE_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Validação de webhook habilitada, mas WEBHOOK_SIGNATURE_SECRET não está definido.",
        )

    received_signature = headers.get(WEBHOOK_SIGNATURE_HEADER)
    if not received_signature:
        raise HTTPException(status_code=401, detail="Assinatura do webhook ausente")

    signature = received_signature.strip()
    if signature.startswith("sha256="):
        signature = signature[7:]

    expected_signature = hmac.new(
        WEBHOOK_SIGNATURE_SECRET.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Assinatura do webhook inválida")

def generate_signature(raw_body: bytes) -> str:
    """Generate a HMAC-SHA256 signature for testing or internal use."""
    if not WEBHOOK_SIGNATURE_SECRET:
        return ""
    return hmac.new(
        WEBHOOK_SIGNATURE_SECRET.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

