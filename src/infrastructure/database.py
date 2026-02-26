from sqlmodel import SQLModel, create_engine, Session
from src.core.config import DATA_DIR
import os
import sqlite3

# Import models so SQLModel knows about them before create_all
from src.domain.models import Patient, Appointment, NotificationLog

# Database Setup
DATABASE_FILE = os.path.join(DATA_DIR, "post_clinics.db")
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

engine = create_engine(DATABASE_URL, echo=False)

def _get_columns(cursor, table_name: str) -> list[str]:
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]


def _apply_lightweight_migrations():
    if not os.path.exists(DATABASE_FILE):
        return

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        tables = {row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")}

        if "appointment" in tables:
            appointment_columns = _get_columns(cursor, "appointment")
            if "notified_24h" not in appointment_columns:
                cursor.execute("ALTER TABLE appointment ADD COLUMN notified_24h BOOLEAN DEFAULT 0")
            if "notified_3h" not in appointment_columns:
                cursor.execute("ALTER TABLE appointment ADD COLUMN notified_3h BOOLEAN DEFAULT 0")
            if "professional" not in appointment_columns:
                cursor.execute("ALTER TABLE appointment ADD COLUMN professional VARCHAR DEFAULT 'Clínica Geral'")

            cursor.execute(
                """
                UPDATE appointment
                SET service = 'Odontopediatria (Consulta)'
                WHERE LOWER(TRIM(service)) = 'odontopediatria (retorno)'
                """
            )
            cursor.execute(
                """
                UPDATE appointment
                SET service = 'Paciente com necessidades especiais (1ª vez)'
                WHERE LOWER(TRIM(service)) = 'pacientes especiais (1ª vez)'
                """
            )
            cursor.execute(
                """
                UPDATE appointment
                SET service = 'Paciente com necessidades especiais (Consulta)'
                WHERE LOWER(TRIM(service)) IN (
                    'pacientes especiais (retorno)',
                    'paciente com necessidades especiais (retorno)'
                )
                """
            )

        if "patient" in tables:
            patient_columns = _get_columns(cursor, "patient")
            if "contact_phone" not in patient_columns:
                cursor.execute("ALTER TABLE patient ADD COLUMN contact_phone VARCHAR")
            if "responsible_name" not in patient_columns:
                cursor.execute("ALTER TABLE patient ADD COLUMN responsible_name VARCHAR")

            cursor.execute(
                """
                UPDATE patient
                SET contact_phone = phone
                WHERE contact_phone IS NULL OR TRIM(contact_phone) = ''
                """
            )

        conn.commit()
    finally:
        conn.close()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    _apply_lightweight_migrations()

def get_session():
    with Session(engine) as session:
        yield session

if __name__ == "__main__":
    create_db_and_tables()
    print("Database tables created.")
