"""
models/__init__.py — Import all ORM models so SQLAlchemy registers them
with the metadata before create_all() is called.
"""
from app.models.user import User, UserRole
from app.models.id_counter import IdCounter
from app.models.department import Department
from app.models.course import Course
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.attendance import CourseSubject, StudentSubjectSummary, DailyAttendanceLog, DailyAttendanceStatus
from app.models.result import StudentMarksRecord, ResultStatus
from app.models.fee import Fee, FeeType, FeeStatus
from app.models.notification import Notification, NotificationType, NotificationStatus, NotificationCategory
from app.models.bot_run_log import BotRunLog, BotStatus
from app.models.admission_staging import AdmissionStaging

__all__ = [
    "User", "UserRole",
    "IdCounter",
    "Department",
    "Course",
    "Student",
    "Faculty",
    "CourseSubject", "StudentSubjectSummary", "DailyAttendanceLog", "DailyAttendanceStatus",
    "Result", "Grade", "ResultStatus",
    "Fee", "FeeType", "FeeStatus",
    "Notification", "NotificationType", "NotificationStatus", "NotificationCategory",
    "BotRunLog", "BotStatus",
    "AdmissionStaging",
]
