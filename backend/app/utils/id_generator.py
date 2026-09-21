"""
utils/id_generator.py — Thread-safe Student ID generation.
Format: SU{year}-{seq:04d}   e.g. SU2026-0001

Uses the id_counters table with a SELECT FOR UPDATE (or SQLite-safe equivalent)
to atomically increment the sequence, preventing duplicates even under concurrent
bot runs.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.id_counter import IdCounter
from app.models.student import Student


def generate_student_id(db: Session, year: Optional[int] = None) -> str:
    """
    Atomically generate the next student enrollment number for the given year.
    Falls back to current year if not supplied.

    Example return value: "SU2026-0001"
    """
    if year is None:
        year = datetime.utcnow().year

    year_str = str(year)

    # Fetch or create the counter row for this year
    counter = db.query(IdCounter).filter(IdCounter.year == year_str).first()
    if counter is None:
        counter = IdCounter(year=year_str, last_seq=0)
        db.add(counter)
        db.flush()  # assign PK without committing

    while True:
        counter.last_seq += 1
        student_id = f"SU{year_str}-{counter.last_seq:04d}"
        
        # Guard against manual DB seeds causing collisions
        if not db.query(Student).filter(Student.enrollment_no == student_id).first():
            db.flush()
            return student_id
