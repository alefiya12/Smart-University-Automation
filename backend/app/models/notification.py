"""
models/notification.py — Notification ORM model.
Notification matrix (from blueprint):
  Admission Approved  → Email
  Password Created    → Email
  Low Attendance      → Email + SMS + In-App
  Result Published    → Email + SMS + In-App
  Announcements       → In-App only
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class NotificationType(str, enum.Enum):
    email = "email"
    sms = "sms"
    in_app = "in_app"


class NotificationStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"
    read = "read"  # for in_app only


class NotificationCategory(str, enum.Enum):
    admission = "admission"
    attendance_warning = "attendance_warning"
    result_published = "result_published"
    fee_reminder = "fee_reminder"
    announcement = "announcement"
    password_created = "password_created"
    general = "general"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=True)  # null = broadcast
    title = Column(String(250), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    category = Column(Enum(NotificationCategory), default=NotificationCategory.general, nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.pending, nullable=False)
    is_read = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)  # if status==failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    sent_at = Column(DateTime, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="notifications")

    def __repr__(self):
        return f"<Notification id={self.id} type={self.notification_type} status={self.status}>"
