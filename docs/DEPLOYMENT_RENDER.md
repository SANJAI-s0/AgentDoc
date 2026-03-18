# AgentDoc Deployment Guide - Render Free Tier

## Quick Deploy (5 minutes)

### Prerequisites
1. GitHub account with this repository
2. Render account (free): https://render.com
3. MongoDB Atlas account (free): https://cloud.mongodb.com
4. Google Gemini API key: https://makersuite.google.com/app/apikey

### Step 1: Setup MongoDB Atlas
1. Create free M0 cluster
2. Create database user with password
3. Whitelist all IPs: `0.0.0.0/0`
4. Copy connection string: `mongodb+srv://user:pass@cluster.mongodb.net/`

### Step 2: Deploy on Render
1. Go to Render Dashboard
2. New → Blueprint
3. Connect your GitHub repository
4. Render will detect `render.yaml`

### Step 3: Configure Environment Variables

**Backend:**
```
GEMINI_API_KEY=<your-key>
MONGODB_URI=<your-mongodb-uri>
DJANGO_ALLOWED_HOSTS=<backend-url>.onrender.com
DJANGO_CORS_ALLOWED_ORIGINS=https://<frontend-url>.onrender.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://<frontend-url>.onrender.com
```

**Frontend:**
```
VITE_API_BASE=https://<backend-url>.onrender.com/api
```

### Step 4: Test
1. Visit landing page
2. Click "Launch Demo"
3. Login: `customer_demo / DemoPass123!`

## Free Tier Limitations
- Services sleep after 15 min inactivity
- Cold start: 30-60 seconds
- Local storage is ephemeral
- 15 min max build time
