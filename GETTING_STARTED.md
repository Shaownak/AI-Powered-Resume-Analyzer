# 🚀 Getting Started Guide

This guide will help you get the Resume Screener Platform up and running in just a few minutes!

## 🎯 What You'll Have After Setup

- ✅ A complete AI-powered resume screening platform
- ✅ Web interface for HR teams and recruiters
- ✅ AI microservice for intelligent resume analysis
- ✅ Database for storing jobs, applications, and user data
- ✅ Admin panel for platform management

## 📋 Prerequisites

Before starting, make sure you have:

1. **Docker Desktop** installed
   - Windows: [Download Docker Desktop](https://docs.docker.com/desktop/install/windows-install/)
   - Mac: [Download Docker Desktop](https://docs.docker.com/desktop/install/mac-install/)
   - Linux: [Install Docker Engine](https://docs.docker.com/engine/install/)

2. **Git** installed
   - [Download Git](https://git-scm.com/downloads)

## 🚀 Super Quick Start (5 minutes)

### Step 1: Get the Code
```bash
# Clone the repository
git clone https://github.com/yourusername/resume-screener.git
cd resume-screener
```

### Step 2: Run Setup Script

**On Windows (PowerShell):**
```powershell
.\quick-setup.ps1
```

**On Mac/Linux:**
```bash
chmod +x quick-setup.sh
./quick-setup.sh
```

### Step 3: Create Admin User
```bash
docker-compose exec web python manage.py createsuperuser
```
Enter your email, password when prompted.

### Step 4: Access Your Platform
- **Main Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **AI Service**: http://localhost:8001

🎉 **That's it! Your platform is running!**

## 📖 Manual Setup (if you prefer step-by-step)

### 1. Clone and Enter Directory
```bash
git clone https://github.com/yourusername/resume-screener.git
cd resume-screener
```

### 2. Set Up Environment
```bash
# Copy environment template
cp .env.example .env
# Edit .env file with your preferences (optional for local dev)
```

### 3. Start Services
```bash
# Start all services in background
docker-compose -f docker-compose.dev.yml up -d

# Wait 10 seconds for services to start
```

### 4. Set Up Database
```bash
# Run database migrations
docker-compose exec web python manage.py migrate

# Create superuser account
docker-compose exec web python manage.py createsuperuser
```

### 5. Access Your Platform
Open your browser and go to:
- http://localhost:8000 (main application)
- http://localhost:8000/admin (admin panel)

## 🎨 Using the Platform

### For HR/Recruiters:
1. **Login** at http://localhost:8000/admin with your superuser account
2. **Create Job Postings** in the admin panel
3. **Upload Resumes** for automatic AI analysis
4. **View Analytics** at http://localhost:8000/analytics

### For Applicants:
1. **Register** for an account at http://localhost:8000
2. **Browse Jobs** and apply
3. **Upload Resume** and get instant AI scoring

## 🔧 Common Commands

### View Running Services
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web
docker-compose logs ai-service
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Update Platform
```bash
git pull origin main
docker-compose down
docker-compose up -d --build
```

## 🛠️ Troubleshooting

### Services Won't Start
```bash
# Check if ports are in use
netstat -an | grep :8000
netstat -an | grep :8001

# Stop and restart
docker-compose down
docker-compose up -d
```

### Database Issues
```bash
# Reset database (WARNING: loses all data)
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### Permission Issues (Linux/Mac)
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x quick-setup.sh
```

## 📞 Getting Help

- **Documentation**: See main README.md for complete docs
- **Issues**: Create an issue on GitHub
- **Logs**: Always check `docker-compose logs` for error details

## 🎯 Next Steps

Once everything is running:

1. **Explore the Admin Panel** - Create test jobs and upload sample resumes
2. **Check Analytics** - View the dashboard at `/analytics`
3. **API Testing** - Visit `/api/` for API documentation
4. **Customize** - Edit settings in `.env` file
5. **Deploy** - See deployment guides for production setup

**Happy Screening! 🚀**
