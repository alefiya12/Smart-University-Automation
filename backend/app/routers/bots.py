"""
routers/bots.py — RPA Bot Runner API
Triggers Robot Framework bots as subprocesses, captures logs, and records BotRunLog entries.
Endpoints:
  POST /api/bots/run/{bot_name}  — trigger a bot run
  GET  /api/bots/status/{log_id} — poll run status
  GET  /api/bots/recent          — recent runs for dashboard
"""
import os
import subprocess
import threading
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.utils.deps import require_admin
from app.models.user import User
from app.models.bot_run_log import BotRunLog, BotStatus

router = APIRouter(prefix="/api/bots", tags=["RPA Bot Runner"])

# ── Resolve project-root paths ─────────────────────────────────────────────────
_HERE = os.path.dirname(__file__)  # app/routers/
_BACKEND_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))  # backend/
_PROJECT_ROOT = os.path.abspath(os.path.join(_BACKEND_ROOT, ".."))  # project root
_VENV_ROBOT   = os.path.join(_BACKEND_ROOT, ".venv", "bin", "robot")

_BOT_CONFIG = {
    "admission_bot": {
        "robot_file": os.path.join(_PROJECT_ROOT, "rpa", "admission", "admission_bot.robot"),
        "log_dir":    os.path.join(_PROJECT_ROOT, "logs", "admission"),
        "display_name": "Admission Bot",
        "description": "Reads Excel, creates student accounts, generates enrollment IDs & PDF letters.",
    },
    "attendance_bot": {
        "robot_file": os.path.join(_PROJECT_ROOT, "rpa", "attendance", "attendance_bot.robot"),
        "log_dir":    os.path.join(_PROJECT_ROOT, "logs", "attendance"),
        "display_name": "Attendance Bot",
        "description": "Uploads attendance records, computes percentages, triggers low-attendance alerts.",
    },
    "results_bot": {
        "robot_file": os.path.join(_PROJECT_ROOT, "rpa", "results", "results_bot.robot"),
        "log_dir":    os.path.join(_PROJECT_ROOT, "logs", "results"),
        "display_name": "Results Bot",
        "description": "Processes marks, computes SGPA/CGPA, flags F-grades, publishes approved results.",
    },
}


def _run_bot_subprocess(log_id: int, bot_name: str, config: dict):
    """Background thread: executes robot, updates BotRunLog when done."""
    db = SessionLocal()
    try:
        os.makedirs(config["log_dir"], exist_ok=True)
        log_txt = os.path.join(config["log_dir"], f"run_{log_id}.txt")

        cmd = [
            _VENV_ROBOT,
            "--outputdir", config["log_dir"],
            "--log",    f"log_{log_id}.html",
            "--report", f"report_{log_id}.html",
            "--output", f"output_{log_id}.xml",
            config["robot_file"],
        ]

        with open(log_txt, "w") as fout:
            proc = subprocess.run(
                cmd,
                cwd=_PROJECT_ROOT,
                stdout=fout,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=600,  # 10-min safety timeout
            )

        rc = proc.returncode
        ended = datetime.utcnow()

        # Read captured output for summary
        try:
            with open(log_txt, "r") as f:
                raw_output = f.read()
        except Exception:
            raw_output = ""

        log_path    = os.path.join(config["log_dir"], f"log_{log_id}.html")
        report_path = os.path.join(config["log_dir"], f"report_{log_id}.html")

        # Parse pass/fail counts from robot output
        passed, failed = 0, 0
        for line in raw_output.splitlines():
            if "passed," in line and "failed" in line:
                parts = line.strip().split()
                try:
                    passed = int(parts[0])
                    failed = int(parts[2])
                except Exception:
                    pass

        # Parse actual record counts from output XML if available
        xml_path = os.path.join(config["log_dir"], f"output_{log_id}.xml")
        rec_processed, rec_failed, rec_total = None, None, None
        if os.path.exists(xml_path):
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(xml_path)
                for msg in tree.getroot().iter('msg'):
                    txt = (msg.text or "").strip()
                    if "Total records :" in txt or "Total Rows:" in txt or txt.startswith("Total:"):
                        try:
                            rec_total = int(txt.split(":")[-1].strip())
                        except Exception:
                            pass
                    elif "Succeeded" in txt and ":" in txt:
                        try:
                            rec_processed = int(txt.split(":")[-1].strip())
                        except Exception:
                            pass
                    elif ("Failed" in txt or "Failed/Skipped" in txt) and ":" in txt:
                        try:
                            rec_failed = int(txt.split(":")[-1].strip())
                        except Exception:
                            pass
            except Exception:
                pass

        bot_log = db.query(BotRunLog).filter(BotRunLog.id == log_id).first()
        if bot_log:
            bot_log.ended_at         = ended
            bot_log.duration_seconds = (ended - bot_log.started_at).total_seconds()
            bot_log.records_processed = rec_processed if rec_processed is not None else passed
            bot_log.records_failed    = rec_failed if rec_failed is not None else failed
            bot_log.records_total     = rec_total if rec_total is not None else (passed + failed)
            bot_log.log_file_path     = log_path    if os.path.exists(log_path) else None
            bot_log.report_file_path  = report_path if os.path.exists(report_path) else None
            bot_log.summary           = raw_output[-4000:] if raw_output else None  # last 4K chars

            if rc == 0:
                bot_log.status = BotStatus.success
            elif passed > 0:
                bot_log.status = BotStatus.partial
            else:
                bot_log.status = BotStatus.failed
                bot_log.error_message = raw_output[-2000:]

            db.commit()

    except subprocess.TimeoutExpired:
        db.query(BotRunLog).filter(BotRunLog.id == log_id).update({
            "status": BotStatus.failed,
            "error_message": "Bot run timed out after 10 minutes.",
            "ended_at": datetime.utcnow(),
        })
        db.commit()
    except Exception as exc:
        db.query(BotRunLog).filter(BotRunLog.id == log_id).update({
            "status": BotStatus.failed,
            "error_message": str(exc),
            "ended_at": datetime.utcnow(),
        })
        db.commit()
    finally:
        db.close()


@router.post("/run/{bot_name}", summary="Trigger an RPA bot run (admin)")
def trigger_bot_run(
    bot_name: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if bot_name not in _BOT_CONFIG:
        raise HTTPException(400, f"Unknown bot: {bot_name}. Valid: {list(_BOT_CONFIG.keys())}")

    config = _BOT_CONFIG[bot_name]

    # Check if already running
    existing = db.query(BotRunLog).filter(
        BotRunLog.bot_name == bot_name,
        BotRunLog.status == BotStatus.running,
    ).first()
    if existing:
        raise HTTPException(409, f"Bot '{bot_name}' is already running (log_id={existing.id}).")

    # Create log entry in 'running' state
    bot_log = BotRunLog(
        bot_name=bot_name,
        triggered_by=current_user.username,
        status=BotStatus.running,
        started_at=datetime.utcnow(),
        records_total=0,
        records_processed=0,
        records_failed=0,
    )
    db.add(bot_log)
    db.commit()
    db.refresh(bot_log)

    # Kick off the subprocess in a background thread so HTTP returns immediately
    t = threading.Thread(
        target=_run_bot_subprocess,
        args=(bot_log.id, bot_name, config),
        daemon=True,
    )
    t.start()

    return {
        "success": True,
        "message": f"Bot '{config['display_name']}' started.",
        "log_id": bot_log.id,
        "bot_name": bot_name,
        "started_at": bot_log.started_at.isoformat(),
    }


@router.get("/status/{log_id}", summary="Poll bot run status")
def get_bot_status(
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
            "summary":          log.summary,
        },
    }


@router.get("/recent", summary="Get recent bot runs (last 10 per bot)")
def get_recent_runs(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Returns last 5 runs per bot for the control panel quick history."""
    results = {}
    for bot_name in _BOT_CONFIG:
        logs = db.query(BotRunLog).filter(
            BotRunLog.bot_name == bot_name
        ).order_by(BotRunLog.started_at.desc()).limit(5).all()

        results[bot_name] = [{
            "id":               l.id,
            "status":           l.status.value,
            "triggered_by":     l.triggered_by,
            "started_at":       l.started_at.isoformat() if l.started_at else None,
            "duration_seconds": l.duration_seconds,
            "records_processed":l.records_processed,
            "records_failed":   l.records_failed,
            "records_total":    l.records_total,
            "report_file_path": l.report_file_path,
        } for l in logs]

    return {"success": True, "data": results}


@router.get("/list", summary="List all known bots with metadata")
def list_bots(current_user: User = Depends(require_admin)):
    return {
        "success": True,
        "data": [
            {
                "key": k,
                "display_name": v["display_name"],
                "description": v["description"],
                "robot_file": v["robot_file"],
            }
            for k, v in _BOT_CONFIG.items()
        ],
    }
