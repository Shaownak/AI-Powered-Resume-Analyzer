#!/bin/bash
# Start Django with environment variables for Docker integration

export REDIS_URL="redis://:redis_password@localhost:6379/0"
export AI_MICROSERVICE_URL="http://localhost:8001"
export DATABASE_URL="postgresql://postgres:shaownak@localhost:5432/resume-screener"

echo "Starting Django with environment variables:"
echo "REDIS_URL: $REDIS_URL"
echo "AI_MICROSERVICE_URL: $AI_MICROSERVICE_URL"
echo "DATABASE_URL: $DATABASE_URL"

python manage.py runserver 8000
