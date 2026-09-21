from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import cast, Date
from datetime import date

from app.database import get_db
from app.utils.deps import require_admin
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.bot_run_log import BotRunLog

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats", summary="Get admin dashboard overview stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_user = Depends(require_admin)):
    total_students = db.query(Student).count()
    faculty_members = db.query(Faculty).count()
    
    bot_runs_today = db.query(BotRunLog).filter(cast(BotRunLog.started_at, Date) == date.today()).count()
    
    pending_reviews = db.query(Student).filter(Student.is_admitted == False).count()
    
    return {
        "success": True,
        "data": {
            "total_students": total_students,
            "faculty_members": faculty_members,
            "bot_runs_today": bot_runs_today,
            "pending_reviews": pending_reviews
        }
    }
