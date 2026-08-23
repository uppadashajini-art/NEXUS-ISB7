from fastapi import FastAPI
import os

app = FastAPI()

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