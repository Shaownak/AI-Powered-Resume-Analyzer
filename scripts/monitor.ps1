#!/usr/bin/env pwsh

# Monitoring script for production services
# Usage: .\scripts\monitor.ps1

param(
    [string]$ComposeFile = "docker-compose.prod.yml",
    [string]$LogFile = "resume-screener-monitor.log"
)

function Write-LogMessage {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp - $Message"
    Write-Host $logEntry
    Add-Content -Path $LogFile -Value $logEntry
}

function Test-ServiceHealth {
    param(
        [string]$ServiceName,
        [string]$Url
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-LogMessage "✅ $ServiceName is healthy"
            return $true
        }
    }
    catch {
        Write-LogMessage "❌ $ServiceName is unhealthy: $($_.Exception.Message)"
        return $false
    }
}

function Restart-DockerService {
    param([string]$ServiceName)
    Write-LogMessage "🔄 Restarting $ServiceName..."
    docker-compose -f $ComposeFile restart $ServiceName
    Start-Sleep -Seconds 30
}

Write-LogMessage "🔍 Starting health check..."

# Check if Docker is running
try {
    docker version | Out-Null
}
catch {
    Write-LogMessage "❌ Docker is not running or not accessible"
    exit 1
}

# Check if compose file exists
if (-not (Test-Path $ComposeFile)) {
    Write-LogMessage "❌ Compose file $ComposeFile not found"
    exit 1
}

# Check container status
Write-LogMessage "📊 Checking container status..."
try {
    $containerStatus = docker-compose -f $ComposeFile ps
    if ($containerStatus -notmatch "Up") {
        Write-LogMessage "⚠️ Some containers are not running!"
        Write-LogMessage $containerStatus
    }
}
catch {
    Write-LogMessage "❌ Error checking container status: $($_.Exception.Message)"
}

# Check web application
if (-not (Test-ServiceHealth "Web Application" "http://localhost/health")) {
    try {
        Restart-DockerService "web"
    }
    catch {
        Write-LogMessage "❌ Failed to restart web service: $($_.Exception.Message)"
    }
}

# Check AI microservice
if (-not (Test-ServiceHealth "AI Microservice" "http://localhost:8001/health")) {
    try {
        Restart-DockerService "ai-service"
    }
    catch {
        Write-LogMessage "❌ Failed to restart AI service: $($_.Exception.Message)"
    }
}

# Check database
try {
    $dbCheck = docker-compose -f $ComposeFile exec -T db pg_isready -U postgres
    if ($LASTEXITCODE -eq 0) {
        Write-LogMessage "✅ Database is healthy"
    } else {
        Write-LogMessage "❌ Database is not ready"
        Restart-DockerService "db"
    }
}
catch {
    Write-LogMessage "❌ Error checking database: $($_.Exception.Message)"
}

# Check Redis
try {
    $redisCheck = docker-compose -f $ComposeFile exec -T redis redis-cli ping
    if ($redisCheck -match "PONG") {
        Write-LogMessage "✅ Redis is healthy"
    } else {
        Write-LogMessage "❌ Redis is not responding"
        Restart-DockerService "redis"
    }
}
catch {
    Write-LogMessage "❌ Error checking Redis: $($_.Exception.Message)"
}

# Check disk space (for current drive)
try {
    $drive = Get-PSDrive -Name C
    $diskUsagePercent = [math]::Round((($drive.Used / ($drive.Used + $drive.Free)) * 100), 2)
    if ($diskUsagePercent -gt 80) {
        Write-LogMessage "⚠️ Disk usage is high: $diskUsagePercent%"
    } else {
        Write-LogMessage "✅ Disk usage is normal: $diskUsagePercent%"
    }
}
catch {
    Write-LogMessage "⚠️ Could not check disk usage: $($_.Exception.Message)"
}

# Check memory usage
try {
    $memory = Get-CimInstance -ClassName Win32_OperatingSystem
    $memoryUsagePercent = [math]::Round((($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize) * 100, 2)
    if ($memoryUsagePercent -gt 85) {
        Write-LogMessage "⚠️ Memory usage is high: $memoryUsagePercent%"
    } else {
        Write-LogMessage "✅ Memory usage is normal: $memoryUsagePercent%"
    }
}
catch {
    Write-LogMessage "⚠️ Could not check memory usage: $($_.Exception.Message)"
}

Write-LogMessage "✅ Health check completed"
