#!/bin/bash

set -e

# Function to wait for a service to be ready
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    
    echo "Waiting for $service_name..."
    while ! nc -z "$host" "$port"; do
        sleep 1
    done
    echo "$service_name is ready!"
}

# Wait for database
wait_for_service db 5432 "PostgreSQL"

# Wait for Redis
wait_for_service redis 6379 "Redis"

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --settings=core.settings_production --noinput

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python manage.py shell --settings=core.settings_production << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', '${DJANGO_SUPERUSER_PASSWORD:-admin123}')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
EOF

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --settings=core.settings_production --noinput --clear

# Start the application
echo "Starting application..."
exec "$@"
