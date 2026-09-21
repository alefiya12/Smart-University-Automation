"""
models/attendance.py — Subject-Wise Attendance ORM models.
"""
import enum
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Enum, Float, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class DailyAttendanceStatus(str, enum.Enum):
    Present = "Present"
    Absent = "Absent"


class CourseSubject(Base):
    __tablename__ = "course_subjects"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    subject_name = Column(String(150), nullable=False)
    semester = Column(Integer, default=1, nullable=False)
    credits = Column(Float, default=4.0, nullable=False)
    total_lectures_conducted = Column(Integer, default=0, nullable=False)

    course = relationship("Course", back_populates="course_subjects")
    summaries = relationship("StudentSubjectSummary", back_populates="subject", cascade="all, delete-orphan")
    daily_logs = relationship("DailyAttendanceLog", back_populates="subject", cascade="all, delete-orphan")
    marks_records = relationship("StudentMarksRecord", back_populates="subject", cascade="all, delete-orphan")


class StudentSubjectSummary(Base):
    __tablename__ = "student_subject_summaries"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("course_subjects.id", ondelete="CASCADE"), nullable=False)
    lectures_attended = Column(Integer, default=0, nullable=False)
    cumulative_percentage = Column(Float, default=0.0, nullable=False)
    attendance_warning_flag = Column(Boolean, default=False, nullable=False)
    dashboard_alert_message = Column(String(500), nullable=True)

    student = relationship("Student", back_populates="subject_summaries")
    subject = relationship("CourseSubject", back_populates="summaries")


class DailyAttendanceLog(Base):
    __tablename__ = "daily_attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("course_subjects.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    status = Column(Enum(DailyAttendanceStatus), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="daily_attendance_logs")
    subject = relationship("CourseSubject", back_populates="daily_logs")
