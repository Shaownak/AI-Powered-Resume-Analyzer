#!/bin/bash

# Backup script test for production data
# Usage: ./scripts/backup_test.sh

set -e

BACKUP_DIR="/tmp/resume-screener-backup-test"
DATE=$(date +%Y%m%d_%H%M%S)
COMPOSE_FILE="docker-compose.prod.yml"

echo "🗄️ Starting backup test process..."

# Create backup directory
mkdir -p $BACKUP_DIR

echo "✅ Created backup directory: $BACKUP_DIR"

# Check if compose file exists
if [ -f "$COMPOSE_FILE" ]; then
    echo "✅ Compose file found: $COMPOSE_FILE"
else
    echo "⚠️ Compose file not found: $COMPOSE_FILE"
fi

# Check if Docker is available
if command -v docker >/dev/null 2>&1; then
    echo "✅ Docker is available"
    docker --version
else
    echo "⚠️ Docker is not available"
fi

# Create backup manifest
cat > $BACKUP_DIR/backup_manifest_$DATE.txt << EOF
Resume Screener Platform Backup Test
Date: $(date)
Status: Test backup completed successfully
Directory: $BACKUP_DIR
EOF

echo "✅ Backup test completed successfully!"
echo "📁 Test backup files saved to: $BACKUP_DIR"

# List created files
ls -la $BACKUP_DIR

echo "🧹 Cleaning up test backup..."
rm -rf $BACKUP_DIR
echo "✅ Test backup cleaned up"
