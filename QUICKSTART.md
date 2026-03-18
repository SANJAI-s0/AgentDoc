# AgentDoc - Quick Start Guide

## 🚀 Deploy to Render (5 minutes)

### Prerequisites
- GitHub account
- Render account (free): https://render.com
- MongoDB Atlas account (free): https://cloud.mongodb.com
- Gemini API key: https://makersuite.google.com/app/apikey

### Step 1: Setup MongoDB Atlas (2 min)
1. Create free M0 cluster
2. Create database user
3. Whitelist all IPs: `0.0.0.0/0`
4. Copy connection string

### Step 2: Deploy on Render (3 min)
1. Fork this repository
2. Go to Render Dashboard
3. New → Blueprint
4. Connect your repository
5. Add environment variables:
   - `GEMINI_API_KEY`: Your Gemini key
   - `MONGODB_URI`: Your MongoDB connection string
   - `DJANGO_ALLOWED_HOSTS`: Your backend URL
   - `DJANGO_CORS_ALLOWED_ORIGINS`: Your frontend URL
   - `VITE_API_BASE`: Your backend API URL
6. Deploy!

### Step 3: Test
1. Visit your landing page URL
2. Click "Launch Demo"
3. Login: `customer_demo / DemoPass123!`

## 💻 Local Development

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Landing Page
```bash
cd landing-page
python -m http.server 8080
```

Visit:
- Landing: http://localhost:8080
- Frontend: http://localhost:5173
- Backend: http://localhost:8000

## 📝 Environment Variables

Create `.env` in project root:

```env
# Required
GEMINI_API_KEY=your_key_here
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/

# Optional (defaults shown)
MONGODB_DB_NAME=agentdoc
DJANGO_DEBUG=1
USE_LOCAL_STORAGE=1
```

## 🎯 5-Agent Workflow

1. **Classification** → Identifies document type
2. **Extraction** → Extracts structured data
3. **Validation** → Validates against rules
4. **Routing** → Auto-approve or review
5. **Audit** → Logs all decisions

## 📚 Next Steps

- Read [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) for overview
- Check [docs/DEPLOYMENT_RENDER.md](docs/DEPLOYMENT_RENDER.md) for detailed deployment
- Explore [landing-page/README.md](landing-page/README.md) for landing page docs
- Review [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for full setup instructions

## 🆘 Troubleshooting

**Backend won't start**
- Check MongoDB connection string
- Verify Gemini API key
- Ensure Python 3.11+

**Frontend can't connect**
- Check CORS settings
- Verify VITE_API_BASE
- Ensure backend is running

**Build timeout on Render**
- Use free tier limits
- Remove unused dependencies
- Check build logs

## 🎨 Customize Landing Page

Edit `landing-page/js/config.js`:
```javascript
const CONFIG = {
    demoUrl: 'YOUR_DEMO_URL',
    // ...
};
```

## 📦 What's Included

- ✅ Landing page (HTML/CSS/JS + GSAP)
- ✅ Backend API (Django + CrewAI)
- ✅ Frontend app (React + Vite)
- ✅ 5-agent system
- ✅ Demo data seeder
- ✅ Render deployment config
- ✅ Documentation

## 🔒 Security Notes

- Change demo passwords in production
- Use environment variables for secrets
- Enable HTTPS only
- Set secure cookie flags
- Whitelist specific IPs in MongoDB

## 📊 Free Tier Limits

- Services sleep after 15 min inactivity
- Cold start: 30-60 seconds
- Local storage is ephemeral
- 15 min max build time

## 🎉 Demo Credentials

- **Customer**: `customer_demo / DemoPass123!`
- **Reviewer**: `reviewer_demo / DemoPass123!`

## 📞 Support

- GitHub Issues for bugs
- Documentation for guides
- Demo for hands-on testing
