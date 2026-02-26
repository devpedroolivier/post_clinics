from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON

class ClinicSettings(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default="Espaço Interativo Reabilitare")
    assistant_name: str = Field(default="Cora")
    hours_description: str = Field(default="")
    schedules: dict = Field(default_factory=dict, sa_column=Column(JSON))
    services: list = Field(default_factory=list, sa_column=Column(JSON))
    cancellation_policy: str = Field(default="Cancelamentos devem ser feitos com 24h de antecedência.")
    communication_flow: str = Field(default="Enviamos confirmação 1 dia antes e lembrete 3h antes da consulta.")

class Patient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: str
    contact_phone: str = Field(default="")
    responsible_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class Appointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patient.id")
    datetime: datetime
    service: str = Field(default="Clínica Geral")
    professional: str = Field(default="Clínica Geral")
    status: str  # "scheduled", "confirmed", "cancelled"
    created_at: datetime = Field(default_factory=datetime.now)
    notified_24h: bool = Field(default=False)
    notified_3h: bool = Field(default=False)

class NotificationLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    appointment_id: int = Field(foreign_key="appointment.id")
    notification_type: str  # "24h", "3h"
    status: str  # "sent", "failed"
    error_message: Optional[str] = None
    attempt_count: int = Field(default=1)
    sent_at: datetime = Field(default_factory=datetime.now)
