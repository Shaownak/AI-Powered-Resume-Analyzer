from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from api.routes import router as score_router
from cache.redis_cache import RedisCache
import uvicorn
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="AI Resume Scorer", 
    version="1.0.0",
    description="AI-powered resume scoring microservice with Redis caching and rate limiting"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add SlowAPI middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AI Resume Scorer is running"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    try:
        cache = RedisCache()
        redis_status = "connected" if cache.is_connected() else "disconnected"
        
        return {
            "status": "healthy",
            "redis": redis_status,
            "service": "ai-resume-scorer"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy", 
            "error": str(e),
            "service": "ai-resume-scorer"
        }

# Include API routes
app.include_router(score_router)

if __name__ == "__main__":
    logger.info("Starting AI Resume Scorer microservice...")
    uvicorn.run(app, host="127.0.0.1", port=8001)
