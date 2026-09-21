"""
routers/attendance.py — Subject-Wise Attendance API endpoints.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.deps import require_admin, require_verified
from app.models.user import User, UserRole
from app.models.student import Student
from app.services import attendance_service

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


# ── Bulk via Excel upload (Subject-Wise) ──────────────────────────────────────
@router.post("/bulk/upload", summary="Upload subject-wise attendance Excel (admin)")
async def bulk_attendance_excel(
    course_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    import pandas as pd
    import io
    content = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(content))
        # Keep headers exact but strip whitespace, except student_id and date which should be standardized
        new_cols = []
        for c in df.columns:
            c_str = str(c).strip()
            if c_str.lower() in ['student_id', 'student id', 'enrollment_no', 'enrollment no']:
                new_cols.append('student_id')
            elif c_str.lower() == 'date':
                new_cols.append('date')
            else:
                new_cols.append(c_str)
        df.columns = new_cols
        
        # Replace NaN with None
        records = df.where(df.notna(), None).to_dict(orient='records')
    except Exception as exc:
        raise HTTPException(400, f"Could not parse Excel: {exc}")
        
    result = attendance_service.process_bulk_attendance_excel(
        db, records, course_id, triggered_by=current_user.username
    )
    
    if result.get("failed") > 0 and len(result.get("errors", [])) > 0:
        # If there's an abort error like "Student Not Found" or "Subject mismatch"
        if result["total"] == result["failed"]:
            raise HTTPException(400, f"Upload Aborted. Reason: {result['errors'][0]}")
            
    return {"success": True, **result}


# ── Get student attendance summary ────────────────────────────────────────────
@router.get("/student/{student_id}/summary", summary="Get dashboard summary")
def attendance_summary(
    student_id: int,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404, "Student not found")
    if current_user.role == UserRole.student and student.user_id != current_user.id:
        raise HTTPException(403, "Access denied")

    summaries = attendance_service.get_student_subject_summaries(db, student_id)
    return {"success": True, "data": summaries, "student_id": student_id}


# ── Get raw daily attendance logs ─────────────────────────────────────────────
@router.get("/student/{student_id}", summary="Get daily attendance logs")
def student_attendance(
    student_id: int,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404, "Student not found")
    if current_user.role == UserRole.student and student.user_id != current_user.id:
        raise HTTPException(403, "Access denied")

    logs = attendance_service.get_student_daily_logs(db, student_id)
    return {"success": True, "data": logs}
