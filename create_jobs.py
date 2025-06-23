import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from jobs.models import Job
from django.contrib.auth.models import User

# Check if we have an admin user
print("Checking for admin user...")
if User.objects.filter(username='admin').exists():
    print("Admin user exists!")
else:
    print("Creating admin user...")
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')
    print("Admin user created!")

# Check if we have any jobs
print("\nChecking for jobs...")
job_count = Job.objects.count()
print(f"Found {job_count} jobs in the database.")

# If no jobs exist, create some
if job_count == 0:
    print("Creating sample jobs...")
    admin_user = User.objects.get(username='admin')
    
    # Create sample jobs
    Job.objects.create(
        title="Python Developer",
        description="We are looking for a Python developer with Django experience.",
        posted_by=admin_user
    )
    
    Job.objects.create(
        title="Frontend Developer",
        description="Looking for a Frontend developer with React and JavaScript skills.",
        posted_by=admin_user
    )
    
    Job.objects.create(
        title="Data Scientist",
        description="Data scientist position with experience in Python, pandas, and machine learning.",
        posted_by=admin_user
    )
    
    print(f"Created {Job.objects.count()} sample jobs!")
else:
    print("Sample jobs already exist.")

print("\nSetup complete! Please refresh your browser to see the jobs.")
