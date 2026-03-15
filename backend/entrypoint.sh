#!/bin/sh
set -e

python /app/scripts/wait_for_services.py
python manage.py migrate --noinput
python manage.py seed_demo --skip-if-present

exec "$@"
