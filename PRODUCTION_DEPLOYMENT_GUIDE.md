# Production Deployment Guide

## Overview
This guide covers the complete production deployment of the Resume Screener Platform using Docker, Nginx, and modern DevOps practices.

## Architecture

```
Internet → Nginx (Reverse Proxy) → Django Backend
                                 → AI Microservice
                                 → Redis (Cache/Message Broker)
                                 → PostgreSQL (Database)
```

## 🚀 Quick Start

### Prerequisites
- Docker Engine 24.0+
- Docker Compose v2.0+
- Git
- Domain name with DNS configured
- SSL certificates (Let's Encrypt recommended)

### 1. Clone and Configure

```bash
git clone <your-repository-url>
cd resume-screener
cp .env.example .env
# Edit .env with your production values
```

### 2. Deploy

```bash
chmod +x scripts/*.sh
./scripts/deploy.sh production
```

## 🔧 Configuration

### Environment Variables (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `False` |
| `SECRET_KEY` | Django secret key | `your-secret-key` |
| `ALLOWED_HOSTS` | Allowed hosts | `your-domain.com,www.your-domain.com` |
| `DATABASE_URL` | PostgreSQL URL | `postgresql://user:pass@db:5432/dbname` |
| `REDIS_URL` | Redis URL | `redis://:password@redis:6379/0` |
| `SENTRY_DSN` | Sentry error tracking | `https://...@sentry.io/...` |

### SSL/TLS Configuration

1. **Using Let's Encrypt (Recommended):**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificates
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

2. **Custom Certificates:**
```bash
# Place certificates in docker/nginx/ssl/
cp your-cert.pem docker/nginx/ssl/cert.pem
cp your-key.pem docker/nginx/ssl/key.pem
```

## 🐳 Docker Services

### Service Overview

| Service | Port | Description |
|---------|------|-------------|
| `nginx` | 80, 443 | Reverse proxy and load balancer |
| `web` | 8000 | Django application |
| `ai-service` | 8001 | AI microservice for resume scoring |
| `db` | 5432 | PostgreSQL database |
| `redis` | 6379 | Redis cache and message broker |
| `celery` | - | Background task worker |
| `celery-beat` | - | Task scheduler |

### Health Checks

All services include health checks:
- **Web**: Django management command check
- **AI Service**: HTTP health endpoint
- **Database**: PostgreSQL ready check
- **Redis**: Redis ping command

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

The pipeline includes:
1. **Testing**: Unit tests, integration tests, coverage
2. **Security**: Bandit security scan, dependency checks
3. **Build**: Docker image builds and pushes
4. **Deploy**: Automated deployment to staging/production

### Required Secrets

Configure these in GitHub repository settings:

| Secret | Description |
|--------|-------------|
| `STAGING_HOST` | Staging server IP/hostname |
| `STAGING_USER` | SSH username for staging |
| `STAGING_SSH_KEY` | SSH private key for staging |
| `PRODUCTION_HOST` | Production server IP/hostname |
| `PRODUCTION_USER` | SSH username for production |
| `PRODUCTION_SSH_KEY` | SSH private key for production |
| `SLACK_WEBHOOK` | Slack webhook for notifications |

## 📊 Monitoring & Logging

### Sentry Integration

Error tracking and performance monitoring:

```python
# Automatic with settings_production.py
SENTRY_DSN = "your-sentry-dsn"
```

### Log Management

Logs are collected in volumes:
- **Application logs**: `/app/logs/`
- **Nginx logs**: Container logs
- **Database logs**: Container logs

### Health Monitoring

Use the monitoring script:
```bash
./scripts/monitor.sh
```

Set up cron job for regular checks:
```bash
*/5 * * * * /opt/resume-screener/scripts/monitor.sh
```

## 🗄️ Backup & Recovery

### Automated Backups

```bash
# Manual backup
./scripts/backup.sh

# Schedule daily backups
0 2 * * * /opt/resume-screener/scripts/backup.sh
```

### Recovery Process

```bash
# Restore database
gunzip < db_backup_YYYYMMDD_HHMMSS.sql.gz | docker-compose exec -T db psql -U postgres resume_screener

# Restore media files
docker run --rm -v resume-screener_media_volume:/target -v /opt/backups:/backup alpine tar xzf /backup/media_backup_YYYYMMDD_HHMMSS.tar.gz -C /target

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

## ⚡ Performance Optimization

### Nginx Configuration
- Gzip compression enabled
- Static file caching (1 year)
- HTTP/2 support
- Rate limiting for API endpoints

### Django Optimizations
- WhiteNoise for static files
- Redis caching
- Database connection pooling
- Celery for background tasks

### Database Optimization
- PostgreSQL with optimized settings
- Regular VACUUM and ANALYZE
- Connection pooling
- Read replicas (if needed)

## 🔒 Security

### Implemented Security Measures
- HTTPS enforcement
- Security headers (HSTS, CSP, etc.)
- Rate limiting
- IP-based admin access restriction
- Regular security updates
- Environment variable secrets
- Non-root containers

### Security Checklist
- [ ] Change default passwords
- [ ] Configure firewall rules
- [ ] Enable fail2ban
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Backup encryption

## 🚨 Troubleshooting

### Common Issues

**Service won't start:**
```bash
docker-compose -f docker-compose.prod.yml logs [service-name]
```

**Database connection issues:**
```bash
docker-compose -f docker-compose.prod.yml exec db pg_isready -U postgres
```

**SSL certificate issues:**
```bash
sudo certbot certificates
sudo nginx -t
```

**High memory usage:**
```bash
docker stats
docker system prune
```

### Emergency Procedures

**Emergency shutdown:**
```bash
docker-compose -f docker-compose.prod.yml down
```

**Emergency restart:**
```bash
./scripts/deploy.sh production
```

**Database emergency access:**
```bash
docker-compose -f docker-compose.prod.yml exec db psql -U postgres resume_screener
```

## 📞 Support

- **Documentation**: Check this guide and inline comments
- **Logs**: Use `docker-compose logs` for troubleshooting
- **Monitoring**: Check Sentry dashboard for errors
- **Health**: Use `/health` endpoint for service status

## 🔄 Updates

### Updating the Application

1. Push code to repository
2. CI/CD pipeline automatically builds and deploys
3. Or manually: `./scripts/deploy.sh production`

### Updating Dependencies

1. Update requirements files
2. Rebuild Docker images
3. Test in staging environment
4. Deploy to production

This production setup provides a robust, scalable, and maintainable deployment for the Resume Screener Platform.
