#!/usr/bin/env bash

echo "=== Installing Python Dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Installing Playwright Browser ==="
python -m playwright install chromium

echo "=== Creating Necessary Directories ==="
mkdir -p logs
mkdir -p chrome_profiles

echo "=== Build Completed ==="
