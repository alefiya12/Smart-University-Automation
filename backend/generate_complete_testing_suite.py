"""
generate_complete_testing_suite.py
Generates comprehensive, database-aligned Excel test files for the Smart University Automation System.
Outputs to:
  1. backend/sample_data/ (standard API and backend sample folder)
  2. sample_data/         (root project folder)
  3. docs/sample_data/    (documentation and legacy bot runner folder)
"""
import os
import sqlite3
import pandas as pd
from datetime import date

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_HERE, ".."))

TARGET_DIRS = [
    os.path.join(_HERE, "sample_data"),
    os.path.join(_PROJECT_ROOT, "sample_data"),
    os.path.join(_PROJECT_ROOT, "docs", "sample_data"),
]

for d in TARGET_DIRS:
    os.makedirs(d, exist_ok=True)

print("Starting generation of unified testing Excel suite across all sample_data directories...")

# Fetch existing emails from DB to ensure fresh admissions have 0 duplicates
db_path = os.path.join(_HERE, "smartuniversity.db")
existing_emails = set()
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        existing_emails = {r[0].lower() for r in c.execute("SELECT email FROM users").fetchall()}
        conn.close()
    except Exception as exc:
        print(f"Warning: Could not check existing users: {exc}")

# ==============================================================================
# 1. Fresh Bulk Admissions Upload (New, Unregistered Students)
# ==============================================================================
# Route: POST /api/admission/bulk/upload (Admin -> Admission -> Direct Bulk Upload)
# Required columns: full_name, email
# Optional columns: department_name, course_name, semester, phone, address
potential_admissions = [
    ("Aarav Roy",       "aarav.roy.test2026@university.edu",       "Computer Science and Engineering", "B.Tech CSE", 1, "9822001101", "404 Cyber City, Bengaluru, Karnataka"),
    ("Pooja Hegde",     "pooja.hegde.test2026@university.edu",     "Computer Science and Engineering", "B.Tech CSE", 1, "9822001102", "12 Brigade Road, Bengaluru, Karnataka"),
    ("Nikhil Chopra",   "nikhil.chopra.test2026@university.edu",   "Information Technology",           "B.Tech IT",  1, "9822001103", "77 Connaught Place, New Delhi"),
    ("Anjali Deshmukh", "anjali.deshmukh.test2026@university.edu", "Information Technology",           "B.Tech IT",  1, "9822001104", "55 Shivaji Nagar, Pune, Maharashtra"),
    ("Siddharth Sen",   "siddharth.sen.test2026@university.edu",   "Computer Applications",            "Master of Computer Applications", 1, "9822001105", "9 Salt Lake Sector V, Kolkata, WB"),
    ("Kavita Pillai",   "kavita.pillai.test2026@university.edu",   "Computer Applications",            "Master of Computer Applications", 1, "9822001106", "18 MG Road, Thiruvananthapuram, Kerala"),
    ("Varun Grover",    "varun.grover.test2026@university.edu",    "Computer Science and Engineering", "B.Tech CSE", 1, "9822001107", "63 Civil Lines, Nagpur, Maharashtra"),
    ("Sneha Kulkarni",  "sneha.kulkarni.test2026@university.edu",  "Information Technology",           "B.Tech IT",  1, "9822001108", "21 Law College Road, Pune, Maharashtra"),
]

fresh_admissions = []
for name, email, dept, course, sem, phone, addr in potential_admissions:
    if email.lower() not in existing_emails:
        fresh_admissions.append({
            "full_name": name,
            "email": email,
            "department_name": dept,
            "course_name": course,
            "semester": sem,
            "phone": phone,
            "address": addr
        })

df_admissions = pd.DataFrame(fresh_admissions)


# ==============================================================================
# 2. Advanced Seat Allocation Staging Pool
# ==============================================================================
# Route: POST /api/allocation/upload-staging (Admin -> Admission -> Advanced Allocation Engine)
# Required columns: Student_ID, Student_Name, Applied_Course, Candidate_Category,
#                   Class_12_Pct, Entrance_Exam_Score, Core_Subject_Score, Date_Of_Birth
df_allocation = pd.DataFrame([
    {"Student_ID": "CAND-2026-101", "Student_Name": "Aryan Saxena",    "Applied_Course": "MCA-2026", "Candidate_Category": "GEN", "Class_12_Pct": 92.5, "Entrance_Exam_Score": 96.0, "Core_Subject_Score": 95.0, "Date_Of_Birth": "2004-05-12"},
    {"Student_ID": "CAND-2026-102", "Student_Name": "Bhavna Patel",    "Applied_Course": "MCA-2026", "Candidate_Category": "OBC", "Class_12_Pct": 88.0, "Entrance_Exam_Score": 91.5, "Core_Subject_Score": 89.0, "Date_Of_Birth": "2003-11-20"},
    {"Student_ID": "CAND-2026-103", "Student_Name": "Chirag Sen",      "Applied_Course": "MCA-2026", "Candidate_Category": "GEN", "Class_12_Pct": 85.5, "Entrance_Exam_Score": 88.0, "Core_Subject_Score": 86.5, "Date_Of_Birth": "2004-02-14"},
    {"Student_ID": "CAND-2026-104", "Student_Name": "Deepika Rao",     "Applied_Course": "MCA-2026", "Candidate_Category": "SC",  "Class_12_Pct": 78.0, "Entrance_Exam_Score": 84.0, "Core_Subject_Score": 80.0, "Date_Of_Birth": "2003-08-30"},
    {"Student_ID": "CAND-2026-105", "Student_Name": "Eshan Ali",       "Applied_Course": "MCA-2026", "Candidate_Category": "EWS", "Class_12_Pct": 83.0, "Entrance_Exam_Score": 83.5, "Core_Subject_Score": 81.0, "Date_Of_Birth": "2004-04-18"},
    {"Student_ID": "CAND-2026-106", "Student_Name": "Farhan Qureshi",  "Applied_Course": "MCA-2026", "Candidate_Category": "OBC", "Class_12_Pct": 81.5, "Entrance_Exam_Score": 80.0, "Core_Subject_Score": 79.0, "Date_Of_Birth": "2003-09-05"},
    {"Student_ID": "CAND-2026-107", "Student_Name": "Gayatri Mishra",  "Applied_Course": "MCA-2026", "Candidate_Category": "GEN", "Class_12_Pct": 89.0, "Entrance_Exam_Score": 78.5, "Core_Subject_Score": 82.0, "Date_Of_Birth": "2004-07-22"},
    {"Student_ID": "CAND-2026-108", "Student_Name": "Harshit Yadav",   "Applied_Course": "MCA-2026", "Candidate_Category": "OBC", "Class_12_Pct": 76.5, "Entrance_Exam_Score": 75.0, "Core_Subject_Score": 74.0, "Date_Of_Birth": "2003-12-11"},
    {"Student_ID": "CAND-2026-109", "Student_Name": "Ishita Roy",      "Applied_Course": "MCA-2026", "Candidate_Category": "SC",  "Class_12_Pct": 72.0, "Entrance_Exam_Score": 72.0, "Core_Subject_Score": 70.0, "Date_Of_Birth": "2004-01-09"},
    {"Student_ID": "CAND-2026-110", "Student_Name": "Jatin Bhatia",    "Applied_Course": "MCA-2026", "Candidate_Category": "GEN", "Class_12_Pct": 79.0, "Entrance_Exam_Score": 70.5, "Core_Subject_Score": 72.0, "Date_Of_Birth": "2004-06-15"},
    {"Student_ID": "CAND-2026-111", "Student_Name": "Kirti Sanon",     "Applied_Course": "MCA-2026", "Candidate_Category": "ST",  "Class_12_Pct": 69.0, "Entrance_Exam_Score": 68.0, "Core_Subject_Score": 66.0, "Date_Of_Birth": "2003-03-25"},
    {"Student_ID": "CAND-2026-112", "Student_Name": "Lokesh Jain",     "Applied_Course": "MCA-2026", "Candidate_Category": "EWS", "Class_12_Pct": 74.0, "Entrance_Exam_Score": 65.0, "Core_Subject_Score": 67.0, "Date_Of_Birth": "2004-10-02"},
    {"Student_ID": "CAND-2026-113", "Student_Name": "Manish Pandey",   "Applied_Course": "MCA-2026", "Candidate_Category": "GEN", "Class_12_Pct": 71.5, "Entrance_Exam_Score": 62.0, "Core_Subject_Score": 64.0, "Date_Of_Birth": "2004-08-19"},
    {"Student_ID": "CAND-2026-114", "Student_Name": "Nandini Ghosh",   "Applied_Course": "MCA-2026", "Candidate_Category": "ST",  "Class_12_Pct": 65.0, "Entrance_Exam_Score": 58.0, "Core_Subject_Score": 60.0, "Date_Of_Birth": "2003-07-07"},
    {"Student_ID": "CAND-2026-115", "Student_Name": "Omkar Deshmukh",  "Applied_Course": "MCA-2026", "Candidate_Category": "GEN", "Class_12_Pct": 68.0, "Entrance_Exam_Score": 55.0, "Core_Subject_Score": 56.0, "Date_Of_Birth": "2004-03-31"}
])


# ==============================================================================
# 3. Regular Attendance Matrix Bulk Upload (Healthy 80-100% Attendance)
# ==============================================================================
# Route: POST /api/attendance/bulk/upload (Faculty -> Attendance / Admin -> Attendance)
dates = ["2026-10-15", "2026-10-16", "2026-10-17", "2026-10-18", "2026-10-19"]
students_mca = ["SU2026-0001", "SU2026-0002", "SU2026-0003", "SU2026-0010", "SU2026-0014"]

att_rows = []
for d in dates:
    for s in students_mca:
        att_rows.append({
            "student_id": s,
            "date": d,
            "Physics": "Present",
            "Mathematics": "Present" if d != "2026-10-17" or s != "SU2026-0002" else "Absent",
            "Geography": "Present"
        })

df_attendance_healthy = pd.DataFrame(att_rows)


# ==============================================================================
# 4. Critical Low Attendance Edge Case (Triggers < 75% & < 60% Debarment Alerts)
# ==============================================================================
low_att_rows = []
dates_extended = [
    "2026-10-10", "2026-10-11", "2026-10-12", "2026-10-13",
    "2026-10-14", "2026-10-15", "2026-10-16", "2026-10-17",
    "2026-10-18", "2026-10-19"
]
for i, d in enumerate(dates_extended):
    low_att_rows.append({
        "student_id": "SU2026-0004",
        "date": d,
        "Physics": "Present" if i < 4 else "Absent",
        "Mathematics": "Present" if i < 4 else "Absent",
        "Geography": "Present" if i < 4 else "Absent"
    })
    low_att_rows.append({
        "student_id": "SU2026-0005",
        "date": d,
        "Physics": "Present" if i < 7 else "Absent",
        "Mathematics": "Present" if i < 7 else "Absent",
        "Geography": "Present" if i < 7 else "Absent"
    })

df_low_attendance = pd.DataFrame(low_att_rows)


# ==============================================================================
# 5. Examination Results & Marks Upload (Passing & Honors Grades)
# ==============================================================================
# Route: POST /api/results/bulk (Faculty -> Upload Marks / Admin)
marks_data = [
    # SU2026-0001 (Student One)
    {"enrollment_no": "SU2026-0001", "subject_name": "Physics",     "internal_score": 28.5, "external_score": 64.0, "semester": 1, "academic_year": "2026-27"},
    {"enrollment_no": "SU2026-0001", "subject_name": "Mathematics", "internal_score": 26.0, "external_score": 58.5, "semester": 1, "academic_year": "2026-27"},
    {"enrollment_no": "SU2026-0001", "subject_name": "Geography",   "internal_score": 27.0, "external_score": 60.0, "semester": 1, "academic_year": "2026-27"},

    # SU2026-0002 (Student Two)
    {"enrollment_no": "SU2026-0002", "subject_name": "Physics",     "internal_score": 24.0, "external_score": 52.0, "semester": 1, "academic_year": "2026-27"},
    {"enrollment_no": "SU2026-0002", "subject_name": "Mathematics", "internal_score": 22.5, "external_score": 48.0, "semester": 1, "academic_year": "2026-27"},
    {"enrollment_no": "SU2026-0002", "subject_name": "Geography",   "internal_score": 25.0, "external_score": 55.0, "semester": 1, "academic_year": "2026-27"},

    # SU2026-0003 (Duplicate Student)
    {"enrollment_no": "SU2026-0003", "subject_name": "Physics",     "internal_score": 20.0, "external_score": 42.0, "semester": 1, "academic_year": "2026-27"},
    {"enrollment_no": "SU2026-0003", "subject_name": "Mathematics", "internal_score": 18.0, "external_score": 38.0, "semester": 1, "academic_year": "2026-27"},
    {"enrollment_no": "SU2026-0003", "subject_name": "Geography",   "internal_score": 21.0, "external_score": 45.0, "semester": 1, "academic_year": "2026-27"},
]
df_marks = pd.DataFrame(marks_data)


# ==============================================================================
# 6. Dual-Threshold Failure & Borderline Edge Case
# ==============================================================================
dual_threshold_data = [
    # Case A: Passes total (68/100) but FAILS Internal (10.0 < 12.0) -> Must be 'F'
    {"enrollment_no": "SU2026-0010", "subject_name": "Physics",     "internal_score": 10.0, "external_score": 58.0, "semester": 1, "academic_year": "2026-27"},
    # Case B: Passes total (52/100) and passes Internal (27/30) but FAILS External (25.0 < 28.0) -> Must be 'F'
    {"enrollment_no": "SU2026-0010", "subject_name": "Mathematics", "internal_score": 27.0, "external_score": 25.0, "semester": 1, "academic_year": "2026-27"},
    # Case C: Exact Borderline Pass: Exactly 12.0 Internal + 28.0 External = 40.0 -> Must be 'P'
    {"enrollment_no": "SU2026-0010", "subject_name": "Geography",   "internal_score": 12.0, "external_score": 28.0, "semester": 1, "academic_year": "2026-27"},
    # Case D: High Distinction (O Grade)
    {"enrollment_no": "SU2026-0014", "subject_name": "Physics",     "internal_score": 29.5, "external_score": 67.5, "semester": 1, "academic_year": "2026-27"},
]
df_dual_threshold = pd.DataFrame(dual_threshold_data)


# ==============================================================================
# 7. Validation Boundary & Security Rejection Test File
# ==============================================================================
validation_data = [
    {"enrollment_no": "SU2026-0010", "subject_name": "Physics",     "internal_score": 45.0, "external_score": 60.0}, # Out of bounds (internal > 30)
    {"enrollment_no": "SU2026-0010", "subject_name": "Mathematics", "internal_score": 20.0, "external_score": 85.0}, # Out of bounds (external > 70)
    {"enrollment_no": "SU2026-0010", "subject_name": "Geography",   "internal_score": -5.0, "external_score": 50.0}, # Negative score
]
df_validation = pd.DataFrame(validation_data)


# ==============================================================================
# Write to all target directories
# ==============================================================================
file_map = {
    # Standard numbered test suite
    "01_Fresh_Admissions_Bulk_Upload.xlsx": df_admissions,
    "02_Seat_Allocation_Staging_Pool.xlsx": df_allocation,
    "03_Regular_Attendance_Matrix.xlsx": df_attendance_healthy,
    "04_Critical_Low_Attendance_EdgeCase.xlsx": df_low_attendance,
    "05_Semester_Marks_and_Grades.xlsx": df_marks,
    "06_Dual_Threshold_Failing_Marks_EdgeCase.xlsx": df_dual_threshold,
    "07_Invalid_Bounds_Validation_Test.xlsx": df_validation,

    # Convenience aliases for root & legacy references
    "Sample_Admission.xlsx": df_admissions,
    "Sample_Allocation_Staging.xlsx": df_allocation,
    "Sample_Attendance.xlsx": df_attendance_healthy,
    "Sample_Results.xlsx": df_marks,

    # Docs aliases
    "admission_sample.xlsx": df_admissions,
    "attendance_sample.xlsx": df_attendance_healthy,
    "marks_sample.xlsx": df_marks,
}

for target_dir in TARGET_DIRS:
    for filename, df in file_map.items():
        # Only write docs aliases in docs/ or root/backend if appropriate
        out_path = os.path.join(target_dir, filename)
        df.to_excel(out_path, index=False)

print("✓ Successfully synchronized all test Excel spreadsheets across:")
for d in TARGET_DIRS:
    print(f"  ➜ {d}")
