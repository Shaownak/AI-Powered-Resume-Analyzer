#!/bin/bash
# Production deployment script

set -e

echo "🚀 Starting production deployment..."

# Configuration
PROJECT_DIR="/opt/resume-screener"
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="/opt/backups/resume-screener"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
    exit 1
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root"
fi

# Check if project directory exists
if [[ ! -d "$PROJECT_DIR" ]]; then
    error "Project directory $PROJECT_DIR does not exist"
fi

cd "$PROJECT_DIR"

# Check if git repository
if [[ ! -d ".git" ]]; then
    error "Not a git repository"
fi

# Check if compose file exists
if [[ ! -f "$COMPOSE_FILE" ]]; then
    error "Docker compose file $COMPOSE_FILE not found"
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

log "Creating database backup..."
docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump -U postgres resume_screener | gzip > "$BACKUP_DIR/database_$(date +%Y%m%d_%H%M%S).sql.gz"

log "Backing up media files..."
tar -czf "$BACKUP_DIR/media_$(date +%Y%m%d_%H%M%S).tar.gz" -C . media/ || warn "Media backup failed"

log "Pulling latest code..."
git fetch origin
git reset --hard origin/main

log "Pulling Docker images..."
docker-compose -f "$COMPOSE_FILE" pull

log "Building and starting services..."
docker-compose -f "$COMPOSE_FILE" up -d --no-deps --build web ai-service

log "Running database migrations..."
docker-compose -f "$COMPOSE_FILE" exec web python manage.py migrate

log "Collecting static files..."
docker-compose -f "$COMPOSE_FILE" exec web python manage.py collectstatic --noinput

log "Restarting nginx..."
docker-compose -f "$COMPOSE_FILE" restart nginx

log "Cleaning up old Docker images..."
docker system prune -f

# Health check
log "Performing health check..."
sleep 10

if curl -f http://localhost/health > /dev/null 2>&1; then
    log "✅ Health check passed"
else
    error "❌ Health check failed"
fi

# Check system status
if curl -f http://localhost/api/system-status/ > /dev/null 2>&1; then
    log "✅ System status check passed"
else
    warn "⚠️ System status check failed"
fi

log "🎉 Deployment completed successfully!"

# Display running services
log "Running services:"
docker-compose -f "$COMPOSE_FILE" ps

# Display recent logs
log "Recent logs:"
docker-compose -f "$COMPOSE_FILE" logs --tail=20 web ai-service nginx
