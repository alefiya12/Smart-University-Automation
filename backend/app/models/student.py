"""
models/student.py — Student profile ORM model.
Enrollment number format: SU{year}-{0001} (e.g. SU2026-0001)
Generated via utils/id_generator.py using the id_counters table.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    enrollment_no = Column(String(20), unique=True, index=True, nullable=False)  # SU2026-0001
    full_name = Column(String(150), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    semester = Column(Integer, default=1, nullable=False)
    phone = Column(String(15), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    address = Column(String(500), nullable=True)
    guardian_name = Column(String(150), nullable=True)
    guardian_phone = Column(String(15), nullable=True)
    admission_year = Column(Integer, nullable=True)
    is_admitted = Column(Integer, default=0, nullable=False)  # 0=pending, 1=admitted, 2=rejected
    temp_password = Column(String(256), nullable=True)  # cleared after first login
    academic_standing = Column(String(50), default='Good Standing', nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    department = relationship("Department", back_populates="students")
    course = relationship("Course", back_populates="students")
    subject_summaries = relationship("StudentSubjectSummary", back_populates="student", cascade="all, delete-orphan")
    daily_attendance_logs = relationship("DailyAttendanceLog", back_populates="student", cascade="all, delete-orphan")
    marks_records = relationship("StudentMarksRecord", back_populates="student", cascade="all, delete-orphan")
    fees = relationship("Fee", back_populates="student", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student id={self.id} enrollment={self.enrollment_no!r}>"
