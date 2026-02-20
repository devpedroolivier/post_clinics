import sqlite3

def inspect_db(path, label):
    print(f"=== {label} ===")
    print(f"Path: {path}")
    conn = sqlite3.connect(path)
    c = conn.cursor()
    
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
    print(f"Tables: {tables}")
    
    for t in tables:
        c.execute(f"SELECT COUNT(*) FROM {t}")
        count = c.fetchone()[0]
        print(f"\n  [{t}] {count} rows")
        
        c.execute(f"PRAGMA table_info({t})")
        cols = [r[1] for r in c.fetchall()]
        print(f"  Columns: {cols}")
        
        c.execute(f"SELECT * FROM {t}")
        rows = c.fetchall()
        for r in rows:
            print(f"    {r}")
    
    conn.close()
    print()

inspect_db(r"c:\Users\Pedri\noshowai_mvp\data\post_clinics.db", "CURRENT DB")
inspect_db(r"c:\Users\Pedri\noshowai_mvp\data\post_clinics_backup_20260206_103450.db", "BACKUP DB")
