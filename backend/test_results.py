import os
import sys
import asyncio
from app.database import SessionLocal
from app.services.result_service import process_bulk_results
from app.models.student import Student

db = SessionLocal()

# Provide a student ID from our DB
student = db.query(Student).first()
enrollment_no = student.enrollment_no

print(f"Testing for student: {enrollment_no}")

records_valid = [
    {"student_id": enrollment_no, "subject_name": "Mathematics", "internal_score": 15, "external_score": 50}, # PASS
    {"student_id": enrollment_no, "subject_name": "Physics", "internal_score": 11, "external_score": 60} # FAIL internal threshold
]

res = process_bulk_results(db, records_valid, triggered_by="test")
print("Valid Run Result:", res)

records_invalid = [
    {"student_id": enrollment_no, "subject_name": "Physics", "internal_score": 35, "external_score": 50} # Out of bounds
]

res2 = process_bulk_results(db, records_invalid, triggered_by="test")
print("Invalid Run Result:", res2)

db.refresh(student)
print("Student Academic Standing:", student.academic_standing)

db.close()
