import os
from datetime import datetime
from typing import Any, Optional

from eth_rpc import PrivateKeyWallet
from eth_typing import HexStr
from fastapi import APIRouter, Request
from sqlalchemy import create_engine

from talos.core.job_scheduler import JobScheduler
from talos.database import check_migration_status, get_session
from talos.database.models import Counter
from talos.utils import RoflClient

routes = APIRouter()


@routes.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {"message": "Talos API", "version": "1.0.0", "docs": "/docs", "status": "running"}


@routes.post("/database/init")
async def database_init() -> dict[str, str]:
    """Initialize the database."""
    from talos.database import init_database

    try:
        init_database()
    except Exception as e:
        return {"error": str(e)}
    return {"message": "Database initialized"}


@routes.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@routes.get("/database/url")
async def database_url() -> dict[str, str]:
    """Get database URL."""
    from talos.database.session import get_database_url

    try:
        return {"url": get_database_url()}
    except Exception as e:
        return {"error": str(e)}


@routes.get("/keys/generate/test")
async def generate_key_test() -> dict[str, str]:
    """Generate a key for testing purposes."""
    try:
        rofl_client = RoflClient()
        key = await rofl_client.generate_key("test")
        wallet = PrivateKeyWallet(private_key=HexStr(key))
        return {"wallet": wallet.address}
    except PermissionError as pe:
        return {
            "error": f"ROFL service unavailable: {pe}",
            "suggestion": "Ensure ROFL daemon is running and socket is properly mounted",
        }
    except Exception as e:
        import traceback

        return {"error": str(e), "traceback": traceback.format_exc()}


@routes.get("/migrations/status")
async def migration_status() -> dict[str, Optional[str | bool]]:
    """Get database migration status."""
    from talos.database.session import get_database_url

    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        return check_migration_status(engine)
    except Exception as e:
        import traceback

        return {"error": str(e), "traceback": traceback.format_exc()}


@routes.get("/database/filepath")
async def database_filepath() -> dict[str, str]:
    """Get database filepath."""
    from talos.database.session import get_database_url

    try:
        url = get_database_url()
        # For SQLite URLs, extract the file path
        if url.startswith("sqlite:///"):
            # Handle both 3 and 4 slash variants
            path = url[10:] if url.startswith("sqlite:////") else url[9:]
            if os.path.exists(path):
                # List directory contents to help with debugging
                dir_path = os.path.dirname(path)
                if os.path.exists(dir_path):
                    files = os.listdir(dir_path)
                    return {"files": files}
                return {"error": f"Database file does not exist at path: {path}"}
            else:
                # Create directory if it doesn't exist
                dir_path = os.path.dirname(path)
                os.makedirs(dir_path, exist_ok=True)
                # Create empty database file
                with open(path, "a"):
                    os.utime(path, None)
                return {"filepath": path}

        return {"filepath": url}
    except Exception as e:
        import traceback

        return {"error": str(e), "traceback": traceback.format_exc()}


@routes.post("/database/migration")
async def database_migration() -> dict[str, str]:
    """Run database migrations."""
    from talos.database import run_migrations
    from talos.database.session import get_database_url

    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        run_migrations(engine)
        return {"message": "Database migrations completed successfully"}
    except Exception as e:
        import traceback

        return {"error": str(e), "traceback": traceback.format_exc()}


@routes.get("/tables")
async def tables_in_database() -> dict[str, list[str]]:
    """Get list of tables in the database."""
    from sqlalchemy import inspect

    from talos.database.session import get_database_url

    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return {"tables": tables}
    except Exception as e:
        import traceback

        return {"error": str(e), "traceback": traceback.format_exc()}


@routes.post("/counter")
async def increment_counter() -> dict[str, int]:
    """Increment counter."""
    try:
        with get_session() as session:
            counter = session.query(Counter).filter(Counter.name == "test").first()
            if not counter:
                counter = Counter(name="test", value=0)
                session.add(counter)
                session.commit()
                session.refresh(counter)
            counter.value += 1
            session.commit()
            return counter.value
    except Exception as e:
        import traceback

        return {"error": str(e), "traceback": traceback.format_exc()}


# Scheduler Management Routes


def _get_scheduler(request: Request) -> JobScheduler | None:
    """Get the scheduler instance from the app state."""
    return request.app.state.get_scheduler()


@routes.get("/scheduler/status")
async def scheduler_status(request: Request) -> dict[str, Any]:
    """Get scheduler status and information."""
    scheduler = _get_scheduler(request)
    if not scheduler:
        return {"error": "Scheduler not available"}

    return {"running": scheduler.is_running(), "timezone": scheduler.timezone, "job_count": len(scheduler.list_jobs())}


@routes.get("/scheduler/jobs")
async def list_scheduled_jobs(request: Request) -> dict[str, Any]:
    """List all scheduled jobs."""
    scheduler = _get_scheduler(request)
    if not scheduler:
        return {"error": "Scheduler not available"}

    jobs = scheduler.list_jobs()
    job_data = []

    for job in jobs:
        job_data.append(
            {
                "name": job.name,
                "description": job.description,
                "cron_expression": job.cron_expression,
                "execute_at": job.execute_at.isoformat() if job.execute_at else None,
                "enabled": job.enabled,
                "max_instances": job.max_instances,
                "is_recurring": job.is_recurring(),
                "is_one_time": job.is_one_time(),
            }
        )

    return {"jobs": job_data, "count": len(job_data)}


@routes.get("/scheduler/jobs/{job_name}")
async def get_scheduled_job(request: Request, job_name: str) -> dict[str, Any]:
    """Get a specific scheduled job by name."""
    scheduler = _get_scheduler(request)
    if not scheduler:
        return {"error": "Scheduler not available"}

    job = scheduler.get_job(job_name)
    if not job:
        return {"error": f"Job '{job_name}' not found"}

    return {
        "name": job.name,
        "description": job.description,
        "cron_expression": job.cron_expression,
        "execute_at": job.execute_at.isoformat() if job.execute_at else None,
        "enabled": job.enabled,
        "max_instances": job.max_instances,
        "is_recurring": job.is_recurring(),
        "is_one_time": job.is_one_time(),
    }


@routes.post("/scheduler/jobs/{job_name}/pause")
async def pause_scheduled_job(request: Request, job_name: str) -> dict[str, Any]:
    """Pause a scheduled job."""
    scheduler = _get_scheduler(request)
    if not scheduler:
        return {"error": "Scheduler not available"}

    success = scheduler.pause_job(job_name)
    if success:
        return {"message": f"Job '{job_name}' paused successfully"}
    else:
        return {"error": f"Failed to pause job '{job_name}'"}


@routes.post("/scheduler/jobs/{job_name}/resume")
async def resume_scheduled_job(request: Request, job_name: str) -> dict[str, Any]:
    """Resume a scheduled job."""
    scheduler = _get_scheduler(request)
    if not scheduler:
        return {"error": "Scheduler not available"}

    success = scheduler.resume_job(job_name)
    if success:
        return {"message": f"Job '{job_name}' resumed successfully"}
    else:
        return {"error": f"Failed to resume job '{job_name}'"}


@routes.delete("/scheduler/jobs/{job_name}")
async def remove_scheduled_job(request: Request, job_name: str) -> dict[str, Any]:
    """Remove a scheduled job."""
    scheduler = _get_scheduler(request)
    if not scheduler:
        return {"error": "Scheduler not available"}

    success = scheduler.unregister_job(job_name)
    if success:
        return {"message": f"Job '{job_name}' removed successfully"}
    else:
        return {"error": f"Failed to remove job '{job_name}'"}


@routes.post("/scheduler/start")
async def start_scheduler(request: Request) -> dict[str, Any]:
    """Start the scheduler."""
    scheduler = _get_scheduler(request)
    if not scheduler:
        return {"error": "Scheduler not available"}

    if scheduler.is_running():
        return {"message": "Scheduler is already running"}

    scheduler.start()
    return {"message": "Scheduler started successfully"}


@routes.post("/scheduler/stop")
async def stop_scheduler(request: Request) -> dict[str, Any]:
    """Stop the scheduler."""
    scheduler = _get_scheduler(request)
    if not scheduler:
        return {"error": "Scheduler not available"}

    if not scheduler.is_running():
        return {"message": "Scheduler is not running"}

    scheduler.stop()
    return {"message": "Scheduler stopped successfully"}
