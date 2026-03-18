# AgentDoc — Project Structure

> Complete file and folder map with descriptions.
> Generated: March 2026

```
AgentDoc/
│
│   .env                          # Local environment variables (gitignored)
│   .env.docker.example           # Docker environment template
│   .env.example                  # Environment variable template for new setups
│   .gitignore                    # Git ignore rules
│   CHANGES.md                    # Changelog and version history
│   CODE_OF_CONDUCT.md            # Community contribution guidelines
│   docker-compose.yml            # Docker Compose for local dev (backend + MongoDB + MinIO)
│   QUICKSTART.md                 # 5-minute setup guide
│   README.md                     # Main project documentation
│   render.yaml                   # Render.com deployment blueprint
│   SECURITY.md                   # Security policy and vulnerability reporting
│   STRUCTURE.md                  # This file — full project structure map
│
├───.github/
│   │   dependabot.yml            # Automated dependency update config
│   │
│   └───workflows/
│           cd-aws-ecs.yml        # CD pipeline — deploy to AWS ECS
│           cd-render.yml         # CD pipeline — deploy to Render
│           ci.yml                # CI pipeline — lint, test, build checks
│
├───backend/                      # Django application root
│   │   control_plane.sqlite3     # SQLite DB for Django auth, sessions, admin
│   │   Dockerfile                # Development Docker image
│   │   Dockerfile.prod           # Production Docker image (multi-stage)
│   │   entrypoint.sh             # Docker entrypoint — runs migrations then gunicorn
│   │   manage.py                 # Django management CLI
│   │   migrate_to_langchain.bat  # Windows script — migrate CrewAI → LangChain
│   │   migrate_to_langchain.sh   # Unix script — migrate CrewAI → LangChain
│   │   render-start.sh           # Render start command — collectstatic + gunicorn
│   │   requirements-ci.txt       # Minimal deps for CI (no heavy ML libs)
│   │   requirements-dev.txt      # Dev extras (pytest, black, ruff, etc.)
│   │   requirements.txt          # Production Python dependencies
│   │   runtime.txt               # Python version pin for Render (python-3.11.x)
│   │
│   ├───apps/                     # Django applications
│   │   │   __init__.py
│   │   │
│   │   ├───agents/               # 5-Agent AI workflow engine
│   │   │   │   apps.py           # Django app config
│   │   │   │   crew.py           # DocumentCrewFactory — builds and runs the workflow
│   │   │   │   events.py         # Django signals emitted after each agent stage
│   │   │   │   langchain_agents.py   # LangChain agent definitions (classification, extraction, etc.)
│   │   │   │   langchain_workflow.py # LangChain chain orchestration
│   │   │   │   runner.py         # execute_document_workflow() — main entry point
│   │   │   │   schemas.py        # Pydantic models for all agent inputs/outputs
│   │   │   │   signals.py        # Signal receivers for agent stage events
│   │   │   │   workflow.py       # run_document_workflow_sync() wrapper
│   │   │   │   __init__.py
│   │   │   │
│   │   │   ├───prompts/
│   │   │   │   │   library.py    # All 5 agent system prompts (classification, extraction, etc.)
│   │   │   │   │   __init__.py
│   │   │   │   └───__pycache__/
│   │   │   │
│   │   │   ├───tools/
│   │   │   │   │   document_tools.py  # OCRTool, HashTool, PolicyLookupTool, FieldExtractionTool
│   │   │   │   │   __init__.py
│   │   │   │   └───__pycache__/
│   │   │   │
│   │   │   └───__pycache__/
│   │   │
│   │   ├───api/                  # REST API — all HTTP endpoints
│   │   │   │   apps.py           # Django app config
│   │   │   │   serializers.py    # DRF serializers for request validation
│   │   │   │   urls.py           # URL patterns for all /api/* routes
│   │   │   │   views.py          # All API views (auth, documents, reviews, search, audit)
│   │   │   │   __init__.py
│   │   │   │
│   │   │   ├───migrations/
│   │   │   │   │   __init__.py
│   │   │   │   └───__pycache__/
│   │   │   │
│   │   │   └───__pycache__/
│   │   │
│   │   ├───core/                 # Core app — shared utilities and management commands
│   │   │   │   apps.py
│   │   │   │   __init__.py
│   │   │   │
│   │   │   ├───management/
│   │   │   │   │   __init__.py
│   │   │   │   └───commands/
│   │   │   │           seed_demo.py   # Creates customer_demo + reviewer_demo accounts
│   │   │   │           __init__.py
│   │   │   │
│   │   │   ├───migrations/
│   │   │   │   │   __init__.py
│   │   │   │   └───__pycache__/
│   │   │   │
│   │   │   └───__pycache__/
│   │   │
│   │   ├───documents/            # Documents app — Django model placeholder
│   │   │   │   apps.py
│   │   │   │   __init__.py
│   │   │   │
│   │   │   ├───migrations/
│   │   │   │   │   __init__.py
│   │   │   │   └───__pycache__/
│   │   │   │
│   │   │   └───__pycache__/
│   │   │
│   │   ├───reviews/              # Reviews app — human review workflow
│   │   │   │   apps.py
│   │   │   │   services.py       # trigger_review_workflow(), send_review_notification()
│   │   │   │   __init__.py
│   │   │   │
│   │   │   ├───migrations/
│   │   │   │   │   __init__.py
│   │   │   │   └───__pycache__/
│   │   │   │
│   │   │   └───__pycache__/
│   │   │
│   │   └───__pycache__/
│   │
│   ├───config/                   # Django project configuration
│   │   │   asgi.py               # ASGI entry point (async support)
│   │   │   settings.py           # All Django settings — env-driven, section-organized
│   │   │   urls.py               # Root URL config (/, /app/, /api/, /admin/)
│   │   │   wsgi.py               # WSGI entry point (gunicorn)
│   │   │   __init__.py
│   │   └───__pycache__/
│   │
│   ├───media/                    # Uploaded files (USE_LOCAL_STORAGE=1, gitignored)
│   │   └───incoming/
│   │       └───doc_a75b5eb94b4f/
│   │               sample_input.txt   # Example uploaded document
│   │
│   ├───scripts/                  # Operational scripts
│   │       preflight_check.py    # Pre-startup checks (MongoDB, env vars, storage)
│   │       wait_for_services.py  # Docker health-wait for MongoDB + MinIO
│   │
│   ├───services/                 # External service clients
│   │   │   minio_client.py       # LocalStorageService (dev) / MinioStorageService (prod)
│   │   │   mongodb.py            # MongoService — all MongoDB CRUD operations
│   │   │   notifications.py      # send_review_email() — SMTP with graceful fallback
│   │   │   vector_search.py      # VectorSearchService — embeddings + semantic search
│   │   │   __init__.py
│   │   └───__pycache__/
│   │
│   ├───static/                   # Static assets served by WhiteNoise
│   │   │   .gitignore            # Ignores staticfiles/ build output
│   │   │   index.html            # Standalone HTML reference (not used in production)
│   │   │   package.json          # Minimal package.json (no build step required)
│   │   │   README.md             # Static assets documentation
│   │   │
│   │   ├───css/
│   │   │       app-bundle.css    # Full app styles — variables, layout, components, dark mode
│   │   │
│   │   ├───js/
│   │   │       app-bundle.js     # Full app JS — API client, Auth, Dashboard, Documents, Reviews
│   │   │       app.js            # Legacy app controller (superseded by app-bundle.js)
│   │   │
│   │   ├───landing-css/
│   │   │       landing.css       # Landing page styles — hero, features, workflow, footer
│   │   │
│   │   └───landing-js/
│   │           landing.js        # Landing page JS — GSAP animations, mobile menu, scroll effects
│   │
│   ├───templates/                # Django HTML templates
│   │       index.html            # App shell — loads app-bundle.css + app-bundle.js
│   │       landing.html          # Public landing page — loads landing.css + landing.js
│   │
│   └───tests/
│           test_schemas.py       # Pydantic schema validation tests
│           __init__.py
│
├───deploy/                       # Deployment configurations
│   │
│   ├───aws/                      # AWS ECS deployment
│   │   │   .env.aws.example      # AWS-specific environment variable template
│   │   │   docker-compose.aws.yml # Docker Compose for AWS deployment
│   │   │   README.md             # AWS deployment guide
│   │   │
│   │   └───ecs/
│   │           backend-taskdef.json   # ECS task definition — backend service
│   │           frontend-taskdef.json  # ECS task definition — frontend service
│   │
│   └───render/                   # Render.com deployment
│           backend.env.example   # Backend environment variables for Render
│           frontend.env.example  # Frontend environment variables for Render
│           README.md             # Render deployment guide
│
├───docs/                         # Project documentation
│   │   API_REFERENCE.md          # Full REST API endpoint reference
│   │   ARCHITECTURE.md           # System architecture overview
│   │   ARCHITECTURE_VISUAL.md    # Visual architecture with Mermaid diagrams
│   │   AUTHENTICATION_GUIDE.md   # JWT auth flow, roles, token management
│   │   BACKEND_STRUCTURE.md      # Django app and service layer documentation
│   │   CHANGES_SUMMARY.md        # Summary of recent changes
│   │   COMPLETE_UPDATE_SUMMARY.md # Full update history
│   │   CSS_FIX_SUMMARY.md        # CSS fixes and styling notes
│   │   DEPLOYMENT.md             # General deployment documentation
│   │   DEPLOYMENT_CHECKLIST.md   # Step-by-step deployment checklist
│   │   DEPLOYMENT_GUIDE.md       # Detailed deployment guide
│   │   DEPLOYMENT_INTEGRATED.md  # Integrated single-service deployment guide
│   │   DEPLOYMENT_RENDER.md      # Render-specific deployment steps
│   │   DEPLOYMENT_SUCCESS.md     # Post-deployment verification guide
│   │   DOCUMENTATION_INDEX.md    # Index of all documentation files
│   │   DOCUMENT_MANAGEMENT_GUIDE.md # Document upload, processing, and management
│   │   ENVIRONMENT_VARIABLES.md  # All environment variables with descriptions
│   │   ENV_UPDATE_SUMMARY.md     # Environment variable change history
│   │   FILES_ORGANIZED.md        # File organization notes
│   │   INTEGRATION_COMPLETE.md   # Frontend-backend integration completion notes
│   │   INTEGRATION_GUIDE.md      # Frontend-backend integration guide
│   │   INTEGRATION_SUMMARY.md    # Integration summary and status
│   │   LANGCHAIN_MIGRATION.md    # CrewAI → LangChain migration guide
│   │   LANGCHAIN_MIGRATION_SUMMARY.md # Migration summary and status
│   │   MIGRATION_TO_LANGCHAIN.md # Detailed migration steps
│   │   PROJECT_REPORT.md         # Full project report
│   │   PROJECT_STATUS.md         # Current project status and progress
│   │   PROJECT_STRUCTURE.md      # Legacy structure documentation
│   │   PROJECT_SUMMARY.md        # Executive project summary
│   │   README.md                 # Docs index and navigation
│   │   SESSION_SUMMARY.md        # Development session notes
│   │   SETUP_GUIDE.md            # Complete local setup instructions
│   │   solution.md               # Solution design and approach
│   │   TROUBLESHOOTING.md        # Common issues and fixes
│   │   UNIQUE_VALUE_BLUEPRINT.md # Product differentiation and value proposition
│   │   USER_GUIDE.md             # End-user guide for the application
│   │   VIEWING_DIAGRAMS.md       # How to render Mermaid diagrams
│   │
│   └───assets/                   # Diagrams and visual assets
│           agent-flow.svg            # Agent workflow SVG diagram
│           agent-workflow.mmd        # Agent workflow Mermaid source
│           architecture-complete.mmd # Full system architecture Mermaid source
│           architecture-dark.svg     # Architecture diagram (dark theme)
│           architecture.svg          # Architecture diagram (light theme)
│           backend-flow.svg          # Backend data flow SVG
│           data-flow.mmd             # Data flow sequence diagram Mermaid source
│           deployment-architecture.mmd # Deployment architecture Mermaid source
│           fullstack-flow.svg        # Full-stack flow SVG
│           ui-flow.svg               # UI navigation flow SVG
│
├───sample/                       # Sample documents for testing the workflow
│   │   README.md                 # Sample documents usage guide
│   │
│   ├───contract/
│   │       expected_output.json  # Expected agent output for contract document
│   │       sample_input.txt      # Sample contract text
│   │
│   ├───handwritten_form/
│   │       expected_output.json  # Expected agent output for handwritten form
│   │       sample_input.txt      # Sample handwritten form text
│   │
│   ├───insurance_claim/
│   │       expected_output.json  # Expected agent output for insurance claim
│   │       sample_input.txt      # Sample insurance claim text
│   │
│   ├───invoice/
│   │       expected_output.json  # Expected agent output for invoice
│   │       sample_input.txt      # Sample invoice text
│   │
│   ├───kyc_form/
│   │       expected_output.json  # Expected agent output for KYC form
│   │       sample_input.txt      # Sample KYC form text
│   │
│   ├───loan_application/
│   │       expected_output.json  # Expected agent output for loan application
│   │       sample_input.txt      # Sample loan application text
│   │
│   ├───receipt/
│   │       expected_output.json  # Expected agent output for receipt
│   │       sample_input.txt      # Sample receipt text
│   │
│   └───shipping_document/
│           expected_output.json  # Expected agent output for shipping document
│           sample_input.txt      # Sample shipping document text
│
└───scripts/
        preflight.ps1             # PowerShell preflight check — validates env, MongoDB, Python version
```

---

## Key File Roles

| File | Purpose |
|---|---|
| `backend/config/settings.py` | Single source of truth for all Django configuration |
| `backend/config/urls.py` | Routes `/`, `/app/`, `/api/*`, `/admin/` |
| `backend/apps/api/views.py` | All 25+ REST API endpoints |
| `backend/apps/agents/crew.py` | `DocumentCrewFactory` — runs the 5-agent pipeline |
| `backend/apps/agents/runner.py` | `execute_document_workflow()` — called by the upload view |
| `backend/apps/agents/schemas.py` | Pydantic models for every agent stage output |
| `backend/services/mongodb.py` | `MongoService` — all MongoDB read/write operations |
| `backend/services/minio_client.py` | Storage abstraction — local disk or MinIO/S3 |
| `backend/services/vector_search.py` | Sentence-transformer embeddings + semantic search |
| `backend/static/js/app-bundle.js` | Frontend SPA — Auth, Dashboard, Documents, Reviews |
| `backend/templates/index.html` | App shell loaded at `/app/` |
| `backend/templates/landing.html` | Public landing page loaded at `/` |

## MongoDB Collections

| Collection | Contents |
|---|---|
| `documents` | Document records with status, type, metadata, embeddings |
| `extractions` | Per-document field extraction results |
| `validation_results` | Validation checks, risk scores, issues |
| `reviews` | Review queue entries with assignment and status |
| `pages` | Per-page OCR text and image references |
| `audit_logs` | Immutable event log for every workflow action |
| `users` | User profiles with role and preferences |
