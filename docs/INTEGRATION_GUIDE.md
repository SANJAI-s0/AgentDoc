# Integration Guide

## Frontend to Backend
Frontend client file:
- `frontend/src/api/client.js`

Behavior:
- reads `VITE_API_BASE`
- stores JWT access/refresh in local storage
- attaches `Authorization: Bearer <token>` on API calls
- auto-refreshes access token via `/api/auth/refresh/` after 401

## Backend to MongoDB
Configured in `backend/config/settings.py` via:
- `MONGODB_URI`
- `MONGODB_DB_NAME`
- `MONGODB_VECTOR_INDEX`

Collections used:
- `documents`
- `pages`
- `extractions`
- `validation_results`
- `reviews`
- `audit_logs`
- `users`

## Backend to MinIO
Configured via:
- `MINIO_ENDPOINT`
- `MINIO_ACCESS_KEY`
- `MINIO_SECRET_KEY`
- `MINIO_BUCKET`
- `MINIO_SECURE`

Upload path pattern:
- `incoming/<document_id>/<file_name>`

## Backend to CrewAI and Gemini
Configured via:
- `GEMINI_API_KEY`
- `GEMINI_MODEL`

Workflow files:
- `backend/apps/agents/crew.py`
- `backend/apps/agents/workflow.py`
- `backend/apps/agents/runner.py`

## Backend to Notifications
Notification service:
- `backend/services/notifications.py`

SMTP variables:
- `DEFAULT_FROM_EMAIL`
- `SMTP_HOST`
- `SMTP_PORT`
- `REVIEW_PORTAL_URL`

## Runtime Sequence
1. Frontend uploads via `/api/documents/upload/`.
2. Django writes file to MinIO and metadata to MongoDB.
3. CrewAI workflow runs and persists stage outputs.
4. Validation/routing determines auto-complete vs human review.
5. If review required, Django sends email and records review task.
6. Reviewer submits action via `/api/reviews/{review_id}/submit/`.
7. Django updates review/document state and appends audit logs.

## Local to Atlas Migration
Only change environment variable:
- `MONGODB_URI`

No application code change is required.
