import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.faculty import Faculty
from app.models.student import Student
from app.models.department import Department
from app.models.course import Course
from app.utils.security import hash_password

def seed():
    db = SessionLocal()
    try:
        # 1. Admin
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@smartuniversity.edu",
                hashed_password=hash_password("Admin@1234"),
                role=UserRole.admin,
                is_active=True,
                is_verified=True
            )
            db.add(admin)
        else:
            admin.hashed_password = hash_password("Admin@1234")
            admin.is_active = True
            admin.is_verified = True
        
        # 2. Department & Course
        dept = db.query(Department).first()
        if not dept:
            dept = Department(name="Computer Applications", code="MCA")
            db.add(dept)
            db.flush()
        
        course = db.query(Course).first()
        if not course:
            course = Course(
                department_id=dept.id,
                name="Master of Computer Applications",
                code="MCA-2026",
                duration_semesters=4,
                total_seats=60,
                min_class_12_pct=50.0,
                min_core_subject_score=50.0,
                min_attendance_pct=75.0
            )
            db.add(course)
            db.flush()

        # 3. Faculty user & profile
        fac_user = db.query(User).filter(User.email == "rajesh.sharma@faculty.edu").first()
        if not fac_user:
            fac_user = User(
                username="rajesh_sharma",
                email="rajesh.sharma@faculty.edu",
                hashed_password=hash_password("Faculty@123"),
                role=UserRole.faculty,
                is_active=True,
                is_verified=True
            )
            db.add(fac_user)
            db.flush()
        else:
            fac_user.hashed_password = hash_password("Faculty@123")
            fac_user.role = UserRole.faculty
            fac_user.is_active = True
            fac_user.is_verified = True

        fac_prof = db.query(Faculty).filter(Faculty.user_id == fac_user.id).first()
        if not fac_prof:
            fac_prof = Faculty(
                user_id=fac_user.id,
                department_id=dept.id,
                employee_id="FAC-MCA-001",
                designation="Associate Professor",
                phone="9876543210"
            )
            db.add(fac_prof)

        # 4. Student user & profile
        stud_user = db.query(User).filter(User.email == "arjun.patel@student.edu").first()
        if not stud_user:
            stud_user = User(
                username="arjun_patel",
                email="arjun.patel@student.edu",
                hashed_password=hash_password("Student@123"),
                role=UserRole.student,
                is_active=True,
                is_verified=True
            )
            db.add(stud_user)
            db.flush()
        else:
            stud_user.hashed_password = hash_password("Student@123")
            stud_user.role = UserRole.student
            stud_user.is_active = True
            stud_user.is_verified = True

        stud_prof = db.query(Student).filter(Student.user_id == stud_user.id).first()
        if not stud_prof:
            stud_prof = Student(
                user_id=stud_user.id,
                enrollment_no="SU2026-0010",
                full_name="Arjun Patel",
                department_id=dept.id,
                course_id=course.id,
                semester=1,
                phone="9123456780",
                admission_year=2026,
                is_admitted=1
            )
            db.add(stud_prof)
        else:
            stud_prof.enrollment_no = "SU2026-0010"
            stud_prof.full_name = "Arjun Patel"
            stud_prof.course_id = course.id
            stud_prof.is_admitted = 1

        db.commit()
        print("✓ All test portal users successfully provisioned & verified.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding users: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
