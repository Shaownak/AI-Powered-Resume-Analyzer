# GitHub Secrets Configuration Guide

This document lists all the secrets you need to configure in your GitHub repository for the CI/CD pipeline to work.

## Required GitHub Secrets

### Production Deployment Secrets
- `PRODUCTION_HOST`: Your production server IP address or hostname
- `PRODUCTION_USER`: SSH username for your production server
- `PRODUCTION_SSH_KEY`: Private SSH key for accessing your production server
- `PRODUCTION_DOMAIN`: Your production domain (e.g., yourdomain.com)

### Staging Deployment Secrets (Optional)
- `STAGING_HOST`: Your staging server IP address or hostname
- `STAGING_USER`: SSH username for your staging server
- `STAGING_SSH_KEY`: Private SSH key for accessing your staging server

### Notification Secrets (Optional)
- `SLACK_WEBHOOK`: Slack webhook URL for deployment notifications

## How to Configure Secrets

1. Go to your GitHub repository
2. Click on **Settings**
3. Click on **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add each secret with the name and value

## Example SSH Key Generation

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "github-actions@yourdomain.com" -f github-actions-key

# Copy public key to your server
ssh-copy-id -i github-actions-key.pub user@your-server.com

# Add private key content to GitHub secret PRODUCTION_SSH_KEY
cat github-actions-key
```

## Production Server Setup

Your production server should have:

1. Docker and Docker Compose installed
2. Git repository cloned to `/opt/resume-screener`
3. Environment variables configured in `.env` file
4. SSL certificates in place (if using HTTPS)
5. User with sudo access for Docker commands

## Environment Variables on Server

Create a `.env` file on your production server:

```bash
# Production Environment Variables
DEBUG=False
SECRET_KEY=your-super-secure-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://postgres:secure_password@db:5432/resume_screener
REDIS_URL=redis://:redis_password@redis:6379/0
DB_PASSWORD=secure_password
REDIS_PASSWORD=redis_password
EMAIL_HOST=smtp.yourdomain.com
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=email_password
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
ENVIRONMENT=production
RELEASE_VERSION=1.0.0
```

## SSL Certificate Setup

If using HTTPS, place your SSL certificates in:
```
docker/nginx/ssl/cert.pem
docker/nginx/ssl/key.pem
```

## First Deployment

For the first deployment, manually run on your server:

```bash
# Clone repository
sudo mkdir -p /opt/resume-screener
sudo chown $USER:$USER /opt/resume-screener
git clone https://github.com/yourusername/resume-screener.git /opt/resume-screener
cd /opt/resume-screener

# Create .env file (see above)
nano .env

# Initial deployment
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## Monitoring and Logs

Check deployment status:
```bash
# Check running containers
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f ai-service
docker-compose -f docker-compose.prod.yml logs -f nginx

# Check system status
curl https://yourdomain.com/api/system-status/
```
