#!/usr/bin/env bash

echo "=== Installing Python Dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Installing Playwright Browser ==="
python -m playwright install chromium

echo "=== Creating Directories ==="
mkdir -p logs
mkdir -p chrome_profiles

echo "=== Verification ==="
python -c "import flask; print('✓ Flask installed')"
python -c "import playwright; print('✓ Playwright installed')"
python -c "import gunicorn; print('✓ Gunicorn installed')"

echo "=== Build Completed Successfully ==="
