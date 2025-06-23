# Start development environment WITHOUT nginx (current setup)
# Services: PostgreSQL, Redis, AI Microservice only
# Django runs on host (python manage.py runserver)

Write-Host "🚀 Starting Development Environment (No nginx)" -ForegroundColor Green
Write-Host "Services: PostgreSQL + Redis + AI Microservice" -ForegroundColor Yellow
Write-Host "Django will run on host machine" -ForegroundColor Yellow

docker-compose -f docker-compose.dev.yml up -d db redis ai-service

Write-Host ""
Write-Host "✅ Docker services started!" -ForegroundColor Green
Write-Host "📊 Check status: docker-compose -f docker-compose.dev.yml ps" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔧 To start Django on host:" -ForegroundColor Cyan
Write-Host "   $env:REDIS_URL='redis://:redis_password@localhost:6379/0'" -ForegroundColor Gray
Write-Host "   $env:AI_MICROSERVICE_URL='http://localhost:8001'" -ForegroundColor Gray
Write-Host "   python manage.py runserver 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "🌐 Access your app:" -ForegroundColor Cyan
Write-Host "   Django:        http://localhost:8000" -ForegroundColor White
Write-Host "   AI Service:    http://localhost:8001" -ForegroundColor White
Write-Host "   PostgreSQL:    localhost:5432" -ForegroundColor White
Write-Host "   Redis:         localhost:6379" -ForegroundColor White
