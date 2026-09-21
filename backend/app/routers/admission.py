"""
routers/admission.py — Admission API endpoints.
Routes:
  POST /api/admission/bulk              — trigger bulk admission (admin)
  POST /api/admission/                  — create single admission record (admin)
  GET  /api/admission/                  — list all students (admin)
  GET  /api/admission/{student_id}      — get single student detail (admin/student)
  PATCH /api/admission/{student_id}/status — approve/reject (admin)
"""
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.deps import require_admin, require_verified, get_current_user
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.department import Department
from app.models.course import Course
from app.schemas.admission import (
    AdmissionRecordIn, AdmissionRecordOut,
    BulkAdmissionRequest, BulkAdmissionResponse,
    AdmissionStatusUpdate,
)
from app.services import admission_service

router = APIRouter(prefix="/api/admission", tags=["Admission"])


# ── Bulk admission via JSON body ──────────────────────────────────────────────
@router.post(
    "/bulk",
    response_model=BulkAdmissionResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk-process admission records (admin only)",
)
def bulk_admissions(
    body: BulkAdmissionRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    records = [r.model_dump() for r in body.records]
    result = admission_service.process_bulk_admissions(
        db, records, triggered_by=current_user.username
    )
    return BulkAdmissionResponse(
        bot_run_id=result['bot_run_id'],
        total=result['total'],
        succeeded=result['succeeded'],
        failed=result['failed'],
        errors=result['errors'],
        message=f"Processed {result['total']} records: {result['succeeded']} admitted, {result['failed']} failed.",
    )


# ── Bulk admission via Excel upload ──────────────────────────────────────────
@router.post(
    "/bulk/upload",
    response_model=BulkAdmissionResponse,
    summary="Upload Excel file and run admission bot (admin only)",
)
async def bulk_admissions_excel(
    file: UploadFile = File(..., description="Excel file (.xlsx) with admission data"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    import pandas as pd
    import io
    content = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(content))
        # Normalize column names
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
        records = df.where(df.notna(), None).to_dict(orient='records')
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Could not parse Excel file: {exc}")

    result = admission_service.process_bulk_admissions(
        db, records, triggered_by=current_user.username
    )
    return BulkAdmissionResponse(
        bot_run_id=result['bot_run_id'],
        total=result['total'],
        succeeded=result['succeeded'],
        failed=result['failed'],
        errors=result['errors'],
        message=f"Processed {result['total']} records: {result['succeeded']} admitted, {result['failed']} failed.",
    )


# ── List all students ─────────────────────────────────────────────────────────
@router.get(
    "/",
    summary="List all admitted students (admin only)",
)
def list_students(
    page: int = 1,
    page_size: int = 20,
    department_id: Optional[int] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    q = db.query(Student)
    if department_id:
        q = q.filter(Student.department_id == department_id)
    if search:
        q = q.join(User, Student.user_id == User.id).filter(
            (Student.enrollment_no.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.username.ilike(f"%{search}%"))
        )
    total = q.count()
    students = q.offset((page - 1) * page_size).limit(page_size).all()

    def _serialize(s):
        dept   = db.query(Department).filter(Department.id == s.department_id).first()
        course = db.query(Course).filter(Course.id == s.course_id).first()
        user   = db.query(User).filter(User.id == s.user_id).first()
        return {
            "id": s.id, "enrollment_no": s.enrollment_no,
            "email": user.email if user else None,
            "username": s.full_name if s.full_name else (user.username if user else None),
            "department": dept.name if dept else None,
            "course": course.name if course else None,
            "semester": s.semester, "is_admitted": s.is_admitted,
            "admission_year": s.admission_year,
        }

    return {
        "success": True,
        "data": [_serialize(s) for s in students],
        "pagination": {"page": page, "page_size": page_size, "total": total, "pages": -(-total // page_size)},
    }


# ── Get logged-in student profile ──────────────────────────────────────────────
@router.get("/me", summary="Get authenticated student's profile")
def get_my_student_profile(
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found for this user")

    dept   = db.query(Department).filter(Department.id == student.department_id).first()
    course = db.query(Course).filter(Course.id == student.course_id).first()
    return {
        "success": True,
        "data": {
            "id": student.id,
            "enrollment_no": student.enrollment_no,
            "full_name": student.full_name or current_user.username,
            "email": current_user.email,
            "username": current_user.username,
            "department": dept.name if dept else None,
            "department_id": student.department_id,
            "course": course.name if course else None,
            "course_id": student.course_id,
            "semester": student.semester,
            "phone": student.phone,
            "address": student.address,
            "guardian_name": student.guardian_name,
            "guardian_phone": student.guardian_phone,
            "is_admitted": student.is_admitted,
            "admission_year": student.admission_year,
            "academic_standing": student.academic_standing,
        },
    }


# ── Get single student ────────────────────────────────────────────────────────
@router.get("/{student_id}", summary="Get student admission detail")
def get_student(
    student_id: int,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    # Students can only view their own record
    if current_user.role == UserRole.student and student.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    dept   = db.query(Department).filter(Department.id == student.department_id).first()
    course = db.query(Course).filter(Course.id == student.course_id).first()
    user   = db.query(User).filter(User.id == student.user_id).first()
    return {
        "success": True,
        "data": {
            "id": student.id, "enrollment_no": student.enrollment_no,
            "email": user.email if user else None,
            "username": user.username if user else None,
            "department": dept.name if dept else None,
            "course": course.name if course else None,
            "semester": student.semester, "phone": student.phone,
            "address": student.address, "guardian_name": student.guardian_name,
            "is_admitted": student.is_admitted,
            "admission_year": student.admission_year,
        },
    }


# ── Update admission status ───────────────────────────────────────────────────
@router.patch("/{student_id}/status", summary="Approve or reject admission (admin only)")
def update_status(
    student_id: int,
    body: AdmissionStatusUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.is_admitted = body.is_admitted
    db.commit()
    return {"success": True, "message": "Admission status updated.", "is_admitted": student.is_admitted}


from pydantic import BaseModel
class StudentUpdate(BaseModel):
    full_name: str
    email: str
    department_id: int
    course_id: int
    semester: int
    is_admitted: int = 0

@router.put("/{student_id}", summary="Update student details (admin only)")
def update_student(
    student_id: int,
    body: StudentUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    user = db.query(User).filter(User.id == student.user_id).first()
    if user:
        user.email = body.email
    
    student.full_name = body.full_name
    student.department_id = body.department_id
    student.course_id = body.course_id
    student.semester = body.semester
    student.is_admitted = body.is_admitted
    
    db.commit()
    return {"success": True, "message": "Student updated successfully"}

@router.delete("/{student_id}", summary="Delete student record (admin only)")
def delete_student(
    student_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    user = db.query(User).filter(User.id == student.user_id).first()
    db.delete(student)
    if user:
        db.delete(user)
        
    db.commit()
    return {"success": True, "message": "Student deleted successfully"}


# ── Download admission letter PDF ─────────────────────────────────────────────
@router.get("/{student_id}/letter", summary="Download admission letter PDF by ID")
def download_letter(
    student_id: int,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if current_user.role == UserRole.student and student.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Regenerate on-demand
    from app.services.pdf_service import generate_admission_letter
    from app.services.admission_service import _get_or_create_department
    user   = db.query(User).filter(User.id == student.user_id).first()
    dept   = db.query(Department).filter(Department.id == student.department_id).first()
    course = db.query(Course).filter(Course.id == student.course_id).first()
    try:
        path = generate_admission_letter(
            enrollment_no=student.enrollment_no,
            student_name=student.full_name if student.full_name else (user.username if user else "Student"),
            email=user.email if user else "",
            department=dept.name if dept else "",
            course=course.name if course else "",
            semester=student.semester,
            admission_year=student.admission_year or 2026,
            temp_password=student.temp_password or "[see email]",
        )
        return FileResponse(path, media_type="application/pdf",
                            filename=f"admission_letter_{student.enrollment_no}.pdf")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {exc}")


@router.get("/letter/{enrollment_no}", summary="Download admission letter PDF by enrollment number")
def download_letter_by_enrollment(
    enrollment_no: str,
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.enrollment_no == enrollment_no).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    from app.services.pdf_service import generate_admission_letter
    user   = db.query(User).filter(User.id == student.user_id).first()
    dept   = db.query(Department).filter(Department.id == student.department_id).first()
    course = db.query(Course).filter(Course.id == student.course_id).first()
    try:
        path = generate_admission_letter(
            enrollment_no=student.enrollment_no,
            student_name=student.full_name if student.full_name else (user.username if user else "Student"),
            email=user.email if user else "",
            department=dept.name if dept else "",
            course=course.name if course else "",
            semester=student.semester,
            admission_year=student.admission_year or 2026,
            temp_password=student.temp_password or "[see email]",
        )
        return FileResponse(path, media_type="application/pdf",
                            filename=f"admission_letter_{student.enrollment_no}.pdf")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {exc}")
