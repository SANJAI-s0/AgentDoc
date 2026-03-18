# AgentDoc — Agentic AI Document Intelligence System

> Automate end-to-end document workflows with 5 autonomous AI agents

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django 4.2](https://img.shields.io/badge/django-4.2-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

---

## Table of Contents

- [Overview](#overview)
- [5-Agent System](#5-agent-system)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Demo Credentials](#demo-credentials)
- [Deployment](#deployment)
- [Security](#security)
- [Use Cases](#use-cases)
- [Roadmap](#roadmap)

---

## Overview

AgentDoc is a production-ready, **integrated monolithic** document intelligence platform. It combines a Django backend, a vanilla JS frontend, and a 5-agent AI pipeline into a single deployable service — no separate frontend server, no CORS complexity.

### What it solves

Organizations process massive volumes of heterogeneous documents — KYC forms, invoices, insurance claims, contracts, shipping documents. Manual handling is slow, error-prone, and expensive. AgentDoc automates the full lifecycle:

```
Upload → Classify → Extract → Validate → Route → Review → Audit
```

Every step is handled by a specialized AI agent. Low-risk documents are auto-approved in seconds. High-risk or ambiguous documents are routed to a human review queue with full context and instructions.

---

## 5-Agent System

### Agent 1 — Classification Agent

Handles ingestion, preprocessing, and document classification in a single pass.

- Validates file metadata, MIME type, and storage path
- Assesses image quality and OCR readiness (threshold: 0.7)
- Classifies document type using keyword scoring + vector similarity boost
- Confidence < 0.85 → routes to manual review

**Supported document types:** `invoice`, `receipt`, `kyc_form`, `loan_application`, `insurance_claim`, `shipping_document`, `contract`, `handwritten_form`

**Output:** document type, confidence score, quality score, next action

---

### Agent 2 — Extraction Agent

Extracts structured fields from document content.

- Runs OCR via Tesseract (primary) and PaddleOCR (secondary), picks best result
- Applies regex patterns for dates, amounts, and named fields
- Produces per-field confidence scores and evidence strings
- Identifies missing required fields per document type policy

**Output:** structured field map, confidence map, missing fields list

---

### Agent 3 — Validation Agent

Validates extracted data against business rules.

- Checks all required fields are present and non-empty
- Applies cross-field consistency checks
- Calculates a composite risk score (0.0–1.0) based on:
  - Missing fields penalty (+0.12 per field, max 0.48)
  - Low classification confidence penalty (+0.18)
  - Handwritten document penalty (+0.12)
  - Low image quality penalty (+0.14)
- Risk > policy threshold → flags for review

**Output:** validation status, risk score, check results, issues list

---

### Agent 4 — Routing Agent

Makes the final routing decision and prepares human review instructions.

| Risk Score | Destination | SLA |
|---|---|---|
| ≤ 0.6, no issues | `auto_approve` | 5 min |
| > 0.6 or issues | `operations_review` | 30 min |
| > 0.75 | `fraud_review` | 20 min |

- Generates reviewer instructions with extracted fields and confidence context
- Handles exceptions (low quality, suspected fraud, missing data)
- Assigns SLA deadlines based on priority

**Output:** queue assignment, exception record, review instructions

---

### Agent 5 — Audit Agent

Creates an immutable, searchable audit trail.

- Records full workflow timeline with per-stage status
- Generates a `searchable_summary` string for vector indexing
- Stores audit entry in MongoDB `audit_logs` collection
- Updates document vector embedding for semantic search

**Output:** audit summary, timeline, searchable metadata

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Single Django Service                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   GET /          → templates/landing.html  (GSAP landing)   │
│   GET /app/      → templates/index.html    (SPA shell)       │
│   /api/*         → Django REST Framework   (JWT auth)        │
│   /admin/        → Django Admin                              │
│   /static/*      → WhiteNoise (compressed, cached)          │
│   /media/*       → Local disk (dev) / MinIO (prod)          │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                  5-Agent Workflow Engine                     │
│                                                              │
│  Classification → Extraction → Validation → Routing → Audit │
│                                                              │
│  LangChain + Google Gemini (gemini-2.5-flash)               │
│  Falls back to deterministic simulation if API unavailable  │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                       Data Layer                             │
│                                                              │
│  SQLite          → Django auth, sessions (control plane)    │
│  MongoDB         → documents, reviews, extractions, audit   │
│  Local disk      → uploaded files (USE_LOCAL_STORAGE=1)     │
│  Vector search   → sentence-transformers embeddings         │
└──────────────────────────────────────────────────────────────┘
```

### Frontend Architecture

The frontend is a zero-build vanilla JS SPA served directly by Django:

- `templates/landing.html` — public marketing page with GSAP animations
- `templates/index.html` — authenticated app shell (hash-based routing)
- `static/js/app-bundle.js` — all app logic: Auth, Dashboard, Documents, Reviews
- `static/css/app-bundle.css` — full app styles with dark mode support

Hash routing: `#login` → `#signup` → `#dashboard` → `#documents` → `#reviews`

Authentication flow:
1. `GET /api/auth/me/` on load — restores session from `localStorage` JWT
2. `POST /api/auth/login/` — returns `access` + `refresh` tokens
3. All API calls include `Authorization: Bearer <access_token>`
4. `POST /api/auth/refresh/` — auto-called on 401 responses

---

## Technology Stack

| Layer | Technology |
|---|---|
| Web framework | Django 4.2 + Django REST Framework |
| Authentication | SimpleJWT (access + refresh tokens) |
| AI / LLM | Google Gemini 2.5 Flash via LangChain |
| OCR | Tesseract + PaddleOCR (best-of-two) |
| Image processing | OpenCV + Pillow |
| Vector embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Document database | MongoDB (local or Atlas) |
| Control plane DB | SQLite |
| File storage | Local disk (dev) / MinIO S3 (prod) |
| Static files | WhiteNoise (compressed + cached) |
| Frontend | HTML5 + CSS3 + Vanilla JS + GSAP 3.12 |
| WSGI server | Gunicorn |
| Deployment | Render (single free-tier service) |

---

## Project Structure

```
AgentDoc/
├── .env                          # Environment variables (gitignored)
├── .env.example                  # Template for .env
├── README.md
│
└── backend/
    ├── manage.py
    ├── requirements.txt
    ├── requirements-dev.txt
    ├── Dockerfile
    ├── Dockerfile.prod
    ├── entrypoint.sh
    ├── render-start.sh
    │
    ├── config/
    │   ├── settings.py           # All Django settings
    │   ├── urls.py               # Root URL config
    │   ├── wsgi.py
    │   └── asgi.py
    │
    ├── apps/
    │   ├── api/
    │   │   ├── views.py          # All REST API views (25+ endpoints)
    │   │   ├── serializers.py    # DRF serializers
    │   │   └── urls.py           # API URL patterns
    │   │
    │   ├── agents/
    │   │   ├── crew.py           # DocumentCrewFactory — workflow engine
    │   │   ├── runner.py         # execute_document_workflow entry point
    │   │   ├── workflow.py       # run_document_workflow_sync
    │   │   ├── schemas.py        # Pydantic models for all agent outputs
    │   │   ├── events.py         # Django signals for stage events
    │   │   ├── prompts/
    │   │   │   └── library.py    # All 5 agent system prompts
    │   │   └── tools/
    │   │       └── document_tools.py  # OCR, hash, policy, field extraction
    │   │
    │   ├── core/
    │   │   └── management/commands/seed_demo.py  # Demo data seeder
    │   │
    │   ├── documents/            # Document Django app (models placeholder)
    │   └── reviews/
    │       └── services.py       # trigger_review_workflow
    │
    ├── services/
    │   ├── mongodb.py            # MongoService — all DB operations
    │   ├── minio_client.py       # LocalStorageService / MinioStorageService
    │   ├── vector_search.py      # VectorSearchService — embeddings + search
    │   └── notifications.py     # send_review_email
    │
    ├── templates/
    │   ├── landing.html          # Public landing page
    │   └── index.html            # App shell (loads app-bundle.js)
    │
    ├── static/
    │   ├── css/app-bundle.css    # Full app styles
    │   ├── js/app-bundle.js      # Auth + Dashboard + Documents + Reviews
    │   ├── landing-css/landing.css
    │   └── landing-js/landing.js
    │
    └── tests/
        └── test_schemas.py
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- MongoDB running locally (`mongodb://localhost:27017`) or an Atlas URI
- Google Gemini API key (free tier available at [aistudio.google.com](https://aistudio.google.com/app/apikey))

### 1. Clone and set up environment

```bash
git clone https://github.com/yourusername/AgentDoc.git
cd AgentDoc

# Copy and edit environment file
cp .env.example .env
# Set GEMINI_API_KEY and MONGODB_URI at minimum
```

### 2. Install dependencies

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Initialize database and seed demo data

```bash
python manage.py migrate
python manage.py seed_demo
```

This creates two demo accounts:
- `customer_demo / DemoPass123!` — customer role
- `reviewer_demo / DemoPass123!` — reviewer role

### 4. Run the server

```bash
python manage.py runserver
```

| URL | Description |
|---|---|
| http://localhost:8000/ | Landing page |
| http://localhost:8000/app/ | Application |
| http://localhost:8000/api/ | REST API |
| http://localhost:8000/admin/ | Django admin |

---

## Environment Variables

All variables go in `AgentDoc/.env` (one level above `backend/`).

### Required

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `MONGODB_URI` | MongoDB connection string |
| `DJANGO_SECRET_KEY` | Django secret key (change in production) |

### Storage

| Variable | Default | Description |
|---|---|---|
| `USE_LOCAL_STORAGE` | `1` | `1` = local disk, `0` = MinIO/S3 |
| `MEDIA_ROOT` | `backend/media` | Local file storage path |
| `MINIO_ENDPOINT` | `localhost:9000` | MinIO endpoint (if USE_LOCAL_STORAGE=0) |
| `MINIO_ACCESS_KEY` | `minioadmin` | MinIO access key |
| `MINIO_SECRET_KEY` | `minioadmin` | MinIO secret key |
| `MINIO_BUCKET` | `documents` | MinIO bucket name |

### Django

| Variable | Default | Description |
|---|---|---|
| `DJANGO_DEBUG` | `0` | `1` for development |
| `DJANGO_ALLOWED_HOSTS` | `*` | Comma-separated allowed hosts |
| `DJANGO_CORS_ALLOWED_ORIGINS` | `http://localhost:8000` | Allowed CORS origins |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `http://localhost:8000` | Trusted CSRF origins |

### JWT

| Variable | Default | Description |
|---|---|---|
| `JWT_ACCESS_MINUTES` | `60` | Access token lifetime in minutes |
| `JWT_REFRESH_DAYS` | `7` | Refresh token lifetime in days |

### AI

| Variable | Default | Description |
|---|---|---|
| `GEMINI_MODEL` | `gemini/gemini-2.5-flash` | Gemini model identifier |
| `MONGODB_ENABLE_VECTOR_SEARCH` | `1` | Enable vector embeddings |
| `EMBEDDING_VECTOR_DIMENSIONS` | `165` | Embedding dimensions |

### Email (optional)

| Variable | Default | Description |
|---|---|---|
| `SMTP_HOST` | `localhost` | SMTP server host |
| `SMTP_PORT` | `1025` | SMTP server port |
| `DEFAULT_FROM_EMAIL` | `ops@agentdoc.local` | Sender address |
| `REVIEW_PORTAL_URL` | `http://localhost:8000/app/#reviews` | Link in review emails |

---

## API Reference

All endpoints are prefixed with `/api/`. Authentication uses `Authorization: Bearer <access_token>` except where noted.

### Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/auth/csrf/` | No | Set CSRF cookie |
| GET | `/api/auth/me/` | No | Get current session |
| POST | `/api/auth/signup/` | No | Register new user |
| POST | `/api/auth/login/` | No | Login, returns JWT tokens |
| POST | `/api/auth/refresh/` | No | Refresh access token |
| POST | `/api/auth/logout/` | No | Invalidate refresh token |

**Login request:**
```json
{ "username": "customer_demo", "password": "DemoPass123!" }
```

**Login response:**
```json
{
  "authenticated": true,
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>",
  "token_type": "Bearer",
  "user": {
    "username": "customer_demo",
    "email": "customer@example.com",
    "display_name": "Demo Customer",
    "role": "customer"
  }
}
```

---

### Dashboard

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/dashboard/` | Stats + recent documents |
| GET | `/api/health/` | Service health check |

---

### Documents

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/documents/` | List all documents |
| POST | `/api/documents/` | Upload + process document (multipart) |
| POST | `/api/documents/upload/` | Alias for POST /documents/ |
| POST | `/api/documents/upload-url/` | Get presigned upload URL |
| GET | `/api/documents/<id>/` | Document detail with extraction + audit |
| PATCH | `/api/documents/<id>/` | Update title / type hint |
| DELETE | `/api/documents/<id>/` | Delete document and all related data |
| GET | `/api/documents/<id>/status/` | Processing status |
| GET | `/api/documents/<id>/extraction/` | Extraction results |

**Upload request (multipart/form-data):**
```
file=<binary>
source_channel=web
title=My Invoice (optional)
document_type_hint=invoice (optional)
force_review=false (optional)
```

**Upload response:**
```json
{
  "document": {
    "document_id": "doc_abc123",
    "status": "completed",
    "document_type": "invoice",
    ...
  },
  "workflow": {
    "classification": { "document_type": "invoice", "confidence": 0.88 },
    "validation": { "risk_score": 0.24, "overall_status": "approved" },
    "routing": { "destination_queue": "auto_approve" },
    ...
  }
}
```

---

### Reviews

| Method | Endpoint | Auth Role | Description |
|---|---|---|---|
| GET | `/api/reviews/` | reviewer/admin | List review queue |
| POST | `/api/reviews/<doc_id>/action/` | reviewer/admin | Approve / reject / request changes |
| POST | `/api/reviews/<review_id>/submit/` | reviewer/admin | Submit review with corrections |
| POST | `/api/trigger-review/` | reviewer/admin | Manually trigger review |

**Review action request:**
```json
{ "decision": "approve", "comment": "All fields verified." }
```

Decisions: `approve` | `reject` | `request_changes`

---

### Search & Audit

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/search/?q=invoice&limit=10` | Full-text search |
| GET | `/api/search/semantic/?q=tax+document` | Vector semantic search |
| GET | `/api/audit/<doc_id>/` | Audit log for a document |

---

## Demo Credentials

```
Customer (upload documents):
  username: customer_demo
  password: DemoPass123!

Reviewer (review queue + approve/reject):
  username: reviewer_demo
  password: DemoPass123!
```

To create your own account, click "Sign up here" on the login page at `/app/`. New accounts default to the `customer` role. Promote to reviewer via Django admin at `/admin/`.

---

## Deployment

### Render (recommended — single free-tier service)

1. Create a free [MongoDB Atlas](https://www.mongodb.com/atlas) M0 cluster and get the connection URI
2. Get a [Gemini API key](https://aistudio.google.com/app/apikey)
3. Push the repo to GitHub
4. Create a new Web Service on Render pointing to the repo
5. Set build command: `pip install -r backend/requirements.txt && cd backend && python manage.py collectstatic --noinput && python manage.py migrate`
6. Set start command: `cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
7. Add environment variables in the Render dashboard (see [Environment Variables](#environment-variables))

Key production env vars:
```
DJANGO_DEBUG=0
DJANGO_SECRET_KEY=<random 50-char string>
DJANGO_ALLOWED_HOSTS=your-app.onrender.com
DJANGO_CORS_ALLOWED_ORIGINS=https://your-app.onrender.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-app.onrender.com
MONGODB_URI=mongodb+srv://...
GEMINI_API_KEY=...
USE_LOCAL_STORAGE=1
```

### Docker

```bash
# Development
docker-compose up --build

# Production
docker-compose -f docker-compose.prod.yml up --build
```

### Free Tier Notes

Render free services sleep after 15 minutes of inactivity. First request after sleep takes 30–60 seconds. Use [UptimeRobot](https://uptimerobot.com) to ping `/api/health/` every 14 minutes to keep it awake.

Local file storage (`USE_LOCAL_STORAGE=1`) is ephemeral on Render — files reset on redeploy. For persistence, switch to MinIO or store file content in MongoDB.

---

## Security

### Authentication
- JWT access tokens (default 60 min) + refresh tokens (default 7 days)
- Refresh tokens are blacklisted on logout
- All protected endpoints require `Authorization: Bearer <token>`
- Role-based access: `customer` (upload/view own docs), `reviewer` (review queue), `admin` (full access)

### Transport & Cookies
- HTTPS enforced in production (`SECURE_SSL_REDIRECT=True`)
- HSTS enabled with 1-year max-age
- Secure, HttpOnly, SameSite=Lax cookies
- CSRF protection on all state-changing requests

### Headers
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection` enabled

### Data
- Passwords hashed with Django's PBKDF2 + SHA256
- Secrets loaded from environment variables, never hardcoded
- MongoDB `_id` fields excluded from all API responses

---

## Use Cases

| Industry | Document Types |
|---|---|
| Banking & Finance | KYC forms, loan applications, account opening |
| Healthcare | Insurance claims, patient intake, prescriptions |
| Logistics | Shipping documents, invoices, customs declarations |
| Legal | Contracts, agreements, compliance documents |
| Accounting | Invoices, receipts, expense reports |

---

## Roadmap

- [x] 5-agent workflow (classify → extract → validate → route → audit)
- [x] JWT authentication with signup/login
- [x] Role-based access (customer / reviewer / admin)
- [x] Local file storage (no MinIO required for dev)
- [x] Semantic vector search
- [x] Document delete and update
- [x] Integrated single-service deployment
- [ ] Real LangChain agent chains (currently uses deterministic simulation)
- [ ] Batch document upload
- [ ] Webhook notifications on workflow completion
- [ ] Advanced analytics dashboard
- [ ] Multi-language OCR support
- [ ] Custom document type policies via admin UI
- [ ] Mobile-responsive review interface

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes with tests where applicable
4. Submit a pull request

Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

---

## License

MIT License — see LICENSE file for details.

---

**Version:** 1.1.0 | **Status:** Production Ready | **Last Updated:** March 2026
