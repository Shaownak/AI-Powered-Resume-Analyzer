# 🚀 AI-Powered Resume Screener Platform

An enterprise-grade, full-stack application that uses AI to intelligently analyze and screen resumes. Built with Django, FastAPI microservices, PostgreSQL, Redis, and React frontend - fully containerized with comprehensive CI/CD pipeline.

![Platform Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Django](https://img.shields.io/badge/Django-5.0.2-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-orange)

## 📋 Table of Contents

- [🎯 Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [🔧 Local Development Setup](#-local-development-setup)
- [🐳 Docker Deployment](#-docker-deployment)
- [🔄 CI/CD Pipeline](#-cicd-pipeline)
- [📱 API Documentation](#-api-documentation)
- [🧪 Testing](#-testing)
- [📊 Monitoring & Analytics](#-monitoring--analytics)
- [🔐 Security Features](#-security-features)
- [🤝 Contributing](#-contributing)

## 🎯 Features

### 🤖 AI-Powered Resume Analysis
- **Intelligent Resume Parsing**: Extract text from PDF and DOC files
- **AI-Driven Candidate Scoring**: Machine learning algorithms score resume-job fit
- **Keyword Matching**: Advanced semantic analysis for skill and requirement matching
- **Multi-format Support**: PDF, DOC, DOCX resume processing

### 👥 User Management
- **Role-Based Access Control**: HR, Recruiters, and Applicants with different permissions
- **Custom User Authentication**: Email-based authentication with secure password policies
- **Profile Management**: Comprehensive user profiles with preferences
- **Multi-tenant Support**: Organization-level data isolation

### 💼 Job Management
- **Job Posting System**: Create, edit, and manage job postings
- **Application Tracking**: Complete applicant tracking system (ATS)
- **Bulk Operations**: Process multiple resumes simultaneously
- **Status Management**: Track application status through hiring pipeline

### 📊 Analytics & Reporting
- **Real-time Dashboard**: Live statistics and metrics
- **Candidate Analytics**: Score distributions, skill analysis
- **Performance Metrics**: System health and processing statistics
- **Export Capabilities**: Generate reports in multiple formats

### 🔄 Microservices Architecture
- **Django Backend**: Robust web framework for main application
- **FastAPI AI Service**: High-performance microservice for AI processing
- **Redis Caching**: Fast data caching and session management
- **PostgreSQL Database**: Reliable and scalable data storage
- **Nginx Reverse Proxy**: Load balancing and SSL termination

### 🌐 Modern Frontend
- **React Integration**: Modern, responsive user interface
- **Real-time Updates**: WebSocket connections for live updates
- **Mobile Responsive**: Works seamlessly on all devices
- **Progressive Web App**: Offline capabilities and app-like experience

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  Nginx Proxy    │    │   Django Web    │
│   (Port 3000)   │◄──►│   (Port 80/443) │◄──►│   (Port 8000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────┐             │
                       │  FastAPI AI     │◄────────────┘
                       │  (Port 8001)    │
                       └─────────────────┘
                                │
        ┌──────────────────────────────────────────────────┐
        │                                                  │
        ▼                      ▼                          ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │      Redis      │    │   File Storage  │
│   (Port 5432)   │    │   (Port 6379)   │    │     /media/     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/resume-screener.git
cd resume-screener
```

### 2. Quick Setup with Docker
```bash
# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Admin: http://localhost:8000/admin
```

### 3. Create Superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

## 🔧 Local Development Setup

### 1. Backend Setup (Django)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-production.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start Django development server
python manage.py runserver
```

### 2. AI Microservice Setup (FastAPI)

```bash
# Navigate to AI service directory
cd ai_microservice

# Install dependencies
pip install -r requirements.txt

# Start FastAPI service
python main.py

# Service will be available at http://localhost:8001
```

### 3. Frontend Setup (React)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Frontend will be available at http://localhost:3000
```

### 4. Database Setup (PostgreSQL)

```bash
# Using Docker
docker run --name resume-postgres \
  -e POSTGRES_DB=resume-screener \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 -d postgres:15

# Or install PostgreSQL locally and create database
createdb resume-screener
```

### 5. Redis Setup

```bash
# Using Docker
docker run --name resume-redis \
  -p 6379:6379 -d redis:7-alpine

# Or install Redis locally
redis-server
```

## 🐳 Docker Deployment

### Development Environment
```bash
# Start all development services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Environment
```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations in production
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### Available Services
- **Web Application**: http://localhost:8000
- **AI Microservice**: http://localhost:8001
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Nginx**: http://localhost (production only)

## 🔄 CI/CD Pipeline

The platform includes a comprehensive GitHub Actions CI/CD pipeline:

### Pipeline Stages
1. **Testing**: Unit tests, integration tests, code quality checks
2. **Building**: Docker image creation and registry push
3. **Security**: Vulnerability scanning with Trivy
4. **Deployment**: Automated deployment to staging/production

### Setup CI/CD
1. Push code to GitHub repository
2. Configure GitHub secrets (see `DEPLOYMENT_SECRETS.md`)
3. Pipeline automatically triggers on push to `main` or `develop`

### GitHub Secrets Required
```
PRODUCTION_HOST=your-server-ip
PRODUCTION_USER=deployment-user
PRODUCTION_SSH_KEY=your-private-key
PRODUCTION_DOMAIN=your-domain.com
```

## 📱 API Documentation

### Main API Endpoints

#### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/register/` - User registration

#### Jobs
- `GET /api/jobs/` - List all jobs
- `POST /api/jobs/` - Create new job
- `GET /api/jobs/{id}/` - Job details
- `PUT /api/jobs/{id}/` - Update job
- `DELETE /api/jobs/{id}/` - Delete job

#### Applications
- `POST /api/applications/` - Submit application
- `GET /api/applications/` - List applications
- `GET /api/applications/{id}/` - Application details

#### Resume Processing
- `POST /api/resumes/upload/` - Upload resume
- `GET /api/resumes/{id}/score/` - Get resume score
- `POST /api/resumes/bulk-process/` - Bulk process resumes

### AI Microservice API
- `POST /score/` - Score resume against job description
- `POST /extract/` - Extract text from resume file
- `GET /health/` - Service health check

## 🧪 Testing

### Run All Tests
```bash
# Django tests
python manage.py test

# AI service tests
cd ai_microservice
python -m pytest

# Frontend tests
cd frontend
npm test

# Integration tests
python manage.py test --settings=core.settings_test
```

### Test Coverage
```bash
# Generate coverage report
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Load Testing
```bash
# Using locust
pip install locust
locust -f tests/load_test.py
```

## 📊 Monitoring & Analytics

### System Monitoring
- **Health Checks**: `/health/` endpoint for all services
- **System Status**: Real-time system status dashboard
- **Performance Metrics**: Response times, throughput, error rates

### Business Analytics
- **Resume Processing Stats**: Success rates, processing times
- **User Activity**: Login patterns, feature usage
- **Job Performance**: Application rates, conversion metrics

### Accessing Analytics
- **Django Admin**: http://localhost:8000/admin
- **Analytics Dashboard**: http://localhost:8000/analytics
- **System Status**: http://localhost:8000/status

## 🔐 Security Features

### Data Protection
- **Encrypted Data Storage**: Sensitive data encryption
- **Secure File Upload**: Virus scanning and file validation
- **GDPR Compliance**: Data privacy and deletion capabilities

### Authentication & Authorization
- **JWT Token Authentication**: Secure API access
- **Role-Based Permissions**: Granular access control
- **Session Management**: Secure session handling

### Infrastructure Security
- **HTTPS Enforcement**: SSL/TLS encryption
- **CORS Configuration**: Cross-origin request security
- **Rate Limiting**: API abuse prevention
- **Security Headers**: Comprehensive security headers

## 📄 Environment Configuration

### Required Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/resume_screener
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# AI Service
AI_MICROSERVICE_URL=http://localhost:8001

# Email (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Storage (Optional)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
```

## 🛠️ Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check PostgreSQL status
docker-compose ps postgres

# View database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d
python manage.py migrate
```

#### AI Service Not Responding
```bash
# Check AI service logs
docker-compose logs ai-service

# Restart AI service
docker-compose restart ai-service

# Test AI service directly
curl http://localhost:8001/health/
```

#### Frontend Build Issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for port conflicts
lsof -i :3000
```

### Performance Optimization
- **Database Indexing**: Ensure proper database indexes
- **Redis Caching**: Configure Redis for optimal performance
- **File Storage**: Use CDN for static files in production
- **Load Balancing**: Scale services horizontally

## 📚 Additional Resources

### Documentation
- [Django Documentation](https://docs.djangoproject.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Project Documentation
- `CICD_DEPLOYMENT_GUIDE.md` - Complete CI/CD setup guide
- `DEPLOYMENT_SECRETS.md` - Security configuration guide
- `PIPELINE_STATUS.md` - Current pipeline status

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React code
- Write tests for new features
- Update documentation as needed

## 📞 Support

For support and questions:
- **Issues**: [GitHub Issues](https://github.com/yourusername/resume-screener/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/resume-screener/discussions)
- **Email**: support@resumescreener.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django community for the excellent web framework
- FastAPI team for the high-performance API framework
- scikit-learn contributors for machine learning capabilities
- All contributors who have helped make this project better

---

**Built with ❤️ using Django, FastAPI, React, and modern DevOps practices**