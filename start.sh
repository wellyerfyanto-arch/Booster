#!/usr/bin/env bash

echo "=== Starting Traffic Automation ==="
echo "Using PORT: $PORT"

python -m gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 app:app
