#!/usr/bin/env bash

echo "=========================================="
echo "🚀 Starting Real Browser Automation"
echo "=========================================="

echo "📊 Environment Info:"
echo "   PORT: $PORT"
echo "   PWD: $(pwd)"
echo "   Python: $(python --version)"

echo "🔍 Checking installations:"
python -c "import playwright; print('   Playwright: OK')"
python -c "import flask; print('   Flask: OK')"

echo "📁 Directory contents:"
ls -la

echo "🔧 Starting server..."
python -m gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 app:app
