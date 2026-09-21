import pandas as pd

# Data mimicking the new Subject-Wise Result Automation schema
data = [
    {
        "enrollment_no": "SU2026-0001",
        "subject_name": "Mathematics",
        "internal_score": 25.00,  # Valid (Pass >= 12)
        "external_score": 60.00   # Valid (Pass >= 28)
    },
    {
        "enrollment_no": "SU2026-0001",
        "subject_name": "Physics",
        "internal_score": 10.00,  # Valid score, but FAILS internal threshold (< 12)
        "external_score": 50.00   # Valid
    },
    {
        "enrollment_no": "SU2026-0003",
        "subject_name": "Mathematics",
        "internal_score": 20.00,
        "external_score": 55.00
    },
    {
        "enrollment_no": "SU2026-0003",
        "subject_name": "Physics",
        "internal_score": 22.00,
        "external_score": 65.00
    }
]

df = pd.DataFrame(data)
df.to_excel("../sample_results.xlsx", index=False)
print("sample_results.xlsx generated successfully in the root folder.")
