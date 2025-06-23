from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="AI Resume Scorer - Simple Version")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI Resume Scorer is running"}

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "service": "ai-resume-scorer",
        "redis_status": "disabled",
        "cors": "enabled"
    }

if __name__ == "__main__":
    print("Starting simple AI Resume Scorer...")
    uvicorn.run(app, host="127.0.0.1", port=8001)
