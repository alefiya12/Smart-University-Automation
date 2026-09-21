"""
main.py — FastAPI application entry point for Smart University Automation System.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import engine, Base
import app.models  # noqa: F401 — registers all ORM models with metadata

# ─── Startup / Shutdown ──────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create all DB tables on startup (dev: simple create_all pattern)."""
    Base.metadata.create_all(bind=engine)
    yield  # application runs here
    # teardown (if needed) goes below yield


# ─── App instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    lifespan=lifespan,
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Smart University Automation System — REST API powering "
        "admission, attendance, result processing, fee management, "
        "and notification modules via RPA bots."
    ),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
from app.routers import auth as auth_router
from app.routers import admission as admission_router
from app.routers import attendance as attendance_router
from app.routers import results as results_router
from app.routers import logs as logs_router
from app.routers import faculty as faculty_router
from app.routers import departments as departments_router
from app.routers import fees as fees_router
from app.routers import dashboard as dashboard_router
from app.routers import allocation as allocation_router
from app.routers import notifications as notifications_router

app.include_router(auth_router.router)
app.include_router(admission_router.router)
app.include_router(attendance_router.router)
app.include_router(results_router.router)
app.include_router(logs_router.router)
app.include_router(faculty_router.router)
app.include_router(departments_router.router)
app.include_router(fees_router.router)
app.include_router(dashboard_router.router)
app.include_router(allocation_router.router)
app.include_router(notifications_router.router)


@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
