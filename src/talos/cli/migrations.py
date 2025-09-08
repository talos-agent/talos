"""CLI commands for database migrations."""

import typer
from sqlalchemy import create_engine

from talos.database import (
    run_migrations,
    check_migration_status,
    create_migration,
    get_current_revision,
    get_head_revision,
)
from talos.database.session import get_database_url

app = typer.Typer(help="Database migration commands")


@app.command()
def status() -> None:
    """Check the current migration status."""
    database_url = get_database_url()
    engine = create_engine(database_url)
    
    status_info = check_migration_status(engine)
    
    typer.echo("Database Migration Status:")
    typer.echo(f"  Current revision: {status_info['current_revision']}")
    typer.echo(f"  Head revision: {status_info['head_revision']}")
    typer.echo(f"  Up to date: {status_info['is_up_to_date']}")
    typer.echo(f"  Needs migration: {status_info['needs_migration']}")


@app.command()
def upgrade() -> None:
    """Run all pending migrations."""
    database_url = get_database_url()
    engine = create_engine(database_url)
    
    typer.echo("Running database migrations...")
    run_migrations(engine)
    typer.echo("Migrations completed successfully!")


@app.command()
def create(message: str = typer.Argument(..., help="Migration message")) -> None:
    """Create a new migration file."""
    typer.echo(f"Creating migration: {message}")
    revision = create_migration(message)
    typer.echo(f"Created migration with revision: {revision}")


@app.command()
def current() -> None:
    """Show the current database revision."""
    database_url = get_database_url()
    engine = create_engine(database_url)
    
    current_rev = get_current_revision(engine)
    typer.echo(f"Current database revision: {current_rev}")


@app.command()
def head() -> None:
    """Show the head revision."""
    head_rev = get_head_revision()
    typer.echo(f"Head revision: {head_rev}")


if __name__ == "__main__":
    app()
