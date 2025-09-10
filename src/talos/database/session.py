import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Note: Base is imported for potential future use but not currently needed
# from .models import Base

_SessionLocal: Optional[sessionmaker] = None
_engine = None


def get_database_url() -> str:
    """Get database URL from environment or default to SQLite."""
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        # For SQLite URLs, ensure the directory exists
        if db_url.startswith("sqlite:////"):
            db_path = db_url[10:]  # Remove "sqlite:///" prefix
            # Make path absolute if it's not already
            if not os.path.isabs(db_path):
                db_path = f"/{db_path}"  # Add leading slash for absolute path
            print("DB PATH:", db_path)
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            # Convert to 4-slash format for absolute paths
            if os.path.isabs(db_path):
                db_url = f"sqlite:////{db_path}"
        return db_url

    db_path = "/app/data"
    if not os.path.exists(db_path):
        os.makedirs(db_path, exist_ok=True)
    return f"sqlite:///{db_path}/talos_data.db"


def init_database(database_url: Optional[str] = None) -> None:
    """Initialize the database connection."""
    global _SessionLocal, _engine

    if database_url is None:
        database_url = get_database_url()

    if database_url.startswith("sqlite"):
        _engine = create_engine(
            database_url, connect_args={"check_same_thread": False}, poolclass=StaticPool, echo=False
        )
    else:
        _engine = create_engine(database_url, echo=False)

    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

    # Note: Tables are created by Alembic migrations, not here


def get_session() -> Session:
    """Get a database session."""
    if _SessionLocal is None:
        init_database()

    assert _SessionLocal is not None
    return _SessionLocal()
