# Architecture

## Overview Assets

### Light Version
![Architecture Overview](./assets/architecture.svg)

### Dark Version
![Architecture Overview Dark](./assets/architecture-dark.svg)

## Focused Diagrams

### UI Flow Diagram
![UI Flow](./assets/ui-flow.svg)

### Backend Flow Diagram
![Backend Flow](./assets/backend-flow.svg)

### Full Stack Flow Diagram
![Full Stack Flow](./assets/fullstack-flow.svg)

### Agent Flow Diagram
![Agent Flow](./assets/agent-flow.svg)

## Architecture Views

### UI Flow
- customer uploads document
- user tracks status and history
- reviewer processes queue items
- semantic search retrieves relevant documents

### Backend Flow
- Django validates request and JWT identity
- MinIO stores binary object
- MongoDB stores workflow state
- CrewAI executes sequential multi-agent reasoning with Pydantic outputs
- Django sends SMTP notifications for review tasks
- agent stage events append audit logs via Django signals

### Full Stack Flow
- React -> Django API -> CrewAI -> Gemini
- Django persists state to MongoDB and file objects to MinIO
- human review callbacks update records and close workflow loop

### Agent Flow
- Ingestion
- Preprocessing
- Classification
- Extraction
- Validation
- Routing
- Exception
- Review
- Audit

## High-Level Diagram
```mermaid
flowchart LR
    U[Customer] --> FE[React Frontend]
    FE --> API[Django API]
    API --> MINIO[(MinIO)]
    API --> MDB[(MongoDB)]
    API --> CREW[CrewAI Workflow]
    CREW --> GEMINI[Google Gemini]
    Reviewer[Reviewer] --> FE
```
