import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    expected_token = os.getenv("ADMIN_TOKEN", "post-clinics-mvp-secure-token")
    if credentials.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Token inválido")
    return credentials.credentials
