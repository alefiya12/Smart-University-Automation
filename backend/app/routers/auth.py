"""
routers/auth.py — Authentication API endpoints.
All business logic delegated to services/auth_service.py.

Routes:
  POST /api/auth/register
  POST /api/auth/login
  GET  /api/auth/verify
  POST /api/auth/forgot-password
  POST /api/auth/reset-password
  POST /api/auth/refresh
  POST /api/auth/seed-admin   (one-time bootstrap, disabled after first admin exists)
  GET  /api/auth/me
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    RegisterRequest, RegisterResponse,
    LoginRequest, TokenResponse,
    RefreshRequest,
    ForgotPasswordRequest, ResetPasswordRequest,
    MessageResponse, UserOut,
)
from app.services import auth_service
from app.utils.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new faculty or student account",
)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = auth_service.register_user(
            db,
            username=body.username,
            email=body.email,
            password=body.password,
            role=body.role,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return RegisterResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role.value,
        message="Account created. Please check your email to verify your account.",
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive JWT access + refresh tokens",
)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    try:
        tokens = auth_service.login_user(db, body.username, body.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return TokenResponse(**tokens)


@router.get(
    "/verify",
    response_model=MessageResponse,
    summary="Verify email address via token sent in email",
)
def verify_email(token: str = Query(..., description="Email verification token"), db: Session = Depends(get_db)):
    try:
        auth_service.verify_email(db, token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return MessageResponse(message="Email verified successfully. You can now log in.")


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request a password reset email",
)
def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    auth_service.forgot_password(db, body.email)
    # Always return 200 to avoid email enumeration
    return MessageResponse(message="If that email is registered, a reset link has been sent.")


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password using token from email",
)
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        auth_service.reset_password(db, body.token, body.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return MessageResponse(message="Password reset successfully. You can now log in.")


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Exchange a refresh token for a new token pair",
)
def refresh_token(body: RefreshRequest, db: Session = Depends(get_db)):
    try:
        tokens = auth_service.refresh_access_token(db, body.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return TokenResponse(**tokens)


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get currently authenticated user profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post(
    "/seed-admin",
    response_model=MessageResponse,
    summary="One-time: seed the first admin account (disabled once admin exists)",
)
def seed_admin(
    username: str = Query(default="admin"),
    email: str = Query(...),
    password: str = Query(...),
    db: Session = Depends(get_db),
):
    try:
        auth_service.seed_admin(db, username, email, password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return MessageResponse(message=f"Admin account '{username}' created successfully.")
