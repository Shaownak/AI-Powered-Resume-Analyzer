#!/usr/bin/env pwsh

# Production deployment script
# Usage: .\scripts\deploy.ps1 [environment]

param(
    [string]$Environment = "production"
)

$ComposeFile = "docker-compose.$Environment.yml"

Write-Host "🚀 Deploying Resume Screener Platform to $Environment..." -ForegroundColor Green

# Check if compose file exists
if (-not (Test-Path $ComposeFile)) {
    Write-Host "❌ Error: $ComposeFile not found!" -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ Error: .env file not found! Copy .env.example to .env and configure it." -ForegroundColor Red
    exit 1
}

# Check if Docker is running
try {
    docker version | Out-Null
}
catch {
    Write-Host "❌ Error: Docker is not running or not accessible!" -ForegroundColor Red
    exit 1
}

# Pull latest images
Write-Host "📦 Pulling latest Docker images..." -ForegroundColor Blue
try {
    docker-compose -f $ComposeFile pull
}
catch {
    Write-Host "⚠️ Warning: Could not pull some images. Continuing with existing images..." -ForegroundColor Yellow
}

# Stop existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Blue
try {
    docker-compose -f $ComposeFile down
}
catch {
    Write-Host "⚠️ Warning: Error stopping containers, continuing..." -ForegroundColor Yellow
}

# Start services
Write-Host "🔄 Starting services..." -ForegroundColor Blue
try {
    docker-compose -f $ComposeFile up -d
    if ($LASTEXITCODE -ne 0) {
        throw "Docker compose up failed"
    }
}
catch {
    Write-Host "❌ Error starting services: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Blue
Start-Sleep -Seconds 30

# Check service health
Write-Host "🏥 Checking service health..." -ForegroundColor Blue
$containerStatus = docker-compose -f $ComposeFile ps
Write-Host $containerStatus

# Run migrations
Write-Host "🗄️ Running database migrations..." -ForegroundColor Blue
try {
    docker-compose -f $ComposeFile exec -T web python manage.py migrate --settings=core.settings_production
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ Warning: Migrations may have failed, check logs" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "⚠️ Warning: Could not run migrations: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Collect static files
Write-Host "📁 Collecting static files..." -ForegroundColor Blue
try {
    docker-compose -f $ComposeFile exec -T web python manage.py collectstatic --noinput --settings=core.settings_production
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ Warning: Static file collection may have failed" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "⚠️ Warning: Could not collect static files: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Check if everything is running
Write-Host "✅ Checking if all services are running..." -ForegroundColor Blue
$containerStatus = docker-compose -f $ComposeFile ps
if ($containerStatus -match "Exit") {
    Write-Host "❌ Some services failed to start!" -ForegroundColor Red
    docker-compose -f $ComposeFile logs
    exit 1
}

Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
Write-Host "🌐 Application should be available at: https://your-domain.com" -ForegroundColor Green

# Optional: Run a quick health check
Write-Host "🏥 Running health check..." -ForegroundColor Blue
Start-Sleep -Seconds 10
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing -TimeoutSec 10
    if ($healthResponse.StatusCode -eq 200) {
        Write-Host "✅ Health check passed!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Health check returned status: $($healthResponse.StatusCode)" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "⚠️ Health check failed, but deployment completed. Check logs if needed." -ForegroundColor Yellow
}

Write-Host "📋 To view logs: docker-compose -f $ComposeFile logs -f" -ForegroundColor Cyan
Write-Host "🔄 To restart: docker-compose -f $ComposeFile restart" -ForegroundColor Cyan
Write-Host "🛑 To stop: docker-compose -f $ComposeFile down" -ForegroundColor Cyan
