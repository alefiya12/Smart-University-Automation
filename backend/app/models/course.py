"""
models/course.py — Course ORM model.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    code = Column(String(20), nullable=True)           # e.g. "MCA", "BCA"
    duration_semesters = Column(Integer, default=6)    # total semesters
    
    # --- Admission Configurations ---
    total_seats = Column(Integer, default=60)
    quota_obc = Column(Float, default=27.0)
    quota_sc = Column(Float, default=15.0)
    quota_st = Column(Float, default=7.5)
    quota_ews = Column(Float, default=10.0)
    
    min_class_12_pct = Column(Float, default=60.0)
    min_core_subject_score = Column(Float, default=50.0)
    
    min_attendance_pct = Column(Float, default=75.0)
    
    relaxation_sc_st_pct = Column(Float, default=5.0)
    relaxation_obc_ews_pct = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    department = relationship("Department", back_populates="courses")
    students = relationship("Student", back_populates="course")
    staging_records = relationship("AdmissionStaging", back_populates="course", cascade="all, delete-orphan")
    course_subjects = relationship("CourseSubject", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Course id={self.id} name={self.name!r}>"
