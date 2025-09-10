#!/usr/bin/env python3
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import create_engine

from talos.core.job_scheduler import JobScheduler
from talos.database import check_migration_status, init_database, run_migrations
from talos.server.jobs import IncrementCounterJob, TwapOHMJob

from .routes import routes

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: JobScheduler | None = None


def get_scheduler() -> JobScheduler | None:
    """Get the global scheduler instance."""
    return scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan with startup and shutdown events."""
    # Startup
    global scheduler
    try:
        # Initialize database connection
        init_database()

        # Get database engine for migration checks
        from talos.database.session import get_database_url

        database_url = get_database_url()
        engine = create_engine(database_url)

        # Check migration status
        migration_status = check_migration_status(engine)
        logger.info(f"Database migration status: {migration_status}")

        if migration_status["needs_migration"]:
            logger.info("Running database migrations...")
            run_migrations(engine)
            logger.info("Database migrations completed successfully")
        else:
            logger.info("Database is up to date")

        # Initialize job scheduler
        scheduler = JobScheduler(timezone="UTC")

        # Register example jobs
        increment_counter_job = IncrementCounterJob()
        scheduler.register_job(increment_counter_job)
        logger.info(f"Registered job: {increment_counter_job.name}")

        twap_ohm_job = TwapOHMJob()
        scheduler.register_job(twap_ohm_job)
        logger.info(f"Registered job: {twap_ohm_job.name}")

        # Start the scheduler
        scheduler.start()
        logger.info("Job scheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Talos API server")

    # Stop the scheduler
    if scheduler:
        scheduler.stop()
        logger.info("Job scheduler stopped")


app = FastAPI(
    title="Talos Test API",
    description="A simple REST API for testing purposes",
    version="0.1.3",
    lifespan=lifespan,
)

# Add scheduler to app state
app.state.get_scheduler = get_scheduler

app.include_router(routes)
