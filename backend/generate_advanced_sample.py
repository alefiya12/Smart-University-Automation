import pandas as pd
import random
from datetime import datetime, timedelta

def random_date(start, end):
    return start + timedelta(days=random.randint(0, int((end - start).days)))

start_date = datetime(2004, 1, 1)
end_date = datetime(2006, 12, 31)

data = [
    {"Student_ID": "STG001", "Student_Name": "Aarav Sharma", "Applied_Course": "B.Tech CSE", "Candidate_Category": "GEN", "Class_12_Pct": 88.5, "Entrance_Exam_Score": 145.0, "Core_Subject_Score": 92.0, "Date_Of_Birth": random_date(start_date, end_date).strftime('%Y-%m-%d')},
    {"Student_ID": "STG002", "Student_Name": "Riya Singh", "Applied_Course": "B.Tech CSE", "Candidate_Category": "OBC", "Class_12_Pct": 75.0, "Entrance_Exam_Score": 130.5, "Core_Subject_Score": 78.0, "Date_Of_Birth": random_date(start_date, end_date).strftime('%Y-%m-%d')},
    {"Student_ID": "STG003", "Student_Name": "Vihaan Patel", "Applied_Course": "B.Tech CSE", "Candidate_Category": "SC", "Class_12_Pct": 62.0, "Entrance_Exam_Score": 110.0, "Core_Subject_Score": 55.0, "Date_Of_Birth": random_date(start_date, end_date).strftime('%Y-%m-%d')},
    {"Student_ID": "STG004", "Student_Name": "Ananya Gupta", "Applied_Course": "B.Tech CSE", "Candidate_Category": "GEN", "Class_12_Pct": 91.0, "Entrance_Exam_Score": 145.0, "Core_Subject_Score": 95.0, "Date_Of_Birth": random_date(start_date, end_date).strftime('%Y-%m-%d')},
    {"Student_ID": "STG005", "Student_Name": "Ishaan Verma", "Applied_Course": "B.Tech CSE", "Candidate_Category": "ST", "Class_12_Pct": 58.0, "Entrance_Exam_Score": 95.0, "Core_Subject_Score": 48.0, "Date_Of_Birth": random_date(start_date, end_date).strftime('%Y-%m-%d')},
    {"Student_ID": "STG006", "Student_Name": "Diya Reddy", "Applied_Course": "B.Tech CSE", "Candidate_Category": "EWS", "Class_12_Pct": 82.5, "Entrance_Exam_Score": 138.0, "Core_Subject_Score": 85.0, "Date_Of_Birth": random_date(start_date, end_date).strftime('%Y-%m-%d')},
    {"Student_ID": "STG007", "Student_Name": "Kabir Das", "Applied_Course": "B.Tech CSE", "Candidate_Category": "OBC", "Class_12_Pct": 68.0, "Entrance_Exam_Score": 115.0, "Core_Subject_Score": 65.0, "Date_Of_Birth": random_date(start_date, end_date).strftime('%Y-%m-%d')},
    {"Student_ID": "STG008", "Student_Name": "Saanvi Kumar", "Applied_Course": "B.Tech CSE", "Candidate_Category": "GEN", "Class_12_Pct": 59.5, "Entrance_Exam_Score": 140.0, "Core_Subject_Score": 88.0, "Date_Of_Birth": random_date(start_date, end_date).strftime('%Y-%m-%d')},
    {"Student_ID": "STG009", "Student_Name": "Aditya Joshi", "Applied_Course": "B.Tech CSE", "Candidate_Category": "GEN", "Class_12_Pct": 86.0, "Entrance_Exam_Score": 145.0, "Core_Subject_Score": 92.0, "Date_Of_Birth": random_date(start_date, end_date).strftime('%Y-%m-%d')},
    {"Student_ID": "STG010", "Student_Name": "Meera Rao", "Applied_Course": "B.Tech CSE", "Candidate_Category": "SC", "Class_12_Pct": 78.0, "Entrance_Exam_Score": 122.5, "Core_Subject_Score": 72.0, "Date_Of_Birth": random_date(start_date, end_date).strftime('%Y-%m-%d')},
    {"Student_ID": "STG011", "Student_Name": "Karan Malhotra", "Applied_Course": "B.Tech CSE", "Candidate_Category": "GEN", "Class_12_Pct": 95.0, "Entrance_Exam_Score": 148.0, "Core_Subject_Score": 98.0, "Date_Of_Birth": random_date(start_date, end_date).strftime('%Y-%m-%d')},
    {"Student_ID": "STG012", "Student_Name": "Pooja Desai", "Applied_Course": "B.Tech CSE", "Candidate_Category": "OBC", "Class_12_Pct": 88.0, "Entrance_Exam_Score": 135.0, "Core_Subject_Score": 90.0, "Date_Of_Birth": random_date(start_date, end_date).strftime('%Y-%m-%d')}
]

df = pd.DataFrame(data)
df.to_excel("backend/sample_data/advanced_allocation_sample.xlsx", index=False)
print("File backend/sample_data/advanced_allocation_sample.xlsx generated successfully.")
