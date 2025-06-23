import logging
import os
import tempfile

import uvicorn
from ai.scorer import calculate_resume_score
from fastapi import FastAPI, File, Form, Request, UploadFile
from PyPDF2 import PdfReader

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Resume Scorer", version="1.0.0", description="AI-powered resume scoring microservice")


def extract_text_from_pdf(file_bytes):
    """Extract text from PDF bytes."""
    try:
        if not file_bytes:
            return ""

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file_bytes)
            tmp_file.flush()

            reader = PdfReader(tmp_file.name)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            os.unlink(tmp_file.name)
            return text.strip()

    except Exception as e:
        logger.error(f"PDF text extraction error: {e}")
        return ""


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AI Resume Scorer is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "redis": "not_connected", "service": "ai-resume-scorer"}


@app.post("/score/")
async def score_resume(file: UploadFile = File(...), job_description: str = Form(...), async_mode: bool = Form(False)):
    """Score a resume against a job description"""
    try:
        # Read file and extract text
        file_bytes = await file.read()
        logger.info(f"📄 Received file: {file.filename}, size: {len(file_bytes)} bytes")

        resume_text = extract_text_from_pdf(file_bytes)
        if not resume_text.strip():
            return {"error": "Could not extract text from PDF", "score": 0.0}

        logger.info(f"📝 Job description: {job_description[:100]}...")

        # Calculate score
        score = calculate_resume_score(resume_text, job_description)
        result_score = round(score * 100, 2)

        logger.info(f"🎯 Calculated score: {result_score}%")
        return {"score": result_score, "cached": False, "task_id": None, "redis": "not_connected"}

    except Exception as e:
        logger.error(f"❌ Scoring error: {e}")
        return {"error": str(e), "score": 0.0}


if __name__ == "__main__":
    logger.info("Starting AI Resume Scorer microservice...")
    uvicorn.run(app, host="127.0.0.1", port=8001)
