"""
Tests for POST /api/validate

Place this file at: tests/test_validation_api.py

Run with (from project root):
    pytest tests/test_validation_api.py -v

Covers the Milestone 2 testing checklist for Member 4:
- Valid startup idea
- Empty startup idea
- Very short startup idea
- Orchestrator not available (graceful 503, not a crash)
- Invalid request body (missing 'idea' field)
"""

import pytest
from fastapi.testclient import TestClient

from server.main import app

client = TestClient(app)


def test_empty_idea_returns_400():
    """Submitting an empty idea should be rejected before hitting the orchestrator."""
    response = client.post("/api/validate", json={"idea": ""})
    assert response.status_code in (400, 422)  # 422 if FastAPI's own validation catches it first


def test_very_short_idea_returns_400():
    """Submitting a startup idea that's too short should be rejected."""
    response = client.post("/api/validate", json={"idea": "AI app"})
    assert response.status_code in (400, 422)


def test_missing_idea_field_returns_422():
    """Submitting a request with no 'idea' key at all should fail request validation."""
    response = client.post("/api/validate", json={})
    assert response.status_code == 422


def test_valid_idea_when_orchestrator_unavailable_returns_503():
    """
    Until Member 1's orchestrator.py is implemented, a valid, well-formed
    idea should fail gracefully with a 503, not crash with a 500 or stack trace.

    NOTE: Once orchestrator.py exists, this test should be updated to expect
    a 200 with real market_analysis / competitor_analysis data instead.
    """
    response = client.post(
        "/api/validate",
        json={"idea": "AI based platform for personalized fitness plans"},
    )
    assert response.status_code in (200, 503)

    if response.status_code == 503:
        body = response.json()
        assert "detail" in body


def test_valid_idea_returns_expected_structure_when_available():
    """
    If the orchestrator IS available and returns 200, the response
    must match the expected structure from the milestone doc.
    """
    response = client.post(
        "/api/validate",
        json={"idea": "AI based platform for personalized fitness plans"},
    )

    if response.status_code != 200:
        pytest.skip("Orchestrator not available yet — skipping structure check")

    data = response.json()
    assert "idea" in data
    assert "market_analysis" in data
    assert "competitor_analysis" in data

    market = data["market_analysis"]
    assert "industry" in market
    assert "market_opportunity" in market
    assert "market_trends" in market
    assert "customer_segments" in market

    competitor = data["competitor_analysis"]
    assert "direct_competitors" in competitor
    assert "indirect_competitors" in competitor
    assert "market_gaps" in competitor


def test_wrong_http_method_not_allowed():
    """GET should not be allowed on /api/validate — it's a POST-only endpoint."""
    response = client.get("/api/validate")
    assert response.status_code == 405