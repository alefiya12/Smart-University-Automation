"""
models/bot_run_log.py — Bot execution audit log ORM model.
Every bot run (admission, attendance, results) must create one entry.
Idempotency: bots check if a run for the same (bot_name, date, source_file) already succeeded.
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, Float
from app.database import Base


class BotStatus(str, enum.Enum):
    running = "running"
    success = "success"
    partial = "partial"   # some records succeeded, some failed
    failed  = "failed"


class BotRunLog(Base):
    __tablename__ = "bot_run_logs"

    id = Column(Integer, primary_key=True, index=True)
    bot_name = Column(String(100), nullable=False, index=True)   # e.g. "admission_bot"
    triggered_by = Column(String(80), nullable=True)             # username of admin who ran it
    source_file = Column(String(500), nullable=True)             # Excel file path/name
    status = Column(Enum(BotStatus), default=BotStatus.running, nullable=False)
    records_total = Column(Integer, default=0)
    records_processed = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    log_file_path = Column(String(500), nullable=True)           # path to Robot Framework log.html
    report_file_path = Column(String(500), nullable=True)        # path to Robot Framework report.html
    error_message = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)                        # JSON summary of per-record results

    def __repr__(self):
        return f"<BotRunLog id={self.id} bot={self.bot_name!r} status={self.status}>"
