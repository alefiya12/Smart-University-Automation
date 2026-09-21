"""
services/auth_service.py — Business logic for all authentication operations.
Keeps routers thin; all DB + email logic lives here.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.student import Student
from app.models.faculty import Faculty
from app.utils.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    generate_secure_token,
)
from app.services.email_service import send_verification_email, send_password_reset_email
from app.config import settings

logger = logging.getLogger(__name__)

RESET_TOKEN_TTL_HOURS = 1


# ─── Register ──────────────────────────────────────────────────────────────────
def register_user(db: Session, username: str, email: str, password: str, role: str) -> User:
    # Duplicate checks
    if db.query(User).filter(User.username == username).first():
        raise ValueError("Username already taken")
    if db.query(User).filter(User.email == email).first():
        raise ValueError("Email already registered")

    verification_token = generate_secure_token()
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=UserRole(role),
        is_active=True,
        is_verified=False,
        verification_token=verification_token,
    )
    db.add(user)
    db.flush()  # get user.id

    # Create profile row
    if role == "student":
        # Enrollment number generated during admission bot; stub for self-registered students
        from app.utils.id_generator import generate_student_id
        enroll = generate_student_id(db)
        profile = Student(user_id=user.id, enrollment_no=enroll)
        db.add(profile)
    elif role == "faculty":
        profile = Faculty(user_id=user.id)
        db.add(profile)

    db.commit()
    db.refresh(user)

    # Send verification email (non-blocking; failure doesn't abort registration)
    try:
        send_verification_email(user.email, user.username, verification_token)
    except Exception as exc:
        logger.warning("Verification email failed for %s: %s", user.email, exc)

    return user


# ─── Email Verification ────────────────────────────────────────────────────────
def verify_email(db: Session, token: str) -> User:
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise ValueError("Invalid or expired verification token")
    user.is_verified = True
    user.verification_token = None
    db.commit()
    db.refresh(user)
    return user


# ─── Login ─────────────────────────────────────────────────────────────────────
def login_user(db: Session, username_or_email: str, password: str) -> dict:
    # Accept username OR email
    user = (
        db.query(User).filter(User.username == username_or_email).first()
        or db.query(User).filter(User.email == username_or_email).first()
    )
    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Invalid credentials")
    if not user.is_active:
        raise ValueError("Account is disabled")
    if not user.is_verified:
        raise ValueError("Email not verified — check your inbox")

    token_data = {"sub": str(user.id), "role": user.role.value}
    return {
        "access_token":  create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type":    "bearer",
        "role":          user.role.value,
        "username":      user.username,
        "user_id":       user.id,
    }


# ─── Refresh ───────────────────────────────────────────────────────────────────
def refresh_access_token(db: Session, refresh_token: str) -> dict:
    from jose import JWTError
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")
        user_id = int(payload["sub"])
    except (JWTError, KeyError, TypeError):
        raise ValueError("Invalid refresh token")

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise ValueError("User not found")

    token_data = {"sub": str(user.id), "role": user.role.value}
    return {
        "access_token":  create_access_token(token_data),
        "refresh_token": create_refresh_token(token_data),
        "token_type":    "bearer",
        "role":          user.role.value,
        "username":      user.username,
        "user_id":       user.id,
    }


# ─── Forgot Password ───────────────────────────────────────────────────────────
def forgot_password(db: Session, email: str) -> bool:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Don't reveal whether email exists
        return True

    token = generate_secure_token()
    user.reset_token = token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=RESET_TOKEN_TTL_HOURS)
    db.commit()

    try:
        send_password_reset_email(user.email, user.username, token)
    except Exception as exc:
        logger.warning("Reset email failed for %s: %s", email, exc)

    return True


# ─── Reset Password ────────────────────────────────────────────────────────────
def reset_password(db: Session, token: str, new_password: str) -> User:
    user = db.query(User).filter(User.reset_token == token).first()
    if not user:
        raise ValueError("Invalid or expired reset token")
    if user.reset_token_expires and user.reset_token_expires < datetime.utcnow():
        raise ValueError("Reset token has expired")

    user.hashed_password = hash_password(new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    db.refresh(user)
    return user


# ─── Seed Admin (one-time) ────────────────────────────────────────────────────
def seed_admin(db: Session, username: str, email: str, password: str) -> User:
    if db.query(User).filter(User.role == UserRole.admin).first():
        raise ValueError("Admin already exists")
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=UserRole.admin,
        is_active=True,
        is_verified=True,   # admin is pre-verified
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
