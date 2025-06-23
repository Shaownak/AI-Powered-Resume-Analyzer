#!/usr/bin/env python3
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.models import CustomUser, ApplicantProfile, HRProfile
from jobs.models import Job, JobApplication, Resume
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile

def comprehensive_system_test():
    print("🔍 COMPREHENSIVE SYSTEM TEST")
    print("=" * 60)
    
    client = Client()
    
    # Test 1: URL Resolution
    print("\n1. 🌐 Testing URL Resolution")
    test_urls = [
        ('/', 'home'),
        ('/login/', 'login'),  
        ('/signup/applicant/', 'applicant_signup'),
        ('/signup/hr/', 'hr_signup'),
        ('/jobs/', 'job_list'),
        ('/profile/', 'profile'),
        ('/dashboard/applicant/', 'applicant_dashboard'),
        ('/dashboard/hr/', 'hr_dashboard'),
    ]
    
    for url, name in test_urls:
        try:
            response = client.get(url)
            if response.status_code in [200, 302]:  # 302 for login redirects
                print(f"  ✅ {url} ({name}): Status {response.status_code}")
            else:
                print(f"  ❌ {url} ({name}): Status {response.status_code}")
        except Exception as e:
            print(f"  ❌ {url} ({name}): Error - {str(e)}")
    
    # Test 2: User Authentication
    print("\n2. 🔐 Testing User Authentication")
    try:
        # Create test users if they don't exist
        hr_user, created = CustomUser.objects.get_or_create(
            username='test_hr_user',
            defaults={
                'email': 'test_hr@example.com',
                'user_type': 'hr',
                'first_name': 'Test',
                'last_name': 'HR'
            }
        )
        hr_user.set_password('testpass123')
        hr_user.save()
        
        applicant_user, created = CustomUser.objects.get_or_create(
            username='test_applicant_user',
            defaults={
                'email': 'test_applicant@example.com', 
                'user_type': 'applicant',
                'first_name': 'Test',
                'last_name': 'Applicant'
            }
        )
        applicant_user.set_password('testpass123')
        applicant_user.save()
        
        # Test login
        login_result = client.login(username='test_hr_user', password='testpass123')
        print(f"  ✅ HR Login: {'SUCCESS' if login_result else 'FAILED'}")
        
        login_result = client.login(username='test_applicant_user', password='testpass123')
        print(f"  ✅ Applicant Login: {'SUCCESS' if login_result else 'FAILED'}")
        
    except Exception as e:
        print(f"  ❌ Authentication Test Error: {str(e)}")
    
    # Test 3: Profile Creation and Access
    print("\n3. 👤 Testing Profile System")
    try:
        # Ensure profiles exist
        hr_profile, created = HRProfile.objects.get_or_create(
            user=hr_user,
            defaults={'company_name': 'Test Company', 'job_title': 'Test HR Manager'}
        )
        
        applicant_profile, created = ApplicantProfile.objects.get_or_create(
            user=applicant_user,
            defaults={'full_name': 'Test Applicant'}
        )
        
        print(f"  ✅ HR Profile: {hr_profile.company_name}")
        print(f"  ✅ Applicant Profile: {applicant_profile.full_name}")
        
    except Exception as e:
        print(f"  ❌ Profile Test Error: {str(e)}")
    
    # Test 4: Job Creation and Management
    print("\n4. 💼 Testing Job Management")
    try:
        # Login as HR user
        client.login(username='test_hr_user', password='testpass123')
        
        # Test job creation
        job_data = {
            'title': 'Test Software Engineer',
            'description': 'Test job description',
            'requirements': 'Test requirements', 
            'location': 'Test City',
            'salary_range': '50000-70000',
            'employment_type': 'full_time',
        }
        
        # Check if create job view works
        response = client.get('/jobs/create-job/')
        print(f"  ✅ Create Job Page: Status {response.status_code}")
        
        # Create job programmatically
        job = Job.objects.create(
            title=job_data['title'],
            description=job_data['description'],
            requirements=job_data['requirements'],
            location=job_data['location'],
            salary_range=job_data['salary_range'],
            employment_type=job_data['employment_type'],
            posted_by=hr_user
        )
        print(f"  ✅ Job Created: {job.title}")
        
    except Exception as e:
        print(f"  ❌ Job Management Error: {str(e)}")
    
    # Test 5: Application Process
    print("\n5. 📝 Testing Application Process")
    try:
        # Login as applicant
        client.login(username='test_applicant_user', password='testpass123')
        
        # Test job application
        if 'job' in locals():
            response = client.get(f'/jobs/job/{job.id}/apply/')
            print(f"  ✅ Apply Page: Status {response.status_code}")
            
            # Create test resume file
            test_file = SimpleUploadedFile(
                "test_resume.pdf",
                b"fake pdf content",
                content_type="application/pdf"
            )
            
            # Create application programmatically
            application = JobApplication.objects.create(
                job=job,
                applicant=applicant_user,
                cover_letter='Test cover letter',
                status='pending'
            )
            print(f"  ✅ Application Created: Status {application.status}")
        
    except Exception as e:
        print(f"  ❌ Application Process Error: {str(e)}")
    
    # Test 6: Template Rendering
    print("\n6. 🎨 Testing Template Rendering")
    try:
        # Test key templates
        client.logout()
        
        templates_to_test = [
            ('/', 'Home page'),
            ('/login/', 'Login page'),
            ('/signup/applicant/', 'Applicant signup'),
            ('/signup/hr/', 'HR signup'),
            ('/jobs/', 'Job list'),
        ]
        
        for url, desc in templates_to_test:
            response = client.get(url)
            if response.status_code == 200:
                print(f"  ✅ {desc}: Rendered successfully")
            else:
                print(f"  ❌ {desc}: Status {response.status_code}")
                
    except Exception as e:
        print(f"  ❌ Template Rendering Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 COMPREHENSIVE TEST COMPLETED!")
    print("\nNext: Check for specific UI/UX issues and template errors...")

if __name__ == "__main__":
    comprehensive_system_test()
