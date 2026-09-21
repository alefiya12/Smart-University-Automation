# Smart University Automation System

> An RPA-driven university management platform automating admission, attendance,
> result processing, fee management, and notifications using Robot Framework,
> FastAPI, and React.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Folder Structure](#folder-structure)
4. [Tech Stack](#tech-stack)
5. [Required Environment Variables](#required-environment-variables)
6. [Quick Start — Backend](#quick-start--backend)
7. [Quick Start — Frontend](#quick-start--frontend)
8. [Running RPA Bots](#running-rpa-bots)
9. [User Roles](#user-roles)
10. [Modules](#modules)
11. [API Documentation](#api-documentation)

---

## Project Overview

Smart University Automation System replaces manual university workflows with
intelligent RPA bots that process Excel data files and drive the web portal
programmatically. Three core bots handle:

| Bot | Trigger | Output |
|-----|---------|--------|
| **Admission Bot** | Approved-applicant Excel | Student accounts, PDF letters, confirmation emails |
| **Attendance Bot** | Faculty attendance Excel | Attendance records, low-attendance warning emails |
| **Results Bot** | Marks Excel | Grade calculation, SGPA/CGPA, marksheet PDFs, result emails |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Excel / Data Files                                          │
│        │                                                     │
│  Robot Framework Bots  (rpa/)                               │
│        │  thin .robot suites + Python keyword libraries      │
│        ▼                                                     │
│  FastAPI REST API  (backend/)   ◄──── React SPA (frontend/) │
│        │                                                     │
│  SQLite / SQLAlchemy  (smartuniversity.db)                   │
│        │                                                     │
│  ReportLab PDFs  →  reports/                                 │
│  smtplib emails  →  SMTP server                              │
│  Robot logs      →  logs/                                    │
└──────────────────────────────────────────────────────────────┘
```

---

## Folder Structure

```
SmartUniversityAutomation/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── config.py        # Settings from .env
│   │   ├── database.py      # SQLAlchemy engine + session
│   │   ├── models/          # ORM models (users, students, attendance…)
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── routers/         # API route handlers
│   │   ├── services/        # Business logic (auth, email, pdf…)
│   │   └── utils/           # Helpers (security, id_generator…)
│   ├── requirements.txt
│   └── .env.example
│
├── rpa/
│   ├── admission/           # admission_bot.robot + AdmissionKeywords.py
│   ├── attendance/          # attendance_bot.robot + AttendanceKeywords.py
│   ├── results/             # results_bot.robot + ResultKeywords.py
│   ├── resources/           # common.resource (shared keywords)
│   └── data/                # Input Excel files for bots
│
├── frontend/
│   ├── src/
│   │   ├── styles/          # theme.css (design tokens) + global.css
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Route-level page components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── contexts/        # React context (AuthContext…)
│   │   ├── services/        # Axios API client
│   │   └── utils/           # Formatters, validators
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── reports/                 # Robot Framework HTML reports + generated PDFs
├── logs/                    # Robot Framework execution logs
├── docs/                    # Additional documentation
├── .gitignore
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Python 3.11+, FastAPI 0.115, Uvicorn |
| Database | SQLite (dev) via SQLAlchemy 2.0 + Alembic |
| Authentication | JWT (python-jose) + bcrypt (cost ≥ 12) |
| RPA Bots | Robot Framework 7, SeleniumLibrary, Selenium 4 |
| PDF Generation | ReportLab 4 |
| Email | aiosmtplib (async SMTP) |
| Frontend | React 18, Vite 5, React Router v6 |
| HTTP Client | Axios |

---

## Required Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in every value:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | SQLAlchemy DB URL | `sqlite:///./smartuniversity.db` |
| `JWT_SECRET_KEY` | Long random string for JWT signing | `openssl rand -hex 32` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USERNAME` | Email account username | `uni@gmail.com` |
| `SMTP_PASSWORD` | Gmail App Password | (from Google Account) |
| `SMTP_FROM_EMAIL` | Sender address | `uni@gmail.com` |
| `FRONTEND_URL` | Frontend base URL (for email links) | `http://localhost:5173` |

> **Gmail users**: Create an App Password at  
> Google Account → Security → 2-Step Verification → App Passwords.

---

## Quick Start — Backend

```bash
# 1. Navigate to backend
cd backend

# 2. Create & activate virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy and configure environment
cp .env.example .env
# Edit .env with your values

# 5. Start development server
uvicorn app.main:app --reload --port 8000
```

API docs available at: **http://localhost:8000/api/docs**

---

## Quick Start — Frontend

```bash
# Requires Node.js >= 18

cd frontend
npm install
npm run dev
```

Frontend available at: **http://localhost:5173**

---

## Running RPA Bots

```bash
# Activate backend venv first (bots call the API)
source backend/.venv/bin/activate

# Run Admission Bot
robot --outputdir logs/ rpa/admission/admission_bot.robot

# Run Attendance Bot
robot --outputdir logs/ rpa/attendance/attendance_bot.robot

# Run Results Bot
robot --outputdir logs/ rpa/results/results_bot.robot
```

Bot execution logs are saved to `logs/` and linked from the Admin → Bot Logs screen.

---

## User Roles

| Role | Capabilities |
|------|-------------|
| **Admin** | Full access; trigger bots; manage students, faculty, departments; view all logs |
| **Faculty** | Record/upload attendance; upload marks; view own classes |
| **Student** | View admission status, attendance, results, fees, notifications |

> Admins are seeded manually or via the `/api/auth/seed-admin` endpoint (never self-registerable).

---

## Modules

| # | Module | Status |
|---|--------|--------|
| 1 | Student Admission Automation | Step 5 |
| 2 | Attendance Automation | Step 6 |
| 3 | Examination / Result Processing | Step 7 |
| 4 | Fee Management | Step 5+ |
| 5 | Notification System (Email/In-App) | Steps 5–7 |
| 6 | Bot Run Logs / Admin Audit | Step 8 |

---

## API Documentation

Once the backend is running, interactive API docs are at:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json
