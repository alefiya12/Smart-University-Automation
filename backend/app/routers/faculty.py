from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.faculty import Faculty
from app.models.department import Department
from app.utils.security import hash_password, generate_temp_password
from app.utils.deps import require_admin, require_verified
from pydantic import BaseModel

router = APIRouter(prefix="/api/faculty", tags=["Faculty"])

class FacultyCreate(BaseModel):
    name: str
    email: str
    department_id: int
    employee_id: str
    designation: str = "Professor"
    phone: str = None

@router.get("/me", summary="Get current logged-in faculty profile")
def get_my_faculty_profile(db: Session = Depends(get_db), current_user: User = Depends(require_verified)):
    faculty = db.query(Faculty).filter(Faculty.user_id == current_user.id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found for this user")

    dept = faculty.department
    return {
        "success": True,
        "data": {
            "id": faculty.id,
            "employee_id": faculty.employee_id,
            "name": current_user.username,
            "email": current_user.email,
            "department": dept.name if dept else "",
            "department_id": faculty.department_id,
            "designation": faculty.designation,
            "phone": faculty.phone,
        }
    }

@router.get("/")
def get_faculty(db: Session = Depends(get_db), current_user: User = Depends(require_verified)):
    faculty_list = db.query(Faculty).all()
    result = []
    for f in faculty_list:
        user = f.user
        dept = f.department
        result.append({
            "id": f.id,
            "employee_id": f.employee_id,
            "name": user.username if user else "Unknown",
            "email": user.email if user else "",
            "department": dept.name if dept else "",
            "designation": f.designation,
            "phone": f.phone,
        })
    return result

@router.post("/")
def create_faculty(data: FacultyCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    # Check duplicate email
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(Faculty).filter(Faculty.employee_id == data.employee_id).first():
        raise HTTPException(status_code=400, detail="Employee ID already exists")

    temp_pw = generate_temp_password()
    user = User(
        username=data.name,
        email=data.email,
        hashed_password=hash_password(temp_pw),
        role=UserRole.faculty,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.flush()

    faculty = Faculty(
        user_id=user.id,
        department_id=data.department_id,
        employee_id=data.employee_id,
        designation=data.designation,
        phone=data.phone,
    )
    db.add(faculty)
    db.commit()
    return {"message": "Faculty created successfully", "temp_password": temp_pw}

class FacultyUpdate(BaseModel):
    name: str
    email: str
    department_id: int
    designation: str
    phone: str = None

@router.put("/{faculty_id}")
def update_faculty(faculty_id: int, data: FacultyUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
        
    user = faculty.user
    if user:
        user.username = data.name
        user.email = data.email
        
    faculty.department_id = data.department_id
    faculty.designation = data.designation
    faculty.phone = data.phone
    
    db.commit()
    return {"message": "Faculty updated successfully"}

@router.delete("/{faculty_id}")
def delete_faculty(faculty_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
        
    user = faculty.user
    db.delete(faculty)
    if user:
        db.delete(user)
        
    db.commit()
    return {"message": "Faculty deleted successfully"}
