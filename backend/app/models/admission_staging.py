"""
models/admission_staging.py — Admission Staging ORM model.
"""
import enum
from sqlalchemy import Column, Integer, String, Float, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class CandidateCategory(str, enum.Enum):
    GEN = "GEN"
    OBC = "OBC"
    SC = "SC"
    ST = "ST"
    EWS = "EWS"

class AdmissionStatus(str, enum.Enum):
    PENDING = "PENDING"
    ELIGIBLE_FOR_ADMISSION = "ELIGIBLE_FOR_ADMISSION"
    ADMISSION_CONFIRMED = "ADMISSION_CONFIRMED"
    ADMISSION_CANCELLED = "ADMISSION_CANCELLED"
    WAITLISTED = "WAITLISTED"
    REJECTED_INELIGIBLE = "REJECTED_INELIGIBLE"

class AllocatedSeatType(str, enum.Enum):
    OPEN_MERIT = "OPEN_MERIT"
    RESERVED_QUOTA = "RESERVED_QUOTA"
    NONE = "NONE"


class AdmissionStaging(Base):
    __tablename__ = "admission_staging"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, index=True, nullable=False)
    student_name = Column(String(150), nullable=False)
    
    applied_course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    
    candidate_category = Column(Enum(CandidateCategory), default=CandidateCategory.GEN, nullable=False)
    class_12_pct = Column(Float, nullable=False)
    entrance_exam_score = Column(Float, nullable=False)
    core_subject_score = Column(Float, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    
    # Processed Results
    final_admission_status = Column(Enum(AdmissionStatus), default=AdmissionStatus.PENDING, nullable=False)
    allocated_seat_type = Column(Enum(AllocatedSeatType), default=AllocatedSeatType.NONE, nullable=False)
    waitlist_rank = Column(Integer, nullable=True)
    reason_code_logs = Column(String(500), nullable=True)

    # Relationships
    course = relationship("Course", back_populates="staging_records")

    def __repr__(self):
        return f"<AdmissionStaging student_id={self.student_id!r} status={self.final_admission_status}>"
