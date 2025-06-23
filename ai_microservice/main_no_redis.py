import logging

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Resume Scorer - No Redis", version="1.0.0", description="AI-powered resume scoring service (simplified version)"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory cache (for demo purposes)
simple_cache = {}


class ResumeScore(BaseModel):
    job_id: int
    resume_text: str


class ScoreResponse(BaseModel):
    score: float
    feedback: str
    status: str


@app.get("/")
async def root():
    return {"message": "AI Resume Scorer API", "version": "1.0.0", "status": "running", "redis": "disabled"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ai-resume-scorer", "redis_status": "disabled", "cache": "in-memory"}


@app.post("/score", response_model=ScoreResponse)
async def score_resume(request: ResumeScore):
    """Simple resume scoring without Redis"""
    try:
        # Simple scoring logic (demo)
        text_length = len(request.resume_text)
        word_count = len(request.resume_text.split())

        # Basic scoring based on content length and keywords
        keywords = ["python", "javascript", "react", "django", "experience", "skills", "education"]
        keyword_score = sum(1 for keyword in keywords if keyword.lower() in request.resume_text.lower())

        # Calculate score (0-100)
        base_score = min(text_length / 20, 30)  # Max 30 points for length
        keyword_points = keyword_score * 10  # 10 points per keyword
        score = min(base_score + keyword_points, 100)

        # Generate feedback
        feedback = f"Resume analyzed: {word_count} words, {keyword_score} relevant keywords found."

        # Store in simple cache
        cache_key = f"job_{request.job_id}_score"
        simple_cache[cache_key] = {"score": score, "feedback": feedback, "word_count": word_count}

        logger.info(f"Scored resume for job {request.job_id}: {score}/100")

        return ScoreResponse(score=score, feedback=feedback, status="completed")

    except Exception as e:
        logger.error(f"Error scoring resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")


@app.get("/cache-stats")
async def cache_stats():
    """Get cache statistics"""
    return {"cached_items": len(simple_cache), "cache_type": "in-memory", "redis_status": "disabled"}


if __name__ == "__main__":
    print("🚀 Starting AI Resume Scorer (No Redis Version)...")
    print("📊 Health endpoint: http://localhost:8001/health")
    print("🎯 API docs: http://localhost:8001/docs")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
