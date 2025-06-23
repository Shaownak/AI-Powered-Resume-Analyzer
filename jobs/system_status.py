import logging
import os
from urllib.parse import urlparse

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from django.conf import settings

logger = logging.getLogger(__name__)

def check_redis_status():
    """Check if Redis is running and accessible"""
    try:
        # Get Redis connection details from environment or Django settings
        redis_url = os.getenv('REDIS_URL', 'redis://:redis_password@redis:6379/0')
        parsed_url = urlparse(redis_url)
        
        # Extract connection parameters
        host = parsed_url.hostname or 'redis'
        port = parsed_url.port or 6379
        password = parsed_url.password
        db = int(parsed_url.path.lstrip('/')) if parsed_url.path.lstrip('/') else 0
        
        # Try connecting to Redis (Docker instance)
        r = redis.Redis(
            host=host, 
            port=port, 
            password=password,
            db=db, 
            socket_timeout=3, 
            socket_connect_timeout=3
        )
        r.ping()
        
        # Test basic operations
        r.set('health_check', 'ok', ex=60)  # Set with 60s expiry
        test_value = r.get('health_check')
        
        if test_value:
            return {
                'status': 'online',
                'message': 'Redis is running and accessible',
                'color': 'green'
            }
        else:
            return {
                'status': 'degraded',
                'message': 'Redis connected but operations failing',
                'color': 'yellow'
            }
    except redis.ConnectionError as e:
        return {
            'status': 'offline',
            'message': f'Redis connection failed: {str(e)[:50]}...',
            'color': 'red'
        }
    except redis.TimeoutError:
        return {
            'status': 'timeout',
            'message': 'Redis connection timeout',
            'color': 'yellow'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Redis error: {str(e)[:50]}...',
            'color': 'red'
        }

def check_ai_microservice_status():
    """Check if AI microservice is running and accessible"""
    try:
        # Get AI microservice URL from environment or settings
        ai_service_url = os.getenv('AI_MICROSERVICE_URL', 'http://ai-service:8001')
        health_url = f"{ai_service_url}/health"
        
        # Try to reach the AI microservice health endpoint
        response = requests.get(health_url, timeout=3)
        if response.status_code == 200:
            return {
                'status': 'online',
                'message': 'AI microservice is running',
                'color': 'green'
            }
        else:
            return {
                'status': 'degraded',
                'message': f'AI service returned status {response.status_code}',
                'color': 'yellow'
            }
    except requests.exceptions.ConnectionError:
        return {
            'status': 'offline',
            'message': 'AI microservice unreachable',
            'color': 'red'
        }
    except requests.exceptions.Timeout:
        return {
            'status': 'timeout',
            'message': 'AI microservice timeout',
            'color': 'yellow'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'AI service error: {str(e)}',
            'color': 'red'
        }

def check_database_status():
    """Check database connectivity"""
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        return {
            'status': 'online',
            'message': 'Database connected',
            'color': 'green'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Database error: {str(e)}',
            'color': 'red'
        }

def get_system_status():
    """Get overall system status"""
    redis_status = check_redis_status()
    ai_status = check_ai_microservice_status()
    db_status = check_database_status()
    
    # Determine overall health
    statuses = [redis_status['status'], ai_status['status'], db_status['status']]
    
    if all(s == 'online' for s in statuses):
        overall_status = {
            'status': 'healthy',
            'message': 'All systems operational',
            'color': 'green'
        }
    elif any(s == 'offline' for s in statuses):
        overall_status = {
            'status': 'critical',
            'message': 'One or more services offline',
            'color': 'red'
        }
    else:
        overall_status = {
            'status': 'degraded',
            'message': 'System experiencing issues',
            'color': 'yellow'
        }
    
    return {
        'overall': overall_status,
        'services': {
            'redis': redis_status,
            'ai_microservice': ai_status,
            'database': db_status
        }
    }
