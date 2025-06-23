# Start development environment WITH nginx
# Services: PostgreSQL, Redis, AI Microservice, Django, nginx
# Everything runs in Docker containers

Write-Host "🚀 Starting Development Environment (With nginx)" -ForegroundColor Green
Write-Host "Services: PostgreSQL + Redis + AI Microservice + Django + nginx" -ForegroundColor Yellow
Write-Host "Everything runs in Docker containers" -ForegroundColor Yellow

# Build and start all services including nginx
docker-compose -f docker-compose.dev.yml --profile with-nginx up -d --build

Write-Host ""
Write-Host "✅ All Docker services started!" -ForegroundColor Green
Write-Host "📊 Check status: docker-compose -f docker-compose.dev.yml --profile with-nginx ps" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Access your app through nginx:" -ForegroundColor Cyan
Write-Host "   nginx (main):  http://localhost:8080" -ForegroundColor White
Write-Host "   Django direct: http://localhost:8000" -ForegroundColor Gray
Write-Host "   AI Service:    http://localhost:8001" -ForegroundColor Gray
Write-Host "   PostgreSQL:    localhost:5432" -ForegroundColor White
Write-Host "   Redis:         localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "📋 nginx routes:" -ForegroundColor Cyan
Write-Host "   /              -> Django (web:8000)" -ForegroundColor Gray
Write-Host "   /api/ai/       -> AI Service (ai-service:8001)" -ForegroundColor Gray
Write-Host "   /static/       -> Static files" -ForegroundColor Gray
Write-Host "   /nginx-health  -> nginx health check" -ForegroundColor Gray
