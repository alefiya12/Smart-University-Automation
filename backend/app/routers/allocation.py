"""
routers/allocation.py — Automated Admission Allocation System API.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.utils.deps import require_admin
from app.models.user import User
from app.models.course import Course
from app.models.admission_staging import AdmissionStaging, CandidateCategory
from app.services import allocation_service

router = APIRouter(prefix="/api/allocation", tags=["Allocation"])


@router.post("/upload-staging", summary="Upload Excel file to Staging DB (admin only)")
async def upload_staging(
    file: UploadFile = File(..., description="Excel file (.xlsx) with candidate records"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    import pandas as pd
    import io
    content = await file.read()
    try:
        df = pd.read_excel(io.BytesIO(content))
        # Normalize columns by stripping whitespaces
        df.columns = [str(c).strip() for c in df.columns]
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Could not parse Excel file: {exc}")
                            
    # Expecting columns: Student_ID, Student_Name, Applied_Course, Candidate_Category, 
    # Class_12_Pct, Entrance_Exam_Score, Core_Subject_Score, Date_Of_Birth
    
    # Pre-fetch courses for foreign key mapping
    courses = db.query(Course).all()
    course_map = {}
    for c in courses:
        course_map[c.name.lower()] = c.id
        if c.code:
            course_map[c.code.lower()] = c.id
    
    inserted = 0
    errors = []
    
    for idx, row in df.iterrows():
        try:
            course_name = str(row.get('Applied_Course', '')).strip()
            c_id = course_map.get(course_name.lower())
            
            if not c_id:
                errors.append(f"Row {idx+1}: Course '{course_name}' not found.")
                continue
                
            cat_str = str(row.get('Candidate_Category', 'GEN')).strip().upper()
            try:
                category = CandidateCategory(cat_str)
            except ValueError:
                category = CandidateCategory.GEN
                
            record = AdmissionStaging(
                student_id=str(row['Student_ID']),
                student_name=str(row['Student_Name']).title(),
                applied_course_id=c_id,
                candidate_category=category,
                class_12_pct=float(row['Class_12_Pct']),
                entrance_exam_score=float(row['Entrance_Exam_Score']),
                core_subject_score=float(row['Core_Subject_Score']),
                date_of_birth=pd.to_datetime(row['Date_Of_Birth']).date(),
            )
            db.add(record)
            inserted += 1
        except Exception as e:
            errors.append(f"Row {idx+1}: Parsing error - {str(e)}")
            
    db.commit()
    
    if inserted == 0 and errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to stage any records. First error: {errors[0]}")
    
    return {
        "success": True,
        "message": f"Staged {inserted} records successfully. {len(errors)} errors skipped.",
        "errors": errors
    }


@router.get("/staging", summary="Get Staged Admission Records (admin only)")
def get_staging_records(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    records = db.query(AdmissionStaging).order_by(AdmissionStaging.id.desc()).all()
    
    data = []
    for r in records:
        data.append({
            "id": r.id,
            "student_id": r.student_id,
            "student_name": r.student_name,
            "applied_course": r.course.name if r.course else "Unknown",
            "candidate_category": r.candidate_category.value,
            "class_12_pct": r.class_12_pct,
            "entrance_exam_score": r.entrance_exam_score,
            "core_subject_score": r.core_subject_score,
            "final_admission_status": r.final_admission_status.value,
            "allocated_seat_type": r.allocated_seat_type.value,
            "waitlist_rank": r.waitlist_rank,
            "reason_code_logs": r.reason_code_logs
        })
        
    return {
        "success": True,
        "data": data
    }


@router.delete("/staging", summary="Clear Staged Admission Records (admin only)")
def clear_staging_records(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        db.query(AdmissionStaging).delete()
        db.commit()
        return {"success": True, "message": "Staging area cleared successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run", summary="Trigger the Allocation Algorithm (admin only)")
def run_allocation(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    results = allocation_service.run_allocation_for_all_courses(db)
    return {
        "success": True,
        "message": "Allocation completed successfully.",
        "data": results
    }


@router.post("/{staging_id}/confirm", summary="Confirm an eligible admission (admin only)")
def confirm_allocation(
    staging_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    from app.models.admission_staging import AdmissionStatus
    record = db.query(AdmissionStaging).filter(AdmissionStaging.id == staging_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    if record.final_admission_status != AdmissionStatus.ELIGIBLE_FOR_ADMISSION:
        raise HTTPException(status_code=400, detail="Only ELIGIBLE_FOR_ADMISSION records can be confirmed.")
        
    record.final_admission_status = AdmissionStatus.ADMISSION_CONFIRMED
    db.commit()
    
    return {"success": True, "message": f"Confirmed admission for {record.student_name}"}


@router.post("/{staging_id}/cancel", summary="Cancel admission and advance waitlist (admin only)")
def cancel_allocation(
    staging_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    from app.models.admission_staging import AdmissionStatus, AllocatedSeatType
    record = db.query(AdmissionStaging).filter(AdmissionStaging.id == staging_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    if record.final_admission_status not in [AdmissionStatus.ELIGIBLE_FOR_ADMISSION, AdmissionStatus.ADMISSION_CONFIRMED]:
        raise HTTPException(status_code=400, detail="Only eligible or confirmed records can be cancelled.")
        
    course_id = record.applied_course_id
    seat_type = record.allocated_seat_type
    category = record.candidate_category
    
    # 1. Cancel the student
    record.final_admission_status = AdmissionStatus.ADMISSION_CANCELLED
    record.reason_code_logs = (record.reason_code_logs or "") + " [CANCELLED by Admin]"
    
    # 2. Advance the waitlist
    # Find the best waitlisted candidate
    waitlist = db.query(AdmissionStaging).filter(
        AdmissionStaging.applied_course_id == course_id,
        AdmissionStaging.final_admission_status == AdmissionStatus.WAITLISTED
    ).order_by(AdmissionStaging.waitlist_rank.asc()).all()
    
    promoted_candidate = None
    
    if seat_type == AllocatedSeatType.RESERVED_QUOTA:
        # Try to find the next waitlisted student IN THE SAME CATEGORY
        for w in waitlist:
            if w.candidate_category == category:
                promoted_candidate = w
                break
        
        # Open Question Fallback: If no one in that quota, convert to OPEN_MERIT
        if not promoted_candidate and waitlist:
            promoted_candidate = waitlist[0]
            seat_type = AllocatedSeatType.OPEN_MERIT
    else:
        # If it was an open merit seat, just pick the top of the waitlist
        if waitlist:
            promoted_candidate = waitlist[0]
            
    # Promote the candidate
    if promoted_candidate:
        promoted_candidate.final_admission_status = AdmissionStatus.ELIGIBLE_FOR_ADMISSION
        promoted_candidate.allocated_seat_type = seat_type
        old_rank = promoted_candidate.waitlist_rank
        promoted_candidate.waitlist_rank = None
        promoted_candidate.reason_code_logs = f"Eligible via Waitlist Promotion (was Rank #{old_rank}, filled {seat_type.value} seat)"
        
        # Shift remaining waitlist ranks up
        for w in waitlist:
            if w.id != promoted_candidate.id and w.waitlist_rank and w.waitlist_rank > old_rank:
                w.waitlist_rank -= 1
                w.reason_code_logs = f"Waitlisted: Overall Rank #{w.waitlist_rank} (shifted up)"
                
    db.commit()
    
    msg = f"Cancelled admission for {record.student_name}."
    if promoted_candidate:
        msg += f" Promoted {promoted_candidate.student_name} from waitlist."
        
    return {"success": True, "message": msg}


@router.post("/commit", summary="Commit & Provision Confirmed Admissions (admin only)")
def commit_allocations(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    from app.services.admission_service import process_single_admission
    from app.models.admission_staging import AdmissionStatus
    
    confirmed = db.query(AdmissionStaging).filter(
        AdmissionStaging.final_admission_status == AdmissionStatus.ADMISSION_CONFIRMED
    ).all()
    
    if not confirmed:
        return {"success": False, "message": "No confirmed admissions to commit."}
        
    succeeded, failed = 0, 0
    errors = []
    
    for record in confirmed:
        try:
            from datetime import datetime
            
            # Generate dummy email if not provided in Excel
            email = f"{record.student_id.lower().replace('-', '')}@student.smartuniversity.edu"
            
            payload = {
                'email': email,
                'full_name': record.student_name,
                'department_name': record.course.department.name if record.course and record.course.department else 'General',
                'course_name': record.course.name if record.course else 'Unknown',
                'admission_year': datetime.utcnow().year
            }
            
            result = process_single_admission(db, payload)
            if result['success']:
                succeeded += 1
                # Mark as provisioned
                record.reason_code_logs = (record.reason_code_logs or "") + f" [PROVISIONED: {result['enrollment_no']}]"
                db.commit() # Commit the reason_code_logs update
            else:
                failed += 1
                errors.append(f"{record.student_id}: {result.get('error')}")
        except Exception as e:
            db.rollback()
            failed += 1
            errors.append(f"{record.student_id}: {str(e)}")
            
    db.commit()
    
    if succeeded == 0 and failed > 0:
        return {
            "success": False,
            "message": f"Provisioned 0 accounts. Reason: {errors[0] if errors else 'Unknown error'}",
            "errors": errors
        }
        
    return {
        "success": True,
        "message": f"Successfully provisioned {succeeded} accounts." + (f" ({failed} failed)" if failed > 0 else ""),
        "succeeded": succeeded,
        "failed": failed,
        "errors": errors
    }


@router.get("/export", summary="Export Allocation Results as Excel (admin only)")
def export_allocation(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    import pandas as pd
    
    records = db.query(AdmissionStaging).all()
    
    data = []
    for r in records:
        data.append({
            "Student_ID": r.student_id,
            "Student_Name": r.student_name,
            "Applied_Course": r.course.name if r.course else "Unknown",
            "Candidate_Category": r.candidate_category.value,
            "Class_12_Pct": r.class_12_pct,
            "Entrance_Exam_Score": r.entrance_exam_score,
            "Core_Subject_Score": r.core_subject_score,
            "Date_Of_Birth": r.date_of_birth,
            "Final_Admission_Status": r.final_admission_status.value,
            "Allocated_Seat_Type": r.allocated_seat_type.value,
            "Waitlist_Rank": r.waitlist_rank,
            "Reason_Code_Logs": r.reason_code_logs
        })
        
    df = pd.DataFrame(data)
    
    export_path = "backend/sample_data/allocation_results.xlsx"
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    df.to_excel(export_path, index=False)
    
    return FileResponse(
        export_path, 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
        filename="allocation_results.xlsx"
    )
