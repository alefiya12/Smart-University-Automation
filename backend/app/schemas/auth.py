"""
schemas/auth.py — Pydantic request/response schemas for authentication endpoints.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


# ─── Register ──────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=80, pattern=r'^[a-zA-Z0-9_.-]+$')
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(..., pattern=r'^(faculty|student)$')  # admin never self-registers

    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class RegisterResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    message: str

    model_config = {"from_attributes": True}


# ─── Login ─────────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str = Field(..., description="username or email")
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    username: str
    user_id: int


# ─── Refresh ───────────────────────────────────────────────────────────────────
class RefreshRequest(BaseModel):
    refresh_token: str


# ─── Email Verification ────────────────────────────────────────────────────────
class VerifyEmailResponse(BaseModel):
    message: str


# ─── Forgot / Reset password ───────────────────────────────────────────────────
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator('new_password')
    @classmethod
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class MessageResponse(BaseModel):
    message: str


# ─── Current user ──────────────────────────────────────────────────────────────
class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    is_verified: bool

    model_config = {"from_attributes": True}
