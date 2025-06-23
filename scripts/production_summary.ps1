# Final Production Scripts Summary
# Usage: .\scripts\production_summary.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Resume Screener Platform - Production Ready" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check AI Microservice Status
Write-Host "🤖 AI Microservice Status:" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ AI Microservice is running and healthy" -ForegroundColor Green
        $healthData = $response.Content | ConvertFrom-Json
        Write-Host "   📊 Status: $($healthData.status)" -ForegroundColor Gray
        Write-Host "   🔗 Redis: $($healthData.redis)" -ForegroundColor Gray
        Write-Host "   🎯 Service: $($healthData.service)" -ForegroundColor Gray
    }
}
catch {
    Write-Host "   ❌ AI Microservice is not running" -ForegroundColor Red
}
Write-Host ""

# Check Production Files
Write-Host "📁 Production Files Status:" -ForegroundColor Yellow
$ProductionFiles = @{
    "docker-compose.prod.yml" = "Docker Compose configuration"
    "Dockerfile" = "Main application Dockerfile"
    "ai_microservice/Dockerfile" = "AI microservice Dockerfile"
    "requirements-production.txt" = "Production dependencies"
    ".env.example" = "Environment variables template"
    "core/settings_production.py" = "Production Django settings"
    "PRODUCTION_DEPLOYMENT_GUIDE.md" = "Deployment documentation"
}

foreach ($file in $ProductionFiles.Keys) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file - $($ProductionFiles[$file])" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file - $($ProductionFiles[$file])" -ForegroundColor Red
    }
}
Write-Host ""

# Check Scripts
Write-Host "🛠️ Production Scripts Status:" -ForegroundColor Yellow
$Scripts = @{
    "scripts/backup.ps1" = "Backup script (PowerShell)"
    "scripts/deploy.ps1" = "Deployment script (PowerShell)"
    "scripts/monitor.ps1" = "Monitoring script (PowerShell)"
    "scripts/backup.sh" = "Backup script (Bash)"
    "scripts/deploy.sh" = "Deployment script (Bash)"
    "scripts/monitor.sh" = "Monitoring script (Bash)"
}

foreach ($script in $Scripts.Keys) {
    if (Test-Path $script) {
        Write-Host "   ✅ $script - $($Scripts[$script])" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $script - $($Scripts[$script])" -ForegroundColor Red
    }
}
Write-Host ""

# Environment Check
Write-Host "🌍 Environment Configuration:" -ForegroundColor Yellow
if (Test-Path ".env") {
    $envLines = (Get-Content ".env" | Where-Object { $_ -notmatch "^#" -and $_ -ne "" }).Count
    Write-Host "   ✅ .env file exists with $envLines configuration lines" -ForegroundColor Green
} else {
    Write-Host "   ⚠️ .env file not found - copy from .env.example" -ForegroundColor Yellow
}

# Docker Check
Write-Host "🐳 Docker Configuration:" -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "   ✅ Docker is available" -ForegroundColor Green
    
    # Test Docker Compose config
    docker-compose -f docker-compose.prod.yml config --quiet
    Write-Host "   ✅ Docker Compose configuration is valid" -ForegroundColor Green
}
catch {
    Write-Host "   ❌ Docker is not available or configuration is invalid" -ForegroundColor Red
}
Write-Host ""

# System Resources
Write-Host "💻 System Resources:" -ForegroundColor Yellow
try {
    $drive = Get-PSDrive -Name C
    $diskUsage = [math]::Round((($drive.Used / ($drive.Used + $drive.Free)) * 100), 2)
    if ($diskUsage -gt 80) {
        Write-Host "   ⚠️ Disk usage: $diskUsage% (consider cleanup)" -ForegroundColor Yellow
    } else {
        Write-Host "   ✅ Disk usage: $diskUsage%" -ForegroundColor Green
    }
    
    $memory = Get-CimInstance -ClassName Win32_OperatingSystem
    $memoryUsage = [math]::Round((($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize) * 100, 2)
    if ($memoryUsage -gt 85) {
        Write-Host "   ⚠️ Memory usage: $memoryUsage%" -ForegroundColor Yellow
    } else {
        Write-Host "   ✅ Memory usage: $memoryUsage%" -ForegroundColor Green
    }
}
catch {
    Write-Host "   ⚠️ Could not check system resources" -ForegroundColor Yellow
}
Write-Host ""

# Deployment Commands
Write-Host "🚀 Ready for Production Deployment!" -ForegroundColor Green
Write-Host ""
Write-Host "Quick Start Commands:" -ForegroundColor Cyan
Write-Host "   1. Configure environment:" -ForegroundColor White
Write-Host "      Copy-Item .env.example .env" -ForegroundColor Gray
Write-Host "      # Edit .env with your production values" -ForegroundColor Gray
Write-Host ""
Write-Host "   2. Deploy with Docker Compose:" -ForegroundColor White
Write-Host "      docker-compose -f docker-compose.prod.yml up -d" -ForegroundColor Gray
Write-Host ""
Write-Host "   3. Run deployment script:" -ForegroundColor White
Write-Host "      .\scripts\deploy.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "   4. Monitor services:" -ForegroundColor White
Write-Host "      .\scripts\monitor.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "   5. Backup data:" -ForegroundColor White
Write-Host "      .\scripts\backup.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "   • PRODUCTION_DEPLOYMENT_GUIDE.md - Complete deployment guide" -ForegroundColor White
Write-Host "   • PRODUCTION_IMPLEMENTATION_COMPLETE.md - Implementation details" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
