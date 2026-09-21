from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.department import Department
from app.models.course import Course
from app.models.attendance import CourseSubject
from app.utils.deps import require_admin
from app.models.user import User

router = APIRouter(prefix="/api/departments", tags=["Departments"])

class DepartmentCreate(BaseModel):
    name: str
    code: str

from typing import Optional

class CourseCreate(BaseModel):
    name: str
    code: str
    duration_semesters: int = 6
    total_seats: int = 60
    quota_obc: float = 27.0
    quota_sc: float = 15.0
    quota_st: float = 7.5
    quota_ews: float = 10.0
    min_class_12_pct: float = 60.0
    min_core_subject_score: float = 50.0
    relaxation_sc_st_pct: float = 5.0
    relaxation_obc_ews_pct: float = 0.0

class CourseSubjectCreate(BaseModel):
    subject_name: str
    semester: int = 1

@router.get("/")
def get_departments(db: Session = Depends(get_db)):
    depts = db.query(Department).all()
    result = []
    for d in depts:
        result.append({
            "id": d.id,
            "name": d.name,
            "code": d.code,
            "courses": [{
                "id": c.id, 
                "name": c.name, 
                "code": c.code, 
                "duration_semesters": c.duration_semesters,
                "total_seats": c.total_seats,
                "quota_obc": c.quota_obc,
                "quota_sc": c.quota_sc,
                "quota_st": c.quota_st,
                "quota_ews": c.quota_ews,
                "min_class_12_pct": c.min_class_12_pct,
                "min_core_subject_score": c.min_core_subject_score,
                "relaxation_sc_st_pct": c.relaxation_sc_st_pct,
                "relaxation_obc_ews_pct": c.relaxation_obc_ews_pct
            } for c in d.courses]
        })
    return result

@router.post("/")
def create_department(data: DepartmentCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    if db.query(Department).filter(Department.name == data.name).first():
        raise HTTPException(status_code=400, detail="Department name already exists")
    if db.query(Department).filter(Department.code == data.code).first():
        raise HTTPException(status_code=400, detail="Department code already exists")
    
    dept = Department(name=data.name, code=data.code)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept

@router.post("/{dept_id}/courses")
def create_course(dept_id: int, data: CourseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    if db.query(Course).filter(Course.code == data.code).first():
        raise HTTPException(status_code=400, detail="Course code already exists")
        
    course = Course(
        department_id=dept.id,
        name=data.name,
        code=data.code,
        duration_semesters=data.duration_semesters,
        total_seats=data.total_seats,
        quota_obc=data.quota_obc,
        quota_sc=data.quota_sc,
        quota_st=data.quota_st,
        quota_ews=data.quota_ews,
        min_class_12_pct=data.min_class_12_pct,
        min_core_subject_score=data.min_core_subject_score,
        relaxation_sc_st_pct=data.relaxation_sc_st_pct,
        relaxation_obc_ews_pct=data.relaxation_obc_ews_pct
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

@router.get("/courses/{course_id}/subjects")
def get_course_subjects(course_id: int, db: Session = Depends(get_db)):
    subjects = db.query(CourseSubject).filter(CourseSubject.course_id == course_id).all()
    return subjects

@router.post("/courses/{course_id}/subjects")
def add_course_subject(course_id: int, data: CourseSubjectCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    subject_name = data.subject_name.strip()
    if db.query(CourseSubject).filter(CourseSubject.course_id == course_id, CourseSubject.subject_name.ilike(subject_name)).first():
        raise HTTPException(status_code=400, detail="Subject already exists in this course")
        
    new_sub = CourseSubject(course_id=course_id, subject_name=subject_name.title(), semester=data.semester, total_lectures_conducted=0)
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return new_sub

@router.delete("/courses/{course_id}/subjects/{subject_id}")
def delete_course_subject(course_id: int, subject_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    sub = db.query(CourseSubject).filter(CourseSubject.id == subject_id, CourseSubject.course_id == course_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subject not found")
    db.delete(sub)
    db.commit()
    return {"success": True, "message": "Subject removed"}

@router.put("/{dept_id}")
def update_department(dept_id: int, data: DepartmentCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
        
    dept.name = data.name
    dept.code = data.code
    db.commit()
    return {"message": "Department updated"}

@router.delete("/{dept_id}")
def delete_department(dept_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
        
    db.delete(dept)
    db.commit()
    return {"message": "Department deleted"}

@router.put("/courses/{course_id}")
def update_course(course_id: int, data: CourseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    course.name = data.name
    course.code = data.code
    course.duration_semesters = data.duration_semesters
    course.total_seats = data.total_seats
    course.quota_obc = data.quota_obc
    course.quota_sc = data.quota_sc
    course.quota_st = data.quota_st
    course.quota_ews = data.quota_ews
    course.min_class_12_pct = data.min_class_12_pct
    course.min_core_subject_score = data.min_core_subject_score
    course.relaxation_sc_st_pct = data.relaxation_sc_st_pct
    course.relaxation_obc_ews_pct = data.relaxation_obc_ews_pct
    
    db.commit()
    return {"message": "Course updated"}

@router.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    db.delete(course)
    db.commit()
    return {"message": "Course deleted"}
