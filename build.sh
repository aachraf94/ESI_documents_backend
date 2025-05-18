#!/usr/bin/env bash

# ESI Document Backend Build Script
# This script prepares the application for deployment

# Exit on error, but allow specific commands to fail without stopping
set -o errexit

# Log function for better visibility
log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# Error handling function
handle_error() {
    log "ERROR: $1"
    exit 1
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verify prerequisites
log "Verifying prerequisites..."
command_exists python || handle_error "Python not found, please install Python 3.8+"
command_exists pip || handle_error "pip not found"

# Create necessary directories
log "Creating necessary directories..."
mkdir -p logs
mkdir -p staticfiles

# Install dependencies with proper error handling
log "Installing dependencies..."
pip install -r requirements.txt || handle_error "Failed to install dependencies"

# Validate critical environment variables
log "Validating environment variables..."
if [ -z "$DATABASE_URL" ] && [ -z "$DB_HOST" ]; then
    log "WARNING: No database configuration found. Using default or local settings."
fi

# Collect static files
log "Collecting static files..."
python manage.py collectstatic --no-input || handle_error "Failed to collect static files"

# Apply database migrations with retry logic
log "Applying database migrations..."
migration_attempts=0
max_attempts=3

until python manage.py migrate --no-input || [ $migration_attempts -ge $max_attempts ]
do
    migration_attempts=$((migration_attempts+1))
    log "Migration attempt $migration_attempts of $max_attempts failed, retrying in 5 seconds..."
    sleep 5
done

if [ $migration_attempts -ge $max_attempts ]; then
    handle_error "Failed to apply migrations after $max_attempts attempts"
fi

# Create superuser if it doesn't exist
log "Setting up superuser..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    if not User.objects.filter(email='admin@example.com').exists():
        # Create superuser without username parameter
        User.objects.create_superuser(
            email='admin@example.com', 
            first_name='Admin', 
            last_name='User', 
            password='adminpassword'
        )
        print("✅ Superuser created successfully")
    else:
        print("ℹ️ Superuser already exists")
except Exception as e:
    print(f"⚠️ Note: Could not create superuser: {str(e)}")
    # Continue even if superuser creation fails
    pass
END

# Verify the application is ready to start
log "Running application checks..."
python manage.py check --deploy || log "WARNING: Some deployment checks failed, review the output above"

log "Build completed successfully! 🚀"
