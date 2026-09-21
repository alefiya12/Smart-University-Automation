from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional

_BACKEND_DIR = Path(__file__).resolve().parent.parent
_DEFAULT_DB_PATH = (_BACKEND_DIR / "smartuniversity.db").resolve()
_ROOT_DIR = _BACKEND_DIR.parent


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Smart University Automation System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database — Anchored to authoritative backend database
    DATABASE_URL: str = f"sqlite:///{_DEFAULT_DB_PATH}"

    # JWT
    JWT_SECRET_KEY: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_NAME: str = "Smart University"
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_USE_TLS: bool = True

    # Frontend URL
    FRONTEND_URL: str = "http://localhost:5173"

    # RPA / Logs
    ROBOT_LOG_DIR: str = "../logs"
    ROBOT_REPORTS_DIR: str = "../reports"

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
