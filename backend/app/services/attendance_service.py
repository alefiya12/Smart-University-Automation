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
                    
                if isinstance(v, str):
                    v_clean = v.strip().lower()
                    status_val = 1 if v_clean in ["1", "present", "p", "true", "yes"] else 0
                else:
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
                
                # Update StudentSubjectSummary safely using session cache
                summary_key = (student.id, subject.id)
                if not hasattr(db, '_summary_cache'):
                    db._summary_cache = {}
                summary = db._summary_cache.get(summary_key)
                if not summary:
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
                db._summary_cache[summary_key] = summary
                
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
                
                if pct <= 60.0:
                    summ.attendance_warning_flag = True
                    summ.dashboard_alert_message = f"CRITICAL ALERT: Your attendance in {summ.subject.subject_name} is {pct:.1f}%, critically below the 60.0% debarment threshold."
                elif pct < threshold:
                    summ.attendance_warning_flag = True
                    summ.dashboard_alert_message = f"Warning: Your attendance in {summ.subject.subject_name} is {pct:.1f}%, which is below the required {threshold}%."
                else:
                    summ.attendance_warning_flag = False
                    summ.dashboard_alert_message = None

                if summ.attendance_warning_flag:
                    # Create notification if no unread warning exists
                    existing_notif = db.query(Notification).filter(
                        Notification.student_id == summ.student_id,
                        Notification.title == f"Low Attendance: {summ.subject.subject_name}",
                        Notification.category == NotificationCategory.attendance_warning,
                        Notification.is_read == False
                    ).first()

                    if not existing_notif:
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
    run_log = db.merge(run_log)
    db.commit()

    return {'bot_run_id': run_log.id, 'total': len(records), 'succeeded': succeeded, 'failed': failed, 'errors': errors}

def get_student_subject_summaries(db: Session, student_id: int):
    """Fetch accurate, strictly deduplicated dashboard attendance summaries for a student."""
    student = db.query(Student).filter(Student.id == student_id).first()
    threshold = student.course.min_attendance_pct if (student and student.course and student.course.min_attendance_pct) else 75.0

    summaries = db.query(StudentSubjectSummary).filter(StudentSubjectSummary.student_id == student_id).all()
    res = []
    seen_subject_ids = set()
    seen_subject_names = set()

    for s in summaries:
        if not s.subject:
            continue
        sub_name = s.subject.subject_name.strip()
        norm_key = sub_name.lower()
        if norm_key in seen_subject_names:
            continue
        seen_subject_names.add(norm_key)
        seen_subject_ids.add(s.subject_id)

        # Count actual attendance logs for this student and subject
        actual_attended = db.query(DailyAttendanceLog).filter(
            DailyAttendanceLog.student_id == student_id,
            DailyAttendanceLog.subject_id == s.subject_id,
            DailyAttendanceLog.status == DailyAttendanceStatus.Present
        ).count()

        actual_total_logs = db.query(DailyAttendanceLog).filter(
            DailyAttendanceLog.student_id == student_id,
            DailyAttendanceLog.subject_id == s.subject_id
        ).count()

        # Distinct dates when this subject was taught
        distinct_dates = db.query(func.count(func.distinct(DailyAttendanceLog.date))).filter(
            DailyAttendanceLog.subject_id == s.subject_id
        ).scalar() or 0

        # Best estimate of total conducted
        total_conducted = max(
            actual_total_logs,
            distinct_dates,
            s.subject.total_lectures_conducted if s.subject else 0,
            s.lectures_attended if s.lectures_attended else 0,
            1 if actual_attended > 0 else 0
        )

        attended = actual_attended if actual_total_logs > 0 else (s.lectures_attended or 0)
        pct = round((attended / total_conducted * 100.0), 1) if total_conducted > 0 else 0.0

        is_warning = pct < threshold if total_conducted > 0 else False
        alert_msg = (
            f"Warning: Your attendance in {sub_name} is {pct:.1f}%, below the required {threshold}% threshold."
            if is_warning else None
        )

        res.append({
            "id": s.id,
            "subject_id": s.subject_id,
            "subject_name": sub_name,
            "subject": sub_name,
            "semester": s.subject.semester or (student.semester if student else 1),
            "total_conducted": total_conducted,
            "total_classes": total_conducted,
            "lectures_attended": attended,
            "present": attended,
            "absent": max(0, total_conducted - attended),
            "percentage": pct,
            "cumulative_percentage": pct,
            "warning_flag": is_warning,
            "warning": is_warning,
            "dashboard_alert_message": alert_msg,
            "alert": alert_msg,
        })

    # If student has daily logs for subjects not yet in StudentSubjectSummary, include them
    unsummarized_logs = db.query(DailyAttendanceLog.subject_id).filter(
        DailyAttendanceLog.student_id == student_id
    ).distinct().all()

    for (sub_id,) in unsummarized_logs:
        if sub_id in seen_subject_ids:
            continue
        sub = db.query(CourseSubject).filter(CourseSubject.id == sub_id).first()
        if not sub:
            continue
        sub_name = sub.subject_name.strip()
        norm_key = sub_name.lower()
        if norm_key in seen_subject_names:
            continue
        seen_subject_names.add(norm_key)
        seen_subject_ids.add(sub.id)

        actual_attended = db.query(DailyAttendanceLog).filter(
            DailyAttendanceLog.student_id == student_id,
            DailyAttendanceLog.subject_id == sub_id,
            DailyAttendanceLog.status == DailyAttendanceStatus.Present
        ).count()

        actual_total = db.query(DailyAttendanceLog).filter(
            DailyAttendanceLog.student_id == student_id,
            DailyAttendanceLog.subject_id == sub_id
        ).count()

        distinct_dates = db.query(func.count(func.distinct(DailyAttendanceLog.date))).filter(
            DailyAttendanceLog.subject_id == sub_id
        ).scalar() or 0

        total_conducted = max(actual_total, distinct_dates, sub.total_lectures_conducted, 1)
        pct = round((actual_attended / total_conducted * 100.0), 1) if total_conducted > 0 else 0.0
        is_warning = pct < threshold if total_conducted > 0 else False

        res.append({
            "id": None,
            "subject_id": sub.id,
            "subject_name": sub_name,
            "subject": sub_name,
            "semester": sub.semester or (student.semester if student else 1),
            "total_conducted": total_conducted,
            "total_classes": total_conducted,
            "lectures_attended": actual_attended,
            "present": actual_attended,
            "absent": max(0, total_conducted - actual_attended),
            "percentage": pct,
            "cumulative_percentage": pct,
            "warning_flag": is_warning,
            "warning": is_warning,
            "dashboard_alert_message": f"Warning: Your attendance in {sub_name} is {pct:.1f}%, below {threshold}%." if is_warning else None,
            "alert": f"Warning: Your attendance in {sub_name} is {pct:.1f}%, below {threshold}%." if is_warning else None,
        })

    return res

def get_student_daily_logs(db: Session, student_id: int):
    """Return chronological daily attendance logs with standardized date and badge fields."""
    logs = db.query(DailyAttendanceLog).filter(
        DailyAttendanceLog.student_id == student_id
    ).order_by(DailyAttendanceLog.date.desc(), DailyAttendanceLog.id.desc()).all()
    
    res = []
    for l in logs:
        sub_name = l.subject.subject_name.strip() if l.subject else "Subject"
        sem = l.subject.semester if (l.subject and l.subject.semester) else 1
        
        # Standardize readable date formatting
        dt_raw = l.date
        date_iso = str(dt_raw)
        formatted_date = date_iso
        day_of_week = ""
        try:
            if isinstance(dt_raw, str):
                p_date = datetime.strptime(dt_raw, "%Y-%m-%d").date()
            else:
                p_date = dt_raw
            formatted_date = p_date.strftime("%d %b %Y")  # e.g., '01 Sep 2026'
            day_of_week = p_date.strftime("%A")          # e.g., 'Tuesday'
        except Exception:
            pass

        status_str = l.status.value if hasattr(l.status, 'value') else str(l.status)
        res.append({
            "id": l.id,
            "subject": sub_name,
            "subject_name": sub_name,
            "semester": sem,
            "date": date_iso,
            "formatted_date": formatted_date,
            "day_of_week": day_of_week,
            "status": status_str,
            "session_type": "Regular Lecture",
        })
    return res
