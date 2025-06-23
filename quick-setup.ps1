# Resume Screener Platform - Quick Setup Script (PowerShell)
# This script helps you get the platform running quickly on Windows

Write-Host "🚀 Resume Screener Platform - Quick Setup" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Check if Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    Write-Host "   Visit: https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor Yellow
    exit 1
}

# Check if Docker Compose is installed
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose is not installed. Please install Docker Compose first." -ForegroundColor Red
    Write-Host "   Visit: https://docs.docker.com/compose/install/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Docker and Docker Compose are installed" -ForegroundColor Green

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📄 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created. Please edit it with your configuration." -ForegroundColor Green
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Start the services
Write-Host "🐳 Starting Docker services..." -ForegroundColor Yellow
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if services are running
Write-Host "🔍 Checking service status..." -ForegroundColor Yellow
docker-compose ps

# Run migrations
Write-Host "🗄️ Running database migrations..." -ForegroundColor Yellow
docker-compose exec web python manage.py migrate

# Create static files directory
Write-Host "📁 Collecting static files..." -ForegroundColor Yellow
docker-compose exec web python manage.py collectstatic --noinput

Write-Host ""
Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Access your application:" -ForegroundColor Cyan
Write-Host "   🌐 Frontend:       http://localhost:3000" -ForegroundColor Gray
Write-Host "   🖥️  Django Admin:   http://localhost:8000/admin" -ForegroundColor Gray
Write-Host "   🔧 API Docs:       http://localhost:8000/api/" -ForegroundColor Gray
Write-Host "   🤖 AI Service:     http://localhost:8001/docs" -ForegroundColor Gray
Write-Host "   📊 Analytics:      http://localhost:8000/analytics" -ForegroundColor Gray
Write-Host ""
Write-Host "🔧 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Create a superuser: docker-compose exec web python manage.py createsuperuser" -ForegroundColor Gray
Write-Host "   2. Access Django admin to configure your platform" -ForegroundColor Gray
Write-Host "   3. Start uploading resumes and creating jobs!" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 For more information, see README.md" -ForegroundColor Yellow
Write-Host "🐛 Issues? Check the troubleshooting section in README.md" -ForegroundColor Yellow
