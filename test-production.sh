#!/bin/bash

# 🧪 Local Production Test Script
# This script sets up and tests your app in production mode locally

echo "🚀 Photo Reader OCR - Local Production Test"
echo "============================================"

# Check if we're in the right directory
if [ ! -f "backend/app.py" ]; then
    echo "❌ Error: Please run this script from the photo-reader root directory"
    exit 1
fi

# Create fresh virtual environment
echo "📦 Creating fresh virtual environment..."
rm -rf venv
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install production dependencies
echo "📥 Installing production dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# If torch installation fails, try CPU-only versions
if [ $? -ne 0 ]; then
    echo "⚠️  Installing CPU-only PyTorch versions..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# Test with gunicorn
echo "🌐 Starting production server with Gunicorn..."
echo "   Backend will be available at: http://127.0.0.1:8001"
echo "   Health check: http://127.0.0.1:8001/health"
echo "   Press Ctrl+C to stop"
echo ""

cd backend
PORT=8001 gunicorn app:app --bind 127.0.0.1:8001 --workers 1 --timeout 120 --reload