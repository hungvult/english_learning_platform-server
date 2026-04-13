from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Import all models so SQLModel metadata is populated
import app.models  # noqa: F401
from app.api.v1.router import api_router

app = FastAPI(
    title="English Learning Platform API",
    version="1.0.0",
    description="Backend API for the English Learning Platform",
)

# CORS — allow Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static audio files
audio_dir = os.path.join(os.path.dirname(__file__), "static", "audio")
os.makedirs(audio_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "english-learning-platform"}
