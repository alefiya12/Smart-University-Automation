import pandas as pd
import os

# Ensure directories exist
os.makedirs("docs/sample_data", exist_ok=True)
os.makedirs("backend/sample_data", exist_ok=True)

# ==============================================================================
# 1. Direct Bulk / Bot Admission Sample (MCA Course)
# Used by: RPA Admission Bot & /api/admission/bulk/upload
# ==============================================================================
direct_admission_data = [
    {
        "full_name": "Aarav Sharma",
        "email": "aarav.sharma@student.smartuniversity.edu",
        "phone": "9876500001",
        "department_name": "Computer Science",
        "course_name": "MCA",
        "semester": 1,
        "admission_year": 2026,
        "guardian_name": "Ramesh Sharma",
        "address": "12 Lotus Enclave, Mumbai"
    },
    {
        "full_name": "Ananya Patel",
        "email": "ananya.patel@student.smartuniversity.edu",
        "phone": "9876500002",
        "department_name": "Computer Science",
        "course_name": "MCA",
        "semester": 1,
        "admission_year": 2026,
        "guardian_name": "Suresh Patel",
        "address": "45 Green Park, Pune"
    },
    {
        "full_name": "Ishaan Verma",
        "email": "ishaan.verma@student.smartuniversity.edu",
        "phone": "9876500003",
        "department_name": "Computer Science",
        "course_name": "MCA",
        "semester": 1,
        "admission_year": 2026,
        "guardian_name": "Mahesh Verma",
        "address": "88 Civil Lines, Delhi"
    },
    {
        "full_name": "Riya Gupta",
        "email": "riya.gupta@student.smartuniversity.edu",
        "phone": "9876500004",
        "department_name": "Computer Science",
        "course_name": "MCA",
        "semester": 1,
        "admission_year": 2026,
        "guardian_name": "Alok Gupta",
        "address": "77 Ring Road, Bangalore"
    },
    {
        "full_name": "Vihaan Das",
        "email": "vihaan.das@student.smartuniversity.edu",
        "phone": "9876500005",
        "department_name": "Computer Science",
        "course_name": "MCA",
        "semester": 1,
        "admission_year": 2026,
        "guardian_name": "Biplab Das",
        "address": "19 Lake View, Kolkata"
    },
    {
        "full_name": "Saanvi Iyer",
        "email": "saanvi.iyer@student.smartuniversity.edu",
        "phone": "9876500006",
        "department_name": "Computer Science",
        "course_name": "MCA",
        "semester": 1,
        "admission_year": 2026,
        "guardian_name": "Sundar Iyer",
        "address": "34 Temple Street, Chennai"
    },
    {
        "full_name": "Kabir Mehta",
        "email": "kabir.mehta@student.smartuniversity.edu",
        "phone": "9876500007",
        "department_name": "Computer Science",
        "course_name": "MCA",
        "semester": 1,
        "admission_year": 2026,
        "guardian_name": "Nitin Mehta",
        "address": "50 University Road, Ahmedabad"
    },
    {
        "full_name": "Pooja Reddy",
        "email": "pooja.reddy@student.smartuniversity.edu",
        "phone": "9876500008",
        "department_name": "Computer Science",
        "course_name": "MCA",
        "semester": 1,
        "admission_year": 2026,
        "guardian_name": "Venkatesh Reddy",
        "address": "22 Hitech City, Hyderabad"
    }
]

df_direct = pd.DataFrame(direct_admission_data)

# Save to canonical locations
path1 = "docs/sample_data/admission_sample.xlsx"
path2 = "backend/sample_data/admission_sample.xlsx"
path3 = "sample_mca_admissions.xlsx"

df_direct.to_excel(path1, index=False)
df_direct.to_excel(path2, index=False)
df_direct.to_excel(path3, index=False)

print(f"✓ Saved Direct Admission MCA sample to:")
print(f"  - {path1}")
print(f"  - {path2}")
print(f"  - {path3}")


# ==============================================================================
# 2. Quota Allocation Staging Sample (MCA Course)
# Used by: Admin Allocation Engine on /dashboard/admin/admission -> Upload Staging
# ==============================================================================
allocation_staging_data = [
    {"Student_ID": "MCA001", "Student_Name": "Aarav Sharma", "Applied_Course": "MCA", "Candidate_Category": "GEN", "Class_12_Pct": 88.5, "Entrance_Exam_Score": 142.0, "Core_Subject_Score": 85.0, "Date_Of_Birth": "2002-05-14"},
    {"Student_ID": "MCA002", "Student_Name": "Riya Gupta", "Applied_Course": "MCA", "Candidate_Category": "GEN", "Class_12_Pct": 91.2, "Entrance_Exam_Score": 139.5, "Core_Subject_Score": 88.0, "Date_Of_Birth": "2002-09-20"},
    {"Student_ID": "MCA003", "Student_Name": "Vihaan Patel", "Applied_Course": "MCA", "Candidate_Category": "OBC", "Class_12_Pct": 84.0, "Entrance_Exam_Score": 135.0, "Core_Subject_Score": 79.0, "Date_Of_Birth": "2003-01-11"},
    {"Student_ID": "MCA004", "Student_Name": "Ananya Reddy", "Applied_Course": "MCA", "Candidate_Category": "OBC", "Class_12_Pct": 82.5, "Entrance_Exam_Score": 128.5, "Core_Subject_Score": 75.0, "Date_Of_Birth": "2002-11-03"},
    {"Student_ID": "MCA005", "Student_Name": "Ishaan Das", "Applied_Course": "MCA", "Candidate_Category": "SC",  "Class_12_Pct": 76.0, "Entrance_Exam_Score": 122.0, "Core_Subject_Score": 71.0, "Date_Of_Birth": "2001-07-25"},
    {"Student_ID": "MCA006", "Student_Name": "Diya Nair", "Applied_Course": "MCA", "Candidate_Category": "SC",  "Class_12_Pct": 74.5, "Entrance_Exam_Score": 118.0, "Core_Subject_Score": 68.0, "Date_Of_Birth": "2003-04-18"},
    {"Student_ID": "MCA007", "Student_Name": "Kabir Joshi", "Applied_Course": "MCA", "Candidate_Category": "ST",  "Class_12_Pct": 70.0, "Entrance_Exam_Score": 112.5, "Core_Subject_Score": 64.0, "Date_Of_Birth": "2002-03-30"},
    {"Student_ID": "MCA008", "Student_Name": "Saanvi Rao", "Applied_Course": "MCA", "Candidate_Category": "ST",  "Class_12_Pct": 69.5, "Entrance_Exam_Score": 108.0, "Core_Subject_Score": 62.0, "Date_Of_Birth": "2001-12-15"},
    {"Student_ID": "MCA009", "Student_Name": "Aditya Verma", "Applied_Course": "MCA", "Candidate_Category": "EWS", "Class_12_Pct": 85.0, "Entrance_Exam_Score": 131.0, "Core_Subject_Score": 77.0, "Date_Of_Birth": "2002-08-08"},
    {"Student_ID": "MCA010", "Student_Name": "Meera Bhatia", "Applied_Course": "MCA", "Candidate_Category": "EWS", "Class_12_Pct": 83.5, "Entrance_Exam_Score": 126.5, "Core_Subject_Score": 74.0, "Date_Of_Birth": "2003-06-22"},
    {"Student_ID": "MCA011", "Student_Name": "Karan Malhotra", "Applied_Course": "MCA", "Candidate_Category": "GEN", "Class_12_Pct": 79.0, "Entrance_Exam_Score": 119.0, "Core_Subject_Score": 70.0, "Date_Of_Birth": "2002-10-10"},
    {"Student_ID": "MCA012", "Student_Name": "Pooja Desai", "Applied_Course": "MCA", "Candidate_Category": "GEN", "Class_12_Pct": 77.5, "Entrance_Exam_Score": 115.0, "Core_Subject_Score": 67.0, "Date_Of_Birth": "2003-02-14"},
]

df_alloc = pd.DataFrame(allocation_staging_data)

path4 = "backend/sample_data/mca_allocation_sample.xlsx"
path5 = "sample_mca_allocation_staging.xlsx"

df_alloc.to_excel(path4, index=False)
df_alloc.to_excel(path5, index=False)

print(f"✓ Saved Quota Allocation MCA sample to:")
print(f"  - {path4}")
print(f"  - {path5}")
