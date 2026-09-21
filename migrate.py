import sqlite3

conn = sqlite3.connect('backend/smartuniversity.db')
c = conn.cursor()

new_columns = [
    ("total_seats", "INTEGER DEFAULT 60"),
    ("quota_obc", "FLOAT DEFAULT 27.0"),
    ("quota_sc", "FLOAT DEFAULT 15.0"),
    ("quota_st", "FLOAT DEFAULT 7.5"),
    ("quota_ews", "FLOAT DEFAULT 10.0"),
    ("min_class_12_pct", "FLOAT DEFAULT 60.0"),
    ("min_core_subject_score", "FLOAT DEFAULT 50.0"),
    ("relaxation_sc_st_pct", "FLOAT DEFAULT 5.0"),
    ("relaxation_obc_ews_pct", "FLOAT DEFAULT 0.0")
]

for col_name, col_type in new_columns:
    try:
        c.execute(f"ALTER TABLE courses ADD COLUMN {col_name} {col_type}")
        print(f"Added {col_name}")
    except sqlite3.OperationalError as e:
        print(f"Skipped {col_name}: {e}")

conn.commit()
conn.close()

import sys
sys.path.append('backend')
from app.database import engine, Base
from app.models.admission_staging import AdmissionStaging
from app.models.course import Course

Base.metadata.create_all(bind=engine)
print("Migration completed.")
