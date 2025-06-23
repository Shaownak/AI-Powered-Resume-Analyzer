#!/usr/bin/env pwsh

# Backup script for production data
# Usage: .\scripts\backup.ps1

param(
    [string]$BackupDir = "C:\backups\resume-screener",
    [string]$ComposeFile = "docker-compose.prod.yml"
)

$Date = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "🗄️ Starting backup process..." -ForegroundColor Green

# Create backup directory
if (-not (Test-Path $BackupDir)) {
    try {
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
        Write-Host "📁 Created backup directory: $BackupDir" -ForegroundColor Blue
    }    catch {
        Write-Host "❌ Error creating backup directory: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Check if Docker is running
try {
    docker version | Out-Null
}
catch {
    Write-Host "❌ Error: Docker is not running or not accessible!" -ForegroundColor Red
    exit 1
}

# Check if compose file exists
if (-not (Test-Path $ComposeFile)) {
    Write-Host "❌ Error: $ComposeFile not found!" -ForegroundColor Red
    exit 1
}

# Backup PostgreSQL database
Write-Host "📦 Backing up PostgreSQL database..." -ForegroundColor Blue
try {
    $dbBackupFile = Join-Path $BackupDir "db_backup_$Date.sql"
    $gzipFile = "$dbBackupFile.gz"
    
    # Export database
    docker-compose -f $ComposeFile exec -T db pg_dump -U postgres resume_screener > $dbBackupFile
    
    # Compress the backup (using built-in compression if available)
    if (Get-Command "7z" -ErrorAction SilentlyContinue) {
        7z a -tgzip $gzipFile $dbBackupFile
        Remove-Item $dbBackupFile
        Write-Host "✅ Database backup compressed: $gzipFile" -ForegroundColor Green
    } else {
        Write-Host "✅ Database backup created: $dbBackupFile (7z not found, file not compressed)" -ForegroundColor Green
    }
}
catch {
    Write-Host "❌ Error backing up database: $($_.Exception.Message)" -ForegroundColor Red
}

# Backup media files
Write-Host "📸 Backing up media files..." -ForegroundColor Blue
try {
    $mediaBackupFile = Join-Path $BackupDir "media_backup_$Date.tar.gz"
    docker run --rm -v resume-screener_media_volume:/source -v "${BackupDir}:/backup" alpine tar czf "/backup/media_backup_$Date.tar.gz" -C /source .
    Write-Host "✅ Media files backup created: $mediaBackupFile" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error backing up media files: $($_.Exception.Message)" -ForegroundColor Red
}

# Backup static files
Write-Host "🎨 Backing up static files..." -ForegroundColor Blue
try {
    $staticBackupFile = Join-Path $BackupDir "static_backup_$Date.tar.gz"
    docker run --rm -v resume-screener_static_volume:/source -v "${BackupDir}:/backup" alpine tar czf "/backup/static_backup_$Date.tar.gz" -C /source .
    Write-Host "✅ Static files backup created: $staticBackupFile" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error backing up static files: $($_.Exception.Message)" -ForegroundColor Red
}

# Backup logs
Write-Host "📋 Backing up logs..." -ForegroundColor Blue
try {
    $logsBackupFile = Join-Path $BackupDir "logs_backup_$Date.tar.gz"
    docker run --rm -v resume-screener_logs_volume:/source -v "${BackupDir}:/backup" alpine tar czf "/backup/logs_backup_$Date.tar.gz" -C /source .
    Write-Host "✅ Logs backup created: $logsBackupFile" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error backing up logs: $($_.Exception.Message)" -ForegroundColor Red
}

# Create backup manifest
$manifestFile = Join-Path $BackupDir "backup_manifest_$Date.txt"
$manifestContent = @"
Resume Screener Platform Backup
Date: $(Get-Date)
Database: db_backup_$Date.sql$(if (Test-Path "$BackupDir\db_backup_$Date.sql.gz") { ".gz" })
Media Files: media_backup_$Date.tar.gz
Static Files: static_backup_$Date.tar.gz
Logs: logs_backup_$Date.tar.gz
"@

try {
    Set-Content -Path $manifestFile -Value $manifestContent
    Write-Host "📋 Backup manifest created: $manifestFile" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Warning: Could not create backup manifest: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "✅ Backup completed successfully!" -ForegroundColor Green
Write-Host "📁 Backup files saved to: $BackupDir" -ForegroundColor Green

# Clean up old backups (keep last 7 days)
Write-Host "🧹 Cleaning up old backups (older than 7 days)..." -ForegroundColor Blue
try {
    $cutoffDate = (Get-Date).AddDays(-7)
    Get-ChildItem -Path $BackupDir -File | Where-Object { $_.LastWriteTime -lt $cutoffDate } | Remove-Item -Force
    Write-Host "✅ Old backups cleaned up" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Warning: Could not clean up old backups: $($_.Exception.Message)" -ForegroundColor Yellow
}
