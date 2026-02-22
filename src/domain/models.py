from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Patient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: str
    created_at: datetime = Field(default_factory=datetime.now)

class Appointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patient.id")
    datetime: datetime
    service: str = Field(default="Clínica Geral")
    status: str  # "scheduled", "confirmed", "cancelled"
    created_at: datetime = Field(default_factory=datetime.now)
    notified_24h: bool = Field(default=False)
    notified_3h: bool = Field(default=False)
