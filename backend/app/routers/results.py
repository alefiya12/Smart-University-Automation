"""
routers/results.py — Result Processing API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.utils.deps import require_admin, require_faculty, require_verified
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.result import StudentMarksRecord, ResultStatus
from app.models.attendance import CourseSubject
from app.services import result_service

router = APIRouter(prefix="/api/results", tags=["Results"])


class ReviewNote(BaseModel):
    notes: str = ""


# ── Bulk marks upload ─────────────────────────────────────────────────────────
@router.post("/bulk", summary="Upload marks and calculate grades (admin)")
def bulk_results(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    import pandas as pd, io
    import asyncio
    
    loop = asyncio.new_event_loop()
    content = loop.run_until_complete(file.read())
    loop.close()

    try:
        df = pd.read_excel(io.BytesIO(content))
        # Standardize columns
        df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
        
        # Ensure enrollment_no is aliased properly if they use student_id
        if 'student_id' in df.columns and 'enrollment_no' not in df.columns:
            df['enrollment_no'] = df['student_id']
            
        records = df.where(df.notna(), None).to_dict(orient='records')
    except Exception as exc:
        raise HTTPException(400, f"Could not parse Excel: {exc}")
        
    result = result_service.process_bulk_results(db, records, triggered_by=current_user.username)
    if result.get("failed") > 0 and len(result.get("errors", [])) > 0:
        raise HTTPException(400, f"Upload Aborted. Reason: {result['errors'][0]}")
        
    return {"success": True, **result}


# ── Excel Export ──────────────────────────────────────────────────────────────
@router.get("/export", summary="Export Subject-Wise Results as Excel (admin)")
def export_results(
    course_id: int = Query(...),
    semester: int = Query(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    import pandas as pd
    
    # Query all results for the course and semester
    results = db.query(StudentMarksRecord).join(Student).filter(
        Student.course_id == course_id,
        StudentMarksRecord.semester_number == semester
    ).all()
    
    if not results:
        raise HTTPException(404, "No results found for the specified course and semester.")
        
    # Group by student to dynamically compute SGPA if not yet published
    sgpa_map = {}
    for r in results:
        if r.student_id not in sgpa_map:
            student_results = [res for res in results if res.student_id == r.student_id]
            sgpa_map[r.student_id] = result_service.compute_sgpa(student_results)
            
    data = []
    for r in results:
        data.append({
            "Student_ID": r.student.enrollment_no,
            "Student_Name": r.student.full_name or r.student.user.username,
            "Subject_Name": r.subject.subject_name,
            "Internal_Score": r.internal_score,
            "External_Score": r.external_score,
            "Total_Marks_Obtained": r.total_marks_obtained,
            "Grade_Letter": r.grade_letter,
            "Pass_Status": r.pass_status,
            "Calculated_SGPA": r.sgpa if r.sgpa is not None else sgpa_map.get(r.student_id, 0.0)
        })
        
    df = pd.DataFrame(data)
    
    export_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'reports', 'exports')
    os.makedirs(export_dir, exist_ok=True)
    filename = f"Results_Course_{course_id}_Sem_{semester}.xlsx"
    filepath = os.path.join(export_dir, filename)
    
    df.to_excel(filepath, index=False)
    
    return FileResponse(filepath, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=filename)


# ── Bulk marks via JSON ───────────────────────────────────────────────────────
class BulkResultsJSON(BaseModel):
    records: list

@router.post("/bulk/json", summary="Upload marks via JSON (admin/faculty)")
def bulk_results_json(
    body: BulkResultsJSON,
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db),
):
    result = result_service.process_bulk_results(db, body.records, triggered_by=current_user.username)
    if result.get("failed") > 0 and len(result.get("errors", [])) > 0:
        raise HTTPException(400, f"Upload Aborted. Reason: {result['errors'][0]}")
    return {"success": True, **result}


# ── Approve / Reject ──────────────────────────────────────────────────────────
@router.post("/{result_id}/approve", summary="Admin approve an F-grade result")
def approve_result(
    result_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    res = db.query(StudentMarksRecord).filter(StudentMarksRecord.id == result_id).first()
    if not res:
        raise HTTPException(404, "Result not found")
    res.status = ResultStatus.approved
    db.commit()
    return {"success": True, "message": "Result approved"}


@router.post("/{result_id}/reject", summary="Admin reject a result (requires re-upload)")
def reject_result(
    result_id: int,
    body: ReviewNote,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    res = db.query(StudentMarksRecord).filter(StudentMarksRecord.id == result_id).first()
    if not res:
        raise HTTPException(404, "Result not found")
    res.status = ResultStatus.rejected
    res.review_notes = body.notes
    db.commit()
    return {"success": True, "message": "Result rejected"}


# ── Publish Results (per student-semester) ────────────────────────────────────
@router.post("/publish/{student_id}/{semester}", summary="Publish results for a student (admin)")
def publish_results(
    student_id: int,
    semester: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404, "Student not found")
    data = result_service.publish_student_results(db, student_id, semester)
    return {"success": True, "data": data}


# ── Get Student Dashboard Results ─────────────────────────────────────────────
@router.get("/student/{student_id}", summary="Get published results for a student")
def get_student_results(
    student_id: int,
    semester: Optional[int] = None,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404, "Student not found")
    if current_user.role == UserRole.student and student.user_id != current_user.id:
        raise HTTPException(403, "Access denied")

    q = db.query(StudentMarksRecord).filter(
        StudentMarksRecord.student_id == student_id,
        StudentMarksRecord.status == ResultStatus.published
    )
    if semester:
        q = q.filter(StudentMarksRecord.semester_number == semester)
        
    records = q.all()
    
    formatted = []
    for r in records:
        formatted.append({
            "id": r.id,
            "subject": r.subject.subject_name,
            "internal_score": r.internal_score,
            "external_score": r.external_score,
            "total_marks_obtained": r.total_marks_obtained,
            "grade_letter": r.grade_letter,
            "grade_points": r.grade_points,
            "pass_status": r.pass_status,
            "semester": r.semester_number,
            "academic_year": r.academic_year,
            "sgpa": r.sgpa,
            "cgpa": r.cgpa
        })
        
    return {"success": True, "data": formatted}


# ── Download Marksheet PDF ───────────────────────────────────────────────────
@router.get("/{student_id}/semester/{semester}/marksheet", summary="Download Semester Marksheet PDF")
def download_marksheet_pdf(
    student_id: int,
    semester: int,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(404, "Student not found")
    if current_user.role == UserRole.student and student.user_id != current_user.id:
        raise HTTPException(403, "Access denied")

    records = db.query(StudentMarksRecord).filter(
        StudentMarksRecord.student_id == student_id,
        StudentMarksRecord.semester_number == semester
    ).all()

    if not records:
        raise HTTPException(404, f"No results found for {student.enrollment_no} in Semester {semester}")

    # Generate or get marksheet PDF
    from app.services.pdf_service import generate_marksheet
    results_payload = []
    for r in records:
        results_payload.append({
            'subject_name': r.subject.subject_name if r.subject else 'Subject',
            'credits': r.subject.credits if r.subject else 4.0,
            'internal_score': float(r.internal_score),
            'external_score': float(r.external_score),
            'total_marks_obtained': float(r.total_marks_obtained),
            'grade_letter': r.grade_letter,
            'pass_status': r.pass_status
        })

    sgpa = records[0].sgpa if records[0].sgpa is not None else result_service.compute_sgpa(records)
    cgpa = records[0].cgpa if records[0].cgpa is not None else result_service.compute_cgpa(db, student_id)
    acad_year = records[0].academic_year or str(student.admission_year or 2026)

    filepath = generate_marksheet(
        enrollment_no=student.enrollment_no,
        student_name=student.full_name or student.user.username,
        department=student.department.name if student.department else "General",
        course=student.course.name if student.course else "General",
        semester=semester,
        academic_year=acad_year,
        results=results_payload,
        sgpa=sgpa,
        cgpa=cgpa
    )

    if not os.path.exists(filepath):
        raise HTTPException(500, "Failed to generate marksheet PDF")

    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=f"Marksheet_{student.enrollment_no}_Sem{semester}.pdf"
    )
