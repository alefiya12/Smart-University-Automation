import sqlite3
from app.database import engine, Base
# Import all models to ensure they are registered with Base
from app.models.user import User
from app.models.student import Student
from app.models.department import Department
from app.models.course import Course
from app.models.attendance import CourseSubject
from app.models.result import StudentMarksRecord

# 1. Drop old results table
conn = sqlite3.connect("smartuniversity.db")
c = conn.cursor()
try:
    c.execute("DROP TABLE IF EXISTS results")
except Exception as e:
    print("Error dropping results:", e)

# 2. Add columns to students
try:
    c.execute("ALTER TABLE students ADD COLUMN academic_standing VARCHAR(50) NOT NULL DEFAULT 'Good Standing'")
except Exception as e:
    print("Column academic_standing may already exist:", e)

# 3. Add columns to course_subjects
try:
    c.execute("ALTER TABLE course_subjects ADD COLUMN credits FLOAT NOT NULL DEFAULT 4.0")
except Exception as e:
    print("Column credits may already exist:", e)

conn.commit()
conn.close()

# 4. Create new tables via SQLAlchemy
Base.metadata.create_all(bind=engine)
print("Migration completed.")
