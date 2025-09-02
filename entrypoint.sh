#!/bin/bash
set -e

# Ensure the data directory exists (should already exist from Dockerfile)
mkdir -p /app/data

# Run migrations if needed
echo "Running database migrations..."
python -c "
from talos.database import init_database, run_migrations, check_migration_status
from talos.database.session import get_database_url
from sqlalchemy import create_engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    init_database()
    database_url = get_database_url()
    engine = create_engine(database_url)
    migration_status = check_migration_status(engine)
    logger.info(f'Database migration status: {migration_status}')

    if migration_status['needs_migration']:
        logger.info('Running database migrations...')
        run_migrations(engine)
        logger.info('Database migrations completed successfully')
    else:
        logger.info('Database is up to date')
except Exception as e:
    logger.error(f'Failed to run database migrations: {e}')
    exit(1)
"

# Execute the main command
exec "$@"
