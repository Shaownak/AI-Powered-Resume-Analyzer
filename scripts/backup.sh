#!/bin/bash

# Backup script for production data
# Usage: ./scripts/backup.sh

set -e

BACKUP_DIR="/opt/backups/resume-screener"
DATE=$(date +%Y%m%d_%H%M%S)
COMPOSE_FILE="docker-compose.prod.yml"

echo "🗄️ Starting backup process..."

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL database
echo "📦 Backing up PostgreSQL database..."
docker-compose -f $COMPOSE_FILE exec -T db pg_dump -U postgres resume_screener | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup media files
echo "📸 Backing up media files..."
docker run --rm -v resume-screener_media_volume:/source -v $BACKUP_DIR:/backup alpine tar czf /backup/media_backup_$DATE.tar.gz -C /source .

# Backup static files
echo "🎨 Backing up static files..."
docker run --rm -v resume-screener_static_volume:/source -v $BACKUP_DIR:/backup alpine tar czf /backup/static_backup_$DATE.tar.gz -C /source .

# Backup logs
echo "📋 Backing up logs..."
docker run --rm -v resume-screener_logs_volume:/source -v $BACKUP_DIR:/backup alpine tar czf /backup/logs_backup_$DATE.tar.gz -C /source .

# Create backup manifest
cat > $BACKUP_DIR/backup_manifest_$DATE.txt << EOF
Resume Screener Platform Backup
Date: $(date)
Database: db_backup_$DATE.sql.gz
Media Files: media_backup_$DATE.tar.gz
Static Files: static_backup_$DATE.tar.gz
Logs: logs_backup_$DATE.tar.gz
EOF

echo "✅ Backup completed successfully!"
echo "📁 Backup files saved to: $BACKUP_DIR"

# Clean up old backups (keep last 7 days)
find $BACKUP_DIR -type f -mtime +7 -delete
echo "🧹 Cleaned up old backups (older than 7 days)"
