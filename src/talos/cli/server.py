#!/usr/bin/env python3
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from eth_rpc import PrivateKeyWallet
from eth_typing import HexStr
from fastapi import FastAPI
from sqlalchemy import create_engine

from talos.database import check_migration_status
from talos.utils import RoflClient

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan with startup and shutdown events."""
    # Startup
    # try:
    #     # Initialize database connection
    #     init_database()

    #     # Get database engine for migration checks
    #     from talos.database.session import get_database_url

    #     database_url = get_database_url()
    #     engine = create_engine(database_url)

    #     # Check migration status
    #     migration_status = check_migration_status(engine)
    #     logger.info(f"Database migration status: {migration_status}")

    #     if migration_status["needs_migration"]:
    #         logger.info("Running database migrations...")
    #         run_migrations(engine)
    #         logger.info("Database migrations completed successfully")
    #     else:
    #         logger.info("Database is up to date")

    # except Exception as e:
    #     logger.error(f"Failed to run database migrations: {e}")
    #     raise

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


@app.post("/database/init")
async def database_init() -> dict[str, str]:
    """Initialize the database."""
    from talos.database import init_database

    try:
        init_database()
    except Exception as e:
        return {"error": str(e)}
    return {"message": "Database initialized"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/database/url")
async def database_url() -> dict[str, str]:
    """Get database URL."""
    from talos.database.session import get_database_url

    try:
        return {"url": get_database_url()}
    except Exception as e:
        return {"error": str(e)}


@app.get("/keys/generate/test")
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


@app.get("/migrations/status")
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


@app.get("/database/filepath")
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


@app.get("/database/migration")
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


@app.get("/tables")
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7000)
