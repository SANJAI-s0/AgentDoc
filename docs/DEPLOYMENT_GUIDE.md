# Deployment Guide

## Local Setup (Recommended First)

### Prerequisites
- Python 3.11+
- Node.js 20+
- MongoDB Community Edition
- MinIO
- MailHog
- Google Gemini API key

### Steps
1. Copy env file:
```powershell
Copy-Item .env.example .env
```
2. Set `GEMINI_API_KEY` in `.env`.
3. Backend:
```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo --skip-if-present
python manage.py runserver
```
4. Frontend:
```powershell
cd ..\frontend
npm install
npm run dev
```

### Local URLs
- React: `http://localhost:5173`
- Django API health: `http://localhost:8000/api/health/`
- MailHog UI: `http://localhost:8025`
- MinIO Console: `http://localhost:9001`

## Docker Compose Setup

1. Copy Docker env:
```powershell
Copy-Item .env.docker.example .env.docker
```
2. Set `GEMINI_API_KEY`.
3. Start:
```bash
docker compose up --build
```

Services:
- `django-api`
- `react-web`
- `mongodb`
- `minio`
- `createbucket`
- `mailhog`

## Hosted Deployment

### MongoDB Atlas Switch
Change only:
```env
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>/<db>?retryWrites=true&w=majority
```

No code changes required for local -> Atlas migration.

### Production Notes
- keep MinIO self-hosted and TLS-enabled (`MINIO_SECURE=1`)
- replace MailHog with real SMTP
- update CORS origins for hosted frontend
- set secure cookie and host settings in Django env variables

## Post-Deploy Checklist
- `GET /api/health/` returns `ok`
- login returns JWT and frontend can fetch `/api/dashboard/`
- upload endpoint processes sample document
- review queue and review submit endpoints work
- audit endpoint returns workflow events
