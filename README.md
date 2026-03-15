# AgentDoc
Agentic AI Document Intelligence System for Autonomous Workflow Automation

## Alternative Titles
- Designing an Agentic AI for Intelligent Document Workflow Automation
- Autonomous Document Processing and Validation Using AI Agents
- AI-Powered End-to-End Document Intelligence Platform

## Problem Statement
Organizations process large volumes of KYC forms, invoices, receipts, insurance claims, shipping documents, loan applications, contracts, and handwritten forms. Many are scanned, handwritten, inconsistent, or poorly formatted. Manual processing introduces delays, human errors, compliance risks, and high operational costs.

AgentDoc is an agentic AI platform that automates ingestion, classification, extraction, validation, routing, exception handling, and human review with complete auditability.

## 1. Project Overview
The platform ingests and processes multi-format documents and routes each case through autonomous decision stages. It goes beyond OCR by combining:
- Multi-step agent workflow
- Structured Pydantic outputs
- Rule-based and semantic validation
- Workflow routing and exception policies
- Human-in-the-loop intervention
- Immutable audit trail

## 2. Architecture
Containerized modular architecture:
- React SPA (`Vite + React Router + Axios + React Query + Tailwind + React-PDF`)
- Django REST API backend
- CrewAI orchestrator with stage-specific agents
- Gemini model (`gemini-2.5-flash`) for reasoning and structured outputs
- MongoDB (documents, pages, extraction, validation, reviews, audit)
- MinIO object storage (original files and stage artifacts)
- SMTP notifications (MailHog local dev)

Communication model:
1. Frontend uploads through backend-issued MinIO presigned URLs.
2. Backend finalizes ingestion and runs CrewAI workflow.
3. Agent stage outputs persist to MongoDB collections.
4. Routing triggers auto-approve, exception, or human review.
5. Review actions return via API and are fully audited.

## 3. Technology Stack
- Backend: `Python + Django + DRF + CrewAI + Gemini + MongoDB + MinIO`
- Frontend: `React + Vite + React Router + Axios + React Query + Tailwind + React-PDF`
- OCR/Preprocess: `Tesseract + PaddleOCR (optional) + OpenCV`
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2` normalized to 165 dimensions
- Vector search: MongoDB Vector Search compatible + local cosine fallback
- Deployment: Docker Compose, Render, AWS

## 4. Agent System
Agents are defined in `backend/apps/agents/crew.py` and output models in `backend/apps/agents/schemas.py`.

Stages:
1. Ingestion Agent
2. Preprocessing Agent
3. Classification Agent
4. Extraction Agent
5. Validation Agent
6. Routing Agent
7. Exception Agent
8. Review Agent
9. Audit Agent

## 5. Workflow Pipeline
`Upload -> Ingestion -> Preprocessing -> Classification -> Extraction -> Validation -> Routing -> (Auto-approve | Review | Exception) -> Audit`

Branching:
- Low confidence or policy issues -> review queue
- High risk -> exception escalation
- Valid + low risk -> auto-approve

## 6. Database Design
MongoDB collections:
- `documents`
- `pages`
- `extractions`
- `validation_results`
- `reviews`
- `audit_logs`
- `users`

`documents.vector_embedding` stores normalized vectors (165 dimensions by default).

## 7. APIs
Authentication:
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `POST /api/auth/logout/`
- `GET /api/auth/me/`

Documents:
- `POST /api/documents/upload-url/` (issue MinIO presigned upload URL)
- `POST /api/documents/upload/` (multipart or presigned finalize)
- `GET /api/documents/`
- `GET /api/documents/{id}/`
- `GET /api/documents/{id}/status/`
- `GET /api/documents/{id}/extraction/`

Review/HITL:
- `GET /api/reviews/`
- `POST /api/reviews/{document_id}/action/`
- `POST /api/reviews/{review_id}/submit/`
- `POST /api/trigger-review/`

Search + Audit:
- `GET /api/search/semantic/?q=...&limit=...`
- `GET /api/audit/{document_id}/`

## 8. Frontend
Routes:
- `/login`
- `/dashboard`
- `/documents`
- `/reviews`
- `/search`

Features:
- Dashboard with periodic refresh
- Drag-and-drop upload with progress
- Side-by-side review workspace (source preview + editable JSON)
- Semantic search + status filter

## 9. Human-in-the-Loop + Notifications
When review is required:
1. Workflow triggers review creation in Django.
2. Review record is upserted in MongoDB.
3. Email is sent via Django `send_mail`.
4. Reviewer edits extracted JSON in frontend.
5. Decision/corrections are submitted via API.
6. Document, review, and audit collections are updated.

## Frontend/Backend Connection (Important)
Use these settings to keep frontend and backend connected correctly:
- Frontend API base: `VITE_API_BASE`
- Backend CORS allowlist: `DJANGO_CORS_ALLOWED_ORIGINS`
- Backend CSRF trust: `DJANGO_CSRF_TRUSTED_ORIGINS`

Examples:
- Local dev frontend: `http://localhost:5173`
- Local dev backend API base: `http://localhost:8000/api`
- Production same-origin reverse proxy: `VITE_API_BASE=/api`
- Production split domains: `VITE_API_BASE=https://api.<domain>/api`

Presigned upload note:
- Your MinIO/S3 bucket must allow browser CORS for frontend origins (`PUT`, `GET`, `HEAD`, plus `Authorization` and `Content-Type` headers).

## Local Setup
### Prerequisites
- Python 3.11+
- Node.js 20+
- MongoDB
- MinIO
- MailHog
- Gemini API key

### Environment
Copy `.env.example` to `.env` and set at least:
- `GEMINI_API_KEY`
- `AGENT_INTERNAL_TOKEN`

### Run (non-docker)
In a terminal run the backend server:
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
# Optional (recommended for local tests):
pip install -r requirements-dev.txt

python manage.py makemigrations

python manage.py migrate
python manage.py seed_demo --skip-if-present
python manage.py runserver
```

In another terminal run the frontend:
```powershell
cd frontend
npm install
npm run dev
```

In another terminal run the MinIO server:
```powershell
& "$env:USERPROFILE\go\bin\minio.exe" server C:\minio-data --console-address ":9001"
```

## Docker
```powershell
Copy-Item .env.docker.example .env.docker
docker compose up --build
```

## Demo Credentials
- Customer: `customer_demo` / `DemoPass123!`
- Reviewer: `reviewer_demo` / `DemoPass123!`

## Cloud Deployment Bundles
- Render bundle guide: [deploy/render/README.md](deploy/render/README.md)
- AWS bundle guide: [deploy/aws/README.md](deploy/aws/README.md)

### Key Render Files
- Blueprint: [render.yaml](render.yaml)
- Backend start script: [backend/render-start.sh](backend/render-start.sh)
- Render backend env template: [deploy/render/backend.env.example](deploy/render/backend.env.example)
- Render frontend env template: [deploy/render/frontend.env.example](deploy/render/frontend.env.example)

### Key AWS Files
- EC2 compose stack: [deploy/aws/docker-compose.aws.yml](deploy/aws/docker-compose.aws.yml)
- AWS env template: [deploy/aws/.env.aws.example](deploy/aws/.env.aws.example)
- ECS backend task template: [deploy/aws/ecs/backend-taskdef.json](deploy/aws/ecs/backend-taskdef.json)
- ECS frontend task template: [deploy/aws/ecs/frontend-taskdef.json](deploy/aws/ecs/frontend-taskdef.json)
- Production frontend image + proxy: [frontend/Dockerfile.prod](frontend/Dockerfile.prod), [frontend/nginx.prod.conf](frontend/nginx.prod.conf)
- Production backend image: [backend/Dockerfile.prod](backend/Dockerfile.prod)

## GitHub Actions (CI/CD)
This repo now includes up-to-date automation under `.github/`:
- CI: `.github/workflows/ci.yml`
  - Backend: installs `backend/requirements-ci.txt`, compiles source, runs `pytest`.
  - Frontend: installs dependencies and runs production build.
- CD Render: `.github/workflows/cd-render.yml`
  - Auto-triggers after successful `CI` on `main`.
  - Can also be run manually with `workflow_dispatch`.
- CD AWS ECS: `.github/workflows/cd-aws-ecs.yml`
  - Manual deployment workflow for building/pushing ECR images and deploying ECS services.
- Dependency updates: `.github/dependabot.yml` (weekly updates for GitHub Actions, pip, and npm).

### Required GitHub Secrets
Render CD:
- `RENDER_BACKEND_DEPLOY_HOOK`
- `RENDER_FRONTEND_DEPLOY_HOOK`

AWS ECS CD:
- `AWS_ROLE_TO_ASSUME` (OIDC role ARN for GitHub Actions)

### Required GitHub Repository Variables (AWS ECS)
- `AWS_REGION`
- `ECS_CLUSTER`
- `ECS_BACKEND_SERVICE`
- `ECS_FRONTEND_SERVICE`
- `ECR_BACKEND_REPOSITORY`
- `ECR_FRONTEND_REPOSITORY`

Optional variable:
- `VITE_API_BASE` (defaults to `/api` in the AWS workflow)


## Uniqueness and UX Toolkit
To make the project more efficient and user-friendly, these files are now included:
- Product differentiation and strategy: [docs/UNIQUE_VALUE_BLUEPRINT.md](docs/UNIQUE_VALUE_BLUEPRINT.md)
- Role-based usage guide: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- Fast issue resolution guide: [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- Local readiness checker: [backend/scripts/preflight_check.py](backend/scripts/preflight_check.py)
- Windows helper command: [scripts/preflight.ps1](scripts/preflight.ps1)

In-app help route:
- `/help`

Run the local preflight before demos or deployments:
```powershell
.\scripts\preflight.ps1
```
