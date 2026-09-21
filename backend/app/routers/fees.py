from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date

from app.database import get_db
from app.utils.deps import require_admin, require_verified
from app.models.user import User, UserRole
from app.models.fee import Fee, FeeType, FeeStatus
from app.models.student import Student

router = APIRouter(prefix="/api/fees", tags=["Fees"])


class FeeCreate(BaseModel):
    enrollment_no: str
    fee_type: FeeType
    amount: float
    description: str = None
    due_date: date = None
    semester: int = None
    academic_year: str = None


@router.get("/", summary="List all student fee records (admin)")
def get_fees(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    fees = db.query(Fee).all()
    result = []
    for f in fees:
        student = f.student
        result.append({
            "id": f.id,
            "student_name": student.full_name if student.full_name else (student.user.username if student.user else "Unknown"),
            "enrollment_no": student.enrollment_no,
            "fee_type": f.fee_type,
            "description": f.description,
            "amount": f.amount,
            "status": f.status,
            "due_date": f.due_date,
            "semester": f.semester,
            "academic_year": f.academic_year,
            "paid_date": f.paid_date,
            "receipt_no": f.receipt_no
        })
    return result


@router.get("/my", summary="Get fee records for current logged-in student")
def get_my_fees(db: Session = Depends(get_db), current_user: User = Depends(require_verified)):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        return {"success": True, "data": []}

    fees = db.query(Fee).filter(Fee.student_id == student.id).order_by(Fee.due_date.desc()).all()
    data = []
    for f in fees:
        data.append({
            "id": f.id,
            "fee_type": f.fee_type.value if hasattr(f.fee_type, 'value') else f.fee_type,
            "description": f.description,
            "amount": f.amount,
            "status": f.status.value if hasattr(f.status, 'value') else f.status,
            "due_date": f.due_date.isoformat() if f.due_date else None,
            "semester": f.semester,
            "academic_year": f.academic_year,
            "paid_date": f.paid_date.isoformat() if f.paid_date else None,
            "receipt_no": f.receipt_no
        })
    return {"success": True, "data": data}


@router.post("/", summary="Generate fee invoice (admin)")
def create_fee(data: FeeCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    student = db.query(Student).filter(Student.enrollment_no == data.enrollment_no).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    fee = Fee(
        student_id=student.id,
        fee_type=data.fee_type,
        amount=data.amount,
        description=data.description,
        due_date=data.due_date,
        semester=data.semester,
        academic_year=data.academic_year,
        status=FeeStatus.pending
    )
    db.add(fee)
    db.commit()
    db.refresh(fee)
    return {"message": "Fee invoice created successfully"}


class FeeUpdate(BaseModel):
    amount: float
    due_date: date = None
    status: FeeStatus


@router.put("/{fee_id}", summary="Update fee invoice (admin)")
def update_fee(fee_id: int, data: FeeUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    fee = db.query(Fee).filter(Fee.id == fee_id).first()
    if not fee:
        raise HTTPException(status_code=404, detail="Fee invoice not found")
        
    fee.amount = data.amount
    fee.due_date = data.due_date
    
    # If marking as paid, record the paid_date
    if data.status == FeeStatus.paid and fee.status != FeeStatus.paid:
        fee.paid_date = date.today()
    elif data.status != FeeStatus.paid:
        fee.paid_date = None
        
    fee.status = data.status
    db.commit()
    return {"message": "Fee invoice updated successfully"}


@router.delete("/{fee_id}", summary="Delete fee invoice (admin)")
def delete_fee(fee_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    fee = db.query(Fee).filter(Fee.id == fee_id).first()
    if not fee:
        raise HTTPException(status_code=404, detail="Fee invoice not found")
        
    db.delete(fee)
    db.commit()
    return {"message": "Fee invoice deleted successfully"}
