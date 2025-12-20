# Deployment Guide

## GSI Reference Architecture Generator

This guide covers deploying the application to production using Vercel (frontend) and Railway or Render (backend).

---

## Prerequisites

Before deploying, ensure you have:

- [ ] GitHub account with the repository pushed
- [ ] Anthropic API key from [console.anthropic.com](https://console.anthropic.com)
- [ ] Vercel account (free tier available)
- [ ] Railway or Render account (free tier available)

---

## Backend Deployment

### Option A: Railway

Railway provides easy Python deployment with automatic builds.

#### Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Select the `backend` directory as the root

#### Step 2: Configure Environment Variables

In the Railway dashboard, go to Variables and add:

| Variable | Value |
|----------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `CORS_ORIGINS` | Your Vercel frontend URL (e.g., `https://your-app.vercel.app`) |
| `ENVIRONMENT` | `production` |

#### Step 3: Configure Build Settings

Railway should auto-detect Python. If not, set:

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### Step 4: Deploy

Click "Deploy" and wait for the build to complete. Note your Railway URL (e.g., `https://your-app.up.railway.app`).

---

### Option B: Render

Render offers a generous free tier for Python applications.

#### Step 1: Create Render Web Service

1. Go to [render.com](https://render.com) and sign in
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `gsi-architecture-generator-api`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### Step 2: Configure Environment Variables

In the Render dashboard, add environment variables:

| Variable | Value |
|----------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `CORS_ORIGINS` | Your Vercel frontend URL |
| `ENVIRONMENT` | `production` |

#### Step 3: Deploy

Click "Create Web Service" and wait for deployment. Note your Render URL (e.g., `https://your-app.onrender.com`).

---

## Frontend Deployment

### Vercel

Vercel is optimized for React/Vite applications.

#### Step 1: Import Project

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

#### Step 2: Configure Environment Variables

Add the following environment variable:

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | Your backend URL (Railway or Render) |

**Important**: The variable must be prefixed with `VITE_` for Vite to include it in the build.

#### Step 3: Deploy

Click "Deploy" and wait for the build. Your app will be available at `https://your-project.vercel.app`.

---

## Post-Deployment Verification

### 1. Check Backend Health

```bash
curl https://your-backend-url.com/api/health
```

Expected response:
```json
{"status":"healthy","service":"gsi-architecture-generator"}
```

### 2. Check Frontend

1. Open your Vercel URL in a browser
2. Verify the form loads correctly
3. Try generating an architecture

### 3. Test End-to-End

1. Select any configuration options
2. Click "Generate Architecture"
3. Verify all four tabs display content
4. Test copy and download buttons

---

## Updating CORS After Deployment

After deploying the frontend, update the backend's `CORS_ORIGINS`:

1. Go to your Railway/Render dashboard
2. Update the `CORS_ORIGINS` variable to your Vercel URL
3. Redeploy the backend

**Multiple Origins**: Separate with commas:
```
https://your-app.vercel.app,https://your-custom-domain.com
```

---

## Custom Domain (Optional)

### Vercel Custom Domain

1. Go to Project Settings → Domains
2. Add your domain
3. Configure DNS as instructed
4. Update backend `CORS_ORIGINS` to include the new domain

### Railway/Render Custom Domain

Both platforms support custom domains in their settings. Configure DNS according to their documentation.

---

## Monitoring and Logs

### Railway Logs

- View in Railway dashboard → Deployments → View Logs
- Real-time log streaming available

### Render Logs

- View in Render dashboard → Service → Logs
- Search and filter available

### Vercel Logs

- View in Vercel dashboard → Deployments → Functions
- Real-time and historical logs available

---

## Troubleshooting

### Frontend shows "Failed to generate architecture"

**Possible causes**:
1. Backend not running or wrong URL
2. CORS not configured correctly
3. Network/firewall issues

**Solutions**:
1. Verify `VITE_API_URL` points to correct backend
2. Check backend `CORS_ORIGINS` includes frontend URL
3. Check backend logs for errors

### Backend returns 503 "Service not initialized"

**Cause**: Missing or invalid `ANTHROPIC_API_KEY`

**Solution**: Verify the API key is set correctly in environment variables

### Backend returns 500 "Failed to parse Claude response"

**Cause**: Claude API returned truncated or invalid JSON

**Solutions**:
1. Retry the request
2. Check Claude API status at [status.anthropic.com](https://status.anthropic.com)
3. Verify API key has sufficient quota

### Slow response times

**Cause**: Claude API processing time

**Solutions**:
1. This is expected (5-10 seconds for generation)
2. Consider Railway/Render paid tiers for better performance
3. Render free tier spins down after inactivity (cold starts)

### CORS errors in browser console

**Cause**: Backend CORS not configured for frontend origin

**Solution**:
1. Check `CORS_ORIGINS` environment variable
2. Ensure no trailing slashes in URLs
3. Redeploy backend after updating

---

## Cost Considerations

### Vercel (Frontend)
- Free tier: 100GB bandwidth/month, sufficient for most use cases
- Pro tier: $20/month for more bandwidth and features

### Railway (Backend)
- Free tier: $5 of usage/month
- Hobby tier: $5/month + usage

### Render (Backend)
- Free tier: 750 hours/month, spins down after 15 minutes inactivity
- Starter tier: $7/month for always-on

### Anthropic API
- Pay-per-token pricing
- Estimate ~$0.02-0.05 per architecture generation
- Monitor usage in Anthropic console

---

## Security Checklist

Before going live:

- [ ] `ANTHROPIC_API_KEY` is set as environment variable (not in code)
- [ ] `CORS_ORIGINS` is set to specific domain (not `*`)
- [ ] `ENVIRONMENT` is set to `production`
- [ ] HTTPS is enabled (automatic on Vercel/Railway/Render)
- [ ] No sensitive data in git repository
- [ ] `.env` files are in `.gitignore`
