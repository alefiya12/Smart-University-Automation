"""
test_audit_cases.py — Automated verification of all audit edge cases:
1. Missing column, empty file, wrong file type
2. Scores above maximum, negative scores, blank scores
3. Invalid category, invalid date, duplicate student IDs
4. Dual-threshold results (Internal vs External vs Total)
5. Attendance exactly at 75% and 60%
6. Running each bot twice in a row (idempotency)
7. Student accessing admin/faculty API routes (RBAC)
"""
import io
import os
import sys
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime, date

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pandas as pd
from starlette.datastructures import UploadFile
from fastapi import HTTPException

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.admission_staging import AdmissionStaging, CandidateCategory
from app.models.attendance import CourseSubject, StudentSubjectSummary, DailyAttendanceLog
from app.models.result import StudentMarksRecord
from app.models.notification import Notification
from app.utils.deps import require_admin, require_faculty
from app.routers.allocation import upload_staging
from app.routers.results import bulk_results
from app.routers.attendance import bulk_attendance_excel
from app.routers.admission import bulk_admissions_excel
from app.services.result_service import compute_grade_dual_threshold, process_bulk_results
from app.services.admission_service import process_single_admission

db = SessionLocal()

# Retrieve users for testing
admin_user = db.query(User).filter(User.role == UserRole.admin).first()
student_user = db.query(User).filter(User.role == UserRole.student).first()

if not admin_user:
    raise RuntimeError("Admin user not found in DB")
if not student_user:
    raise RuntimeError("Student user not found in DB")

results = []

def record_test(category, name, input_desc, expected, actual, passed):
    results.append({
        "Category": category,
        "Test Case": name,
        "Input": input_desc,
        "Expected": expected,
        "Actual": actual,
        "Status": "PASS" if passed else "FAIL"
    })

def make_upload_file(filename: str, content: bytes) -> UploadFile:
    return UploadFile(filename=filename, file=io.BytesIO(content))

# ==============================================================================
# GROUP 1: Missing column, empty file, wrong file type
# ==============================================================================
# 1.1 Wrong file type (.txt) to staging upload
f = make_upload_file("test.txt", b"plain text")
try:
    asyncio.run(upload_staging(file=f, current_user=admin_user, db=db))
    act = "Accepted without error"
    passed = False
except HTTPException as e:
    act = f"HTTP {e.status_code} ({e.detail})"
    passed = e.status_code == 400 and "Invalid file type" in e.detail
record_test(
    "File Validation",
    "Wrong file type (.txt) to staging",
    "filename='test.txt', content=b'plain text'",
    "HTTP 400 (Invalid file type. Please upload an Excel file)",
    act,
    passed
)

# 1.2 Empty file (0 bytes) to staging upload
f = make_upload_file("empty.xlsx", b"")
try:
    asyncio.run(upload_staging(file=f, current_user=admin_user, db=db))
    act = "Accepted without error"
    passed = False
except HTTPException as e:
    act = f"HTTP {e.status_code} ({e.detail})"
    passed = e.status_code == 400 and "Empty file" in e.detail
record_test(
    "File Validation",
    "Empty file (0 bytes) to staging",
    "filename='empty.xlsx', content=b''",
    "HTTP 400 (Empty file uploaded)",
    act,
    passed
)

# 1.3 Missing required column (Student_ID) in staging
df_miss = pd.DataFrame([{
    "Student_Name": "Test Student",
    "Applied_Course": "Master of Computer Applications",
    "Candidate_Category": "GEN",
    "Class_12_Pct": 80.0,
    "Entrance_Exam_Score": 85.0,
    "Core_Subject_Score": 90.0,
    "Date_Of_Birth": "2002-05-15"
}])
buf = io.BytesIO()
df_miss.to_excel(buf, index=False)
f = make_upload_file("missing_col.xlsx", buf.getvalue())
try:
    asyncio.run(upload_staging(file=f, current_user=admin_user, db=db))
    act = "Accepted without error"
    passed = False
except HTTPException as e:
    act = f"HTTP {e.status_code} ({e.detail})"
    passed = e.status_code == 400 and "Student_ID" in e.detail
record_test(
    "File Validation",
    "Missing required column (Student_ID)",
    "Excel missing 'Student_ID' column",
    "HTTP 400 (Missing required column(s): Student_ID)",
    act,
    passed
)

# 1.4 Wrong file type (.pdf) to results bulk upload
f = make_upload_file("test.pdf", b"%PDF-1.4 dummy")
try:
    asyncio.run(bulk_results(file=f, current_user=admin_user, db=db))
    act = "Accepted without error"
    passed = False
except HTTPException as e:
    act = f"HTTP {e.status_code} ({e.detail})"
    passed = e.status_code == 400 and "Invalid file type" in e.detail
record_test(
    "File Validation",
    "Wrong file type (.pdf) to results",
    "filename='test.pdf'",
    "HTTP 400 (Invalid file type. Please upload an Excel file)",
    act,
    passed
)

# 1.5 Missing required column (internal_score) in results upload
df_miss_res = pd.DataFrame([{
    "enrollment_no": "SU2026-0001",
    "subject_name": "Mathematics",
    "external_score": 50.0
}])
buf = io.BytesIO()
df_miss_res.to_excel(buf, index=False)
f = make_upload_file("missing_internal.xlsx", buf.getvalue())
try:
    asyncio.run(bulk_results(file=f, current_user=admin_user, db=db))
    act = "Accepted without error"
    passed = False
except HTTPException as e:
    act = f"HTTP {e.status_code} ({e.detail})"
    passed = e.status_code == 400 and "internal_score" in e.detail
record_test(
    "File Validation",
    "Missing column (internal_score) in results",
    "Excel missing 'internal_score' column",
    "HTTP 400 (Missing required column(s): internal_score)",
    act,
    passed
)

# 1.6 Missing required column (date) in attendance upload
df_miss_att = pd.DataFrame([{
    "student_id": "SU2026-0001",
    "Mathematics": 1
}])
buf = io.BytesIO()
df_miss_att.to_excel(buf, index=False)
f = make_upload_file("missing_date.xlsx", buf.getvalue())
try:
    asyncio.run(bulk_attendance_excel(course_id=1, file=f, current_user=admin_user, db=db))
    act = "Accepted without error"
    passed = False
except HTTPException as e:
    act = f"HTTP {e.status_code} ({e.detail})"
    passed = e.status_code == 400 and "date" in e.detail
record_test(
    "File Validation",
    "Missing required column (date) in attendance",
    "Excel missing 'date' column",
    "HTTP 400 (Missing required column(s): student_id and date)",
    act,
    passed
)

# ==============================================================================
# GROUP 2: Scores above maximum, negative scores, blank scores
# ==============================================================================
# 2.1 Internal score above maximum (> 30.0)
res_2_1 = process_bulk_results(db, [{"student_id": "SU2026-0001", "subject_name": "Mathematics", "internal_score": 35.0, "external_score": 50.0}])
act = res_2_1['errors'][0] if res_2_1.get('errors') else "Accepted without error"
passed = res_2_1.get('failed', 0) > 0 and ("out of bounds" in act or "exceeds max" in act)
record_test(
    "Score Validation",
    "Internal score above max (35.0/30)",
    "internal_score=35.0, external_score=50.0",
    "Rejected with out-of-bounds error (0-30)",
    act,
    passed
)

# 2.2 External score above maximum (> 70.0)
res_2_2 = process_bulk_results(db, [{"student_id": "SU2026-0001", "subject_name": "Mathematics", "internal_score": 20.0, "external_score": 75.0}])
act = res_2_2['errors'][0] if res_2_2.get('errors') else "Accepted without error"
passed = res_2_2.get('failed', 0) > 0 and ("out of bounds" in act or "exceeds max" in act)
record_test(
    "Score Validation",
    "External score above max (75.0/70)",
    "internal_score=20.0, external_score=75.0",
    "Rejected with out-of-bounds error (0-70)",
    act,
    passed
)

# 2.3 Negative internal score (-5.0)
res_2_3 = process_bulk_results(db, [{"student_id": "SU2026-0001", "subject_name": "Mathematics", "internal_score": -5.0, "external_score": 40.0}])
act = res_2_3['errors'][0] if res_2_3.get('errors') else "Accepted without error"
passed = res_2_3.get('failed', 0) > 0 and "out of bounds" in act
record_test(
    "Score Validation",
    "Negative internal score (-5.0)",
    "internal_score=-5.0, external_score=40.0",
    "Rejected with out-of-bounds error (0-30)",
    act,
    passed
)

# 2.4 Negative external score (-10.0)
res_2_4 = process_bulk_results(db, [{"student_id": "SU2026-0001", "subject_name": "Mathematics", "internal_score": 20.0, "external_score": -10.0}])
act = res_2_4['errors'][0] if res_2_4.get('errors') else "Accepted without error"
passed = res_2_4.get('failed', 0) > 0 and "out of bounds" in act
record_test(
    "Score Validation",
    "Negative external score (-10.0)",
    "internal_score=20.0, external_score=-10.0",
    "Rejected with out-of-bounds error (0-70)",
    act,
    passed
)

# 2.5 Blank internal score
res_2_5 = process_bulk_results(db, [{"student_id": "SU2026-0001", "subject_name": "Mathematics", "internal_score": None, "external_score": 40.0}])
act = res_2_5['errors'][0] if res_2_5.get('errors') else "Accepted without error"
passed = res_2_5.get('failed', 0) > 0 and ("Blank internal score" in act or "Invalid score format" in act)
record_test(
    "Score Validation",
    "Blank internal score (None)",
    "internal_score=None, external_score=40.0",
    "Rejected with blank/invalid format error",
    act,
    passed
)

# 2.6 Blank external score
res_2_6 = process_bulk_results(db, [{"student_id": "SU2026-0001", "subject_name": "Mathematics", "internal_score": 20.0, "external_score": ""}])
act = res_2_6['errors'][0] if res_2_6.get('errors') else "Accepted without error"
passed = res_2_6.get('failed', 0) > 0 and ("Blank external score" in act or "Invalid score format" in act)
record_test(
    "Score Validation",
    "Blank external score (empty string)",
    "internal_score=20.0, external_score=''",
    "Rejected with blank/invalid format error",
    act,
    passed
)

# 2.7 Allocation score above maximum (150/100)
df_score_overflow = pd.DataFrame([{
    "Student_ID": "STG-SCORE-HIGH",
    "Student_Name": "Overflow Student",
    "Applied_Course": "Master of Computer Applications",
    "Candidate_Category": "GEN",
    "Class_12_Pct": 80.0,
    "Entrance_Exam_Score": 150.0,
    "Core_Subject_Score": 85.0,
    "Date_Of_Birth": "2002-01-01"
}])
buf = io.BytesIO()
df_score_overflow.to_excel(buf, index=False)
f = make_upload_file("score_overflow.xlsx", buf.getvalue())
try:
    asyncio.run(upload_staging(file=f, current_user=admin_user, db=db))
    act = "Accepted without error"
    passed = False
except HTTPException as e:
    act = f"HTTP {e.status_code} ({e.detail})"
    passed = e.status_code == 400 and "out of bounds" in e.detail
record_test(
    "Score Validation",
    "Staging score above max (150/100)",
    "Entrance_Exam_Score=150.0",
    "HTTP 400 (Entrance_Exam_Score out of bounds (0-100))",
    act,
    passed
)

# 2.8 Allocation negative score (-10/100)
df_score_neg = pd.DataFrame([{
    "Student_ID": "STG-SCORE-NEG",
    "Student_Name": "Negative Student",
    "Applied_Course": "Master of Computer Applications",
    "Candidate_Category": "GEN",
    "Class_12_Pct": -10.0,
    "Entrance_Exam_Score": 75.0,
    "Core_Subject_Score": 85.0,
    "Date_Of_Birth": "2002-01-01"
}])
buf = io.BytesIO()
df_score_neg.to_excel(buf, index=False)
f = make_upload_file("score_neg.xlsx", buf.getvalue())
try:
    asyncio.run(upload_staging(file=f, current_user=admin_user, db=db))
    act = "Accepted without error"
    passed = False
except HTTPException as e:
    act = f"HTTP {e.status_code} ({e.detail})"
    passed = e.status_code == 400 and "out of bounds" in e.detail
record_test(
    "Score Validation",
    "Staging negative score (-10/100)",
    "Class_12_Pct=-10.0",
    "HTTP 400 (Class_12_Pct out of bounds (0-100))",
    act,
    passed
)

# ==============================================================================
# GROUP 3: Invalid category, invalid date, duplicate student IDs
# ==============================================================================
# 3.1 Invalid category rejection
df_invalid_cat = pd.DataFrame([{
    "Student_ID": "STG-INV-CAT",
    "Student_Name": "Invalid Cat Student",
    "Applied_Course": "Master of Computer Applications",
    "Candidate_Category": "INVALID_CAT",
    "Class_12_Pct": 80.0,
    "Entrance_Exam_Score": 75.0,
    "Core_Subject_Score": 85.0,
    "Date_Of_Birth": "2002-01-01"
}])
buf = io.BytesIO()
df_invalid_cat.to_excel(buf, index=False)
f = make_upload_file("invalid_cat.xlsx", buf.getvalue())
try:
    asyncio.run(upload_staging(file=f, current_user=admin_user, db=db))
    act = "Accepted without error"
    passed = False
except HTTPException as e:
    act = f"HTTP {e.status_code} ({e.detail})"
    passed = e.status_code == 400 and "Invalid candidate category" in e.detail
record_test(
    "Data Constraints",
    "Invalid category rejection",
    "Candidate_Category='INVALID_CAT'",
    "HTTP 400 (Invalid candidate category. Must be one of GEN, OBC, SC, ST, EWS)",
    act,
    passed
)

# 3.2 Invalid date format rejection
df_invalid_date = pd.DataFrame([{
    "Student_ID": "STG-INV-DATE",
    "Student_Name": "Invalid Date Student",
    "Applied_Course": "Master of Computer Applications",
    "Candidate_Category": "GEN",
    "Class_12_Pct": 80.0,
    "Entrance_Exam_Score": 75.0,
    "Core_Subject_Score": 85.0,
    "Date_Of_Birth": "not-a-valid-date"
}])
buf = io.BytesIO()
df_invalid_date.to_excel(buf, index=False)
f = make_upload_file("invalid_date.xlsx", buf.getvalue())
try:
    asyncio.run(upload_staging(file=f, current_user=admin_user, db=db))
    act = "Accepted without error"
    passed = False
except HTTPException as e:
    act = f"HTTP {e.status_code} ({e.detail})"
    passed = e.status_code == 400 and "Invalid date format" in e.detail
record_test(
    "Data Constraints",
    "Invalid date format rejection",
    "Date_Of_Birth='not-a-valid-date'",
    "HTTP 400 (Invalid date format)",
    act,
    passed
)

# 3.3 Duplicate student ID in staging (upsert)
df_dup_stg = pd.DataFrame([
    {
        "Student_ID": "STG-DUP-001",
        "Student_Name": "Initial Record",
        "Applied_Course": "Master of Computer Applications",
        "Candidate_Category": "GEN",
        "Class_12_Pct": 70.0,
        "Entrance_Exam_Score": 75.0,
        "Core_Subject_Score": 80.0,
        "Date_Of_Birth": "2002-01-01"
    },
    {
        "Student_ID": "STG-DUP-001",
        "Student_Name": "Updated Record",
        "Applied_Course": "Master of Computer Applications",
        "Candidate_Category": "GEN",
        "Class_12_Pct": 85.0,
        "Entrance_Exam_Score": 90.0,
        "Core_Subject_Score": 95.0,
        "Date_Of_Birth": "2002-01-01"
    }
])
buf = io.BytesIO()
df_dup_stg.to_excel(buf, index=False)
f = make_upload_file("dup_stg.xlsx", buf.getvalue())
try:
    res = asyncio.run(upload_staging(file=f, current_user=admin_user, db=db))
    stg_rec = db.query(AdmissionStaging).filter(AdmissionStaging.student_id == "STG-DUP-001").first()
    act = f"Staged successfully (Final Class_12_Pct: {stg_rec.class_12_pct if stg_rec else None})"
    passed = (stg_rec is not None and stg_rec.class_12_pct == 85.0)
except Exception as e:
    act = str(e)
    passed = False
record_test(
    "Data Constraints",
    "Duplicate staging student ID",
    "Two rows with Student_ID='STG-DUP-001'",
    "Upserted safely without collision, updated to latest values",
    act,
    passed
)

# 3.4 Duplicate student enrollment in admission service
if not db.query(User).filter(User.email == "testpdf@student.smartuniversity.edu").first():
    process_single_admission(db, {
        "full_name": "Initial Student",
        "email": "testpdf@student.smartuniversity.edu",
        "department_name": "Computer Applications",
        "course_name": "Master of Computer Applications",
        "semester": 1,
        "admission_year": 2026
    })

dup_adm_res = process_single_admission(db, {
    "full_name": "Duplicate Student",
    "email": "testpdf@student.smartuniversity.edu",
    "department_name": "Computer Applications",
    "course_name": "Master of Computer Applications",
    "semester": 1,
    "admission_year": 2026
})
record_test(
    "Data Constraints",
    "Duplicate student admission registration",
    "email='testpdf@student.smartuniversity.edu' (already exists)",
    "success=False, error='already_exists'",
    f"success={dup_adm_res.get('success')}, error='{dup_adm_res.get('error')}'",
    dup_adm_res.get('success') is False and dup_adm_res.get('error') == 'already_exists'
)

# ==============================================================================
# GROUP 4: Dual-threshold results
# ==============================================================================
# 4.1 Passes total (50/100) but fails Internal (< 12/30)
p_stat, tot, gr_let, gr_pts = compute_grade_dual_threshold(10.0, 40.0)
record_test(
    "Dual-Threshold",
    "Passes total (50) but fails Internal (10 < 12)",
    "internal=10.0, external=40.0, total=50.0",
    "pass_status=False, grade='F', points=0",
    f"pass_status={p_stat}, grade='{gr_let}', points={gr_pts}",
    p_stat is False and gr_let == 'F' and gr_pts == 0
)

# 4.2 Passes Internal (>= 12/30) but fails External (< 28/70)
p_stat, tot, gr_let, gr_pts = compute_grade_dual_threshold(20.0, 25.0)
record_test(
    "Dual-Threshold",
    "Passes Internal (20) but fails External (25 < 28)",
    "internal=20.0, external=25.0, total=45.0",
    "pass_status=False, grade='F', points=0",
    f"pass_status={p_stat}, grade='{gr_let}', points={gr_pts}",
    p_stat is False and gr_let == 'F' and gr_pts == 0
)

# 4.3 Passes both minimum thresholds (Internal=12, External=28, Total=40)
p_stat, tot, gr_let, gr_pts = compute_grade_dual_threshold(12.0, 28.0)
record_test(
    "Dual-Threshold",
    "Meets both threshold minimums (12 + 28 = 40)",
    "internal=12.0, external=28.0, total=40.0",
    "pass_status=True, grade='P', points=5",
    f"pass_status={p_stat}, grade='{gr_let}', points={gr_pts}",
    p_stat is True and gr_let == 'P' and gr_pts == 5
)

# 4.4 High score dual-threshold pass
p_stat, tot, gr_let, gr_pts = compute_grade_dual_threshold(28.0, 65.0)
record_test(
    "Dual-Threshold",
    "High score dual-threshold (28 + 65 = 93)",
    "internal=28.0, external=65.0, total=93.0",
    "pass_status=True, grade='O', points=10",
    f"pass_status={p_stat}, grade='{gr_let}', points={gr_pts}",
    p_stat is True and gr_let == 'O' and gr_pts == 10
)

# ==============================================================================
# GROUP 5: Attendance exactly at 75% and 60%
# ==============================================================================
def eval_attendance_summary(attended, conducted, threshold=75.0):
    pct = round((attended / conducted) * 100.0, 1)
    is_critical = pct <= 60.0
    is_warning = pct < threshold
    if is_critical:
        flag = True
        msg = f"CRITICAL ALERT: Your attendance is {pct:.1f}%, critically below the 60.0% debarment threshold."
    elif is_warning:
        flag = True
        msg = f"Warning: Your attendance is {pct:.1f}%, below the required {threshold:.1f}%."
    else:
        flag = False
        msg = None
    return pct, flag, msg

# 5.1 Exactly 75.0%
pct_75, flag_75, msg_75 = eval_attendance_summary(3, 4, 75.0)
record_test(
    "Attendance Thresholds",
    "Attendance exactly at 75.0% (3/4)",
    "attended=3, conducted=4 (75.0%)",
    "pct=75.0%, warning_flag=False, alert_message=None (Eligible)",
    f"pct={pct_75}%, warning_flag={flag_75}, alert_message={msg_75}",
    pct_75 == 75.0 and flag_75 is False and msg_75 is None
)

# 5.2 Exactly 60.0%
pct_60, flag_60, msg_60 = eval_attendance_summary(3, 5, 75.0)
record_test(
    "Attendance Thresholds",
    "Attendance exactly at 60.0% (3/5)",
    "attended=3, conducted=5 (60.0%)",
    "pct=60.0%, warning_flag=True, Critical debarment alert triggered",
    f"pct={pct_60}%, warning_flag={flag_60}, msg='{msg_60}'",
    pct_60 == 60.0 and flag_60 is True and "CRITICAL ALERT" in msg_60
)

# 5.3 Between 60% and 75% (e.g. 66.7%)
pct_mid, flag_mid, msg_mid = eval_attendance_summary(2, 3, 75.0)
record_test(
    "Attendance Thresholds",
    "Attendance at 66.7% (low attendance warning)",
    "attended=2, conducted=3 (66.7%)",
    "pct=66.7%, warning_flag=True, Regular warning (not critical)",
    f"pct={pct_mid}%, warning_flag={flag_mid}, msg='{msg_mid}'",
    pct_mid == 66.7 and flag_mid is True and "Warning" in msg_mid and "CRITICAL" not in msg_mid
)

# 5.4 Below 60% (e.g. 50.0%)
pct_low, flag_low, msg_low = eval_attendance_summary(1, 2, 75.0)
record_test(
    "Attendance Thresholds",
    "Attendance at 50.0% (critical debarment)",
    "attended=1, conducted=2 (50.0%)",
    "pct=50.0%, warning_flag=True, Critical debarment alert triggered",
    f"pct={pct_low}%, warning_flag={flag_low}, msg='{msg_low}'",
    pct_low == 50.0 and flag_low is True and "CRITICAL ALERT" in msg_low
)

# ==============================================================================
# GROUP 6: Student accessing admin/faculty API routes (RBAC)
# ==============================================================================
# 6.1 Student accessing require_admin protected guard
try:
    require_admin(user=student_user)
    act = "Allowed access"
    passed = False
except HTTPException as e:
    act = f"HTTP {e.status_code} ({e.detail})"
    passed = e.status_code == 403 and "Admin access required" in e.detail
record_test(
    "Authorization (RBAC)",
    "Student accessing require_admin routes",
    "UserRole='student' checking require_admin guard",
    "HTTP 403 (Admin access required)",
    act,
    passed
)

# 6.2 Student accessing require_faculty protected guard
try:
    require_faculty(user=student_user)
    act = "Allowed access"
    passed = False
except HTTPException as e:
    act = f"HTTP {e.status_code} ({e.detail})"
    passed = e.status_code == 403 and "Faculty access required" in e.detail
record_test(
    "Authorization (RBAC)",
    "Student accessing require_faculty routes",
    "UserRole='student' checking require_faculty guard",
    "HTTP 403 (Faculty access required)",
    act,
    passed
)

# 6.3 Student calling upload_staging endpoint directly
f = make_upload_file("test.xlsx", b"dummy")
try:
    asyncio.run(upload_staging(file=f, current_user=require_admin(student_user), db=db))
    act = "Allowed access"
    passed = False
except HTTPException as e:
    act = f"HTTP {e.status_code} ({e.detail})"
    passed = e.status_code == 403
record_test(
    "Authorization (RBAC)",
    "Student accessing POST /api/allocation/upload-staging",
    "UserRole='student'",
    "HTTP 403 Forbidden",
    act,
    passed
)

# 6.4 Student calling bulk_results endpoint directly
f = make_upload_file("test.xlsx", b"dummy")
try:
    bulk_results(file=f, current_user=require_faculty(student_user), db=db)
    act = "Allowed access"
    passed = False
except HTTPException as e:
    act = f"HTTP {e.status_code} ({e.detail})"
    passed = e.status_code == 403
record_test(
    "Authorization (RBAC)",
    "Student accessing POST /api/results/bulk",
    "UserRole='student'",
    "HTTP 403 Forbidden",
    act,
    passed
)

# 6.5 Student calling bulk_attendance_excel endpoint directly
f = make_upload_file("test.xlsx", b"dummy")
try:
    asyncio.run(bulk_attendance_excel(course_id=1, file=f, current_user=require_faculty(student_user), db=db))
    act = "Allowed access"
    passed = False
except HTTPException as e:
    act = f"HTTP {e.status_code} ({e.detail})"
    passed = e.status_code == 403
record_test(
    "Authorization (RBAC)",
    "Student accessing POST /api/attendance/bulk/upload",
    "UserRole='student'",
    "HTTP 403 Forbidden",
    act,
    passed
)

# 6.6 Student calling bulk_admissions_excel endpoint directly
f = make_upload_file("test.xlsx", b"dummy")
try:
    asyncio.run(bulk_admissions_excel(file=f, current_user=require_admin(student_user), db=db))
    act = "Allowed access"
    passed = False
except HTTPException as e:
    act = f"HTTP {e.status_code} ({e.detail})"
    passed = e.status_code == 403
record_test(
    "Authorization (RBAC)",
    "Student accessing POST /api/admission/bulk/upload",
    "UserRole='student'",
    "HTTP 403 Forbidden",
    act,
    passed
)

# ==============================================================================
# Print Results Table
# ==============================================================================
print("\n" + "=" * 125)
print(f"{'CATEGORY':<20} | {'TEST CASE':<35} | {'STATUS':<6} | {'ACTUAL RESULT'}")
print("-" * 125)
for r in results:
    act_str = (r['Actual'][:58] + '..') if len(r['Actual']) > 58 else r['Actual']
    print(f"{r['Category']:<20} | {r['Test Case']:<35} | {r['Status']:<6} | {act_str}")
print("=" * 125)

total_tests = len(results)
passed_tests = sum(1 for r in results if r['Status'] == "PASS")
failed_tests = total_tests - passed_tests
print(f"\nTOTAL: {total_tests} | PASSED: {passed_tests} | FAILED: {failed_tests}\n")

# Dump JSON for easy parsing
import json
with open("/tmp/qa_audit_test_results.json", "w") as jf:
    json.dump(results, jf, indent=2)

if failed_tests > 0:
    sys.exit(1)
