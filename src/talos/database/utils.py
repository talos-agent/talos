from datetime import datetime, timedelta
from typing import Optional

from .models import User
from .session import get_session


def cleanup_temporary_users(older_than_hours: int = 24) -> int:
    """
    Clean up temporary users and their data older than specified hours.

    Args:
        older_than_hours: Remove temporary users inactive for this many hours

    Returns:
        Number of users cleaned up
    """
    cutoff_time = datetime.now() - timedelta(hours=older_than_hours)

    with get_session() as session:
        temp_users = session.query(User).filter(User.is_temporary, User.last_active < cutoff_time).all()

        count = len(temp_users)
        for user in temp_users:
            session.delete(user)  # Cascade will delete related data

        session.commit()
        return count


def get_user_stats() -> dict:
    """Get statistics about users in the database."""
    with get_session() as session:
        total_users = session.query(User).count()
        temp_users = session.query(User).filter(User.is_temporary).count()
        permanent_users = total_users - temp_users

        return {"total_users": total_users, "permanent_users": permanent_users, "temporary_users": temp_users}


def get_user_by_id(user_id: str) -> Optional[User]:
    """Get a user by their user_id."""
    with get_session() as session:
        return session.query(User).filter(User.user_id == user_id).first()
