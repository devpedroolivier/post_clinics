from sqlmodel import SQLModel, create_engine, Session
from src.core.config import DATA_DIR
import os

# Import models so SQLModel knows about them before create_all
from src.domain.models import Patient, Appointment

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
