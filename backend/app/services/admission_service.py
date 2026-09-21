"""
services/admission_service.py — Business logic for bulk admission processing.
Called both by the API router and by the Robot Framework keyword library.
Idempotent: skips students whose email already has an account.
"""
import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.student import Student
from app.models.department import Department
from app.models.course import Course
from app.models.bot_run_log import BotRunLog, BotStatus
from app.utils.id_generator import generate_student_id
from app.utils.security import hash_password, generate_temp_password
from app.services.email_service import send_admission_confirmation_email
from app.services.pdf_service import generate_admission_letter

logger = logging.getLogger(__name__)


def _get_or_create_department(db: Session, name: str) -> Department:
    dept = db.query(Department).filter(Department.name == name).first()
    if not dept:
        dept = Department(name=name)
        db.add(dept)
        db.flush()
    return dept


def _get_or_create_course(db: Session, dept: Department, name: str) -> Course:
    course = db.query(Course).filter(
        Course.department_id == dept.id,
        Course.name == name,
    ).first()
    if not course:
        course = Course(department_id=dept.id, name=name)
        db.add(course)
        db.flush()
    return course


def process_single_admission(db: Session, record: dict, bot_run_id: Optional[int] = None) -> dict:
    """
    Process one student record. Returns dict with keys: success, enrollment_no, error.
    Idempotent: if email already exists → skips with 'already_exists'.
    """
    email = record.get('email', '').strip().lower()
    full_name = record.get('full_name', '').strip()

    # ── Duplicate check ───────────────────────────────────────────────────────
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        logger.info("Skipping duplicate email: %s", email)
        return {'success': False, 'email': email, 'error': 'already_exists',
                'enrollment_no': None}

    # ── Department + Course (auto-create if missing) ───────────────────────────
    dept_name   = record.get('department_name', 'General')
    course_name = record.get('course_name', 'General')
    dept   = _get_or_create_department(db, dept_name)
    course = _get_or_create_course(db, dept, course_name)

    # ── Generate student ID ────────────────────────────────────────────────────
    adm_year = record.get('admission_year') or datetime.utcnow().year
    enrollment_no = generate_student_id(db, year=adm_year)

    # ── Temp password ─────────────────────────────────────────────────────────
    temp_pw = generate_temp_password()

    # ── Create User account ───────────────────────────────────────────────────
    username = enrollment_no.lower().replace('-', '')   # e.g. su20260001
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(temp_pw),
        role=UserRole.student,
        is_active=True,
        is_verified=True,   # admission bot creates verified accounts
    )
    db.add(user)
    db.flush()

    # ── Create Student profile ────────────────────────────────────────────────
    student = Student(
        user_id=user.id,
        enrollment_no=enrollment_no,
        full_name=full_name,
        department_id=dept.id,
        course_id=course.id,
        semester=record.get('semester', 1),
        phone=record.get('phone'),
        address=record.get('address'),
        guardian_name=record.get('guardian_name'),
        guardian_phone=record.get('guardian_phone'),
        admission_year=adm_year,
        is_admitted=1,
        temp_password=temp_pw,
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    # ── Generate PDF admission letter ─────────────────────────────────────────
    pdf_path = None
    try:
        pdf_path = generate_admission_letter(
            enrollment_no=enrollment_no,
            student_name=full_name,
            email=email,
            department=dept_name,
            course=course_name,
            semester=student.semester,
            admission_year=adm_year,
            temp_password=temp_pw,
        )
    except Exception as exc:
        logger.warning("PDF generation failed for %s: %s", enrollment_no, exc)

    # ── Send confirmation email ───────────────────────────────────────────────
    try:
        send_admission_confirmation_email(
            to=email,
            student_name=full_name,
            enrollment_no=enrollment_no,
            course=course_name,
            department=dept_name,
            temp_password=temp_pw,
        )
    except Exception as exc:
        logger.warning("Admission email failed for %s: %s", email, exc)

    return {
        'success': True,
        'email': email,
        'enrollment_no': enrollment_no,
        'pdf_path': pdf_path,
        'error': None,
    }


def process_bulk_admissions(
    db: Session,
    records: List[dict],
    triggered_by: str = "api",
) -> dict:
    """
    Process a list of admission records. Creates a BotRunLog entry.
    Returns summary dict with bot_run_id, succeeded, failed, errors.
    """
    # Create bot run log entry
    run_log = BotRunLog(
        bot_name="admission_bot",
        triggered_by=triggered_by,
        status=BotStatus.running,
        records_total=len(records),
        started_at=datetime.utcnow(),
    )
    db.add(run_log)
    db.commit()
    db.refresh(run_log)

    succeeded, failed, errors = 0, 0, []
    start = datetime.utcnow()

    for record in records:
        try:
            result = process_single_admission(db, record, bot_run_id=run_log.id)
            if result['success']:
                succeeded += 1
            else:
                failed += 1
                errors.append(f"{record.get('email')}: {result.get('error')}")
        except Exception as exc:
            failed += 1
            errors.append(f"{record.get('email', '?')}: {str(exc)}")
            db.rollback()
            logger.error("Admission failed for %s: %s", record.get('email'), exc)

    # Update run log
    end = datetime.utcnow()
    run_log.status     = BotStatus.success if failed == 0 else (BotStatus.partial if succeeded > 0 else BotStatus.failed)
    run_log.records_processed = succeeded
    run_log.records_failed    = failed
    run_log.ended_at   = end
    run_log.duration_seconds  = (end - start).total_seconds()
    run_log.error_message     = '\n'.join(errors) if errors else None
    db.commit()

    return {
        'bot_run_id': run_log.id,
        'total':      len(records),
        'succeeded':  succeeded,
        'failed':     failed,
        'errors':     errors,
    }
