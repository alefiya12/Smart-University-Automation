"""
schemas/admission.py — Pydantic schemas for admission endpoints.
"""
from typing import Optional, List
from datetime import date
from pydantic import BaseModel, EmailStr, Field


class AdmissionRecordIn(BaseModel):
    """Single student admission record (from Excel row or API body)."""
    full_name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=15)
    date_of_birth: Optional[date] = None
    department_name: str
    course_name: str
    semester: int = Field(default=1, ge=1, le=12)
    address: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    admission_year: Optional[int] = None


class AdmissionRecordOut(BaseModel):
    id: int
    enrollment_no: str
    full_name: str
    email: str
    department: Optional[str]
    course: Optional[str]
    semester: int
    is_admitted: int   # 0=pending, 1=admitted, 2=rejected
    admission_year: Optional[int]

    model_config = {"from_attributes": True}


class BulkAdmissionRequest(BaseModel):
    """Trigger the admission bot for a list of students."""
    records: List[AdmissionRecordIn]


class BulkAdmissionResponse(BaseModel):
    bot_run_id: int
    total: int
    succeeded: int
    failed: int
    errors: List[str] = []
    message: str


class AdmissionStatusUpdate(BaseModel):
    is_admitted: int = Field(..., ge=0, le=2)  # 0/1/2
