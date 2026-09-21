import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.student import Student
from app.models.user import User

engine = create_engine("sqlite:///backend/app/db.sqlite3")
Session = sessionmaker(bind=engine)
db = Session()

students = db.query(Student).all()
for s in students:
    if not s.full_name:
        # Give them a dummy name based on their username for now
        # Or look up their user email and use that
        user = db.query(User).filter(User.id == s.user_id).first()
        if user:
            # Create a mock name, e.g., Alice (su20260001)
            name_map = {
                "su20260001": "Alice Smith",
                "su20260002": "Bob Johnson",
                "su20260003": "Charlie Brown",
                "su20260004": "Diana Prince"
            }
            s.full_name = name_map.get(user.username, f"Student {user.username}")
db.commit()
print("Fixed student names in database!")
