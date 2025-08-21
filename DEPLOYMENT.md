# NFL Draft App Deployment Guide

## Deploying to draft.joshengleman.com

This guide will help you deploy your NFL Draft app to `draft.joshengleman.com` using Railway hosting.

### Prerequisites
- GitHub account
- Railway account (free tier available)
- Access to your GoDaddy DNS settings

### Step 1: Prepare Your Code

1. **Initialize Git Repository** (if not already done):
```bash
git init
git add .
git commit -m "Initial deployment setup"
```

2. **Push to GitHub**:
```bash
# Create a new repository on GitHub first, then:
git remote add origin https://github.com/yourusername/nfl-draft-app.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Railway

1. **Sign up for Railway**: Go to [railway.app](https://railway.app)
2. **Connect GitHub**: Link your GitHub account
3. **Deploy Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `nfl-draft-app` repository
   - Railway will automatically detect it's a Python app

4. **Configure Environment**:
   - Railway will use the `railway.json` file automatically
   - No additional environment variables needed for basic setup

5. **Get Your Railway URL**:
   - After deployment, Railway will give you a URL like: `nfl-draft-app-production-abc123.up.railway.app`

### Step 3: Set up Custom Domain

1. **In Railway Dashboard**:
   - Go to your deployed app
   - Click "Settings" → "Domains"
   - Click "Custom Domain"
   - Enter: `draft.joshengleman.com`

2. **In GoDaddy DNS**:
   - Log into your GoDaddy account
   - Go to "My Products" → "DNS" for joshengleman.com
   - Add a new record:
     - **Type**: CNAME
     - **Name**: draft
     - **Value**: [your-railway-app-url] (the one from step 2.5)
     - **TTL**: 1 Hour (or default)

### Step 4: Test Your Deployment

1. Wait 5-10 minutes for DNS propagation
2. Visit `https://draft.joshengleman.com`
3. Your NFL Draft app should be live!

### Step 5: Update Data

Your app will need fresh data. You can either:

**Option A: Manual Update**
- Use the Admin Dashboard in the web app
- Click "Scrape Data" then "Process Data"

**Option B: Pre-populate Database**
- Run the scripts locally first
- Upload the `data/fantasy_pros.db` file to your repository

### Troubleshooting

**App won't start?**
- Check Railway logs in the dashboard
- Ensure all dependencies are in `requirements.txt`

**Domain not working?**
- DNS changes can take up to 24 hours
- Use the Railway URL directly to test the app first

**Data issues?**
- The app creates a fresh database on first run
- Use the Admin tab to download and process data

### Costs

- **Railway**: Free tier includes 500 hours/month (plenty for personal use)
- **GoDaddy**: No additional cost (using existing domain)

### Security Notes

- The app will be publicly accessible at draft.joshengleman.com
- Consider adding password protection if needed
- No sensitive data is exposed (just fantasy football projections)

### Updating the App

To update your deployed app:
```bash
git add .
git commit -m "Update description"
git push origin main
```

Railway will automatically redeploy when you push to GitHub!
