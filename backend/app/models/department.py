"""
models/department.py — Department ORM model.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, nullable=False)
    code = Column(String(10), unique=True, nullable=True)  # e.g. "CS", "MBA"
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    courses = relationship("Course", back_populates="department", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="department")
    faculty = relationship("Faculty", back_populates="department")

    def __repr__(self):
        return f"<Department id={self.id} name={self.name!r}>"
