import pandas as pd
import random
import os

os.makedirs('sample_data', exist_ok=True)

# 1. Admission Sample
categories = ['GEN', 'SC', 'ST', 'OBC', 'EWS']
admission_data = []

for i in range(1, 21):
    cat = random.choice(categories)
    # Generate some high scores to ensure some get in, some low to get rejected or waitlisted
    if i <= 5: 
        # Very high scores (top rankers)
        e_score = random.randint(90, 99)
        c_score = random.randint(85, 95)
        m_score = random.randint(85, 95)
    elif i <= 15:
        # Average
        e_score = random.randint(60, 89)
        c_score = random.randint(60, 84)
        m_score = random.randint(60, 84)
    else:
        # Low scores (might get rejected based on criteria)
        e_score = random.randint(40, 55)
        c_score = random.randint(40, 55)
        m_score = random.randint(40, 55)

    admission_data.append({
        'Student_ID': f'APP-10{i:02d}',
        'Student_Name': f'Student {i}',
        'Applied_Course': 'MCA',
        'Candidate_Category': cat,
        'Class_12_Pct': m_score,
        'Entrance_Exam_Score': e_score,
        'Core_Subject_Score': c_score,
        'Date_Of_Birth': '2000-05-15'
    })

df_adm = pd.DataFrame(admission_data)
df_adm.to_excel('sample_data/Sample_Admission.xlsx', index=False)


# 2. Attendance Sample (for 10 accepted students)
attendance_data = []
dates = ['2026-09-01', '2026-09-02', '2026-09-03']
for i in range(1, 11):
    sid = f'SU2026-{i:04d}'
    for d in dates:
        attendance_data.append({
            'student_id': sid,
            'date': d,
            'Physics': random.choice([1, 1, 1, 0]),     # High chance of present
            'Mathematics': random.choice([1, 1, 1, 0]),
            'Geography': random.choice([1, 1, 1, 0])
        })

df_att = pd.DataFrame(attendance_data)
df_att.to_excel('sample_data/Sample_Attendance.xlsx', index=False)


# 3. Results Sample (for 10 accepted students)
results_data = []
subjects = ['Physics', 'Mathematics', 'Geography']

for i in range(1, 11):
    sid = f'SU2026-{i:04d}'
    for sub in subjects:
        if i == 10:
            # Let's make student 10 fail in one subject intentionally to test Backlog logic
            if sub == 'Physics':
                internal = random.randint(5, 10)  # Below 12
                external = random.randint(30, 45)
            else:
                internal = random.randint(15, 25)
                external = random.randint(35, 60)
        else:
            internal = random.randint(15, 29)
            external = random.randint(35, 68)
            
        results_data.append({
            'student_id': sid,
            'subject_name': sub,
            'internal_score': internal,
            'external_score': external
        })

df_res = pd.DataFrame(results_data)
df_res.to_excel('sample_data/Sample_Results.xlsx', index=False)

print("Sample files generated successfully!")
