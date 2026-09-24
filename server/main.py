from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.routes.validation import router as validation_router
import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure server/.env is loaded
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

from server.routes import search

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(validation_router)
app.include_router(search.router)

try:
    from server.routes.advisor import router as advisor_router
    app.include_router(advisor_router)
except ImportError:
    pass


@app.get("/")
def root():
    return {
        "project": "AI Based Startup Idea Validator",
        "environment": os.getenv("NODE_ENV", "staging"),
        "status": "Backend is running"
    }

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "environment": os.getenv("NODE_ENV", "staging")
    }