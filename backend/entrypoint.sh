#!/bin/bash
set -e

# Check if we're running as root (which we should be in entrypoint)
if [ "$(id -u)" = "0" ]; then
    # Ensure uploads directory exists with proper permissions
    mkdir -p /app/uploads/images
    chmod -R 755 /app/uploads || true
    
    # Change ownership to appuser
    if id appuser &>/dev/null; then
        chown -R appuser:appuser /app/uploads || true
    fi
    
    # Wait for database to be ready (if using PostgreSQL)
    if [ -n "$DATABASE_URL" ] && [[ "$DATABASE_URL" == postgresql* ]]; then
        echo "Waiting for PostgreSQL to be ready..."
        until python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null; do
            echo "PostgreSQL is unavailable - sleeping"
            sleep 1
        done
        echo "PostgreSQL is up!"
    fi
    
    # Initialize database structure (only if database is empty)
    # This runs only once when the container starts for the first time
    # Note: This only creates tables, no test data is inserted
    if [ ! -f /app/.db_initialized ]; then
        echo "Initializing database structure..."
        python init_prod_db.py && touch /app/.db_initialized || echo "Database initialization completed or skipped"
    else
        echo "Database already initialized, skipping..."
    fi
    
    # Switch to appuser and execute the command
    exec gosu appuser "$@"
else
    # If not running as root, just execute the command
    # Wait for database to be ready (if using PostgreSQL)
    if [ -n "$DATABASE_URL" ] && [[ "$DATABASE_URL" == postgresql* ]]; then
        echo "Waiting for PostgreSQL to be ready..."
        until python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null; do
            echo "PostgreSQL is unavailable - sleeping"
            sleep 1
        done
        echo "PostgreSQL is up!"
    fi
    
    # Initialize database structure
    if [ ! -f /app/.db_initialized ]; then
        echo "Initializing database structure..."
        python init_prod_db.py && touch /app/.db_initialized || echo "Database initialization completed or skipped"
    else
        echo "Database already initialized, skipping..."
    fi
    
    exec "$@"
fi

