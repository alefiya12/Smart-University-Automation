"""
services/result_service.py — Dual-Threshold Grade calculation, SGPA/CGPA, result publishing.
"""
import logging
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.result import StudentMarksRecord, ResultStatus
from app.models.student import Student
from app.models.attendance import CourseSubject
from app.models.user import User
from app.models.bot_run_log import BotRunLog, BotStatus
from app.models.notification import Notification, NotificationType, NotificationStatus, NotificationCategory
from app.services.email_service import send_result_published_email
from app.services.pdf_service import generate_marksheet

logger = logging.getLogger(__name__)

GRADE_SCALE = [
    (90.00, 'O',  10),
    (80.00, 'A+', 9),
    (70.00, 'A',  8),
    (60.00, 'B+', 7),
    (50.00, 'B',  6),
    (40.00, 'P',  5),
]

def compute_grade_dual_threshold(internal: float, external: float) -> Tuple[bool, float, str, int]:
    """
    Applies dual-threshold evaluation.
    Internal: Max 30, Min Passing 12.00
    External: Max 70, Min Passing 28.00
    Returns: (pass_status, total_marks, grade_letter, grade_points)
    """
    total = round(internal + external, 2)
    
    if internal < 12.00 or external < 28.00:
        return False, total, 'F', 0
        
    for threshold, letter, points in GRADE_SCALE:
        if total >= threshold:
            return True, total, letter, points
            
    return True, total, 'P', 5  # Fallback for exact edge cases


def compute_sgpa(results: List[StudentMarksRecord]) -> float:
    """Compute SGPA for a list of StudentMarksRecord objects."""
    total_credits = sum(r.subject.credits for r in results if r.grade_letter != 'F')
    weighted = sum(r.subject.credits * r.grade_points for r in results)
    return round(weighted / total_credits, 2) if total_credits > 0 else 0.0


def compute_cgpa(db: Session, student_id: int) -> float:
    """Compute CGPA across all published semesters."""
    published = db.query(StudentMarksRecord).filter(
        StudentMarksRecord.student_id == student_id,
        StudentMarksRecord.status == ResultStatus.published,
    ).all()
    if not published:
        return 0.0
    total_credits = sum(r.subject.credits for r in published if r.grade_letter != 'F')
    weighted = sum(r.subject.credits * r.grade_points for r in published)
    return round(weighted / total_credits, 2) if total_credits > 0 else 0.0


def publish_student_results(db: Session, student_id: int, semester: int) -> dict:
    """
    Approve + publish all non-F results for a student-semester.
    """
    sem_results = db.query(StudentMarksRecord).filter(
        StudentMarksRecord.student_id == student_id,
        StudentMarksRecord.semester_number == semester,
        StudentMarksRecord.status.in_([ResultStatus.pending, ResultStatus.approved]),
    ).all()

    blocked, published_results = [], []
    for r in sem_results:
        if r.needs_review and r.status != ResultStatus.approved:
            blocked.append(r)
        else:
            r.status = ResultStatus.published
            published_results.append(r)

    if not published_results:
        db.commit()
        return {'published': 0, 'blocked': len(blocked), 'sgpa': 0.0, 'cgpa': 0.0}

    sgpa = compute_sgpa(published_results)
    for r in published_results:
        r.sgpa = sgpa
    db.commit()

    cgpa = compute_cgpa(db, student_id)
    for r in published_results:
        r.cgpa = cgpa
    db.commit()

    # Generate marksheet PDF (legacy mapping structure adapted for PDF generator)
    student = db.query(Student).filter(Student.id == student_id).first()
    user    = db.query(User).filter(User.id == student.user_id).first() if student else None
    pdf_path = None

    if student and user:
        from app.models.department import Department
        from app.models.course import Course
        dept   = db.query(Department).filter(Department.id == student.department_id).first()
        course = db.query(Course).filter(Course.id == student.course_id).first()

        result_rows = [{
            'subject': r.subject.subject_name, 'credits': r.subject.credits,
            'marks': r.total_marks_obtained, 'max_marks': 100.0,
            'grade': r.grade_letter, 'grade_points': r.grade_points,
        } for r in published_results]

        try:
            pdf_path = generate_marksheet(
                enrollment_no=student.enrollment_no,
                student_name=user.username,
                department=dept.name if dept else "",
                course=course.name if course else "",
                semester=semester,
                academic_year=published_results[0].academic_year or str(datetime.utcnow().year),
                results=result_rows,
                sgpa=sgpa, cgpa=cgpa,
            )
        except Exception as exc:
            logger.warning("Marksheet PDF failed: %s", exc)

        # Email
        try:
            send_result_published_email(user.email, user.username, semester, sgpa, cgpa)
        except Exception as exc:
            logger.warning("Result email failed: %s", exc)

        notif = Notification(
            student_id=student_id,
            title=f"Semester {semester} Results Published",
            message=f"Your Semester {semester} results are published. SGPA: {sgpa:.2f} | CGPA: {cgpa:.2f}",
            notification_type=NotificationType.in_app,
            category=NotificationCategory.result_published,
            status=NotificationStatus.sent,
        )
        db.add(notif)
        db.commit()

    return {'published': len(published_results), 'blocked': len(blocked), 'sgpa': sgpa, 'cgpa': cgpa, 'pdf_path': pdf_path}


def process_bulk_results(db: Session, records: List[dict], triggered_by: str = "api") -> dict:
    """
    Bulk-upload marks, strictly evaluating Internal/External thresholds.
    Will rollback entire transaction if ANY row violates 30/70 limits or references invalid data.
    """
    run_log = BotRunLog(
        bot_name="results_bot_advanced", triggered_by=triggered_by,
        status=BotStatus.running, records_total=len(records),
        started_at=datetime.utcnow(),
    )
    db.add(run_log)
    db.commit()
    db.refresh(run_log)

    start = datetime.utcnow()
    
    try:
        # We wrap the core processing in a nested transaction for atomic rollback
        with db.begin_nested():
            for idx, rec in enumerate(records):
                enrollment = str(rec.get('student_id', '') or rec.get('enrollment_no', '')).strip()
                subject_name = str(rec.get('subject_name', '')).strip()
                
                try:
                    internal = float(rec.get('internal_score', 0))
                    external = float(rec.get('external_score', 0))
                except ValueError:
                    raise ValueError(f"Row {idx+1}: Invalid score format for {enrollment}")
                
                # Bounds check
                if internal > 30.00:
                    raise ValueError(f"Row {idx+1}: Internal score {internal} exceeds max 30 for {enrollment}")
                if external > 70.00:
                    raise ValueError(f"Row {idx+1}: External score {external} exceeds max 70 for {enrollment}")
                
                # Fetch Student
                student = db.query(Student).filter(Student.enrollment_no == enrollment).first()
                if not student:
                    raise ValueError(f"Row {idx+1}: Student {enrollment} not found.")
                
                # Fetch Subject based on student's course context
                subject = db.query(CourseSubject).filter(
                    CourseSubject.course_id == student.course_id,
                    CourseSubject.subject_name.ilike(subject_name)
                ).first()
                if not subject:
                    raise ValueError(f"Row {idx+1}: Subject '{subject_name}' not found for student's course.")
                
                # Calculate evaluation logic
                pass_status, total_marks, grade_letter, grade_points = compute_grade_dual_threshold(internal, external)
                needs_review = not pass_status
                
                # Update Academic Standing flag
                if not pass_status:
                    student.academic_standing = 'Backlog'
                
                # Upsert Record
                existing = db.query(StudentMarksRecord).filter(
                    StudentMarksRecord.student_id == student.id,
                    StudentMarksRecord.subject_id == subject.id,
                    StudentMarksRecord.semester_number == student.semester,
                ).first()
                
                if existing:
                    existing.internal_score = internal
                    existing.external_score = external
                    existing.total_marks_obtained = total_marks
                    existing.grade_letter = grade_letter
                    existing.grade_points = grade_points
                    existing.pass_status = pass_status
                    existing.needs_review = needs_review
                    existing.status = ResultStatus.pending
                    existing.review_notes = None
                else:
                    record = StudentMarksRecord(
                        student_id=student.id,
                        subject_id=subject.id,
                        semester_number=student.semester,
                        internal_score=internal,
                        external_score=external,
                        total_marks_obtained=total_marks,
                        grade_letter=grade_letter,
                        grade_points=grade_points,
                        pass_status=pass_status,
                        academic_year=str(datetime.utcnow().year),
                        needs_review=needs_review,
                        status=ResultStatus.pending,
                    )
                    db.add(record)
                    
        # Commit nested transaction block
        db.commit()
        succeeded = len(records)
        failed = 0
        error_msg = None
        
    except Exception as exc:
        db.rollback()
        succeeded = 0
        failed = len(records)
        error_msg = str(exc)
        logger.error("Result upload aborted: %s", exc)

    end = datetime.utcnow()
    run_log.status = BotStatus.success if failed == 0 else BotStatus.failed
    run_log.records_processed = succeeded
    run_log.records_failed    = failed
    run_log.ended_at          = end
    run_log.duration_seconds  = (end - start).total_seconds()
    run_log.error_message     = error_msg
    db.commit()
    
    return {
        'bot_run_id': run_log.id, 
        'total': len(records), 
        'succeeded': succeeded, 
        'failed': failed, 
        'errors': [error_msg] if error_msg else []
    }
