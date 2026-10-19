"""
generate_complete_testing_suite.py
Generates comprehensive, database-aligned Excel test files for the Smart University Automation System.
"""
import os
import pandas as pd
from datetime import date

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Starting generation of complete testing Excel suite...")

# ==============================================================================
# 1. Fresh Bulk Admissions Upload (New, Unregistered Students)
# ==============================================================================
# Route: POST /api/admission/bulk/upload (Admin -> Admission -> Direct Bulk Upload)
# Required columns: full_name, email
# Optional columns: department_name, course_name, semester, phone, address
df_admissions = pd.DataFrame([
    {
        "full_name": "Aditya Kapoor",
        "email": "aditya.kapoor@freshadmit.edu",
        "department_name": "Computer Science and Engineering",
        "course_name": "B.Tech CSE",
        "semester": 1,
        "phone": "9811122201",
        "address": "42 Cyber City, Gurgaon, Haryana"
    },
    {
        "full_name": "Neha Verma",
        "email": "neha.verma@freshadmit.edu",
        "department_name": "Computer Science and Engineering",
        "course_name": "B.Tech CSE",
        "semester": 1,
        "phone": "9811122202",
        "address": "15 Civil Lines, Jaipur, Rajasthan"
    },
    {
        "full_name": "Karan Malhotra",
        "email": "karan.malhotra@freshadmit.edu",
        "department_name": "Information Technology",
        "course_name": "B.Tech IT",
        "semester": 1,
        "phone": "9811122203",
        "address": "88 Mall Road, Shimla, Himachal Pradesh"
    },
    {
        "full_name": "Tanvi Joshi",
        "email": "tanvi.joshi@freshadmit.edu",
        "department_name": "Information Technology",
        "course_name": "B.Tech IT",
        "semester": 1,
        "phone": "9811122204",
        "address": "24 FC Road, Pune, Maharashtra"
    },
    {
        "full_name": "Rishi Nair",
        "email": "rishi.nair@freshadmit.edu",
        "department_name": "Computer Applications",
        "course_name": "Master of Computer Applications",
        "semester": 1,
        "phone": "9811122205",
        "address": "104 Marine Drive, Kochi, Kerala"
    },
    {
        "full_name": "Simran Kaur",
        "email": "simran.kaur@freshadmit.edu",
        "department_name": "Computer Applications",
        "course_name": "Master of Computer Applications",
        "semester": 1,
        "phone": "9811122206",
        "address": "77 Sector 17, Chandigarh"
    },
    {
        "full_name": "Gaurav Saxena",
        "email": "gaurav.saxena@freshadmit.edu",
        "department_name": "Computer Science and Engineering",
        "course_name": "B.Tech CSE",
        "semester": 1,
        "phone": "9811122207",
        "address": "12 Hazratganj, Lucknow, Uttar Pradesh"
    },
    {
        "full_name": "Megha Agarwal",
        "email": "megha.agarwal@freshadmit.edu",
        "department_name": "Information Technology",
        "course_name": "B.Tech IT",
        "semester": 1,
        "phone": "9811122208",
        "address": "33 Park Street, Kolkata, West Bengal"
    }
])
path_1 = os.path.join(OUTPUT_DIR, "01_Fresh_Admissions_Bulk_Upload.xlsx")
df_admissions.to_excel(path_1, index=False)
print(f"Generated: {path_1} ({len(df_admissions)} records)")


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
path_2 = os.path.join(OUTPUT_DIR, "02_Seat_Allocation_Staging_Pool.xlsx")
df_allocation.to_excel(path_2, index=False)
print(f"Generated: {path_2} ({len(df_allocation)} records)")


# ==============================================================================
# 3. Regular Attendance Matrix Bulk Upload (Healthy 80-100% Attendance)
# ==============================================================================
# Route: POST /api/attendance/bulk/upload (Faculty -> Attendance / Admin -> Attendance)
# Course ID: 1 (MCA)
# Required columns: student_id, date, <Subject_Columns...>
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
path_3 = os.path.join(OUTPUT_DIR, "03_Regular_Attendance_Matrix.xlsx")
df_attendance_healthy.to_excel(path_3, index=False)
print(f"Generated: {path_3} ({len(df_attendance_healthy)} records)")


# ==============================================================================
# 4. Critical Low Attendance Edge Case (Triggers < 75% & < 60% Debarment Alerts)
# ==============================================================================
# Consecutive absents for SU2026-0004 & SU2026-0005 to trigger system alerts
low_att_rows = []
dates_extended = [
    "2026-10-10", "2026-10-11", "2026-10-12", "2026-10-13",
    "2026-10-14", "2026-10-15", "2026-10-16", "2026-10-17",
    "2026-10-18", "2026-10-19"
]
for i, d in enumerate(dates_extended):
    # SU2026-0004 attends only 4 out of 10 days = 40% (Critical Alert < 60%)
    low_att_rows.append({
        "student_id": "SU2026-0004",
        "date": d,
        "Physics": "Present" if i < 4 else "Absent",
        "Mathematics": "Present" if i < 4 else "Absent",
        "Geography": "Present" if i < 4 else "Absent"
    })
    # SU2026-0005 attends 7 out of 10 days = 70% (Warning Alert < 75%)
    low_att_rows.append({
        "student_id": "SU2026-0005",
        "date": d,
        "Physics": "Present" if i < 7 else "Absent",
        "Mathematics": "Present" if i < 7 else "Absent",
        "Geography": "Present" if i < 7 else "Absent"
    })

df_low_attendance = pd.DataFrame(low_att_rows)
path_4 = os.path.join(OUTPUT_DIR, "04_Critical_Low_Attendance_EdgeCase.xlsx")
df_low_attendance.to_excel(path_4, index=False)
print(f"Generated: {path_4} ({len(df_low_attendance)} records)")


# ==============================================================================
# 5. Examination Results & Marks Upload (Passing & Honors Grades)
# ==============================================================================
# Route: POST /api/results/bulk (Faculty -> Upload Marks / Admin)
# Columns: enrollment_no, subject_name, internal_score (max 30), external_score (max 70)
marks_data = [
    # Rahul Sharma (SU2026-0015)
    {"enrollment_no": "SU2026-0015", "subject_name": "Physics",     "internal_score": 28.5, "external_score": 64.0}, # Total: 92.5 -> 'O'
    {"enrollment_no": "SU2026-0015", "subject_name": "Mathematics", "internal_score": 26.0, "external_score": 58.5}, # Total: 84.5 -> 'A+'
    {"enrollment_no": "SU2026-0015", "subject_name": "Geography",   "internal_score": 27.0, "external_score": 60.0}, # Total: 87.0 -> 'A+'

    # Priya Singh (SU2026-0016)
    {"enrollment_no": "SU2026-0016", "subject_name": "Physics",     "internal_score": 24.0, "external_score": 52.0}, # Total: 76.0 -> 'A'
    {"enrollment_no": "SU2026-0016", "subject_name": "Mathematics", "internal_score": 22.5, "external_score": 48.0}, # Total: 70.5 -> 'B+'
    {"enrollment_no": "SU2026-0016", "subject_name": "Geography",   "internal_score": 25.0, "external_score": 55.0}, # Total: 80.0 -> 'A+'

    # Amit Kumar (SU2026-0017)
    {"enrollment_no": "SU2026-0017", "subject_name": "Physics",     "internal_score": 20.0, "external_score": 42.0}, # Total: 62.0 -> 'B'
    {"enrollment_no": "SU2026-0017", "subject_name": "Mathematics", "internal_score": 18.0, "external_score": 38.0}, # Total: 56.0 -> 'C'
    {"enrollment_no": "SU2026-0017", "subject_name": "Geography",   "internal_score": 21.0, "external_score": 45.0}, # Total: 66.0 -> 'B+'
]
df_marks = pd.DataFrame(marks_data)
path_5 = os.path.join(OUTPUT_DIR, "05_Semester_Marks_and_Grades.xlsx")
df_marks.to_excel(path_5, index=False)
print(f"Generated: {path_5} ({len(df_marks)} records)")


# ==============================================================================
# 6. Dual-Threshold Failure & Borderline Edge Case
# ==============================================================================
# Tests Dual-Threshold Academic Rule:
# Must score >= 40% in Internal (>= 12.0/30) AND >= 40% in External (>= 28.0/70)
dual_threshold_data = [
    # Case A: Passes total (68/100) but FAILS Internal (10.0 < 12.0) -> Must be 'F'
    {"enrollment_no": "SU2026-0018", "subject_name": "Physics",     "internal_score": 10.0, "external_score": 58.0},

    # Case B: Passes total (52/100) and passes Internal (27/30) but FAILS External (25.0 < 28.0) -> Must be 'F'
    {"enrollment_no": "SU2026-0018", "subject_name": "Mathematics", "internal_score": 27.0, "external_score": 25.0},

    # Case C: Exact Borderline Pass: Exactly 12.0 Internal + 28.0 External = 40.0 -> Must be 'P'
    {"enrollment_no": "SU2026-0018", "subject_name": "Geography",   "internal_score": 12.0, "external_score": 28.0},

    # Case D: High Distinction (O Grade)
    {"enrollment_no": "SU2026-0019", "subject_name": "Physics",     "internal_score": 29.5, "external_score": 67.5},
]
df_dual_threshold = pd.DataFrame(dual_threshold_data)
path_6 = os.path.join(OUTPUT_DIR, "06_Dual_Threshold_Failing_Marks_EdgeCase.xlsx")
df_dual_threshold.to_excel(path_6, index=False)
print(f"Generated: {path_6} ({len(df_dual_threshold)} records)")


# ==============================================================================
# 7. Validation Boundary & Security Rejection Test File
# ==============================================================================
# Tests file rejection / error notification logic
# Internal > 30, External > 70, negative numbers, missing data
validation_data = [
    {"enrollment_no": "SU2026-0020", "subject_name": "Physics",     "internal_score": 45.0, "external_score": 60.0}, # Out of bounds (internal > 30)
    {"enrollment_no": "SU2026-0020", "subject_name": "Mathematics", "internal_score": 20.0, "external_score": 85.0}, # Out of bounds (external > 70)
    {"enrollment_no": "SU2026-0020", "subject_name": "Geography",   "internal_score": -5.0, "external_score": 50.0}, # Negative score
]
df_validation = pd.DataFrame(validation_data)
path_7 = os.path.join(OUTPUT_DIR, "07_Invalid_Bounds_Validation_Test.xlsx")
df_validation.to_excel(path_7, index=False)
print(f"Generated: {path_7} ({len(df_validation)} records)")

print("\nAll 7 test Excel files successfully generated in backend/sample_data/!")
