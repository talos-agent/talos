import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .models import Base

_SessionLocal: Optional[sessionmaker] = None
_engine = None


def get_database_url() -> str:
    """Get database URL from environment or default to SQLite."""
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url
    
    db_path = os.path.join(os.getcwd(), "talos_conversations.db")
    return f"sqlite:///{db_path}"


def init_database(database_url: Optional[str] = None) -> None:
    """Initialize the database connection and create tables."""
    global _SessionLocal, _engine
    
    if database_url is None:
        database_url = get_database_url()
    
    if database_url.startswith("sqlite"):
        _engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
    else:
        _engine = create_engine(database_url, echo=False)
    
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    
    Base.metadata.create_all(bind=_engine)


def get_session() -> Session:
    """Get a database session."""
    if _SessionLocal is None:
        init_database()
    
    return _SessionLocal()
