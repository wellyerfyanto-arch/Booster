#!/usr/bin/env bash
# Start script untuk Render

echo "Starting Traffic Automation Application..."
gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 app:app
