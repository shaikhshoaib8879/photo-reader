# 🚀 Photo Reader OCR - Deployment Guide

## 📋 Prerequisites

1. **Tesseract OCR** must be installed on the deployment platform
2. **Python 3.12** or compatible version
3. **Git repository** pushed to GitHub/GitLab

## 🌐 Deployment Options

### Option 1: Render (Recommended)

#### Step 1: Prepare Your Repository
```bash
# Ensure all files are committed
git add .
git commit -m "Prepare for deployment"
git push origin main
```

#### Step 2: Deploy on Render
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository (`shaikhshoaib8879/photo-reader`)
4. Configure deployment:
   - **Name:** `photo-reader-ocr`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd backend && gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
   - **Instance Type:** `Free`

#### Step 3: Set Environment Variables (if needed)
- `PYTHON_VERSION=3.12`
- PORT is automatically set by Render

#### Step 4: Install System Dependencies
In Render dashboard, add this to your build command:
```bash
apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-eng && pip install -r requirements.txt
```

### Option 2: Railway

#### Step 1: Deploy on Railway
1. Go to [railway.app](https://railway.app) and sign up/login
2. Click "Deploy from GitHub repo"
3. Select your repository (`shaikhshoaib8879/photo-reader`)
4. Railway will automatically detect Python and use the `railway.toml` config

#### Step 2: Add Environment Variables (if needed)
- Railway should auto-detect everything from the config file

### Option 3: Heroku (If you have access)

#### Step 1: Install Heroku CLI and login
```bash
# Install Heroku CLI (if not installed)
curl https://cli-assets.heroku.com/install.sh | sh

# Login to Heroku
heroku login
```

#### Step 2: Create and deploy
```bash
# Create Heroku app
heroku create photo-reader-ocr-your-name

# Add tesseract buildpack
heroku buildpacks:add --index 1 heroku-community/apt
heroku buildpacks:add --index 2 heroku/python

# Create Aptfile for tesseract
echo "tesseract-ocr
tesseract-ocr-eng" > Aptfile

# Deploy
git add .
git commit -m "Add Heroku config"
git push heroku main
```

## 🧪 Local Testing with Production Setup

### Step 1: Create Fresh Virtual Environment
```bash
# Navigate to project root
cd /home/shoaib-shaikh/photo-reader

# Remove old venv if exists
rm -rf venv

# Create new virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### Step 2: Install Production Dependencies
```bash
# Install from the production requirements
pip install -r requirements.txt

# If torch CPU versions fail, install manually:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Step 3: Test with Gunicorn Locally
```bash
# Test the production server setup
cd backend
gunicorn app:app --bind 127.0.0.1:8001 --workers 1 --timeout 120

# Your app should now be running at http://127.0.0.1:8001
```

### Step 4: Test Frontend Connection
```bash
# In another terminal, serve frontend
cd frontend
python3 -m http.server 3000

# Update frontend to point to your deployed backend URL
# Edit index.html and change localhost:8001 to your Render/Railway URL
```

## 📱 Frontend Deployment (Optional)

### Deploy Frontend to Netlify/Vercel
```bash
# For Netlify Drop (drag and drop)
1. Build a simple dist folder:
mkdir dist
cp frontend/* dist/

# Update the API URL in index.html to your deployed backend
# Then drag dist folder to netlify.com/drop

# For Vercel
npx vercel
# Follow prompts and deploy frontend folder
```

## 🔧 Troubleshooting

### Common Issues:

1. **Tesseract not found:**
   - Ensure tesseract is installed on the platform
   - For Render: Add tesseract installation to build command

2. **PyTorch CPU installation fails:**
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
   ```

3. **Memory issues on free tier:**
   - Use CPU-only versions (already configured)
   - Reduce worker count to 1 (already set)
   - Increase timeout (already set to 120s)

4. **CORS errors:**
   - Update frontend API URL to match deployed backend
   - Ensure CORS is properly configured (already done)

## 🎯 Quick Deploy Commands

### For Render:
```bash
# 1. Push to GitHub
git add . && git commit -m "Deploy to Render" && git push

# 2. Use these settings in Render:
# Build: apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-eng && pip install -r requirements.txt
# Start: cd backend && gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

### For Railway:
```bash
# 1. Push to GitHub
git add . && git commit -m "Deploy to Railway" && git push

# 2. Railway will auto-deploy using railway.toml config
```

## 📊 Expected Deployment URL Structure:
- **Backend API:** `https://your-app-name.render.com` or `https://your-app-name.up.railway.app`
- **Health check:** `https://your-app-name.render.com/health`
- **OCR endpoint:** `https://your-app-name.render.com/ocr`

Your app will be ready to process image uploads and extract text using both Tesseract and EasyOCR! 🎉