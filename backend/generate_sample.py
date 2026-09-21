import pandas as pd

data = [
    {"Student_ID": "SU2026-0001", "Date": "2026-09-20", "Physics": 1, "Mathematics": 1},
    {"Student_ID": "SU2026-0003", "Date": "2026-09-20", "Physics": 1, "Mathematics": 0},
    {"Student_ID": "SU2026-0004", "Date": "2026-09-20", "Physics": 0, "Mathematics": 1},
    {"Student_ID": "SU2026-0005", "Date": "2026-09-20", "Physics": 1, "Mathematics": 1},
    {"Student_ID": "SU2026-0006", "Date": "2026-09-20", "Physics": 0, "Mathematics": 0},
    {"Student_ID": "SU2026-0008", "Date": "2026-09-20", "Physics": 1, "Mathematics": 1}
]

df = pd.DataFrame(data)
df.to_excel("../sample_attendance.xlsx", index=False)
print("File regenerated successfully at sample_attendance.xlsx")
