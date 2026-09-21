"""
utils/security.py — Password hashing (bcrypt cost≥12) and JWT token utilities.
"""
from datetime import datetime, timedelta
from typing import Optional
import secrets

from jose import JWTError, jwt

from app.config import settings

import bcrypt as _bcrypt

# ─── bcrypt with cost factor 12 ────────────────────────────────────────────────
_ROUNDS = 12


def hash_password(plain: str) -> str:
    return _bcrypt.hashpw(plain.encode(), _bcrypt.gensalt(rounds=_ROUNDS)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False



# ─── JWT ───────────────────────────────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expire, "type": "access"})
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload.update({"exp": expire, "type": "refresh"})
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Raises JWTError if token is invalid or expired."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def generate_secure_token(length: int = 32) -> str:
    """Cryptographically secure random URL-safe token for email verification / reset."""
    return secrets.token_urlsafe(length)


def generate_temp_password(length: int = 12) -> str:
    """Generates a readable temporary password for student accounts."""
    import string
    alphabet = string.ascii_letters + string.digits
    # Ensure at least one digit and one uppercase
    password = (
        secrets.choice(string.ascii_uppercase) +
        secrets.choice(string.digits) +
        ''.join(secrets.choice(alphabet) for _ in range(length - 2))
    )
    # Shuffle
    lst = list(password)
    secrets.SystemRandom().shuffle(lst)
    return ''.join(lst)
