#!/bin/bash
set -e

# Wait for database to be ready (if using PostgreSQL)
if [ -n "$DATABASE_URL" ] && [[ "$DATABASE_URL" == postgresql* ]]; then
    echo "Waiting for PostgreSQL to be ready..."
    until python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    echo "PostgreSQL is up!"
fi

# Initialize database with test data (only if database is empty)
# This runs only once when the container starts for the first time
if [ ! -f /app/.db_initialized ]; then
    echo "Initializing database with test data..."
    python init_db.py && touch /app/.db_initialized || echo "Database initialization completed or skipped"
else
    echo "Database already initialized, skipping..."
fi

# Start the application
exec "$@"

