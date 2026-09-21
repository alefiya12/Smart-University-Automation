"""
models/id_counter.py — Sequence counter for Student ID generation.
Format: SU{year}-{0001}  e.g. SU2026-0001
"""
from sqlalchemy import Column, Integer, String
from app.database import Base


class IdCounter(Base):
    __tablename__ = "id_counters"

    year = Column(String(4), primary_key=True, nullable=False)  # e.g. "2026"
    last_seq = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<IdCounter year={self.year} last_seq={self.last_seq}>"
