#!/usr/bin/env bash

echo "=========================================="
echo "🚀 Building Real Browser Automation"
echo "=========================================="

echo "1. Updating pip..."
python -m pip install --upgrade pip

echo "2. Installing Python dependencies..."
pip install -r requirements.txt

echo "3. Installing Playwright browser..."
python -m playwright install chromium
python -m playwright install-deps

echo "4. Creating necessary directories..."
mkdir -p templates
mkdir -p logs
mkdir -p chrome_profiles

echo "5. Verifying installations..."
python -c "import flask; print('✅ Flask installed')"
python -c "import playwright; print('✅ Playwright installed')"
python -c "import gunicorn; print('✅ Gunicorn installed')"

echo "6. Directory structure:"
ls -la
echo "Templates:"
ls -la templates/

echo "=========================================="
echo "✅ Build completed successfully!"
echo "=========================================="
