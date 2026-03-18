#!/bin/sh
# Docker dev entrypoint — waits for MongoDB, runs migrations, seeds demo data
set -e

echo "[entrypoint] Waiting for services..."
python /app/scripts/wait_for_services.py

echo "[entrypoint] Running migrations..."
python manage.py migrate --noinput

echo "[entrypoint] Seeding demo data..."
python manage.py seed_demo --skip-if-present

echo "[entrypoint] Starting server..."
exec "$@"
