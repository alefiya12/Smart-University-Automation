# API Design Document — Smart University Automation System

## Base URL
All endpoints are prefixed with `/api`.

## Authentication
All protected endpoints require:
```
Authorization: Bearer <access_token>
```

## Roles
- `admin` — full access
- `faculty` — attendance + results upload
- `student` — read-only own data

---

## Auth Endpoints (Step 4)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | None | Register faculty/student |
| POST | `/api/auth/login` | None | Login → access + refresh tokens |
| GET  | `/api/auth/verify` | None | Verify email via token |
| POST | `/api/auth/forgot-password` | None | Send reset link |
| POST | `/api/auth/reset-password` | None | Reset password with token |
| POST | `/api/auth/refresh` | Refresh token | Get new access token |

## Admission Endpoints (Step 5)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/admission/bulk` | admin | Trigger bot with Excel file |
| GET  | `/api/admission/` | admin | List all applicants |
| GET  | `/api/admission/{id}` | admin/student | Get single admission |
| PATCH| `/api/admission/{id}/status` | admin | Approve/reject |

## Attendance Endpoints (Step 6)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/attendance/bulk` | admin | Trigger bot with Excel |
| POST | `/api/attendance/` | faculty | Record single attendance |
| GET  | `/api/attendance/student/{id}` | faculty/student | Get attendance for student |
| GET  | `/api/attendance/summary/{id}` | faculty/student | Percentage summary |

## Results Endpoints (Step 7)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/results/bulk` | admin | Trigger bot with Excel |
| GET  | `/api/results/student/{id}` | faculty/student | Get results |
| GET  | `/api/results/student/{id}/transcript` | student | Download marksheet PDF |
| PATCH| `/api/results/{id}/approve` | admin | Approve F-grade result |

## Bot Logs Endpoints (Step 8)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET  | `/api/logs/` | admin | List all bot run logs |
| GET  | `/api/logs/{id}` | admin | Get single log detail |

---

## Standard Response Shape

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

## Error Shape

```json
{
  "success": false,
  "error": "VALIDATION_ERROR",
  "message": "Descriptive error message",
  "details": [ ... ]
}
```

## Pagination (where applicable)

```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 150,
    "pages": 8
  }
}
```
