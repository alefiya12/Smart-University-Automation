import sys
import os
import pandas as pd
from datetime import date

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from app.database import SessionLocal
from app.services.attendance_service import process_bulk_attendance_excel, get_student_subject_summaries, get_student_daily_logs
from app.models.student import Student

# 1. Create the Excel data
data = [
    {"student_id": "SU2026-0001", "date": "2026-09-01", "Mathematics": 1, "Physics": 1},
    {"student_id": "SU2026-0002", "date": "2026-09-01", "Mathematics": 1, "Physics": 0},
    {"student_id": "SU2026-0001", "date": "2026-09-02", "Mathematics": 1, "Physics": 1},
    {"student_id": "SU2026-0002", "date": "2026-09-02", "Mathematics": 0, "Physics": 0},
    {"student_id": "SU2026-0001", "date": "2026-09-01", "Mathematics": 1, "Physics": 1}, # duplicate date entry
]

db = SessionLocal()
try:
    print("Testing Upload...")
    res = process_bulk_attendance_excel(db, data, course_id=1, triggered_by="test_script")
    print("Upload Result:", res)

    s1 = db.query(Student).filter(Student.enrollment_no == "SU2026-0001").first()
    s2 = db.query(Student).filter(Student.enrollment_no == "SU2026-0002").first()

    if s1:
        print("\nSummary for SU2026-0001:")
        print(get_student_subject_summaries(db, s1.id))
        print("Daily logs:", len(get_student_daily_logs(db, s1.id)))

    if s2:
        print("\nSummary for SU2026-0002:")
        print(get_student_subject_summaries(db, s2.id))
        print("Daily logs:", len(get_student_daily_logs(db, s2.id)))

finally:
    db.close()
