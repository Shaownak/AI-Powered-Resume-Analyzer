# Comprehensive test script for all production scripts
# Usage: .\scripts\test_all.ps1

Write-Host "=== Resume Screener Platform - Production Scripts Test ===" -ForegroundColor Cyan
Write-Host ""

$TestResults = @()

# Test 1: Backup Script
Write-Host "1. Testing Backup Script..." -ForegroundColor Yellow
try {
    & "scripts\backup_test.ps1"
    $TestResults += "✅ Backup Script: PASSED"
    Write-Host "✅ Backup Script Test: PASSED" -ForegroundColor Green
}
catch {
    $TestResults += "❌ Backup Script: FAILED - $($_.Exception.Message)"
    Write-Host "❌ Backup Script Test: FAILED" -ForegroundColor Red
}
Write-Host ""

# Test 2: Monitor Script
Write-Host "2. Testing Monitor Script..." -ForegroundColor Yellow
try {
    & "scripts\monitor_test.ps1"
    $TestResults += "✅ Monitor Script: PASSED"
    Write-Host "✅ Monitor Script Test: PASSED" -ForegroundColor Green
}
catch {
    $TestResults += "❌ Monitor Script: FAILED - $($_.Exception.Message)"
    Write-Host "❌ Monitor Script Test: FAILED" -ForegroundColor Red
}
Write-Host ""

# Test 3: Deploy Script
Write-Host "3. Testing Deploy Script..." -ForegroundColor Yellow
try {
    & "scripts\deploy_test.ps1" -Environment "prod"
    $TestResults += "✅ Deploy Script: PASSED"
    Write-Host "✅ Deploy Script Test: PASSED" -ForegroundColor Green
}
catch {
    $TestResults += "❌ Deploy Script: FAILED - $($_.Exception.Message)"  
    Write-Host "❌ Deploy Script Test: FAILED" -ForegroundColor Red
}
Write-Host ""

# Test 4: Docker Compose File
Write-Host "4. Testing Docker Compose Configuration..." -ForegroundColor Yellow
try {
    if (Test-Path "docker-compose.prod.yml") {
        docker-compose -f docker-compose.prod.yml config | Out-Null
        $TestResults += "✅ Docker Compose Config: PASSED"
        Write-Host "✅ Docker Compose Config Test: PASSED" -ForegroundColor Green
    } else {
        throw "docker-compose.prod.yml not found"
    }
}
catch {
    $TestResults += "❌ Docker Compose Config: FAILED - $($_.Exception.Message)"
    Write-Host "❌ Docker Compose Config Test: FAILED" -ForegroundColor Red
}
Write-Host ""

# Test 5: Environment Configuration
Write-Host "5. Testing Environment Configuration..." -ForegroundColor Yellow
try {
    if (Test-Path ".env") {
        $envContent = Get-Content ".env"
        if ($envContent.Count -gt 0) {
            $TestResults += "✅ Environment Config: PASSED"
            Write-Host "✅ Environment Config Test: PASSED" -ForegroundColor Green
        } else {
            throw ".env file is empty"
        }
    } else {
        throw ".env file not found"
    }
}
catch {
    $TestResults += "❌ Environment Config: FAILED - $($_.Exception.Message)"
    Write-Host "❌ Environment Config Test: FAILED" -ForegroundColor Red
}
Write-Host ""

# Test 6: AI Microservice Health
Write-Host "6. Testing AI Microservice Health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        $TestResults += "✅ AI Microservice: PASSED"
        Write-Host "✅ AI Microservice Health Test: PASSED" -ForegroundColor Green
        Write-Host "   Response: $($response.Content)" -ForegroundColor Gray
    } else {
        throw "Unexpected status code: $($response.StatusCode)"
    }
}
catch {
    $TestResults += "❌ AI Microservice: FAILED - $($_.Exception.Message)"
    Write-Host "❌ AI Microservice Health Test: FAILED" -ForegroundColor Red
}
Write-Host ""

# Test 7: Required Files
Write-Host "7. Testing Required Production Files..." -ForegroundColor Yellow
$RequiredFiles = @(
    "docker-compose.prod.yml",
    "Dockerfile",
    "ai_microservice/Dockerfile",
    "requirements-production.txt",
    ".env.example",
    "core/settings_production.py",
    "PRODUCTION_DEPLOYMENT_GUIDE.md"
)

$MissingFiles = @()
foreach ($file in $RequiredFiles) {
    if (-not (Test-Path $file)) {
        $MissingFiles += $file
    }
}

if ($MissingFiles.Count -eq 0) {
    $TestResults += "✅ Required Files: PASSED"
    Write-Host "✅ Required Files Test: PASSED" -ForegroundColor Green
} else {
    $TestResults += "❌ Required Files: FAILED - Missing: $($MissingFiles -join ', ')"
    Write-Host "❌ Required Files Test: FAILED" -ForegroundColor Red
    Write-Host "   Missing files: $($MissingFiles -join ', ')" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "=== Test Results Summary ===" -ForegroundColor Cyan
foreach ($result in $TestResults) {
    Write-Host $result
}
Write-Host ""

$PassedCount = ($TestResults | Where-Object { $_ -match "✅" }).Count
$TotalCount = $TestResults.Count

if ($PassedCount -eq $TotalCount) {
    Write-Host "🎉 ALL TESTS PASSED ($PassedCount/$TotalCount)" -ForegroundColor Green
    Write-Host "✅ Production scripts are ready for deployment!" -ForegroundColor Green
} else {
    Write-Host "⚠️ SOME TESTS FAILED ($PassedCount/$TotalCount passed)" -ForegroundColor Yellow
    Write-Host "❌ Please fix the failing tests before production deployment." -ForegroundColor Red
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Review any failed tests and fix issues" -ForegroundColor White
Write-Host "2. Configure production environment variables in .env" -ForegroundColor White
Write-Host "3. Test full deployment in staging environment" -ForegroundColor White
Write-Host "4. Deploy to production using: .\scripts\deploy.ps1" -ForegroundColor White
