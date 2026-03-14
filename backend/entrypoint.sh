#!/bin/bash
set -e

echo "Starting Combat Sports Rankings backend..."

# Railway provides DATABASE_URL — derive sync version for alembic if not set
if [ -z "$DATABASE_URL_SYNC" ] && [ -n "$DATABASE_URL" ]; then
    export DATABASE_URL_SYNC=$(echo "$DATABASE_URL" | sed 's|postgres://|postgresql://|' | sed 's|postgresql+asyncpg://|postgresql://|')
    echo "Auto-derived DATABASE_URL_SYNC from DATABASE_URL"
fi

# Run database migrations (retry once if DB is still starting)
echo "Running database migrations..."
if ! alembic upgrade head 2>&1; then
    echo "Migration failed, retrying in 5 seconds..."
    sleep 5
    alembic upgrade head
fi

if [ "$RUN_SEED" = "true" ]; then
    echo "Seeding database..."
    python seed.py || echo "Seed script failed (may already be seeded)"
fi

echo "Starting server on port ${PORT:-8000}..."
exec gunicorn app.main:app \
    -w 2 \
    -k uvicorn.workers.UvicornWorker \
    --bind "0.0.0.0:${PORT:-8000}" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
