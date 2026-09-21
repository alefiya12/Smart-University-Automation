from app.database import SessionLocal
from app.services.admission_service import process_single_admission
import logging

logging.basicConfig(level=logging.DEBUG)

db = SessionLocal()
payload = {
    'email': 'testpdf@student.smartuniversity.edu',
    'full_name': 'Test PDF Student',
    'department_name': 'General',
    'course_name': 'Unknown',
    'admission_year': 2026,
    'semester': 1
}
res = process_single_admission(db, payload)
print(res)
