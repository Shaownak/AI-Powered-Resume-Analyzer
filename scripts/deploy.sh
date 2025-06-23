#!/bin/bash

# Production deployment script
# Usage: ./scripts/deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
COMPOSE_FILE="docker-compose.${ENVIRONMENT}.yml"

echo "🚀 Deploying Resume Screener Platform to ${ENVIRONMENT}..."

# Check if compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo "❌ Error: $COMPOSE_FILE not found!"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found! Copy .env.example to .env and configure it."
    exit 1
fi

# Pull latest images
echo "📦 Pulling latest Docker images..."
docker-compose -f $COMPOSE_FILE pull

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f $COMPOSE_FILE down

# Start services
echo "🔄 Starting services..."
docker-compose -f $COMPOSE_FILE up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
docker-compose -f $COMPOSE_FILE ps

# Run migrations
echo "🗄️ Running database migrations..."
docker-compose -f $COMPOSE_FILE exec -T web python manage.py migrate --settings=core.settings_production

# Collect static files
echo "📁 Collecting static files..."
docker-compose -f $COMPOSE_FILE exec -T web python manage.py collectstatic --noinput --settings=core.settings_production

# Check if everything is running
echo "✅ Checking if all services are running..."
if docker-compose -f $COMPOSE_FILE ps | grep -q "Exit"; then
    echo "❌ Some services failed to start!"
    docker-compose -f $COMPOSE_FILE logs
    exit 1
fi

echo "🎉 Deployment completed successfully!"
echo "🌐 Application should be available at: https://your-domain.com"

# Optional: Run a quick health check
echo "🏥 Running health check..."
sleep 10
if curl -f http://localhost/health; then
    echo "✅ Health check passed!"
else
    echo "⚠️ Health check failed, but deployment completed. Check logs if needed."
fi

echo "📋 To view logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "🔄 To restart: docker-compose -f $COMPOSE_FILE restart"
echo "🛑 To stop: docker-compose -f $COMPOSE_FILE down"
