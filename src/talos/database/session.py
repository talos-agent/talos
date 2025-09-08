import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .models import Base

_SessionLocal: Optional[sessionmaker] = None
_engine = None


def get_database_url() -> str:
    """Get database URL from environment or default to SQLite."""
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        # For SQLite URLs, ensure the directory exists
        if db_url.startswith("sqlite:///"):
            db_path = db_url[10:]  # Remove "sqlite:///" prefix
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
        return db_url

    db_path = os.path.join(os.getcwd(), "talos_data.db")
    return f"sqlite:///{db_path}"


def init_database(database_url: Optional[str] = None) -> None:
    """Initialize the database connection and create tables."""
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

    Base.metadata.create_all(bind=_engine)


def get_session() -> Session:
    """Get a database session."""
    if _SessionLocal is None:
        init_database()

    assert _SessionLocal is not None
    return _SessionLocal()
