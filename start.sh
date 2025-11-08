#!/usr/bin/env bash
# Start script untuk Render

echo "Starting Traffic Automation Application..."
echo "Current directory: $(pwd)"
echo "Python path: $(which python)"
echo "Gunicorn check: $(python -c 'import gunicorn; print(\"Gunicorn available\")')"

# Gunakan gunicorn dengan Python module
python -m gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 app:app
