"""
AttendanceKeywords.py — Robot Framework keyword library for Subject-Wise Attendance Automation.
Supports matrix format (student_id, date, Subject1, Subject2, ...).
"""
import os
import sys
import logging
from datetime import datetime, date
from typing import List, Optional

_BACKEND_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
if _BACKEND_PATH not in sys.path:
    sys.path.insert(0, _BACKEND_PATH)

from robot.api.deco import keyword
from robot.api import logger as robot_logger

logger = logging.getLogger(__name__)


class AttendanceKeywords:
    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self):
        self._records: List[dict] = []
        self._results: List[dict] = []
        self._processed_students = set()

    @keyword("Load Attendance Excel")
    def load_attendance_excel(self, path: str) -> list:
        """
        Load attendance Excel in matrix format:
        Columns: student_id / enrollment_no, date, Subject1, Subject2...
        """
        import pandas as pd
        robot_logger.info(f"Loading attendance Excel: {path}")
        df = pd.read_excel(path)
        
        # Standardize student_id and date column names
        new_cols = []
        for c in df.columns:
            c_str = str(c).strip()
            c_lower = c_str.lower()
            if c_lower in ['student_id', 'student id', 'enrollment_no', 'enrollment no']:
                new_cols.append('student_id')
            elif c_lower == 'date':
                new_cols.append('date')
            else:
                new_cols.append(c_str)
        df.columns = new_cols

        self._records = df.where(df.notna(), None).to_dict(orient='records')
        robot_logger.info(f"Loaded {len(self._records)} attendance row records")
        return self._records

    @keyword("Process Single Attendance Record")
    def process_single_attendance_record(self, record: dict) -> None:
        """
        Record attendance for all subjects in the row for a student on a specific date.
        """
        from app.database import SessionLocal
        from app.models.student import Student
        from app.models.attendance import (
            CourseSubject, DailyAttendanceLog, DailyAttendanceStatus, StudentSubjectSummary
        )

        db = SessionLocal()
        try:
            enrollment = str(record.get('student_id', '') or record.get('enrollment_no', '')).strip()
            student = db.query(Student).filter(Student.enrollment_no == enrollment).first()
            if not student:
                robot_logger.warn(f"Student not found: {enrollment}")
                self._results.append({'success': False, 'enrollment_no': enrollment, 'error': 'not_found'})
                return

            raw_date = record.get('date')
            if isinstance(raw_date, str):
                try:
                    att_date = date.fromisoformat(raw_date.strip())
                except ValueError:
                    att_date = datetime.strptime(raw_date.strip(), '%Y-%m-%d').date()
            elif hasattr(raw_date, 'date'):
                att_date = raw_date.date()
            else:
                att_date = date.today()

            self._processed_students.add(student.id)
            logged_subjects = []

            for k, v in record.items():
                if k in ['student_id', 'enrollment_no', 'date']:
                    continue
                if v is None:
                    continue

                subject_name = str(k).strip()
                subject = db.query(CourseSubject).filter(
                    CourseSubject.course_id == student.course_id,
                    CourseSubject.subject_name.ilike(subject_name)
                ).first()

                if not subject:
                    subject = CourseSubject(
                        course_id=student.course_id,
                        subject_name=subject_name.title(),
                        semester=student.semester,
                        total_lectures_conducted=0
                    )
                    db.add(subject)
                    db.flush()

                status_val = int(v) if str(v).isdigit() else (1 if str(v).lower() in ['p', 'present', 'true'] else 0)
                status_enum = DailyAttendanceStatus.Present if status_val == 1 else DailyAttendanceStatus.Absent

                existing_log = db.query(DailyAttendanceLog).filter(
                    DailyAttendanceLog.student_id == student.id,
                    DailyAttendanceLog.subject_id == subject.id,
                    DailyAttendanceLog.date == att_date
                ).first()

                if existing_log:
                    existing_log.status = status_enum
                else:
                    new_log = DailyAttendanceLog(
                        student_id=student.id,
                        subject_id=subject.id,
                        date=att_date,
                        status=status_enum
                    )
                    db.add(new_log)
                    subject.total_lectures_conducted += 1

                summary = db.query(StudentSubjectSummary).filter(
                    StudentSubjectSummary.student_id == student.id,
                    StudentSubjectSummary.subject_id == subject.id
                ).first()

                if not summary:
                    summary = StudentSubjectSummary(
                        student_id=student.id,
                        subject_id=subject.id,
                        lectures_attended=0,
                        cumulative_percentage=0.0
                    )
                    db.add(summary)
                    db.flush()

                # Recompute total attended
                total_attended = db.query(DailyAttendanceLog).filter(
                    DailyAttendanceLog.student_id == student.id,
                    DailyAttendanceLog.subject_id == subject.id,
                    DailyAttendanceLog.status == DailyAttendanceStatus.Present
                ).count()
                summary.lectures_attended = total_attended

                total_conducted = max(subject.total_lectures_conducted, 1)
                summary.cumulative_percentage = round((total_attended / total_conducted) * 100.0, 2)

                threshold = student.course.min_attendance_pct if student.course and student.course.min_attendance_pct else 75.0
                if summary.cumulative_percentage < threshold:
                    summary.attendance_warning_flag = True
                    summary.dashboard_alert_message = (
                        f"Warning: Your attendance in {subject.subject_name} is "
                        f"{summary.cumulative_percentage:.1f}%, below the required {threshold}%."
                    )
                else:
                    summary.attendance_warning_flag = False
                    summary.dashboard_alert_message = None

                logged_subjects.append(f"{subject.subject_name}: {status_enum.value} ({summary.cumulative_percentage}%)")

            db.commit()
            robot_logger.info(f"✓ Recorded: {enrollment} | Date: {att_date} | " + ", ".join(logged_subjects))
            self._results.append({'success': True, 'enrollment_no': enrollment, 'date': str(att_date)})

        except Exception as exc:
            robot_logger.error(f"✗ Failed: {record.get('student_id')} — {exc}")
            self._results.append({'success': False, 'enrollment_no': record.get('student_id'), 'error': str(exc)})
            db.rollback()
        finally:
            db.close()

    @keyword("Check And Send Low Attendance Warnings")
    def check_and_send_low_attendance_warnings(self) -> None:
        """Evaluate attendance percentages across processed students and queue warning alerts/emails."""
        from app.database import SessionLocal
        from app.models.student import Student
        from app.models.user import User
        from app.models.attendance import StudentSubjectSummary
        from app.models.notification import Notification, NotificationType, NotificationCategory, NotificationStatus
        from app.services.email_service import send_low_attendance_warning

        db = SessionLocal()
        try:
            summaries = db.query(StudentSubjectSummary).filter(
                StudentSubjectSummary.student_id.in_(self._processed_students),
                StudentSubjectSummary.attendance_warning_flag == True
            ).all()

            for summ in summaries:
                student = summ.student
                subject = summ.subject
                user = db.query(User).filter(User.id == student.user_id).first()
                pct = summ.cumulative_percentage
                threshold = student.course.min_attendance_pct if student.course and student.course.min_attendance_pct else 75.0

                robot_logger.warn(
                    f"⚠ Low attendance warning: {student.enrollment_no} | {subject.subject_name} = {pct:.1f}% (Min {threshold}%)"
                )

                # Add Notification
                notif = Notification(
                    student_id=student.id,
                    title=f"Low Attendance: {subject.subject_name}",
                    message=summ.dashboard_alert_message or f"Attendance {pct:.1f}% is below required {threshold}%.",
                    notification_type=NotificationType.in_app,
                    category=NotificationCategory.attendance_warning,
                    status=NotificationStatus.sent,
                )
                db.add(notif)

                if user and user.email:
                    try:
                        send_low_attendance_warning(
                            to=user.email,
                            student_name=student.full_name or user.username,
                            subject_name=subject.subject_name,
                            percentage=pct,
                            threshold=threshold
                        )
                    except Exception as email_err:
                        robot_logger.warn(f"Email failed for {user.email}: {email_err}")

            db.commit()
        except Exception as exc:
            robot_logger.error(f"Warning check failed: {exc}")
            db.rollback()
        finally:
            db.close()

    @keyword("Log Run Summary")
    def log_run_summary(self) -> None:
        succeeded = sum(1 for r in self._results if r.get('success'))
        failed = len(self._results) - succeeded
        robot_logger.info("=" * 50)
        robot_logger.info("ATTENDANCE BOT SUMMARY")
        robot_logger.info(f"  Total Rows:     {len(self._results)}")
        robot_logger.info(f"  Succeeded:      {succeeded}")
        robot_logger.info(f"  Failed:         {failed}")
        robot_logger.info("=" * 50)
