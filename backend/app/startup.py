"""
Production startup script — replaces entrypoint.sh to avoid shell issues.
Runs migrations then starts uvicorn.
"""

import os
import sys
import traceback

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("=" * 50, flush=True)
print("COMBAT SPORTS RANKINGS — STARTING", flush=True)
print(f"Python: {sys.version}", flush=True)
print(f"CWD: {os.getcwd()}", flush=True)
print(f"PORT env: {os.environ.get('PORT', 'NOT SET')}", flush=True)
print(f"DATABASE_URL set: {'yes' if os.environ.get('DATABASE_URL') else 'NO'}", flush=True)
print("=" * 50, flush=True)


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
        print("[startup] Auto-derived DATABASE_URL_SYNC", flush=True)


def run_migrations():
    """Run alembic migrations — skip if they fail."""
    import subprocess
    import time

    print("[startup] Running database migrations...", flush=True)
    for attempt in range(2):
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("[startup] Migrations complete.", flush=True)
            return
        print(f"[startup] Migration attempt {attempt + 1} failed:", flush=True)
        print(f"  stdout: {result.stdout[:500]}", flush=True)
        print(f"  stderr: {result.stderr[:500]}", flush=True)
        if attempt == 0:
            time.sleep(3)
    print("[startup] WARNING: Migrations failed, starting server anyway...", flush=True)


def run_seed(force: bool = False):
    """Run the seed script if SEED_ON_START is set or force is True."""
    should_seed = os.environ.get("SEED_ON_START", "").lower() in ("1", "true", "yes")
    force_reseed = os.environ.get("FORCE_RESEED", "").lower() in ("1", "true", "yes")

    if should_seed or force or force_reseed:
        print(f"[startup] Running seed (force={force or force_reseed})...", flush=True)
        import asyncio
        from seed import seed
        asyncio.run(seed(force=force or force_reseed))
        # Clear the env var so it doesn't reseed on next restart
        if force_reseed:
            print("[startup] Seed complete. Clear FORCE_RESEED env var to prevent re-seeding.", flush=True)
    else:
        print("[startup] Skipping seed (set SEED_ON_START=1 or FORCE_RESEED=1 to seed)", flush=True)


def start_server():
    """Start uvicorn directly (simpler than gunicorn for initial deploy)."""
    port = int(os.environ.get("PORT", "8000"))
    print(f"[startup] Starting uvicorn on 0.0.0.0:{port}", flush=True)

    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        workers=1,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    try:
        derive_sync_url()
        run_migrations()
        run_seed()
        start_server()
    except Exception as e:
        print(f"[startup] FATAL ERROR: {e}", flush=True)
        traceback.print_exc()
        sys.exit(1)
