from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, create_engine, Session

# Define Models
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

from src.config import DATA_DIR
import os

# Database Setup
DATABASE_FILE = os.path.join(DATA_DIR, "post_clinics.db")
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

if __name__ == "__main__":
    create_db_and_tables()
    print("Database tables created.")
