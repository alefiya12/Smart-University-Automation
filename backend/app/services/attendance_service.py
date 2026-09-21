"""
services/attendance_service.py — Subject-Wise Attendance logic.
"""
import logging
from datetime import datetime, date
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.attendance import CourseSubject, StudentSubjectSummary, DailyAttendanceLog, DailyAttendanceStatus
from app.models.student import Student
from app.models.course import Course
from app.models.user import User
from app.models.bot_run_log import BotRunLog, BotStatus
from app.models.notification import Notification, NotificationType, NotificationStatus, NotificationCategory
from app.services.email_service import send_low_attendance_warning

logger = logging.getLogger(__name__)

def process_bulk_attendance_excel(
    db: Session,
    records: List[dict],
    course_id: int,
    triggered_by: str = "api",
) -> dict:
    """
    Process Excel records for Subject-Wise attendance.
    Records format: [{'student_id': 'SU2026-0001', 'date': '2026-09-01', 'Subject1': 1, 'Subject2': 0, ...}]
    """
    run_log = BotRunLog(
        bot_name="attendance_bot_advanced",
        triggered_by=triggered_by,
        status=BotStatus.running,
        records_total=len(records),
        started_at=datetime.utcnow(),
    )
    db.add(run_log)
    db.commit()
    db.refresh(run_log)

    start = datetime.utcnow()
    errors = []
    succeeded = 0
    failed = 0

    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise ValueError(f"Course ID {course_id} not found.")

        threshold = course.min_attendance_pct if course.min_attendance_pct else 75.0

        # Pass 1: Extract all subjects from headers
        all_headers = set()
        for r in records:
            for k in r.keys():
                k_lower = k.lower()
                if k_lower not in ['student_id', 'date']:
                    # Use original case for subject names
                    all_headers.add(k)

        # Check existing subjects for this course
        existing_subjects = db.query(CourseSubject).filter(CourseSubject.course_id == course_id).all()
        existing_subject_map = {s.subject_name: s for s in existing_subjects}

        # Strict check: ALL subjects in Excel MUST already exist in the database
        for h in all_headers:
            if h not in existing_subject_map:
                raise ValueError(f"Ingestion Aborted: Subject '{h}' does not belong to the selected Course profile. Please add it in Course Settings first.")

        # Pass 2: Verify all students exist
        student_ids_in_excel = {str(r.get('student_id')) for r in records if r.get('student_id')}
        students_in_db = db.query(Student).filter(Student.enrollment_no.in_(student_ids_in_excel)).all()
        student_map = {s.enrollment_no: s for s in students_in_db}
        
        for sid in student_ids_in_excel:
            if sid not in student_map:
                raise ValueError(f"Ingestion Aborted: Student ID '{sid}' is not registered in the system.")

        # Pass 3: Ingestion
        # We need to track which subjects had a lecture on which date to increment total_lectures_conducted exactly once per date.
        # date -> set of subject_names
        date_subject_lectures = {}
        
        for rec in records:
            enrollment_no = str(rec.get('student_id')) if rec.get('student_id') else None
            raw_date = rec.get('date')
            
            if not enrollment_no or not raw_date:
                continue
                
            student = student_map[enrollment_no]
            
            # parse date
            if isinstance(raw_date, str):
                try:
                    att_date = date.fromisoformat(raw_date[:10])
                except Exception:
                    # fallback
                    att_date = date.today()
            elif hasattr(raw_date, 'date'):
                att_date = raw_date.date()
            else:
                att_date = raw_date
                
            for k, v in rec.items():
                k_lower = k.lower()
                if k_lower in ['student_id', 'date']:
                    continue
                    
                subject = existing_subject_map[k]
                
                # Semester validation check
                if student.semester != subject.semester:
                    logger.warning(f"Semester mismatch skipped for {enrollment_no} (Sem {student.semester}) on subject {k} (Sem {subject.semester})")
                    continue
                    
                status_val = int(v) if v is not None else 0
                status_enum = DailyAttendanceStatus.Present if status_val == 1 else DailyAttendanceStatus.Absent
                
                # Check for duplicate
                existing_log = db.query(DailyAttendanceLog).filter(
                    DailyAttendanceLog.student_id == student.id,
                    DailyAttendanceLog.subject_id == subject.id,
                    DailyAttendanceLog.date == att_date
                ).first()
                
                if existing_log:
                    # skip duplicate
                    logger.warning(f"Duplicate date entry skipped for {enrollment_no}, subject {k}, date {att_date}")
                    continue
                    
                # Not a duplicate, insert log
                new_log = DailyAttendanceLog(
                    student_id=student.id,
                    subject_id=subject.id,
                    date=att_date,
                    status=status_enum
                )
                db.add(new_log)
                
                # Track for incrementing total_lectures_conducted
                if att_date not in date_subject_lectures:
                    date_subject_lectures[att_date] = set()
                date_subject_lectures[att_date].add(subject.id)
                
                # Update StudentSubjectSummary
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
                
                if status_enum == DailyAttendanceStatus.Present:
                    summary.lectures_attended += 1
                    
                # We will recalculate percentages after we increment the total_lectures_conducted
                
            succeeded += 1

        db.flush()

        # Increment total lectures conducted for subjects
        for d, sub_ids in date_subject_lectures.items():
            for sid in sub_ids:
                sub_obj = db.query(CourseSubject).filter(CourseSubject.id == sid).first()
                if sub_obj:
                    sub_obj.total_lectures_conducted += 1
        
        db.flush()

        # Recalculate percentages & alerts
        # Get all updated summaries
        updated_subjects = set()
        for sub_ids in date_subject_lectures.values():
            updated_subjects.update(sub_ids)
            
        if updated_subjects and students_in_db:
            student_ids = [s.id for s in students_in_db]
            summaries_to_update = db.query(StudentSubjectSummary).filter(
                StudentSubjectSummary.student_id.in_(student_ids),
                StudentSubjectSummary.subject_id.in_(updated_subjects)
            ).all()
            
            for summ in summaries_to_update:
                total_conducted = summ.subject.total_lectures_conducted
                if total_conducted > 0:
                    pct = (summ.lectures_attended / total_conducted) * 100.0
                else:
                    pct = 0.0
                    
                summ.cumulative_percentage = round(pct, 2)
                
                if pct < threshold:
                    summ.attendance_warning_flag = True
                    summ.dashboard_alert_message = f"Warning: Your attendance in {summ.subject.subject_name} is {pct:.1f}%, which is below the required {threshold}%."
                    
                    # Create notification
                    notif = Notification(
                        student_id=summ.student_id,
                        title=f"Low Attendance: {summ.subject.subject_name}",
                        message=summ.dashboard_alert_message,
                        notification_type=NotificationType.in_app,
                        category=NotificationCategory.attendance_warning,
                        status=NotificationStatus.sent,
                    )
                    db.add(notif)
                    
                    # Also optionally send email
                    user = db.query(User).filter(User.id == summ.student.user_id).first()
                    if user:
                        try:
                            send_low_attendance_warning(
                                to=user.email,
                                student_name=user.username,
                                subject_name=summ.subject.subject_name,
                                percentage=pct,
                                threshold=threshold,
                            )
                        except Exception as e:
                            logger.error(f"Email failed: {e}")
                else:
                    summ.attendance_warning_flag = False
                    summ.dashboard_alert_message = None

        db.commit()

    except Exception as exc:
        db.rollback()
        failed = len(records)
        succeeded = 0
        error_msg = str(exc)
        errors.append(error_msg)
        logger.error(f"Attendance Bulk Upload Failed: {error_msg}")

    end = datetime.utcnow()
    run_log.status = BotStatus.success if not errors else BotStatus.failed
    run_log.records_processed = succeeded
    run_log.records_failed = failed
    run_log.ended_at = end
    run_log.duration_seconds = (end - start).total_seconds()
    run_log.error_message = '\n'.join(errors) if errors else None
    
    # Save run_log safely (especially if rollback happened)
    # The run_log instance is already in this session, but rollback detached or discarded state if it wasn't committed fully,
    # though we committed it at the start. So we can just merge and commit.
    run_log = db.merge(run_log)
    db.commit()

    return {'bot_run_id': run_log.id, 'total': len(records), 'succeeded': succeeded, 'failed': failed, 'errors': errors}

def get_student_subject_summaries(db: Session, student_id: int):
    """Fetch dashboard summaries for a student."""
    summaries = db.query(StudentSubjectSummary).filter(StudentSubjectSummary.student_id == student_id).all()
    res = []
    for s in summaries:
        res.append({
            "subject": s.subject.subject_name,
            "total_classes": s.subject.total_lectures_conducted,
            "present": s.lectures_attended,
            "absent": s.subject.total_lectures_conducted - s.lectures_attended,
            "percentage": s.cumulative_percentage,
            "warning": s.attendance_warning_flag,
            "alert": s.dashboard_alert_message
        })
    return res

def get_student_daily_logs(db: Session, student_id: int):
    logs = db.query(DailyAttendanceLog).filter(DailyAttendanceLog.student_id == student_id).order_by(DailyAttendanceLog.date.desc()).all()
    res = []
    for l in logs:
        res.append({
            "id": l.id,
            "subject": l.subject.subject_name,
            "date": str(l.date),
            "status": l.status.value
        })
    return res
