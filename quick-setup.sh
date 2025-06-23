#!/bin/bash

# Resume Screener Platform - Quick Setup Script
# This script helps you get the platform running quickly

set -e

echo "🚀 Resume Screener Platform - Quick Setup"
echo "=========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
else
    echo "✅ .env file already exists"
fi

# Start the services
echo "🐳 Starting Docker services..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

# Run migrations
echo "🗄️ Running database migrations..."
docker-compose exec web python manage.py migrate

# Create static files directory
echo "📁 Collecting static files..."
docker-compose exec web python manage.py collectstatic --noinput

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Access your application:"
echo "   🌐 Frontend:       http://localhost:3000"
echo "   🖥️  Django Admin:   http://localhost:8000/admin"
echo "   🔧 API Docs:       http://localhost:8000/api/"
echo "   🤖 AI Service:     http://localhost:8001/docs"
echo "   📊 Analytics:      http://localhost:8000/analytics"
echo ""
echo "🔧 Next steps:"
echo "   1. Create a superuser: docker-compose exec web python manage.py createsuperuser"
echo "   2. Access Django admin to configure your platform"
echo "   3. Start uploading resumes and creating jobs!"
echo ""
echo "📚 For more information, see README.md"
echo "🐛 Issues? Check the troubleshooting section in README.md"
