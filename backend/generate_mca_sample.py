import pandas as pd
import random
from datetime import datetime, timedelta

def random_date(start, end):
    return start + timedelta(days=random.randint(0, int((end - start).days)))

start_date = datetime(2001, 1, 1)
end_date = datetime(2004, 12, 31)

first_names = ["Aarav", "Riya", "Vihaan", "Ananya", "Ishaan", "Diya", "Kabir", "Saanvi", "Aditya", "Meera", "Karan", "Pooja", "Arjun", "Neha", "Rahul", "Priya", "Vikram", "Sneha", "Rohan", "Kriti", "Amit", "Nisha", "Raj", "Shruti"]
last_names = ["Sharma", "Singh", "Patel", "Gupta", "Verma", "Reddy", "Das", "Kumar", "Joshi", "Rao", "Malhotra", "Desai", "Mehta", "Iyer", "Nair", "Kapoor", "Chopra", "Bose", "Jain", "Bhatia"]
categories = ["GEN", "OBC", "SC", "ST", "EWS"]

data = []
# Generating exactly 20 rows
for i in range(1, 21):
    category = random.choice(categories)
    # Generate scores somewhat realistic based on category (just for variety)
    if category in ["GEN", "OBC", "EWS"]:
        twelve_pct = round(random.uniform(70, 98), 1)
        exam_score = round(random.uniform(110, 150), 1)
        core_score = round(random.uniform(70, 100), 1)
    else:
        twelve_pct = round(random.uniform(60, 90), 1)
        exam_score = round(random.uniform(90, 135), 1)
        core_score = round(random.uniform(60, 90), 1)
    
    student = {
        "Student_ID": f"MCA{i:03d}",
        "Student_Name": f"{random.choice(first_names)} {random.choice(last_names)}",
        "Applied_Course": "MCA",
        "Candidate_Category": category,
        "Class_12_Pct": twelve_pct,
        "Entrance_Exam_Score": exam_score,
        "Core_Subject_Score": core_score,
        "Date_Of_Birth": random_date(start_date, end_date).strftime('%Y-%m-%d')
    }
    data.append(student)

import os
os.makedirs("backend/sample_data", exist_ok=True)

df = pd.DataFrame(data)
filepath = "backend/sample_data/mca_allocation_sample.xlsx"
df.to_excel(filepath, index=False)
print(f"File {filepath} generated successfully with {len(data)} rows.")
