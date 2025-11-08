#!/usr/bin/env bash
# Build script untuk Render

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing Playwright browsers..."
python -m playwright install chromium
python -m playwright install-deps

echo "Creating necessary directories..."
mkdir -p logs
mkdir -p chrome_profiles

echo "Build completed successfully!"
