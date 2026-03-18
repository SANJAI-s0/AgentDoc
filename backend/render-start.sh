#!/usr/bin/env bash
# Render start command — runs after buildCommand completes
set -e

echo "[render-start] Running migrations..."
python manage.py migrate --noinput

echo "[render-start] Seeding demo data..."
python manage.py seed_demo --skip-if-present

echo "[render-start] Starting gunicorn..."
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${GUNICORN_WORKERS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-120}" \
  --access-logfile - \
  --error-logfile -
