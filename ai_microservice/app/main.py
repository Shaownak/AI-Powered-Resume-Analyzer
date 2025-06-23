from app.api.routes import router as api_router
from app.config import redis_client
from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limiter
limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379")

app = FastAPI(title="Resume Scoring Microservice")
app.state.limiter = limiter

app.include_router(api_router)
