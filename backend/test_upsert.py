from app.database import SessionLocal
from app.models.result import StudentMarksRecord

db = SessionLocal()
records = db.query(StudentMarksRecord).all()
for r in records:
    print(f"Record: ID={r.id}, Student={r.student_id}, Subject={r.subject_id}, Sem={r.semester_number}")
print(f"Total Records: {len(records)}")
db.close()
