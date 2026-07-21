import sys
sys.path.insert(0, ".")

from app.config import settings
from app.database import SessionLocal
from app.auth import hash_password
from app import models

if __name__ == "__main__":
    email = "c.c.sanchez@gmail.com"
    new_pass = sys.argv[1] if len(sys.argv) > 1 else None
    if not new_pass:
        print("Usage: python reset_password.py <new_password>")
        sys.exit(1)

    db = SessionLocal()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        print(f"User {email} not found")
        sys.exit(1)

    user.hashed_password = hash_password(new_pass)
    db.commit()
    print(f"Password updated for {user.username} ({email})")
