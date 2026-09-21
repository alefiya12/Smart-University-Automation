"""
AdmissionKeywords.py — Robot Framework keyword library for Admission Automation.
Thin orchestration in .robot file; all logic here (testable without Robot).
Calls the Python admission_service directly (no browser needed for API-based flow).
"""
import os
import sys
import json
import logging
from datetime import datetime
from typing import List, Optional

# Allow importing backend app modules when run from rpa/ directory
_BACKEND_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
if _BACKEND_PATH not in sys.path:
    sys.path.insert(0, _BACKEND_PATH)

from robot.api.deco import keyword
from robot.api import logger as robot_logger

logger = logging.getLogger(__name__)


class AdmissionKeywords:
    """
    Robot Framework keyword library for bulk admission processing.
    Scope: SUITE — one instance per test suite run.
    """
    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self):
        self._records: List[dict] = []
        self._results: List[dict] = []
        self._run_summary: Optional[dict] = None

    # ── Keyword: Load Admission Excel ─────────────────────────────────────────
    @keyword("Load Admission Excel")
    def load_admission_excel(self, path: str) -> list:
        """
        Read admission data from an Excel file.
        Expected columns: full_name, email, phone, department_name,
                          course_name, semester, address, admission_year
        Returns list of record dicts.
        """
        import pandas as pd
        robot_logger.info(f"Loading admission Excel: {path}")
        df = pd.read_excel(path)
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
        self._records = df.where(df.notna(), None).to_dict(orient='records')
        robot_logger.info(f"Loaded {len(self._records)} records from Excel")
        return self._records

    # ── Keyword: Process Single Admission ────────────────────────────────────
    @keyword("Process Single Admission")
    def process_single_admission(self, record: dict) -> None:
        """
        Process one admission record — creates user+student, generates PDF+email.
        Idempotent: skips if email already exists.
        """
        from app.database import SessionLocal
        from app.services.admission_service import process_single_admission as _process

        db = SessionLocal()
        try:
            result = _process(db, record)
            self._results.append(result)
            if result['success']:
                robot_logger.info(f"✓ Admitted: {result['enrollment_no']} ({record.get('email')})")
            else:
                robot_logger.warn(f"⚠ Skipped: {record.get('email')} — {result.get('error')}")
        except Exception as exc:
            robot_logger.error(f"✗ Failed: {record.get('email')} — {exc}")
            self._results.append({'success': False, 'email': record.get('email'), 'error': str(exc)})
            db.rollback()
        finally:
            db.close()

    # ── Keyword: Log Run Summary ──────────────────────────────────────────────
    @keyword("Log Run Summary")
    def log_run_summary(self) -> None:
        """Write a summary of the run to the Robot Framework log."""
        succeeded = sum(1 for r in self._results if r.get('success'))
        failed    = len(self._results) - succeeded
        robot_logger.info("=" * 50)
        robot_logger.info(f"ADMISSION BOT SUMMARY")
        robot_logger.info(f"  Total records : {len(self._results)}")
        robot_logger.info(f"  Succeeded     : {succeeded}")
        robot_logger.info(f"  Failed/Skipped: {failed}")
        robot_logger.info("=" * 50)
        self._run_summary = {
            'total': len(self._results), 'succeeded': succeeded, 'failed': failed,
            'timestamp': datetime.utcnow().isoformat(),
        }

    # ── Keyword: Get Run Summary (for assertions in tests) ───────────────────
    @keyword("Get Run Summary")
    def get_run_summary(self) -> dict:
        return self._run_summary or {}
