from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from server.routes import search

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)

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