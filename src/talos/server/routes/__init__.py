from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Request
from sqlalchemy import create_engine

from talos.core.job_scheduler import JobScheduler
from talos.database import check_migration_status, get_session
from talos.database.models import Counter
from talos.utils import RoflClient

from .ohm_strategy import ohm_strategy_router

routes = APIRouter()
routes.include_router(ohm_strategy_router)


@routes.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {"message": "Talos API", "version": "0.1.3", "docs": "/docs", "status": "running"}


@routes.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@routes.get("/keys/generate/test")
async def generate_key_test() -> dict[str, str]:
    """Generate a key for testing purposes.  address should be 0x1eB5305647d0998C3373696629b2fE8E21eb10B9"""
    try:
        rofl_client = RoflClient()
        wallet = await rofl_client.get_wallet("test")
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


@routes.get("/tables")
async def tables_in_database() -> dict[str, list[str] | str]:
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


@routes.get("/counter")
async def get_counter() -> dict[str, int | str]:
    """Get counter."""
    with get_session() as session:
        counter = session.query(Counter).filter(Counter.name == "test").first()
        if counter:
            return {"value": counter.value}
        else:
            return {"value": 0}


@routes.post("/counter")
async def increment_counter() -> dict[str, int | str]:
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
            return {"value": counter.value}
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
