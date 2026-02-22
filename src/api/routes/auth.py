import os
from fastapi import APIRouter, HTTPException
from src.domain.schemas import LoginRequest

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/login")
async def login(req: LoginRequest):
    expected_user = os.getenv("ADMIN_USERNAME", "clinica_espaco_interativo_reabilitare")
    expected_pass = os.getenv("ADMIN_PASSWORD", "admin")
    expected_token = os.getenv("ADMIN_TOKEN", "post-clinics-mvp-secure-token")
    
    if req.username == expected_user and req.password == expected_pass:
        return {"token": expected_token}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")
