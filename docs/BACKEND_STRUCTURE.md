# Backend Structure - 5-Agent System

Complete documentation of the AgentDoc backend architecture using 5 specialized agents.

## 📁 Directory Structure

```
backend/
├── apps/
│   ├── agents/                    # 5-Agent System
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── crew.py               # Agent definitions & workflow
│   │   ├── events.py             # Event handlers
│   │   ├── runner.py             # Workflow execution
│   │   ├── schemas.py            # Pydantic models
│   │   ├── signals.py            # Django signals
│   │   ├── workflow.py           # Workflow orchestration
│   │   ├── prompts/
│   │   │   ├── __init__.py
│   │   │   └── library.py        # Agent prompts (5 agents)
│   │   └── tools/
│   │       ├── __init__.py
│   │       └── document_tools.py # OCR, Policy, Search tools
│   │
│   ├── api/                       # REST API Endpoints
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── serializers.py        # DRF serializers
│   │   ├── urls.py               # API routes
│   │   └── views.py              # API views
│   │
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   └── management/
│   │       └── commands/
│   │           └── seed_demo.py  # Demo data seeder
│   │
│   ├── documents/                 # Document models
│   │   ├── __init__.py
│   │   └── apps.py
│   │
│   └── reviews/                   # Review system
│       ├── __init__.py
│       ├── apps.py
│       └── services.py           # Review services
│
├── config/                        # Django configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py               # Main settings
│   ├── urls.py                   # URL configuration
│   └── wsgi.py
│
├── services/                      # External services
│   ├── __init__.py
│   ├── minio_client.py           # MinIO (optional)
│   ├── mongodb.py                # MongoDB connection
│   ├── notifications.py          # Email notifications
│   └── vector_search.py          # Vector search
│
├── tests/                         # Test suite
│   ├── __init__.py
│   └── test_schemas.py
│
├── scripts/                       # Utility scripts
│   ├── preflight_check.py        # Pre-deployment checks
│   └── wait_for_services.py      # Service readiness
│
├── manage.py                      # Django management
├── requirements.txt               # Python dependencies
├── requirements-dev.txt           # Dev dependencies
├── requirements-ci.txt            # CI dependencies
├── Dockerfile                     # Development Docker
├── Dockerfile.prod                # Production Docker
├── entrypoint.sh                  # Docker entrypoint
└── render-start.sh                # Render startup script
```

## 🤖 5-Agent System

### Agent 1: Classification Agent
**File**: `apps/agents/crew.py`
**Prompt**: `apps/agents/prompts/library.py` - `CLASSIFICATION_PROMPT`

**Responsibilities:**
- Document ingestion and metadata validation
- Image quality assessment
- Document type classification
- Confidence scoring

**Tools:**
- `crewai_ocr_tool` - OCR processing
- `crewai_search_knowledge_tool` - Semantic search

**Output**: `ClassificationOutput` schema

### Agent 2: Extraction Agent
**File**: `apps/agents/crew.py`
**Prompt**: `apps/agents/prompts/library.py` - `EXTRACTION_PROMPT`

**Responsibilities:**
- Structured data extraction
- Field-level confidence scoring
- Evidence gathering
- Missing field identification

**Tools:**
- `crewai_ocr_tool` - OCR processing

**Output**: `ExtractionOutput` schema

### Agent 3: Validation Agent
**File**: `apps/agents/crew.py`
**Prompt**: `apps/agents/prompts/library.py` - `VALIDATION_PROMPT`

**Responsibilities:**
- Business rule validation
- Format checking
- Cross-field consistency
- Risk score calculation

**Tools:**
- `crewai_policy_lookup_tool` - Policy rules

**Output**: `ValidationOutput` schema

### Agent 4: Routing Agent
**File**: `apps/agents/crew.py`
**Prompt**: `apps/agents/prompts/library.py` - `ROUTING_PROMPT`

**Responsibilities:**
- Queue assignment (auto_approve/review/exception)
- Exception handling
- Review preparation
- SLA assignment

**Tools:**
- `crewai_search_knowledge_tool` - Knowledge base

**Output**: `RoutingOutput` schema

### Agent 5: Audit Agent
**File**: `apps/agents/crew.py`
**Prompt**: `apps/agents/prompts/library.py` - `AUDIT_PROMPT`

**Responsibilities:**
- Audit trail creation
- Timeline generation
- Searchable summary
- Compliance logging

**Tools:** None (uses previous agent outputs)

**Output**: `AuditOutput` schema

## 📊 Data Models (Pydantic Schemas)

**File**: `apps/agents/schemas.py`

### Core Schemas

```python
# Agent Outputs
- ClassificationOutput
- ExtractionOutput
- ValidationOutput
- RoutingOutput
- AuditOutput

# Supporting Models
- FieldExtraction
- ValidationCheck
- PageDescriptor
- WorkflowState

# Legacy (backward compatibility)
- IngestionOutput
- PreprocessingOutput
- ExceptionOutput
- ReviewOutput
```

## 🔧 Tools

**File**: `apps/agents/tools/document_tools.py`

### OCRTool
- Extracts text from document images
- Handles multiple pages
- Returns confidence scores

### PolicyLookupTool
- Retrieves business rules by document type
- Returns required fields and validation rules

### SearchKnowledgeTool
- Semantic search across documents
- Vector-based similarity matching

## 🔌 API Endpoints

**File**: `apps/api/urls.py` and `apps/api/views.py`

### Authentication
```
POST   /api/auth/login/          # Login
POST   /api/auth/logout/         # Logout
POST   /api/auth/refresh/        # Refresh token
GET    /api/auth/me/             # Current user
```

### Documents
```
POST   /api/documents/upload-url/     # Get presigned URL
POST   /api/documents/upload/         # Upload document
GET    /api/documents/               # List documents
GET    /api/documents/{id}/          # Get document
GET    /api/documents/{id}/status/   # Get status
GET    /api/documents/{id}/extraction/ # Get extraction
```

### Reviews
```
GET    /api/reviews/                    # List reviews
POST   /api/reviews/{id}/submit/       # Submit review
POST   /api/reviews/{doc_id}/action/   # Review action
POST   /api/trigger-review/            # Trigger review
```

### Search & Audit
```
GET    /api/search/semantic/           # Semantic search
GET    /api/audit/{document_id}/       # Audit trail
GET    /api/dashboard/                 # Dashboard stats
```

## 💾 Database Schema

### MongoDB Collections

**Documents Collection**
```javascript
{
  _id: ObjectId,
  document_id: String,
  user_id: String,
  file_name: String,
  mime_type: String,
  storage_path: String,
  document_type: String,
  status: String,
  created_at: DateTime,
  updated_at: DateTime,
  vector_embedding: Array[Float] // 165 dimensions
}
```

**Extractions Collection**
```javascript
{
  _id: ObjectId,
  document_id: String,
  document_type: String,
  fields: Array[FieldExtraction],
  structured_fields: Object,
  confidence_map: Object,
  missing_fields: Array[String],
  created_at: DateTime
}
```

**Validation Results Collection**
```javascript
{
  _id: ObjectId,
  document_id: String,
  overall_status: String,
  is_valid: Boolean,
  risk_score: Float,
  confidence: Float,
  checks: Array[ValidationCheck],
  issues: Array[ValidationCheck],
  created_at: DateTime
}
```

**Reviews Collection**
```javascript
{
  _id: ObjectId,
  document_id: String,
  review_id: String,
  assigned_team: String,
  review_status: String,
  reviewer_feedback: String,
  corrected_fields: Object,
  created_at: DateTime,
  updated_at: DateTime
}
```

**Audit Logs Collection**
```javascript
{
  _id: ObjectId,
  document_id: String,
  workflow_status: String,
  timeline: Array[Object],
  audit_summary: String,
  searchable_summary: String,
  created_at: DateTime
}
```

### SQLite (Control Plane)
```sql
-- Django auth tables
auth_user
auth_group
auth_permission

-- Django sessions
django_session

-- Django migrations
django_migrations
```

## 🔐 Configuration

**File**: `config/settings.py`

### Key Settings

```python
# AI Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini/gemini-2.5-flash"

# MongoDB
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = "agentdoc"
MONGODB_VECTOR_INDEX = "documents_vector_index"

# Storage
USE_LOCAL_STORAGE = os.getenv("USE_LOCAL_STORAGE", "0") == "1"
MEDIA_ROOT = BASE_DIR / "media"

# Security
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DEBUG = os.getenv("DJANGO_DEBUG", "0") == "1"
ALLOWED_HOSTS = [...]
CORS_ALLOWED_ORIGINS = [...]

# JWT
ACCESS_TOKEN_LIFETIME = timedelta(minutes=60)
REFRESH_TOKEN_LIFETIME = timedelta(days=7)
```

## 🚀 Workflow Execution

**File**: `apps/agents/runner.py` and `apps/agents/workflow.py`

### Execution Flow

1. **Document Upload**
   - User uploads via API
   - File stored in local storage
   - Metadata saved to MongoDB

2. **Workflow Trigger**
   - API calls `document_crew_factory.execute()`
   - Payload includes document metadata

3. **Agent Execution (Sequential)**
   ```python
   Agent 1 (Classification) 
     → Agent 2 (Extraction)
     → Agent 3 (Validation)
     → Agent 4 (Routing)
     → Agent 5 (Audit)
   ```

4. **Result Storage**
   - Each agent stores output in MongoDB
   - Final state returned to API

5. **Status Update**
   - Document status updated
   - User notified (if review needed)

## 🧪 Testing

**File**: `tests/test_schemas.py`

### Test Coverage
- Schema validation
- Agent output formats
- Workflow execution
- API endpoints

### Running Tests
```bash
cd backend
python manage.py test
```

## 📦 Dependencies

**File**: `requirements.txt`

### Core Dependencies
```
Django>=4.2,<5.0
djangorestframework>=3.14.0
django-cors-headers>=4.0.0
djangorestframework-simplejwt>=5.2.0
python-dotenv>=1.0.0
pymongo>=4.5.0
crewai>=0.1.0
google-generativeai>=0.3.0
sentence-transformers>=2.2.0
torch>=2.0.0
Pillow>=10.0.0
opencv-python-headless>=4.8.0
pytesseract>=0.3.10
gunicorn>=21.2.0
whitenoise>=6.5.0
```

## 🔄 Deployment

### Local Development
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

### Render Deployment
```bash
# Build Command
cd AgentDoc/backend
pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Start Command
cd AgentDoc/backend
python manage.py seed_demo --skip-if-present
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

## 🔍 Monitoring & Logging

### Logging Configuration
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

### Key Metrics
- Document processing time
- Agent execution time
- API response time
- Error rates
- Queue depths

## 🛡️ Security

### Authentication
- JWT tokens (access + refresh)
- Token expiration: 60 minutes
- Refresh token: 7 days

### Authorization
- Role-based access control
- Customer: Upload, view own documents
- Reviewer: Review queue, approve/reject
- Admin: Full access

### Data Protection
- HTTPS only in production
- Secure cookies
- CORS configuration
- CSRF protection
- Environment variables for secrets

## 📚 Additional Resources

- [API Reference](API_REFERENCE.md)
- [Deployment Guide](DEPLOYMENT_RENDER.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Architecture Visual](ARCHITECTURE_VISUAL.md)

---

**Last Updated**: 2024
**Version**: 5-Agent System
**Status**: Production Ready ✅
