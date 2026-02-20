"""
Restore backup data into the current database.
Migrates appointments adding default values for new columns.
"""
import sqlite3
import shutil
from datetime import datetime

CURRENT_DB = r"c:\Users\Pedri\noshowai_mvp\data\post_clinics.db"
BACKUP_DB = r"c:\Users\Pedri\noshowai_mvp\data\post_clinics_backup_20260206_103450.db"

# Safety: backup current before overwriting
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
safety_copy = CURRENT_DB.replace(".db", f"_pre_restore_{timestamp}.db")
shutil.copy2(CURRENT_DB, safety_copy)
print(f"Safety copy: {safety_copy}")

# Connect to both
current = sqlite3.connect(CURRENT_DB)
backup = sqlite3.connect(BACKUP_DB)

cc = current.cursor()
bc = backup.cursor()

# --- Restore Patients ---
bc.execute("SELECT id, name, phone, created_at FROM patient")
backup_patients = bc.fetchall()

# Clear current patients (only has test data)
cc.execute("DELETE FROM appointment")
cc.execute("DELETE FROM patient")
current.commit()

inserted_p = 0
for pid, name, phone, created_at in backup_patients:
    cc.execute(
        "INSERT INTO patient (id, name, phone, created_at) VALUES (?, ?, ?, ?)",
        (pid, name, phone, created_at)
    )
    inserted_p += 1

current.commit()
print(f"Restored {inserted_p} patients")

# --- Restore Appointments ---
bc.execute("SELECT id, patient_id, datetime, status, created_at FROM appointment")
backup_appointments = bc.fetchall()

inserted_a = 0
for aid, patient_id, dt, status, created_at in backup_appointments:
    cc.execute(
        "INSERT INTO appointment (id, patient_id, datetime, status, created_at, service, notified_24h, notified_3h) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (aid, patient_id, dt, status, created_at, "Clínica Geral", 0, 0)
    )
    inserted_a += 1

current.commit()
print(f"Restored {inserted_a} appointments")

# --- Verify ---
cc.execute("SELECT COUNT(*) FROM patient")
print(f"\nFinal patient count: {cc.fetchone()[0]}")
cc.execute("SELECT COUNT(*) FROM appointment")
print(f"Final appointment count: {cc.fetchone()[0]}")

current.close()
backup.close()
print("\nRestore complete!")
