# Quick deployment script for GitHub Actions (PowerShell)

Write-Host "🚀 Starting GitHub deployment process..." -ForegroundColor Green

# Step 1: Push to GitHub
Write-Host "📤 Pushing code to GitHub..." -ForegroundColor Yellow
git add .
git commit -m "Add CI/CD pipeline and deployment configuration"
git push origin main

# Step 2: Create develop branch if it doesn't exist
$developExists = git show-ref --verify --quiet refs/heads/develop 2>$null
if (-not $developExists) {
    Write-Host "🌿 Creating develop branch..." -ForegroundColor Yellow
    git checkout -b develop
    git push -u origin develop
    git checkout main
}

Write-Host "✅ Code pushed to GitHub!" -ForegroundColor Green
Write-Host ""
Write-Host "🔧 Next steps:" -ForegroundColor Cyan
Write-Host "1. Go to your GitHub repository settings"
Write-Host "2. Add the required secrets (see DEPLOYMENT_SECRETS.md)"
Write-Host "3. Set up your production server (see CICD_DEPLOYMENT_GUIDE.md)"
Write-Host "4. Make a test commit to trigger the CI/CD pipeline"
Write-Host ""
Write-Host "📋 Required GitHub Secrets:" -ForegroundColor Cyan
Write-Host "   - PRODUCTION_HOST" -ForegroundColor Gray
Write-Host "   - PRODUCTION_USER" -ForegroundColor Gray
Write-Host "   - PRODUCTION_SSH_KEY" -ForegroundColor Gray
Write-Host "   - PRODUCTION_DOMAIN" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "   - CICD_DEPLOYMENT_GUIDE.md - Complete setup guide" -ForegroundColor Gray
Write-Host "   - DEPLOYMENT_SECRETS.md - Secrets configuration" -ForegroundColor Gray
Write-Host "   - .github/workflows/main.yml - CI/CD pipeline" -ForegroundColor Gray
Write-Host ""
Write-Host "🎯 Test the pipeline:" -ForegroundColor Cyan
Write-Host "   git commit -m 'Test CI/CD pipeline' --allow-empty" -ForegroundColor Gray
Write-Host "   git push origin main" -ForegroundColor Gray
