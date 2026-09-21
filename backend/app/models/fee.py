"""
models/fee.py — Fee record ORM model.
"""
import enum
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Date, Enum, Text
from sqlalchemy.orm import relationship
from app.database import Base


class FeeType(str, enum.Enum):
    tuition = "tuition"
    exam = "exam"
    library = "library"
    hostel = "hostel"
    other = "other"


class FeeStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    overdue = "overdue"
    waived = "waived"


class Fee(Base):
    __tablename__ = "fees"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    fee_type = Column(Enum(FeeType), default=FeeType.tuition, nullable=False)
    description = Column(String(250), nullable=True)
    amount = Column(Float, nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(Enum(FeeStatus), default=FeeStatus.pending, nullable=False)
    paid_date = Column(Date, nullable=True)
    receipt_no = Column(String(50), nullable=True, unique=True)
    semester = Column(Integer, nullable=True)
    academic_year = Column(String(9), nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="fees")

    def __repr__(self):
        return f"<Fee id={self.id} student_id={self.student_id} amount={self.amount} status={self.status}>"
