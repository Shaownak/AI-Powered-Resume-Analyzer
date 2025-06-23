import hashlib
import json
import logging
from io import BytesIO

from ai.scorer import calculate_resume_score
from cache.redis_cache import RedisCache
from fastapi import APIRouter, BackgroundTasks, File, Form, Request, UploadFile
from PyPDF2 import PdfReader
from slowapi import Limiter
from slowapi.util import get_remote_address
from tasks.queue import get_task_result, score_resume_async  # Temporarily disabled

# Setup logging
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


def extract_text_from_pdf(file_bytes):
    """Extract text from PDF bytes using BytesIO (no temp files)."""
    try:
        if not file_bytes:
            print("❌ No file bytes provided")
            return ""

        print(f"📄 Processing PDF with {len(file_bytes)} bytes")

        # Use BytesIO to avoid temporary file issues
        pdf_stream = BytesIO(file_bytes)

        try:
            reader = PdfReader(pdf_stream)
            print(f"📖 PDF has {len(reader.pages)} pages")

            text = ""
            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text() or ""
                    text += page_text
                    print(f"📄 Page {i+1}: extracted {len(page_text)} characters")
                except Exception as page_error:
                    print(f"⚠️ Error extracting page {i+1}: {page_error}")
                    continue

            print(f"✅ Total extracted: {len(text)} characters from PDF")
            return text

        except Exception as pdf_error:
            print(f"❌ PDF parsing error: {pdf_error}")
            return ""
        finally:
            try:
                pdf_stream.close()
            except:
                pass

    except Exception as e:
        print(f"❌ PDF extraction error: {e}")
        return ""


@router.post("/score/")
@limiter.limit("50/minute")  # Rate limit: 50 requests per minute per IP (increased for testing)
async def score_resume(
    request: Request, file: UploadFile = File(...), job_description: str = Form(...), async_mode: bool = Form(False)
):
    try:
        # Read file and extract text
        file_bytes = await file.read()
        logger.info(f"📄 Received file: {file.filename}, size: {len(file_bytes)} bytes")

        resume_text = extract_text_from_pdf(file_bytes)
        if not resume_text.strip():
            return {"error": "Could not extract text from PDF", "score": 0.0}

        logger.info(f"📝 Job description: {job_description[:100]}...")

        # Generate cache key based on resume text and job description
        cache_key = generate_cache_key(resume_text, job_description)

        # Try to get cached result
        cache = RedisCache()
        cached_result = cache.get_score(cache_key)

        if cached_result:
            logger.info("🎯 Returning cached score")
            return {"score": cached_result, "cached": True, "task_id": None}  # If async mode requested, queue the task
        if async_mode:
            try:
                task_id = score_resume_async(resume_text, job_description)
                logger.info(f"🚀 Started async task: {task_id}")
                return {"task_id": task_id, "status": "processing", "message": "Task queued successfully"}
            except Exception as e:
                logger.error(f"❌ Async task error: {e}")
                # Fall back to sync scoring
                score = calculate_resume_score(resume_text, job_description)
                result_score = round(score * 100, 2)
                cache.set_score(cache_key, result_score)
                return {"score": result_score, "cached": False, "task_id": None, "fallback": "async_failed"}

        # Synchronous scoring
        score = calculate_resume_score(resume_text, job_description)
        result_score = round(score * 100, 2)

        # Cache the result
        cache.set_score(cache_key, result_score)

        logger.info(f"🎯 Calculated score: {result_score}%")
        return {"score": result_score, "cached": False, "task_id": None}

    except Exception as e:
        logger.error(f"❌ Scoring error: {e}")
        return {"error": str(e), "score": 0.0}


@router.get("/task/{task_id}")
@limiter.limit("10/minute")
async def get_task_status(request: Request, task_id: str):
    """Get the status and result of an async scoring task."""
    try:
        result = get_task_result(task_id)
        logger.info(f"📊 Task {task_id} status: {result.get('status', 'unknown')}")
        return result
    except Exception as e:
        logger.error(f"❌ Task status error: {e}")
        return {"error": str(e), "status": "error"}


def generate_cache_key(resume_text: str, job_description: str) -> str:
    """Generate a unique cache key based on resume and job description content."""
    combined_text = f"{resume_text.strip()}{job_description.strip()}"
    return hashlib.md5(combined_text.encode()).hexdigest()
