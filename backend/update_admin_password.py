import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models.user import User
import bcrypt

db = SessionLocal()
admin = db.query(User).filter(User.username == "admin").first()
if admin:
    hashed = bcrypt.hashpw("Admin@1234".encode('utf-8'), bcrypt.gensalt())
    admin.hashed_password = hashed.decode('utf-8')
    admin.is_verified = True
    db.commit()
    print("Admin password updated successfully to Admin@1234")
else:
    print("Admin user not found")
db.close()
