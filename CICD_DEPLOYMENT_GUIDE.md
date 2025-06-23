# Resume Screener Platform - CI/CD Deployment Guide

This guide walks you through setting up a complete CI/CD pipeline for deploying your Django + AI microservice platform to GitHub with automated deployments.

## 🚀 Overview

The CI/CD pipeline includes:
- **Automated Testing**: Django tests, AI microservice tests, code quality checks
- **Docker Image Building**: Multi-stage builds for production optimization
- **Security Scanning**: Vulnerability scanning with Trivy
- **Automated Deployment**: Staging and production deployments
- **Health Monitoring**: Post-deployment health checks
- **Notifications**: Slack notifications for deployment status

## 📋 Prerequisites

### 1. GitHub Repository Setup
```bash
# Initialize git repository (if not already done)
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/resume-screener.git
git push -u origin main

# Create develop branch for staging
git checkout -b develop
git push -u origin develop
```

### 2. Production Server Requirements
- Ubuntu 20.04+ or similar Linux distribution
- Docker and Docker Compose installed
- SSH access configured
- Domain name pointed to server (optional)
- SSL certificate (for HTTPS)

### 3. GitHub Secrets Configuration
Configure these secrets in your GitHub repository:

#### Required Secrets:
```
PRODUCTION_HOST=your-server-ip
PRODUCTION_USER=your-ssh-username
PRODUCTION_SSH_KEY=your-private-ssh-key
PRODUCTION_DOMAIN=yourdomain.com
```

#### Optional Secrets:
```
STAGING_HOST=staging-server-ip
STAGING_USER=staging-ssh-username
STAGING_SSH_KEY=staging-private-ssh-key
SLACK_WEBHOOK=your-slack-webhook-url
```

## 🔧 Server Setup

### 1. Install Docker on Production Server
```bash
# Update package index
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for group changes to take effect
```

### 2. Clone Repository on Server
```bash
# Create project directory
sudo mkdir -p /opt/resume-screener
sudo chown $USER:$USER /opt/resume-screener

# Clone repository
git clone https://github.com/yourusername/resume-screener.git /opt/resume-screener
cd /opt/resume-screener
```

### 3. Configure Environment Variables
```bash
# Create production environment file
nano .env
```

Add the following content:
```env
# Production Environment Variables
DEBUG=False
SECRET_KEY=your-super-secure-secret-key-generate-new-one
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost

# Database Configuration
DATABASE_URL=postgresql://postgres:secure_db_password@db:5432/resume_screener
DB_PASSWORD=secure_db_password

# Redis Configuration
REDIS_URL=redis://:secure_redis_password@redis:6379/0
REDIS_PASSWORD=secure_redis_password

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourdomain.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your_email_password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Monitoring (optional)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
ENVIRONMENT=production
RELEASE_VERSION=1.0.0
```

### 4. SSL Certificate Setup (Optional)
```bash
# Using Let's Encrypt with Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to project
sudo mkdir -p /opt/resume-screener/docker/nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /opt/resume-screener/docker/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /opt/resume-screener/docker/nginx/ssl/key.pem
sudo chown -R $USER:$USER /opt/resume-screener/docker/nginx/ssl
```

## 🚀 Deployment Process

### 1. Initial Manual Deployment
```bash
cd /opt/resume-screener

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Run initial setup
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### 2. Verify Deployment
```bash
# Check running services
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Test endpoints
curl http://localhost/health
curl http://localhost/api/system-status/
```

## 🔄 CI/CD Workflow

### Trigger Conditions:
- **Pull Requests to main**: Run tests only
- **Push to develop**: Run tests → Build → Deploy to staging
- **Push to main**: Run tests → Build → Security scan → Deploy to production

### Pipeline Stages:

1. **Test Stage**:
   - Set up PostgreSQL and Redis services
   - Install Python dependencies
   - Run Django tests and AI microservice tests
   - Code quality checks (flake8, black, isort)

2. **Build Stage**:
   - Build Docker images for web and AI service
   - Push to GitHub Container Registry
   - Cache layers for faster builds

3. **Security Stage**:
   - Vulnerability scanning with Trivy
   - Upload results to GitHub Security tab

4. **Deploy Stage**:
   - SSH to production server
   - Pull latest code and images
   - Rolling deployment with health checks
   - Slack notifications

## 📊 Monitoring and Maintenance

### Health Monitoring
The pipeline includes automatic health checks:
```bash
# Health endpoints
curl https://yourdomain.com/health
curl https://yourdomain.com/api/system-status/
curl https://yourdomain.com/nginx-health
```

### Log Monitoring
```bash
# View application logs
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f ai-service
docker-compose -f docker-compose.prod.yml logs -f nginx

# System monitoring
docker stats
docker-compose -f docker-compose.prod.yml ps
```

### Backup Strategy
Automated backups are created before each deployment:
```bash
# Database backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres resume_screener > backup.sql

# Media files backup
tar -czf media_backup.tar.gz media/
```

## 🔧 Troubleshooting

### Common Issues:

1. **SSH Connection Failed**:
   - Verify SSH key is correctly added to GitHub secrets
   - Test SSH connection: `ssh user@server`
   - Check server firewall settings

2. **Docker Build Failed**:
   - Check Dockerfile syntax
   - Verify base images are available
   - Check for sufficient disk space

3. **Health Check Failed**:
   - Check application logs
   - Verify database connectivity
   - Check Redis connection
   - Verify nginx configuration

4. **Deployment Timeout**:
   - Increase timeout in workflow
   - Check server resources
   - Monitor container startup logs

### Manual Rollback:
```bash
# Rollback to previous version
cd /opt/resume-screener
git log --oneline -10  # Find previous commit
git reset --hard <previous-commit-hash>
docker-compose -f docker-compose.prod.yml up -d --build
```

## 🎯 Best Practices

1. **Security**:
   - Use strong passwords and secrets
   - Regularly update dependencies
   - Monitor security scan results
   - Use HTTPS in production

2. **Performance**:
   - Monitor resource usage
   - Use Docker image caching
   - Optimize database queries
   - Configure proper logging levels

3. **Reliability**:
   - Test deployments in staging first
   - Use rolling deployments
   - Implement proper health checks
   - Have rollback procedures ready

4. **Monitoring**:
   - Set up alerts for critical issues
   - Monitor application metrics
   - Track deployment success rates
   - Review security scan results

## 📚 Next Steps

1. Set up monitoring with Prometheus/Grafana
2. Implement log aggregation with ELK stack
3. Add integration tests
4. Set up automated database migrations
5. Implement blue-green deployments
6. Add performance testing to CI/CD

This CI/CD setup provides a robust, production-ready deployment pipeline for your Resume Screener platform! 🚀
