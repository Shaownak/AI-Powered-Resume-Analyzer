import redis
import json
import hashlib
import logging
import os
from typing import Optional, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self, host=None, port=None, db=None, password=None, decode_responses=True):
        """Initialize Redis connection for caching with fallback handling"""
        
        # Read from environment variables if parameters not provided
        if host is None or port is None:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/1')
            parsed = urlparse(redis_url)
            host = parsed.hostname or 'localhost'
            port = parsed.port or 6379
            db = db or (parsed.path.lstrip('/') or '1')
            password = password or parsed.password
            
        try:
            redis_params = {
                'host': host,
                'port': int(port),
                'db': int(db),
                'decode_responses': decode_responses,
                'socket_connect_timeout': 5,
                'socket_timeout': 5
            }
            
            if password:
                redis_params['password'] = password
                
            self.redis_client = redis.Redis(**redis_params)
            
            # Test connection
            self.redis_client.ping()
            self._connected = True
            logger.info(f"✅ Redis connection established at {host}:{port}")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}. Running without cache.")
            self.redis_client = None
            self._connected = False
    
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def _generate_key(self, prefix: str, *args) -> str:
        """Generate a unique cache key from arguments"""
        key_data = f"{prefix}:{':'.join(map(str, args))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self._connected:
            return None
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, expiry: int = 3600) -> bool:
        """Set value in cache with expiry (default 1 hour)"""
        if not self._connected:
            return False
        try:
            serialized_value = json.dumps(value)
            return self.redis_client.setex(key, expiry, serialized_value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self._connected:
            return False
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self._connected:
            return False
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists check error: {e}")
            return False
    
    def get_score_cache_key(self, resume_text: str, job_description: str) -> str:
        """Generate cache key for resume scoring"""
        return self._generate_key("score", resume_text[:100], job_description[:100])
    
    def get_score(self, cache_key: str) -> Optional[float]:
        """Get cached resume score"""
        cached_data = self.get(cache_key)
        if cached_data and isinstance(cached_data, dict):
            return cached_data.get('score')
        return cached_data  # For backward compatibility if score was stored directly
    def set_score(self, cache_key: str, score: float, expiry: int = 3600) -> bool:
        """Set cached resume score with metadata"""
        import time
        score_data = {
            'score': score,
            'timestamp': str(int(time.time()))
        }
        return self.set(cache_key, score_data, expiry)

# Global cache instance
cache = RedisCache()
