"""
routers/logs.py — Bot Run Logs API (admin audit screen, Step 8).
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.utils.deps import require_admin
from app.models.user import User
from app.models.bot_run_log import BotRunLog, BotStatus

router = APIRouter(prefix="/api/logs", tags=["Bot Run Logs"])


@router.get("/", summary="List all bot run logs (admin)")
def list_logs(
    page: int = 1,
    page_size: int = 20,
    bot_name: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    q = db.query(BotRunLog)
    if bot_name:
        q = q.filter(BotRunLog.bot_name == bot_name)
    if status:
        q = q.filter(BotRunLog.status == status)
    total = q.count()
    logs  = q.order_by(BotRunLog.started_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "success": True,
        "data": [{
            "id":               log.id,
            "bot_name":         log.bot_name,
            "triggered_by":     log.triggered_by,
            "status":           log.status.value,
            "records_total":    log.records_total,
            "records_processed":log.records_processed,
            "records_failed":   log.records_failed,
            "started_at":       log.started_at.isoformat() if log.started_at else None,
            "ended_at":         log.ended_at.isoformat() if log.ended_at else None,
            "duration_seconds": log.duration_seconds,
            "log_file_path":    log.log_file_path,
            "report_file_path": log.report_file_path,
            "error_message":    log.error_message,
            "source_file":      log.source_file,
        } for log in logs],
        "pagination": {
            "page": page, "page_size": page_size,
            "total": total, "pages": -(-total // page_size),
        },
    }


@router.get("/{log_id}", summary="Get single bot run log detail")
def get_log(
    log_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    log = db.query(BotRunLog).filter(BotRunLog.id == log_id).first()
    if not log:
        raise HTTPException(404, "Log not found")
    return {
        "success": True,
        "data": {
            "id": log.id, "bot_name": log.bot_name,
            "triggered_by": log.triggered_by,
            "status": log.status.value,
            "records_total": log.records_total,
            "records_processed": log.records_processed,
            "records_failed": log.records_failed,
            "started_at": log.started_at.isoformat() if log.started_at else None,
            "ended_at":   log.ended_at.isoformat() if log.ended_at else None,
            "duration_seconds": log.duration_seconds,
            "log_file_path": log.log_file_path,
            "report_file_path": log.report_file_path,
            "error_message": log.error_message,
            "summary": log.summary,
            "source_file": log.source_file,
        },
    }


@router.get("/{log_id}/report", summary="Download Robot Framework HTML report")
def download_report(
    log_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    log = db.query(BotRunLog).filter(BotRunLog.id == log_id).first()
    if not log:
        raise HTTPException(404, "Log not found")
    path = log.report_file_path or log.log_file_path
    if not path or not os.path.exists(path):
        raise HTTPException(404, "Report file not found on disk")
    return FileResponse(path, media_type="text/html", filename=os.path.basename(path))
