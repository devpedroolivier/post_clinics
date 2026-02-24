import os
from fastapi import APIRouter, HTTPException
from src.domain.schemas import LoginRequest
from src.core.security import create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/login")
async def login(req: LoginRequest):
    expected_user = os.getenv("ADMIN_USERNAME", "clinica_espaco_interativo_reabilitare")
    expected_pass = os.getenv("ADMIN_PASSWORD", "admin")
    
    if req.username == expected_user and req.password == expected_pass:
        token, expires_in = create_access_token(subject=expected_user)
        # Keep legacy "token" for frontend backward compatibility.
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": expires_in,
            "token": token,
        }
    raise HTTPException(status_code=401, detail="Credenciais inválidas")
