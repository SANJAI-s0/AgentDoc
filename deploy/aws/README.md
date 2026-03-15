# AWS Deployment

This folder contains AWS-specific deployment artifacts separate from Render.

## Included Files
- [docker-compose.aws.yml](/z:/AgentDoc/deploy/aws/docker-compose.aws.yml): EC2 single-host deployment with frontend, backend, MongoDB, and MinIO
- [.env.aws.example](/z:/AgentDoc/deploy/aws/.env.aws.example): environment template for backend service
- [ecs/backend-taskdef.json](/z:/AgentDoc/deploy/aws/ecs/backend-taskdef.json): ECS Fargate backend task definition template
- [ecs/frontend-taskdef.json](/z:/AgentDoc/deploy/aws/ecs/frontend-taskdef.json): ECS Fargate frontend task definition template

## Option A: EC2 + Docker Compose
1. Copy `.env.aws.example` to `.env.aws` in this directory.
2. Fill all secrets (`GEMINI_API_KEY`, SMTP, etc.).
3. Run:
   - `cd deploy/aws`
   - `docker compose -f docker-compose.aws.yml --env-file .env.aws up -d --build`
4. Open `http://<ec2-public-ip>`.

In this mode, frontend proxies `/api` to backend internally.

## Option B: ECS Fargate
- Push `backend` and `frontend` images to ECR.
- Replace placeholders in task definitions under `ecs/`.
- Run backend and frontend as separate services behind an ALB.

## Frontend/Backend Connection Rules
- If frontend is served by same origin and proxies `/api`, set `VITE_API_BASE=/api`.
- If frontend and backend are separate domains, set full backend URL:
  - `VITE_API_BASE=https://api.<your-domain>/api`

And always align backend:
- `DJANGO_CORS_ALLOWED_ORIGINS=https://<frontend-domain>`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://<frontend-domain>`

## MinIO/S3 CORS Requirement
Presigned browser uploads will fail unless your bucket CORS allows the frontend origin for PUT, GET, and HEAD with Authorization and Content-Type headers.
