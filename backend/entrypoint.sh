#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head

if [ "$RUN_SEED" = "true" ]; then
    echo "Seeding database..."
    python seed.py
fi

echo "Starting server on port ${PORT:-8000}..."
exec gunicorn app.main:app \
    -w 2 \
    -k uvicorn.workers.UvicornWorker \
    --bind "0.0.0.0:${PORT:-8000}" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
