#!/usr/bin/env python
"""
Local test script to debug CI issues
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to the path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_test')

try:
    django.setup()
    print("✅ Django setup successful")
    
    # Test basic imports
    from accounts.models import CustomUser
    from jobs.models import Job
    print("✅ Model imports successful")
    
    # Test database connection
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    print("✅ Database connection successful")
    
    # Run basic Django tests
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests([])
    
    if failures:
        print(f"❌ Tests failed: {failures}")
        sys.exit(1)
    else:
        print("✅ All tests passed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
