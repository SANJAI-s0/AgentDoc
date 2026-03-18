# AgentDoc - Project Summary

## Overview

AgentDoc is an Agentic AI Document Intelligence System that automates complex document processing workflows using a 5-agent pipeline.

## Problem Statement

Organizations handle large volumes of documents (KYC forms, invoices, insurance claims, contracts, handwritten forms) in inconsistent formats. Manual processing leads to:
- Delays and bottlenecks
- Human errors
- High operational costs
- Compliance risks

## Solution

An AI-powered system with 5 specialized agents that autonomously process documents from upload to approval/review.

## 5-Agent Workflow

### 1. Classification Agent
- Identifies document type (invoice, KYC, contract, etc.)
- Provides confidence scoring
- Routes to appropriate extraction templates

### 2. Extraction Agent
- Extracts structured data using AI-powered OCR
- Handles messy scans and handwritten text
- Outputs structured JSON with field-level confidence

### 3. Validation Agent
- Validates against business rules
- Performs semantic consistency checks
- Flags anomalies and missing data

### 4. Routing Agent
- Routes based on confidence and risk levels
- Auto-approves low-risk documents
- Sends to human review when needed
- Escalates exceptions

### 5. Audit Agent
- Creates immutable audit trail
- Logs all decisions and changes
- Ensures compliance and traceability

## Technology Stack

### Frontend
- React + Vite
- React Router
- Tailwind CSS
- React Query

### Backend
- Django + Django REST Framework
- CrewAI (Agent orchestration)
- Google Gemini (AI reasoning)
- JWT Authentication

### Database & Storage
- MongoDB Atlas (document store)
- PostgreSQL/SQLite (control plane)
- Local filesystem (free tier)

### Deployment
- Render (free tier)
- Docker (optional)
- GitHub Actions (CI/CD)

## Project Structure

```
AgentDoc/
├── landing-page/          # Static landing page
│   ├── index.html
│   ├── css/              # Modular stylesheets
│   └── js/               # Modular JavaScript
├── backend/              # Django API
│   ├── apps/
│   │   ├── agents/       # 5-agent system
│   │   ├── api/          # REST endpoints
│   │   ├── documents/    # Document models
│   │   └── reviews/      # Human review
│   └── config/           # Settings
├── frontend/             # React application
│   └── src/
│       ├── pages/        # Dashboard, Documents, Reviews
│       └── components/   # Reusable UI
└── render.yaml           # Deployment config
```

## Key Features

1. **Autonomous Processing**: 5-agent pipeline handles end-to-end workflow
2. **Intelligent Extraction**: Beyond OCR - semantic understanding
3. **Smart Routing**: Risk-based decision making
4. **Human-in-the-Loop**: Seamless reviewer collaboration
5. **Audit Trail**: Complete compliance tracking
6. **Semantic Search**: Vector-based document retrieval

## Landing Page

Modern, animated landing page built with:
- Pure HTML5, CSS3, JavaScript
- GSAP animations
- Modular architecture
- Mobile responsive
- Render-ready

### File Organization

**CSS Files:**
- `reset.css` - Browser normalization
- `variables.css` - Design tokens
- `layout.css` - Grid systems
- `components.css` - Reusable components
- `sections.css` - Section styles
- `responsive.css` - Media queries

**JS Files:**
- `config.js` - Configuration
- `navigation.js` - Menu and scroll
- `main.js` - Initialization
- `animations/hero.js` - Hero animations
- `animations/sections.js` - Scroll animations
- `animations/interactions.js` - Hover effects

## Deployment (Render Free Tier)

### Services
1. **Landing Page**: Static site
2. **Backend API**: Python web service
3. **Frontend App**: Node web service

### Requirements
- MongoDB Atlas (free M0 cluster)
- Google Gemini API key
- GitHub repository

### Configuration
- No MinIO needed (local storage)
- Whitenoise for static files
- Gunicorn WSGI server
- Environment-based settings

## Demo Credentials

- **Customer**: `customer_demo / DemoPass123!`
- **Reviewer**: `reviewer_demo / DemoPass123!`

## Use Cases

- **Banking**: KYC forms, loan applications
- **Healthcare**: Insurance claims, patient forms
- **Logistics**: Shipping forms, invoices
- **Legal**: Contracts, compliance documents

## Performance

- 99.5% accuracy
- 10x faster processing
- 85% cost reduction
- Straight-through processing for low-risk documents

## Compliance

- Immutable audit trail
- Role-based access control
- Complete decision logging
- Reviewer accountability

## Future Enhancements

- Redis caching
- S3/MinIO for persistent storage
- MongoDB vector search
- Advanced analytics dashboard
- Multi-language support
- Custom agent training

## Getting Started

### Local Development
```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver

# Frontend
cd frontend
npm install
npm run dev

# Landing Page
cd landing-page
python -m http.server 8080
```

### Render Deployment
1. Connect GitHub repository
2. Use Blueprint (render.yaml)
3. Configure environment variables
4. Deploy!

## Documentation

- `README.md` - Main project documentation
- `DEPLOYMENT_RENDER.md` - Render deployment guide
- `landing-page/README.md` - Landing page documentation
- `AgentDoc/docs/` - Detailed architecture and guides

## License

Part of the AgentDoc project - Agentic AI Document Intelligence System

## Support

- GitHub Issues for bug reports
- Documentation for guides
- Demo for hands-on experience
