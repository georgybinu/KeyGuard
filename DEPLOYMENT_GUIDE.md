# KeyGuard Render Deployment Guide

## Prerequisites
- GitHub account with the KeyGuard repository
- Render account (https://render.com)
- PostgreSQL database already created (✅ You have this!)

## Step 1: Prepare GitHub Repository

1. Initialize git (if not done):
   ```bash
   cd c:\Users\JONES JOSEPH\Desktop\KeyGuard
   git init
   git add .
   git commit -m "Initial commit: KeyGuard with PostgreSQL"
   ```

2. Create a GitHub repository and push:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/keyguard.git
   git branch -M main
   git push -u origin main
   ```

## Step 2: Test Locally with PostgreSQL

1. Install python-dotenv:
   ```bash
   cd backend
   pip install python-dotenv
   ```

2. Verify `.env` file exists with your database URL:
   ```
   DATABASE_URL=postgresql://keyguard_4pec_user:BoW3Pnv12uE8qvYAnBGczYk5xT3I84w1@dpg-d760qcfpm1nc73cn83og-a/keyguard_4pec
   ```

3. Initialize the database:
   ```bash
   python init_db.py
   ```
   You should see: ✅ Database initialized successfully!

4. Test the backend:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

5. In another terminal, test the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

## Step 3: Deploy to Render

### Option A: Using Render Dashboard (Recommended)

1. Go to https://render.com and log in
2. Click "New +" → "Web Service"
3. Connect your GitHub repository (KeyGuard)
4. Configure the backend service:
   - **Name**: `keyguard-backend`
   - **Runtime**: Python 3.11
   - **Build Command**: 
     ```bash
     cd backend && pip install -r requirements.txt && python init_db.py
     ```
   - **Start Command**:
     ```bash
     cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: Free tier is fine for testing

5. Add environment variable:
   - Click "Advanced" → "Add Environment Variable"
   - **Key**: `DATABASE_URL`
   - **Value**: `postgresql://keyguard_4pec_user:BoW3Pnv12uE8qvYAnBGczYk5xT3I84w1@dpg-d760qcfpm1nc73cn83og-a/keyguard_4pec`

6. Click "Create Web Service"

7. Wait for deployment (2-3 minutes)

8. Get your API URL: `https://keyguard-backend.onrender.com`

### Option B: Using render.yaml (Simpler)

1. Push the repo to GitHub
2. Go to https://render.com/dashboard
3. Click "New +" → "Blueprint"
4. Select your GitHub repository
5. Render will automatically read `render.yaml` and deploy both frontend and backend

## Step 4: Update Frontend API URL

After backend deployment, update the frontend to use the Render API URL:

Edit `frontend/src/lib/api.js`:
```javascript
const API_BASE_URL = process.env.VITE_API_URL || 'https://keyguard-backend.onrender.com';
```

Create `frontend/.env.production`:
```
VITE_API_URL=https://keyguard-backend.onrender.com
```

## Step 5: Verify Deployment

1. Check backend health:
   ```
   https://keyguard-backend.onrender.com/docs
   ```
   You should see Swagger API documentation

2. Test a sample API call:
   ```bash
   curl https://keyguard-backend.onrender.com/auth/status
   ```

## Troubleshooting

### Database Connection Error
- Verify `DATABASE_URL` is set in Render environment variables
- Check that your PostgreSQL password contains special characters (yours does - double check they're escaped if needed)
- Test connection locally first with `python init_db.py`

### Frontend Not Connecting to Backend
- Ensure `VITE_API_URL` is set correctly in frontend environment
- Check browser console for CORS issues
- Verify backend URL is accessible (test with curl)

### Build Failures
- Check build logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility (3.11 recommended)

## Environment Variables Summary

| Variable | Value |
|----------|-------|
| DATABASE_URL | `postgresql://keyguard_4pec_user:BoW3Pnv12uE8qvYAnBGczYk5xT3I84w1@dpg-d760qcfpm1nc73cn83og-a/keyguard_4pec` |
| VITE_API_URL | `https://keyguard-backend.onrender.com` (after deployment) |

## Next Steps

1. ✅ Test locally with PostgreSQL
2. ✅ Push to GitHub
3. ✅ Deploy backend to Render
4. ✅ Deploy frontend to Render
5. ✅ Verify both are communicating
6. ✅ Test login, training, and monitoring features

**Estimated deployment time**: 5-10 minutes after pushing to GitHub

Good luck! 🚀
