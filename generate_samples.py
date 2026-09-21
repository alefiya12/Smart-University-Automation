import pandas as pd
import os

os.makedirs('sample_data', exist_ok=True)

# Admission Data
admission_data = {
    'email': ['newstudent1@example.com', 'newstudent2@example.com'],
    'full_name': ['Alice Smith', 'Bob Johnson'],
    'department_name': ['Computer Science', 'Computer Science'],
    'course_name': ['B.Tech CSE', 'B.Tech CSE'],
    'admission_year': [2026, 2026],
    'semester': [1, 1],
    'phone': ['1234567890', '0987654321'],
    'address': ['123 Campus Dr', '456 College Ave'],
    'guardian_name': ['Mr. Smith', 'Mrs. Johnson'],
    'guardian_phone': ['1112223333', '4445556666']
}
pd.DataFrame(admission_data).to_excel('sample_data/admission_sample.xlsx', index=False)

# Attendance Data
attendance_data = {
    'enrollment_no': ['SU2026-0001', 'SU2026-0002', 'SU2026-0001', 'SU2026-0002'],
    'subject': ['CS101', 'CS101', 'CS102', 'CS102'],
    'date': ['2026-09-01', '2026-09-01', '2026-09-01', '2026-09-01'],
    'status': ['present', 'absent', 'present', 'present'],
    'semester': [1, 1, 1, 1]
}
pd.DataFrame(attendance_data).to_excel('sample_data/attendance_sample.xlsx', index=False)

# Results Data
results_data = {
    'enrollment_no': ['SU2026-0001', 'SU2026-0002', 'SU2026-0001', 'SU2026-0002'],
    'subject': ['CS101', 'CS101', 'CS102', 'CS102'],
    'marks': [85, 30, 92, 78],
    'semester': [1, 1, 1, 1],
    'credits': [4.0, 4.0, 3.0, 3.0],
    'max_marks': [100, 100, 100, 100],
    'subject_code': ['CS101-TH', 'CS101-TH', 'CS102-TH', 'CS102-TH'],
    'academic_year': ['2026-2027', '2026-2027', '2026-2027', '2026-2027']
}
pd.DataFrame(results_data).to_excel('sample_data/results_sample.xlsx', index=False)

print("Sample files generated in sample_data/ directory.")
