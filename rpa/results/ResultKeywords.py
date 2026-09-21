"""
ResultKeywords.py — Robot Framework keyword library for Result Processing.
Uses the Dual-Threshold Grade Evaluation Matrix (Internal/30 + External/70).
"""
import os
import sys
import logging
from datetime import datetime
from typing import List, Optional

_BACKEND_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
if _BACKEND_PATH not in sys.path:
    sys.path.insert(0, _BACKEND_PATH)

from robot.api.deco import keyword
from robot.api import logger as robot_logger

logger = logging.getLogger(__name__)


class ResultKeywords:
    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self):
        self._records: List[dict] = []
        self._results: List[dict] = []
        self._failing: List[dict] = []

    @keyword("Load Marks Excel")
    def load_marks_excel(self, path: str) -> list:
        """
        Load marks from Excel.
        Supported columns: enrollment_no / student_id, subject / subject_name,
        internal_score, external_score, semester, academic_year
        """
        import pandas as pd
        robot_logger.info(f"Loading marks Excel: {path}")
        df = pd.read_excel(path)
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
        
        # Normalize column aliases
        if 'student_id' in df.columns and 'enrollment_no' not in df.columns:
            df['enrollment_no'] = df['student_id']
        if 'subject' in df.columns and 'subject_name' not in df.columns:
            df['subject_name'] = df['subject']

        self._records = df.where(df.notna(), None).to_dict(orient='records')
        robot_logger.info(f"Loaded {len(self._records)} mark records")
        return self._records

    @keyword("Process Student Result")
    def process_student_result(self, record: dict) -> None:
        """
        Process one marks record with dual-threshold evaluation:
        - Internal <= 30.00 (pass >= 12.00)
        - External <= 70.00 (pass >= 28.00)
        """
        from app.database import SessionLocal
        from app.models.student import Student
        from app.models.attendance import CourseSubject
        from app.models.result import StudentMarksRecord, ResultStatus
        from app.services.result_service import compute_grade_dual_threshold

        db = SessionLocal()
        try:
            enrollment = str(record.get('enrollment_no', '') or record.get('student_id', '')).strip()
            subject_name = str(record.get('subject_name', '') or record.get('subject', '')).strip()
            internal = float(record.get('internal_score', 0))
            external = float(record.get('external_score', 0))
            semester = int(record.get('semester', 1))
            academic_year = str(record.get('academic_year', str(datetime.utcnow().year)))

            student = db.query(Student).filter(Student.enrollment_no == enrollment).first()
            if not student:
                raise ValueError(f"Student not found: {enrollment}")

            subject = db.query(CourseSubject).filter(
                CourseSubject.course_id == student.course_id,
                CourseSubject.subject_name.ilike(subject_name),
            ).first()
            if not subject:
                # If subject doesn't exist for course yet, create it so bot doesn't crash on initial seed
                subject = CourseSubject(
                    course_id=student.course_id,
                    subject_name=subject_name.title(),
                    semester=semester,
                    credits=float(record.get('credits', 4.0)),
                )
                db.add(subject)
                db.flush()

            pass_status, total_marks, grade_letter, grade_points = compute_grade_dual_threshold(internal, external)
            needs_review = not pass_status

            if not pass_status:
                student.academic_standing = 'Backlog'

            existing = db.query(StudentMarksRecord).filter(
                StudentMarksRecord.student_id == student.id,
                StudentMarksRecord.subject_id == subject.id,
                StudentMarksRecord.semester_number == semester,
            ).first()

            if existing:
                existing.internal_score = internal
                existing.external_score = external
                existing.total_marks_obtained = total_marks
                existing.grade_letter = grade_letter
                existing.grade_points = grade_points
                existing.pass_status = pass_status
                existing.needs_review = needs_review
                existing.academic_year = academic_year
                record_id = existing.id
            else:
                new_record = StudentMarksRecord(
                    student_id=student.id,
                    subject_id=subject.id,
                    semester_number=semester,
                    internal_score=internal,
                    external_score=external,
                    total_marks_obtained=total_marks,
                    grade_letter=grade_letter,
                    grade_points=grade_points,
                    pass_status=pass_status,
                    needs_review=needs_review,
                    academic_year=academic_year,
                    status=ResultStatus.pending,
                )
                db.add(new_record)
                db.flush()
                record_id = new_record.id

            db.commit()

            robot_logger.info(
                f"✓ {enrollment} | {subject_name} | Int: {internal}/30, Ext: {external}/70 "
                f"→ Total: {total_marks} ({grade_letter}, {grade_points} pts) | Pass: {pass_status}"
            )

            if needs_review:
                self._failing.append({
                    'enrollment_no': enrollment,
                    'subject': subject_name,
                    'result_id': record_id,
                    'internal': internal,
                    'external': external,
                })

            self._results.append({
                'success': True,
                'enrollment_no': enrollment,
                'grade': grade_letter,
                'pass_status': pass_status,
                'result_id': record_id,
            })
        except Exception as exc:
            robot_logger.error(f"✗ {record.get('enrollment_no')} — {exc}")
            self._results.append({'success': False, 'enrollment_no': record.get('enrollment_no'), 'error': str(exc)})
            db.rollback()
        finally:
            db.close()

    @keyword("Review Failing Students")
    def review_failing_students(self) -> None:
        """Log all students with failing internal or external thresholds."""
        if not self._failing:
            robot_logger.info("No failing records requiring admin review.")
            return
        robot_logger.warn(f"{len(self._failing)} record(s) failed passing thresholds and require review:")
        for item in self._failing:
            robot_logger.warn(
                f"  ⚠ {item['enrollment_no']} | {item['subject']} "
                f"(Internal={item['internal']}/30, External={item['external']}/70) → result_id={item['result_id']}"
            )

    @keyword("Publish Approved Results")
    def publish_approved_results(self) -> None:
        """Publish results and calculate SGPA/CGPA for students."""
        from app.database import SessionLocal
        from app.models.student import Student
        from app.services.result_service import publish_student_results

        db = SessionLocal()
        try:
            processed = set(r['enrollment_no'] for r in self._results if r.get('success'))
            for enrollment in processed:
                student = db.query(Student).filter(Student.enrollment_no == enrollment).first()
                if not student:
                    continue

                semesters = set()
                for rec in self._records:
                    rec_enr = str(rec.get('enrollment_no', '') or rec.get('student_id', ''))
                    if rec_enr == enrollment and rec.get('semester'):
                        semesters.add(int(rec['semester']))

                if not semesters:
                    semesters = {student.semester}

                for sem in semesters:
                    outcome = publish_student_results(db, student.id, sem)
                    robot_logger.info(
                        f"Published {enrollment} Sem{sem}: {outcome['published']} subjects | "
                        f"SGPA={outcome['sgpa']:.2f} | blocked={outcome['blocked']}"
                    )
        except Exception as exc:
            robot_logger.error(f"Publish failed: {exc}")
        finally:
            db.close()

    @keyword("Log Run Summary")
    def log_run_summary(self) -> None:
        succeeded = sum(1 for r in self._results if r.get('success'))
        failed = len(self._results) - succeeded
        robot_logger.info("=" * 50)
        robot_logger.info("RESULTS BOT SUMMARY")
        robot_logger.info(f"  Total:          {len(self._results)}")
        robot_logger.info(f"  Succeeded:      {succeeded}")
        robot_logger.info(f"  Failed:         {failed}")
        robot_logger.info(f"  Needs Review:   {len(self._failing)}")
        robot_logger.info("=" * 50)
