# Project Structure

## Root
- `README.md`: primary project guide
- `.env.example`: normal local environment template
- `.env.docker.example`: Docker environment template
- `docker-compose.yml`: local multi-service runtime
- `docs/`: project documentation set

## Backend
- `backend/config/`: Django settings, URL routing, ASGI, and WSGI
- `backend/apps/api/`: API views, serializers, routes
- `backend/apps/agents/`: CrewAI schemas, prompts, tools, crew, workflow, and runner
- `backend/apps/reviews/`: review-related logic
- `backend/apps/core/management/commands/`: bootstrap and seed commands
- `backend/services/`: MongoDB, MinIO, search, notifications
- `backend/scripts/`: startup helpers like service readiness checks

## Frontend
- `frontend/src/App.jsx`: application shell and page routing
- `frontend/src/api/client.js`: backend API integration
- `frontend/src/pages/`: dashboard, documents, reviews, search
- `frontend/src/components/`: reusable interface components
- `frontend/src/layouts/`: page shell layout
- `frontend/src/styles/`: global UI styling

## Documentation
- `docs/README.md`
- `docs/PROJECT_REPORT.md`
- `docs/API_REFERENCE.md`
- `docs/DEPLOYMENT_GUIDE.md`
- `docs/ARCHITECTURE.md`
- `docs/PROJECT_STRUCTURE.md`
- `docs/INTEGRATION_GUIDE.md`
- `docs/solution.md`
