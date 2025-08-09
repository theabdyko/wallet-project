#!/bin/bash

# Set execution time limit to 4 seconds
ulimit -t 4

# Set memory limit to 2GB
ulimit -v 2097152

# Function to handle graceful shutdown
cleanup() {
    echo "Received shutdown signal, cleaning up..."
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Function to wait for database
wait_for_database() {
    echo "Waiting for database at $DB_HOST:$DB_PORT..."
    while ! nc -z $DB_HOST $DB_PORT; do
        sleep 1
    done
    echo "Database is ready!"
}

# Function to run development server
run_dev_app() {
    set -e
    echo "Starting Django development server..."
    
    # Export development settings
    export DJANGO_SETTINGS_MODULE=config.settings.dev
    
    # Wait for database
    wait_for_database
    
    # Run migrations
    echo "Running database migrations..."
    python manage.py migrate
    
    # Start Django development server
    echo "Starting Django development server on 0.0.0.0:8000..."
    exec python manage.py runserver 0.0.0.0:8000
}

# Function to run production server
run_prod_app() {
    set -e
    echo "Starting Django production server..."
    
    # Export production settings
    export DJANGO_SETTINGS_MODULE=config.settings.prod
    
    # Wait for database
    wait_for_database

    # Start Django with Gunicorn
    echo "Starting Django production server with Gunicorn on 0.0.0.0:8000..."
    exec gunicorn wallet-project.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --log-level=info
}

# Main script logic
case "${ENVIRONMENT:-dev}" in
    "prod"|"production")
        run_prod_app
        ;;
    "dev"|"development"|*)
        run_dev_app
        ;;
esac
