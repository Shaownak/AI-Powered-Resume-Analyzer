# Start Django with production settings for Docker integration
$env:DJANGO_SETTINGS_MODULE="core.settings_production"
$env:REDIS_URL="redis://:redis_password@localhost:6379/0"
$env:AI_MICROSERVICE_URL="http://localhost:8001"
$env:DATABASE_URL="postgresql://postgres:shaownak@localhost:5432/resume-screener"
$env:DEBUG="True"
$env:ALLOWED_HOSTS="localhost,127.0.0.1,0.0.0.0"

Write-Host "Starting Django with production settings and Docker integration..."
Write-Host "Redis URL: $env:REDIS_URL"
Write-Host "AI Microservice URL: $env:AI_MICROSERVICE_URL"
Write-Host "Database URL: $env:DATABASE_URL"

python manage.py runserver 8000
