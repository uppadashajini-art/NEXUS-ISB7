"""
Integration tests for Member 3 Startup Advisor Route (/api/advisor)
Mounts advisor.router on an isolated test FastAPI instance.
Zero dependencies on main.py.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from server.routes.advisor import router as advisor_router

# Isolated test app mounting the router directly
app = FastAPI()
app.include_router(advisor_router)
client = TestClient(app)


def test_advisor_endpoint_success(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = client.post(
        "/api/advisor",
        json={
            "question": "What should my MVP contain?",
            "validation_context": {
                "idea": "AI customer support copilot for Shopify merchants",
                "market_analysis": {
                    "industry": "E-commerce & SaaS",
                    "customer_segments": [
                        {"segment": "Shopify Boutique Owners", "pain_points": ["Slow response times"]}
                    ]
                },
                "competitor_analysis": {
                    "direct_competitors": [{"name": "Gorgias", "pricing": "$60/mo"}],
                    "market_gaps": ["Instant zero-setup sync for catalog updates"]
                }
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 20
    assert "suggested_followups" in data
    assert isinstance(data["suggested_followups"], list)


def test_advisor_endpoint_without_context(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = client.post(
        "/api/advisor",
        json={
            "question": "Who are my main competitors?"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 10


def test_advisor_endpoint_empty_question_fails():
    response = client.post(
        "/api/advisor",
        json={
            "question": "   ",
            "validation_context": {}
        }
    )
    assert response.status_code == 422


def test_advisor_endpoint_too_short_question_fails():
    response = client.post(
        "/api/advisor",
        json={
            "question": "ab"
        }
    )
    assert response.status_code == 422


def test_advisor_endpoint_wrong_method_returns_405():
    response = client.get("/api/advisor")
    assert response.status_code == 405
