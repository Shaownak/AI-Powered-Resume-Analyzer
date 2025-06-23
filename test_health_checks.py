#!/usr/bin/env python
"""
Test script to verify Redis and AI microservice health checks
"""
import os
import sys
import django

# Set environment variables
os.environ['REDIS_URL'] = 'redis://:redis_password@localhost:6379/0'
os.environ['AI_MICROSERVICE_URL'] = 'http://localhost:8001'

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import and test health checks
from jobs.system_status import check_redis_status, check_ai_microservice_status

print("Testing Redis connection...")
redis_status = check_redis_status()
print(f"Redis Status: {redis_status}")

print("\nTesting AI Microservice connection...")
ai_status = check_ai_microservice_status()
print(f"AI Microservice Status: {ai_status}")

print("\n" + "="*50)
if redis_status['status'] == 'online':
    print("✅ Redis is ONLINE - This should now show correctly in analytics!")
else:
    print("❌ Redis is still showing as offline")

if ai_status['status'] == 'online':
    print("✅ AI Microservice is ONLINE")
else:
    print("❌ AI Microservice is offline")
