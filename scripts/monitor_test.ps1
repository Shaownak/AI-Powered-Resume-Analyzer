# Monitoring script for production services
# Usage: .\scripts\monitor_test.ps1

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
            Write-LogMessage "Service $ServiceName is healthy"
            return $true
        }
    }
    catch {
        Write-LogMessage "Service $ServiceName is unhealthy: $($_.Exception.Message)"
        return $false
    }
}

Write-LogMessage "Starting health check..."

# Check if Docker is running
try {
    docker version | Out-Null
    Write-LogMessage "Docker is available"
}
catch {
    Write-LogMessage "Docker is not running or not accessible"
    exit 1
}

# Check if compose file exists
if (-not (Test-Path $ComposeFile)) {
    Write-LogMessage "Compose file $ComposeFile not found"
}
else {
    Write-LogMessage "Compose file $ComposeFile found"
}

# Check disk space (for current drive)
try {
    $drive = Get-PSDrive -Name C
    $diskUsagePercent = [math]::Round((($drive.Used / ($drive.Used + $drive.Free)) * 100), 2)
    if ($diskUsagePercent -gt 80) {
        Write-LogMessage "WARNING: Disk usage is high: $diskUsagePercent%"
    } else {
        Write-LogMessage "Disk usage is normal: $diskUsagePercent%"
    }
}
catch {
    Write-LogMessage "Could not check disk usage: $($_.Exception.Message)"
}

# Check memory usage
try {
    $memory = Get-CimInstance -ClassName Win32_OperatingSystem
    $memoryUsagePercent = [math]::Round((($memory.TotalVisibleMemorySize - $memory.FreePhysicalMemory) / $memory.TotalVisibleMemorySize) * 100, 2)
    if ($memoryUsagePercent -gt 85) {
        Write-LogMessage "WARNING: Memory usage is high: $memoryUsagePercent%"
    } else {
        Write-LogMessage "Memory usage is normal: $memoryUsagePercent%"
    }
}
catch {
    Write-LogMessage "Could not check memory usage: $($_.Exception.Message)"
}

# Test a health check endpoint (this will fail but shows the functionality)
Test-ServiceHealth "Test Web Service" "http://localhost:8000/health"

Write-LogMessage "Health check completed"
