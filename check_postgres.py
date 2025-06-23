import os
import sys

import psycopg2

import django
from django.db import connection

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

try:
    # Try to connect to PostgreSQL directly
    print("Attempting direct PostgreSQL connection...")
    conn = psycopg2.connect(dbname="resume_screener", user="postgres", password="shaownak", host="localhost", port="5432")
    print("✅ Direct PostgreSQL connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Direct PostgreSQL connection failed: {e}")
    print("\nPossible issues:")
    print("1. PostgreSQL is not running")
    print("2. Database 'resume_screener' does not exist")
    print("3. Username/password is incorrect")
    print("4. PostgreSQL is not listening on port 5432")

try:
    # Try Django connection
    print("\nAttempting Django connection to PostgreSQL...")
    django.setup()

    # Test Django DB connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

    print("✅ Django PostgreSQL connection successful!")

    # Check if tables exist
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'jobs_job'
            )
        """
        )
        job_table_exists = cursor.fetchone()[0]

    if job_table_exists:
        print("✅ Database tables exist!")
    else:
        print("❌ Database tables don't exist. You need to run migrations.")

except Exception as e:
    print(f"❌ Django PostgreSQL connection failed: {e}")
    print("\nTry running these commands:")
    print("1. python manage.py makemigrations")
    print("2. python manage.py migrate")
    print("3. python setup_data.py")
