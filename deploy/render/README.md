# Render Deployment

This project is deployable on Render using the root [render.yaml](/z:/AgentDoc/render.yaml).

## Services
1. `agentdoc-backend` (Python web service)
2. `agentdoc-frontend` (Static site)

## Connection Mapping
- Frontend calls backend using `VITE_API_BASE` (must end with `/api`).
- Backend must allow frontend origin via:
  - `DJANGO_CORS_ALLOWED_ORIGINS`
  - `DJANGO_CSRF_TRUSTED_ORIGINS`

Example:
- `VITE_API_BASE=https://agentdoc-backend.onrender.com/api`
- `DJANGO_CORS_ALLOWED_ORIGINS=https://agentdoc-frontend.onrender.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://agentdoc-frontend.onrender.com`

## Required Secrets
- `MONGODB_URI`
- `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`
- `GEMINI_API_KEY`
- `AGENT_INTERNAL_TOKEN`

## Backend Start
Backend starts with:
- `python manage.py migrate --noinput`
- `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120`

## Health Check
After deploy:
- `GET https://<backend-host>/api/health/`

## MinIO Presigned Upload CORS
Because the frontend uploads directly with presigned URLs, your object storage must allow browser CORS for the frontend origin (`PUT`, `GET`, `HEAD`, plus `Authorization` and `Content-Type` headers).
