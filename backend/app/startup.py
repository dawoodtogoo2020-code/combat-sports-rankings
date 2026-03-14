"""
Production startup script — replaces entrypoint.sh to avoid shell issues.
Runs migrations then starts gunicorn.
"""

import os
import subprocess
import sys
import time


def derive_sync_url():
    """Auto-derive DATABASE_URL_SYNC from DATABASE_URL if not set."""
    db_url = os.environ.get("DATABASE_URL", "")
    if not os.environ.get("DATABASE_URL_SYNC") and db_url:
        sync_url = db_url
        if sync_url.startswith("postgres://"):
            sync_url = sync_url.replace("postgres://", "postgresql://", 1)
        elif "asyncpg" in sync_url:
            sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql://", 1)
        os.environ["DATABASE_URL_SYNC"] = sync_url
        print(f"Auto-derived DATABASE_URL_SYNC from DATABASE_URL")


def run_migrations():
    """Run alembic migrations with retry."""
    print("Running database migrations...")
    for attempt in range(2):
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("Migrations complete.")
            return
        print(f"Migration attempt {attempt + 1} failed: {result.stderr}")
        if attempt == 0:
            print("Retrying in 5 seconds...")
            time.sleep(5)
    print("WARNING: Migrations failed, starting server anyway...")


def run_seed():
    """Run seed script if RUN_SEED=true."""
    if os.environ.get("RUN_SEED", "").lower() == "true":
        print("Seeding database...")
        result = subprocess.run(
            [sys.executable, "seed.py"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Seed failed (may already be seeded): {result.stderr[:200]}")
        else:
            print("Seeding complete.")


def start_server():
    """Start gunicorn with uvicorn workers."""
    port = os.environ.get("PORT", "8000")
    print(f"Starting server on port {port}...")
    os.execvp("gunicorn", [
        "gunicorn",
        "app.main:app",
        "-w", "2",
        "-k", "uvicorn.workers.UvicornWorker",
        "--bind", f"0.0.0.0:{port}",
        "--timeout", "120",
        "--access-logfile", "-",
        "--error-logfile", "-",
    ])


if __name__ == "__main__":
    print("Starting Combat Sports Rankings backend...")
    derive_sync_url()
    run_migrations()
    run_seed()
    start_server()
