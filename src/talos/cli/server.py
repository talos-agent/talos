#!/usr/bin/env python3
"""
Simple REST API server for testing purposes.
Runs on port 8000 with basic CRUD endpoints.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from eth_rpc import PrivateKeyWallet
from eth_typing import HexStr
from fastapi import FastAPI
from sqlalchemy import create_engine

from talos.database import check_migration_status, init_database, run_migrations
from talos.utils import RoflClient

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan with startup and shutdown events."""
    # Startup
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

    except Exception as e:
        logger.error(f"Failed to run database migrations: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Talos API server")


app = FastAPI(
    title="Talos Test API",
    description="A simple REST API for testing purposes",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {"message": "Talos API", "version": "1.0.0", "docs": "/docs", "status": "running"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/keys/generate/test")
async def generate_key_test() -> dict[str, str]:
    """Generate a key for testing purposes."""
    rofl_client = RoflClient()
    key = await rofl_client.generate_key("test")
    wallet = PrivateKeyWallet(private_key=HexStr(key))
    return {"wallet": wallet.address}


@app.get("/migrations/status")
async def migration_status() -> dict[str, Optional[str | bool]]:
    """Get database migration status."""
    from talos.database.session import get_database_url

    database_url = get_database_url()
    engine = create_engine(database_url)
    return check_migration_status(engine)


@app.get("/tables")
async def tables_in_database() -> dict[str, list[str]]:
    """Get list of tables in the database."""
    from sqlalchemy import inspect

    from talos.database.session import get_database_url

    database_url = get_database_url()
    engine = create_engine(database_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return {"tables": tables}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
