from pydantic import BaseModel
from sqlmodel import SQLModel

class LoginRequest(BaseModel):
    username: str
    password: str

class AppointmentCreate(SQLModel):
    patient_name: str
    patient_phone: str
    datetime: str
    service: str = "Clínica Geral"

class AppointmentUpdate(SQLModel):
    patient_name: str | None = None
    patient_phone: str | None = None
    datetime: str | None = None
    service: str | None = None
    status: str | None = None
