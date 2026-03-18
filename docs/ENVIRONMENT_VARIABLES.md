# Environment Variables Reference

Complete guide to all environment variables used in AgentDoc.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Required Variables](#required-variables)
- [Django Core Settings](#django-core-settings)
- [Database Configuration](#database-configuration)
- [Storage Configuration](#storage-configuration)
- [AI Configuration](#ai-configuration)
- [Authentication](#authentication)
- [Email Notifications](#email-notifications)
- [Application URLs](#application-urls)
- [Deployment Settings](#deployment-settings)
- [Security Best Practices](#security-best-practices)

## 🚀 Quick Start

### Minimum Required Configuration

For local development, you only need to set these:

```env
GEMINI_API_KEY=your_gemini_api_key_here
MONGODB_URI=mongodb://localhost:27017
DJANGO_SECRET_KEY=change-me-to-random-string
```

### Copy Example File

```bash
cp .env.example .env
```

Then edit `.env` with your values.

## ✅ Required Variables

These variables MUST be set for the system to work:

### GEMINI_API_KEY
**Required**: Yes  
**Type**: String  
**Description**: Google Gemini API key for AI agent reasoning

**How to get**:
1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy and paste into .env

**Example**:
```env
GEMINI_API_KEY=AIzaSyD...your-key-here
```

### MONGODB_URI
**Required**: Yes  
**Type**: Connection String  
**Description**: MongoDB connection string

**Local**:
```env
MONGODB_URI=mongodb://localhost:27017
```

**MongoDB Atlas** (Free M0 Cluster):
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

### DJANGO_SECRET_KEY
**Required**: Yes  
**Type**: String (50+ characters)  
**Description**: Django secret key for cryptographic signing

**Generate**:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Example**:
```env
DJANGO_SECRET_KEY=django-insecure-abc123...random-50-chars
```

## ⚙️ Django Core Settings

### DJANGO_DEBUG
**Required**: No  
**Default**: 0  
**Type**: Boolean (0 or 1)  
**Description**: Enable Django debug mode

**Values**:
- `0` = False (Production)
- `1` = True (Development)

**Example**:
```env
DJANGO_DEBUG=1  # Development
DJANGO_DEBUG=0  # Production
```

⚠️ **Never set to 1 in production!**

### DJANGO_ALLOWED_HOSTS
**Required**: No  
**Default**: `*`  
**Type**: Comma-separated list  
**Description**: Allowed host headers

**Local**:
```env
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

**Production**:
```env
DJANGO_ALLOWED_HOSTS=your-backend.onrender.com,api.yourdomain.com
```

### DJANGO_CORS_ALLOWED_ORIGINS
**Required**: No  
**Default**: `http://localhost:5173`  
**Type**: Comma-separated URLs  
**Description**: Allowed origins for CORS

**Local**:
```env
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:8080
```

**Production**:
```env
DJANGO_CORS_ALLOWED_ORIGINS=https://your-frontend.onrender.com,https://your-landing.onrender.com
```

### DJANGO_CSRF_TRUSTED_ORIGINS
**Required**: No  
**Default**: `http://localhost:5173`  
**Type**: Comma-separated URLs  
**Description**: Trusted origins for CSRF

**Should match CORS origins**:
```env
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-frontend.onrender.com
```

### DJANGO_USE_X_FORWARDED_HOST
**Required**: No  
**Default**: 1  
**Type**: Boolean (0 or 1)  
**Description**: Use X-Forwarded-Host header

**Render/AWS**: Set to `1`  
**Direct deployment**: Set to `0`

### DJANGO_TRUST_X_FORWARDED_PROTO
**Required**: No  
**Default**: 1  
**Type**: Boolean (0 or 1)  
**Description**: Trust X-Forwarded-Proto for HTTPS

**Behind reverse proxy**: Set to `1`  
**Direct HTTPS**: Set to `0`

### DJANGO_SESSION_COOKIE_SECURE
**Required**: No  
**Default**: 0  
**Type**: Boolean (0 or 1)  
**Description**: Send session cookie only over HTTPS

**Development**: `0`  
**Production**: `1`

### DJANGO_CSRF_COOKIE_SECURE
**Required**: No  
**Default**: 0  
**Type**: Boolean (0 or 1)  
**Description**: Send CSRF cookie only over HTTPS

**Development**: `0`  
**Production**: `1`

## 💾 Database Configuration

### MONGODB_DB_NAME
**Required**: No  
**Default**: `agentdoc`  
**Type**: String  
**Description**: MongoDB database name

```env
MONGODB_DB_NAME=agentdoc
```

### MONGODB_VECTOR_INDEX
**Required**: No  
**Default**: `documents_vector_index`  
**Type**: String  
**Description**: Vector search index name

```env
MONGODB_VECTOR_INDEX=documents_vector_index
```

### MONGODB_ENABLE_VECTOR_SEARCH
**Required**: No  
**Default**: 1  
**Type**: Boolean (0 or 1)  
**Description**: Enable vector search functionality

```env
MONGODB_ENABLE_VECTOR_SEARCH=1
```

### EMBEDDING_VECTOR_DIMENSIONS
**Required**: No  
**Default**: 165  
**Type**: Integer  
**Description**: Vector embedding dimensions

**Must match sentence-transformers model output**:
```env
EMBEDDING_VECTOR_DIMENSIONS=165
```

## 📦 Storage Configuration

### USE_LOCAL_STORAGE
**Required**: No  
**Default**: 0  
**Type**: Boolean (0 or 1)  
**Description**: Use local filesystem instead of MinIO/S3

**Render free tier**: Set to `1`  
**With MinIO/S3**: Set to `0`

```env
USE_LOCAL_STORAGE=1
```

### MEDIA_ROOT
**Required**: No (when USE_LOCAL_STORAGE=1)  
**Default**: `media`  
**Type**: Path  
**Description**: Local storage directory

**Local**:
```env
MEDIA_ROOT=media
```

**Render**:
```env
MEDIA_ROOT=/opt/render/project/src/AgentDoc/backend/media
```

### MinIO/S3 Configuration

Only needed when `USE_LOCAL_STORAGE=0`:

#### MINIO_ENDPOINT
```env
MINIO_ENDPOINT=localhost:9000
```

#### MINIO_ACCESS_KEY
```env
MINIO_ACCESS_KEY=minioadmin
```

#### MINIO_SECRET_KEY
```env
MINIO_SECRET_KEY=minioadmin
```

#### MINIO_BUCKET
```env
MINIO_BUCKET=documents
```

#### MINIO_SECURE
```env
MINIO_SECURE=0  # 0 for HTTP, 1 for HTTPS
```

## 🤖 AI Configuration

### GEMINI_MODEL
**Required**: No  
**Default**: `gemini/gemini-2.5-flash`  
**Type**: String  
**Description**: Gemini model to use

**Options**:
- `gemini/gemini-2.5-flash` (Recommended - Fast & efficient)
- `gemini/gemini-pro` (More capable, slower)

```env
GEMINI_MODEL=gemini/gemini-2.5-flash
```

### AGENT_INTERNAL_TOKEN
**Required**: No  
**Default**: None  
**Type**: String  
**Description**: Token for inter-service communication

**Generate**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

```env
AGENT_INTERNAL_TOKEN=random-secure-token-here
```

## 🔐 Authentication

### JWT_ACCESS_MINUTES
**Required**: No  
**Default**: 60  
**Type**: Integer  
**Description**: JWT access token lifetime in minutes

```env
JWT_ACCESS_MINUTES=60
```

### JWT_REFRESH_DAYS
**Required**: No  
**Default**: 7  
**Type**: Integer  
**Description**: JWT refresh token lifetime in days

```env
JWT_REFRESH_DAYS=7
```

## 📧 Email Notifications

### DEFAULT_FROM_EMAIL
**Required**: No  
**Default**: `ops@agentdoc.local`  
**Type**: Email address  
**Description**: Default sender email

```env
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### SMTP_HOST
**Required**: No  
**Default**: `localhost`  
**Type**: Hostname  
**Description**: SMTP server hostname

**Local (MailHog)**:
```env
SMTP_HOST=localhost
```

**Production**:
```env
SMTP_HOST=smtp.gmail.com
```

### SMTP_PORT
**Required**: No  
**Default**: 1025  
**Type**: Integer  
**Description**: SMTP server port

**MailHog**: `1025`  
**Gmail**: `587`  
**Standard**: `25`

### SMTP_USER
**Required**: No (if SMTP requires auth)  
**Type**: String  
**Description**: SMTP username

```env
SMTP_USER=your-smtp-username
```

### SMTP_PASSWORD
**Required**: No (if SMTP requires auth)  
**Type**: String  
**Description**: SMTP password

```env
SMTP_PASSWORD=your-smtp-password
```

### SMTP_USE_TLS
**Required**: No  
**Default**: 0  
**Type**: Boolean (0 or 1)  
**Description**: Use TLS for SMTP

```env
SMTP_USE_TLS=1
```

## 🌐 Application URLs

### REVIEW_PORTAL_URL
**Required**: No  
**Default**: `http://localhost:5173/reviews`  
**Type**: URL  
**Description**: Review portal URL for email links

**Local**:
```env
REVIEW_PORTAL_URL=http://localhost:5173/reviews
```

**Production**:
```env
REVIEW_PORTAL_URL=https://your-frontend.onrender.com/reviews
```

### VITE_API_BASE
**Required**: Yes (Frontend)  
**Type**: URL  
**Description**: Backend API base URL for frontend

**Local**:
```env
VITE_API_BASE=http://localhost:8000/api
```

**Production**:
```env
VITE_API_BASE=https://your-backend.onrender.com/api
```

## 🚀 Deployment Settings

### PYTHON_VERSION
**Required**: No (Render)  
**Default**: `3.11.0`  
**Type**: Version string  
**Description**: Python version for deployment

```env
PYTHON_VERSION=3.11.0
```

### NODE_VERSION
**Required**: No (Render)  
**Default**: `20.x`  
**Type**: Version string  
**Description**: Node.js version for frontend

```env
NODE_VERSION=20.x
```

## 🔒 Security Best Practices

### 1. Never Commit Secrets

❌ **Don't**:
```bash
git add .env
git commit -m "Add environment variables"
```

✅ **Do**:
- Keep `.env` in `.gitignore`
- Use `.env.example` for templates
- Use environment variables in production

### 2. Generate Strong Keys

**Django Secret Key**:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Random Token**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Production Checklist

- [ ] `DJANGO_DEBUG=0`
- [ ] Strong `DJANGO_SECRET_KEY`
- [ ] `DJANGO_SESSION_COOKIE_SECURE=1`
- [ ] `DJANGO_CSRF_COOKIE_SECURE=1`
- [ ] Specific `DJANGO_ALLOWED_HOSTS`
- [ ] HTTPS URLs in CORS settings
- [ ] Secure SMTP credentials
- [ ] MongoDB Atlas with authentication
- [ ] Strong Gemini API key

### 4. Environment-Specific Files

**Development** (`.env`):
```env
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
MONGODB_URI=mongodb://localhost:27017
```

**Production** (Environment Variables):
```env
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=your-backend.onrender.com
MONGODB_URI=mongodb+srv://...
```

## 📝 Example Configurations

### Local Development

```env
# Core
DJANGO_SECRET_KEY=dev-secret-key-change-me
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:8080

# Database
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=agentdoc

# Storage
USE_LOCAL_STORAGE=1

# AI
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini/gemini-2.5-flash

# Email (MailHog)
SMTP_HOST=localhost
SMTP_PORT=1025
```

### Render Production

```env
# Core
DJANGO_SECRET_KEY=<auto-generated>
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=your-backend.onrender.com
DJANGO_CORS_ALLOWED_ORIGINS=https://your-frontend.onrender.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-frontend.onrender.com
DJANGO_SESSION_COOKIE_SECURE=1
DJANGO_CSRF_COOKIE_SECURE=1

# Database
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DB_NAME=agentdoc

# Storage
USE_LOCAL_STORAGE=1
MEDIA_ROOT=/opt/render/project/src/AgentDoc/backend/media

# AI
GEMINI_API_KEY=your-production-key
GEMINI_MODEL=gemini/gemini-2.5-flash

# URLs
REVIEW_PORTAL_URL=https://your-frontend.onrender.com/reviews
```

## 🆘 Troubleshooting

### Issue: CORS Errors

**Problem**: Frontend can't connect to backend

**Solution**: Check CORS settings
```env
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:5173
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:5173
```

### Issue: MongoDB Connection Failed

**Problem**: Can't connect to MongoDB

**Solution**: Check connection string
```env
# Local
MONGODB_URI=mongodb://localhost:27017

# Atlas
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
```

### Issue: Gemini API Errors

**Problem**: AI agents not working

**Solution**: Verify API key
```env
GEMINI_API_KEY=AIzaSy...your-valid-key
```

### Issue: Static Files Not Loading

**Problem**: CSS/JS not loading in production

**Solution**: Run collectstatic
```bash
python manage.py collectstatic --no-input
```

## 📚 Additional Resources

- [Setup Guide](SETUP_GUIDE.md)
- [Deployment Guide](DEPLOYMENT_RENDER.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Backend Structure](BACKEND_STRUCTURE.md)

---

**Last Updated**: 2024  
**Version**: 5-Agent System  
**Status**: Production Ready ✅
