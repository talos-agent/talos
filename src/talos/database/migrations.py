"""Database migration utilities using Alembic."""

import os
from typing import Optional

from sqlalchemy.engine import Engine

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory

from .session import get_database_url


def get_alembic_config() -> Config:
    """Get Alembic configuration."""
    # Get the project root directory (go up from src/talos/database to project root)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    alembic_cfg_path = os.path.join(project_root, "alembic.ini")

    # Change to the project root directory so relative paths work
    original_cwd = os.getcwd()
    os.chdir(project_root)

    try:
        config = Config(alembic_cfg_path)

        # Override the database URL with environment variable if available
        database_url = get_database_url()
        config.set_main_option("sqlalchemy.url", database_url)

        # Set the prepend_sys_path to include the src directory
        src_dir = os.path.join(project_root, "src")
        config.set_main_option("prepend_sys_path", src_dir)

        return config
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


def get_current_revision(engine: Engine) -> Optional[str]:
    """Get the current database revision."""
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        return context.get_current_revision()


def get_head_revision() -> str:
    """Get the head revision from the migration scripts."""
    config = get_alembic_config()
    script_dir = ScriptDirectory.from_config(config)
    return script_dir.get_current_head()


def is_database_up_to_date(engine: Engine) -> bool:
    """Check if the database is up to date with the latest migration."""
    current_revision = get_current_revision(engine)
    head_revision = get_head_revision()
    return current_revision == head_revision


def run_migrations(engine: Engine) -> None:
    """Run all pending migrations."""
    config = get_alembic_config()

    # Set the database URL in the config
    database_url = get_database_url()
    config.set_main_option("sqlalchemy.url", database_url)

    # Run migrations
    command.upgrade(config, "head")


def run_migrations_to_revision(engine: Engine, revision: str) -> None:
    """Run migrations to a specific revision."""
    config = get_alembic_config()

    # Set the database URL in the config
    database_url = get_database_url()
    config.set_main_option("sqlalchemy.url", database_url)

    # Run migrations to specific revision
    command.upgrade(config, revision)


def create_migration(message: str) -> Optional[str]:
    """Create a new migration file."""
    config = get_alembic_config()

    # Set the database URL in the config
    database_url = get_database_url()
    config.set_main_option("sqlalchemy.url", database_url)

    # Create migration
    command.revision(config, message=message, autogenerate=True)

    # Get the latest migration file
    script_dir = ScriptDirectory.from_config(config)
    head_revision = script_dir.get_current_head()
    return head_revision


def check_migration_status(engine: Engine) -> dict[str, str | bool | None]:
    """Check the current migration status."""
    current_revision = get_current_revision(engine)
    head_revision = get_head_revision()
    is_up_to_date = current_revision == head_revision

    return {
        "current_revision": current_revision,
        "head_revision": head_revision,
        "is_up_to_date": is_up_to_date,
        "needs_migration": not is_up_to_date,
    }
