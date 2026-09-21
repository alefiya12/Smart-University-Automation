import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.database import engine, Base, SessionLocal
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.student import Student
from app.models.department import Department
import bcrypt

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if not db.query(User).filter(User.username == "admin").first():
        hashed = bcrypt.hashpw("admin".encode('utf-8'), bcrypt.gensalt())
        admin = User(username="admin", email="admin@test.com", hashed_password=hashed.decode('utf-8'), role=UserRole.admin)
        db.add(admin)
    
    dept = db.query(Department).first()
    if not dept:
        dept = Department(name="Computer Science", code="CS")
        db.add(dept)
        db.commit()
        db.refresh(dept)
        
    course = db.query(Course).first()
    if not course:
        course = Course(name="Master of Computer Applications", code="MCA", department_id=dept.id, min_attendance_pct=75.0)
        db.add(course)
        db.commit()
        db.refresh(course)
        
    if not db.query(Student).filter(Student.enrollment_no == "SU2026-0001").first():
        s1_user = User(username="student1", email="s1@test.com", hashed_password="dummy", role=UserRole.student)
        db.add(s1_user)
        db.commit()
        db.refresh(s1_user)
        s1 = Student(user_id=s1_user.id, enrollment_no="SU2026-0001", full_name="Student One", course_id=course.id)
        db.add(s1)
        
    if not db.query(Student).filter(Student.enrollment_no == "SU2026-0002").first():
        s2_user = User(username="student2", email="s2@test.com", hashed_password="dummy", role=UserRole.student)
        db.add(s2_user)
        db.commit()
        db.refresh(s2_user)
        s2 = Student(user_id=s2_user.id, enrollment_no="SU2026-0002", full_name="Student Two", course_id=course.id)
        db.add(s2)

    db.commit()
    print("Database seeded successfully.")

if __name__ == "__main__":
    seed()
