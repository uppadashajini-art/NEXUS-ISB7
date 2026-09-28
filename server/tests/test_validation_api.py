"""
Tests for POST /api/validate

Place this file at: server/tests/test_validation_api.py
(This REPLACES your existing Milestone 2 version -- it includes everything
from before, plus new coverage for the M3/M4 fields and the Report
Generation Agent.)

Run with (from project root):
    python -m pytest server/tests/test_validation_api.py -v
"""

import pytest
from fastapi.testclient import TestClient

from server.main import app
from server.agents.report_generation_agent import generate_validation_report

client = TestClient(app)


# ---------------------------------------------------------------------------
# Milestone 2 tests -- basic request validation and graceful failure
# ---------------------------------------------------------------------------

def test_empty_idea_returns_400():
    """Submitting an empty idea should be rejected before hitting the orchestrator."""
    response = client.post("/api/validate", json={"idea": ""})
    assert response.status_code in (400, 422)


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
    If the orchestrator isn't available, a valid, well-formed idea should
    fail gracefully with a 503, not crash with a 500 or stack trace.
    """
    response = client.post(
        "/api/validate",
        json={"idea": "AI based platform for personalized fitness plans"},
    )
    assert response.status_code in (200, 503)

    if response.status_code == 503:
        body = response.json()
        assert "detail" in body


def test_wrong_http_method_not_allowed():
    """GET should not be allowed on /api/validate -- it's a POST-only endpoint."""
    response = client.get("/api/validate")
    assert response.status_code == 405


# ---------------------------------------------------------------------------
# Milestone 3/4 tests -- full response structure with all agents
# ---------------------------------------------------------------------------

def test_valid_idea_returns_expected_structure_when_available():
    """
    When the full pipeline is available, the response must include the
    original M2 fields plus all M3/M4 fields, even if some are null.
    """
    response = client.post(
        "/api/validate",
        json={"idea": "AI based platform for personalized fitness plans"},
    )

    if response.status_code != 200:
        pytest.skip("Orchestrator/agents not fully available -- skipping structure check")

    data = response.json()

    # Milestone 2 fields
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

    # Milestone 3/4 fields -- must be present, even if null/empty
    for field in [
        "swot_analysis",
        "risk_analysis",
        "mvp_recommendations",
        "gtm_strategy",
        "validation_report",
    ]:
        assert field in data, f"Missing expected field: {field}"


def test_validation_report_has_expected_sections_when_present():
    """If validation_report is present, it must contain all required summary fields."""
    response = client.post(
        "/api/validate",
        json={"idea": "AI based platform for personalized fitness plans"},
    )

    if response.status_code != 200:
        pytest.skip("Orchestrator/agents not fully available -- skipping structure check")

    data = response.json()
    report = data.get("validation_report")

    if report is None:
        pytest.skip("validation_report was null for this run -- nothing to check")

    for field in [
        "executive_summary",
        "market_summary",
        "competitor_summary",
        "swot_summary",
        "risk_summary",
        "mvp_summary",
        "gtm_summary",
        "recommendations",
        "conclusion",
    ]:
        assert field in report, f"validation_report missing field: {field}"
        assert isinstance(report[field], str)
        assert len(report[field]) > 0, f"validation_report.{field} is empty"


# ---------------------------------------------------------------------------
# Unit tests -- Report Generation Agent, in isolation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_report_agent_with_full_data():
    """The report agent should produce a complete report when given full input."""
    result = await generate_validation_report(
        idea="AI based platform for personalized fitness plans",
        market_analysis={
            "industry": "Fitness Technology",
            "market_opportunity": "Growing demand for personalized fitness.",
            "market_trends": ["AI-powered coaching", "Wearables"],
        },
        competitor_analysis={
            "direct_competitors": [{"name": "FitAI"}],
            "market_gaps": ["Limited personalization"],
        },
        swot_analysis={
            "strengths": ["AI-driven personalization"],
            "threats": ["Low switching costs for users"],
        },
        risk_analysis=[
            {"risk": "Data privacy concerns", "severity": "High"}
        ],
        mvp_recommendations={
            "must_have": [{"feature": "Personalized workout plan generator"}]
        },
        gtm_strategy={
            "positioning": "Affordable AI fitness coaching for students.",
            "marketing_channels": ["Instagram", "Campus partnerships"],
        },
    )

    report = result["validation_report"]
    assert "Fitness Technology" in report["market_summary"]
    assert "high-severity risk" in report["risk_summary"].lower()
    assert len(report["recommendations"]) > 0


@pytest.mark.asyncio
async def test_report_agent_with_missing_data_degrades_gracefully():
    """
    The report agent must never crash, even if every optional input is
    missing -- it should return fallback text for each section instead.
    """
    result = await generate_validation_report(idea="A minimal test idea for validation")

    report = result["validation_report"]
    assert "not available" in report["market_summary"].lower()
    assert "not available" in report["competitor_summary"].lower()
    assert "not available" in report["swot_summary"].lower()
    assert "not available" in report["risk_summary"].lower()
    assert "not available" in report["mvp_summary"].lower()
    assert "not available" in report["gtm_summary"].lower()
    assert len(report["recommendations"]) > 0
    assert len(report["conclusion"]) > 0


@pytest.mark.asyncio
async def test_report_agent_never_raises_on_malformed_input():
    """Passing unexpected/malformed types should not crash the agent."""
    try:
        result = await generate_validation_report(
            idea="Edge case test idea for the report agent",
            market_analysis={},
            competitor_analysis={"direct_competitors": []},
            risk_analysis=[],
        )
        assert "validation_report" in result
    except Exception as e:
        pytest.fail(f"Report agent raised an exception on malformed input: {e}")