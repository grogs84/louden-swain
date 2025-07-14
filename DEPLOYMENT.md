# Wrestling App Deployment Guide

## Quick Deployment Options for Team Demo

### Option 1: Frontend-Only Demo (Fastest - 5 minutes)

**Deploy React Frontend to Vercel (Free)**

1. **From frontend directory:**
   ```bash
   cd frontend
   npx vercel
   ```
   
2. **Follow prompts:**
   - Login with GitHub/Google/email
   - Select your project settings
   - Deploy!

**Result:** Your team gets a live URL like `https://your-app.vercel.app`

**Note:** This will show the UI but API calls won't work (backend not deployed)

---

### Option 2: Full-Stack Demo (15 minutes)

**A. Deploy Backend to Railway/Render (Free tier)**

**Railway (Recommended):**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "Deploy from GitHub repo"
4. Connect your `louden-swain` repository
5. Select `/backend` as root directory
6. Add environment variables:
   ```
   DATABASE_URL=postgresql://user:password@hostname:port/database
   ```
7. Railway will auto-deploy your FastAPI app

**B. Deploy Frontend with Backend URL**
1. Update `frontend/.env`:
   ```bash
   REACT_APP_API_URL=https://your-backend.railway.app/api
   ```
2. Deploy frontend to Vercel:
   ```bash
   cd frontend
   npx vercel
   ```

---

### Option 3: Docker Deployment (Production-Ready)

**Use existing docker-compose.yml:**

1. **On any server with Docker:**
   ```bash
   git clone your-repo
   cd louden-swain
   docker-compose up -d
   ```

2. **Access:**
   - Frontend: `http://your-server:3000`
   - Backend: `http://your-server:8000`

---

## Quick Demo Instructions for Your Team

### What to Show:

1. **Home Page** - Clean landing page with navigation
2. **Search Function** - Search for "Taylor" or "Penn State"
3. **Wrestler Profiles** - Click on any wrestler result
4. **School Pages** - Browse school information
5. **API Documentation** - Show `your-backend-url/docs`

### Sample Data Available:
- 5 wrestlers (David Taylor, Kyle Dake, Bo Nickal, etc.)
- 5 schools (Penn State, Iowa, Oklahoma State, etc.)
- Search functionality works for names and schools

---

## Environment Variables Needed

### Backend (.env):
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
CORS_ORIGINS=https://your-frontend-url.vercel.app
```

### Frontend (.env):
```bash
REACT_APP_API_URL=https://your-backend.railway.app/api
```

---

## Free Tier Limits

- **Vercel:** Unlimited frontend deployments
- **Railway:** 500 hours/month + $5 credit
- **Render:** 750 hours/month free

Perfect for team demos and development!
