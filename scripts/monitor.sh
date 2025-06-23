#!/bin/bash

# Monitoring script for production services
# Usage: ./scripts/monitor.sh

set -e

COMPOSE_FILE="docker-compose.prod.yml"
LOG_FILE="/var/log/resume-screener-monitor.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

check_service_health() {
    local service=$1
    local url=$2
    
    if curl -s -f "$url" > /dev/null; then
        log_message "✅ $service is healthy"
        return 0
    else
        log_message "❌ $service is unhealthy"
        return 1
    fi
}

restart_service() {
    local service=$1
    log_message "🔄 Restarting $service..."
    docker-compose -f $COMPOSE_FILE restart $service
    sleep 30
}

log_message "🔍 Starting health check..."

# Check container status
log_message "📊 Checking container status..."
if ! docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
    log_message "⚠️ Some containers are not running!"
    docker-compose -f $COMPOSE_FILE ps | tee -a $LOG_FILE
fi

# Check web application
if ! check_service_health "Web Application" "http://localhost/health"; then
    restart_service "web"
fi

# Check AI microservice
if ! check_service_health "AI Microservice" "http://localhost:8001/health"; then
    restart_service "ai-service"
fi

# Check database
if ! docker-compose -f $COMPOSE_FILE exec -T db pg_isready -U postgres; then
    log_message "❌ Database is not ready"
    restart_service "db"
else
    log_message "✅ Database is healthy"
fi

# Check Redis
if ! docker-compose -f $COMPOSE_FILE exec -T redis redis-cli ping; then
    log_message "❌ Redis is not responding"
    restart_service "redis"
else
    log_message "✅ Redis is healthy"
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    log_message "⚠️ Disk usage is high: ${DISK_USAGE}%"
fi

# Check memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
if [ $(echo "$MEMORY_USAGE > 85" | bc) -eq 1 ]; then
    log_message "⚠️ Memory usage is high: ${MEMORY_USAGE}%"
fi

# Check log file sizes
for container in $(docker-compose -f $COMPOSE_FILE ps --services); do
    LOG_SIZE=$(docker logs $container 2>&1 | wc -c)
    if [ $LOG_SIZE -gt 100000000 ]; then  # 100MB
        log_message "⚠️ Container $container has large logs: $(($LOG_SIZE / 1000000))MB"
    fi
done

log_message "✅ Health check completed"
