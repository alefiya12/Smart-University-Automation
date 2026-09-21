"""
models/result.py — Examination Result ORM model.
Includes strict dual-threshold grading rules and tracking metrics.
Grade Scale (per blueprint):
  90-100 → O (Outstanding) = 10 points
  80-89  → A+ = 9 points
  70-79  → A  = 8 points
  60-69  → B+ = 7 points
  50-59  → B  = 6 points
  40-49  → P  = 5 points
  <40 or failed component → F  = 0 points
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Enum, Text, DECIMAL
from sqlalchemy.orm import relationship
from app.database import Base


class ResultStatus(str, enum.Enum):
    pending  = "pending"
    approved = "approved"
    published = "published"
    rejected = "rejected"


class StudentMarksRecord(Base):
    __tablename__ = "student_marks_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("course_subjects.id", ondelete="CASCADE"), nullable=False)
    semester_number = Column(Integer, nullable=False)
    
    internal_score = Column(DECIMAL(5, 2), nullable=False)
    external_score = Column(DECIMAL(5, 2), nullable=False)
    total_marks_obtained = Column(DECIMAL(5, 2), nullable=False)
    
    grade_letter = Column(String(5), nullable=False)
    grade_points = Column(Integer, nullable=False)
    pass_status = Column(Boolean, nullable=False)
    
    academic_year = Column(String(9), nullable=True)
    sgpa = Column(Float, nullable=True)
    cgpa = Column(Float, nullable=True)
    
    needs_review = Column(Boolean, default=False)
    status = Column(Enum(ResultStatus), default=ResultStatus.pending, nullable=False)
    review_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="marks_records")
    subject = relationship("CourseSubject", back_populates="marks_records")

    def __repr__(self):
        return f"<StudentMarksRecord student_id={self.student_id} subject_id={self.subject_id} pass={self.pass_status}>"
