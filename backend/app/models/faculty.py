"""
models/faculty.py — Faculty profile ORM model.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    employee_id = Column(String(30), unique=True, nullable=True)  # e.g. FAC-001
    designation = Column(String(100), nullable=True)   # e.g. "Assistant Professor"
    phone = Column(String(15), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    department = relationship("Department", back_populates="faculty")


    def __repr__(self):
        return f"<Faculty id={self.id} employee_id={self.employee_id!r}>"
