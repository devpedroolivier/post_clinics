import shutil
import sqlite3
import os
from datetime import datetime
from src.config import DATA_DIR
from src.database import create_db_and_tables

def migrate_db():
    print("Starting database migration for Notification Flags...")
    
    db_path = os.path.join(DATA_DIR, "post_clinics.db")
    if not os.path.exists(db_path):
        print("Database not found. Creating new...")
        create_db_and_tables()
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check existing columns
        cursor.execute("PRAGMA table_info(appointment)")
        columns = [info[1] for info in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        # Add notified_24h if missing
        if "notified_24h" not in columns:
            print("Adding 'notified_24h' column...")
            cursor.execute("ALTER TABLE appointment ADD COLUMN notified_24h BOOLEAN DEFAULT 0")
        else:
            print("'notified_24h' already exists.")
            
        # Add notified_3h if missing
        if "notified_3h" not in columns:
            print("Adding 'notified_3h' column...")
            cursor.execute("ALTER TABLE appointment ADD COLUMN notified_3h BOOLEAN DEFAULT 0")
        else:
            print("'notified_3h' already exists.")
            
        conn.commit()
        print("Migration completed successfully.")
        
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
