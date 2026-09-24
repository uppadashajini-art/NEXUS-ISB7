"""
NEXUS-ISB7 — SWOT & Risk Analysis Agent Test Suite
Role: Member 1 — SWOT + Risk + Orchestration

Covers:
- SWOT Analysis quadrant completeness (Strengths, Weaknesses, Opportunities, Threats)
- Multi-dimensional Risk Analysis schema and category validation
- Context grounding from Market Analysis and Competitor Analysis
- Graceful handling of missing or thin context
- Input validation (empty/whitespace idea rejection)
- Integration within the central Orchestrator pipeline
"""

import pytest
from unittest.mock import patch, AsyncMock
from server.agents.swot_risk_agent import run_swot_risk_agent
from server.agents.orchestrator import run_orchestrator
from server.models.validation import SWOTAnalysis, RiskItem, ValidationResponse


@pytest.mark.asyncio
async def test_swot_risk_agent_quadrant_completeness():
    """Verify that SWOT analysis contains all four quadrants with meaningful data."""
    idea = "AI automated liquid cooling and predictive thermal regulation for high-density GPU datacenters"
    market_context = {
        "industry": "Data Center Infrastructure",
        "market_opportunity": "Growing demand for AI compute infrastructure",
        "market_trends": ["Surge in high-density rack deployments", "Stringent energy efficiency mandates"],
        "market_challenges": ["High operational downtime risk", "Vendor hardware fragmentation"]
    }
    competitor_context = {
        "direct_competitors": [{"name": "CoolIT Systems"}, {"name": "Submer"}],
        "market_gaps": ["Telemetry fragmentation across liquid cooling vendors", "Lack of sub-second predictive thermal loops"]
    }

    result = await run_swot_risk_agent(
        idea=idea,
        market_analysis=market_context,
        competitor_analysis=competitor_context
    )

    assert isinstance(result, dict)
    assert "swot_analysis" in result
    assert "risk_analysis" in result

    swot = result["swot_analysis"]
    # Verify strict model validation
    swot_model = SWOTAnalysis(**swot)
    assert len(swot_model.strengths) >= 3
    assert len(swot_model.weaknesses) >= 3
    assert len(swot_model.opportunities) >= 3
    assert len(swot_model.threats) >= 3

    # Check context grounding
    assert any("liquid cooling" in o.lower() or "thermal" in o.lower() or "gap" in o.lower() or "datacenter" in o.lower() for o in swot_model.opportunities + swot_model.strengths)


@pytest.mark.asyncio
async def test_swot_risk_agent_risk_categories_and_severities():
    """Verify that Risk Analysis generates categorized risks with actionable mitigations."""
    idea = "Drone based hyperspectral aerial scanning for early vineyard fungal detection"
    result = await run_swot_risk_agent(idea=idea)

    risks = result["risk_analysis"]
    assert isinstance(risks, list)
    assert len(risks) >= 4

    categories_found = set()
    for item in risks:
        risk_model = RiskItem(**item)
        assert risk_model.risk.strip() != ""
        assert risk_model.severity in ["High", "Medium", "Low"]
        assert risk_model.impact.strip() != ""
        assert risk_model.mitigation.strip() != ""
        categories_found.add(risk_model.category)

    # Must cover major strategic categories
    assert any(c in categories_found for c in ["Technical", "Market", "Competition", "Financial", "Customer Adoption", "Operational"])


@pytest.mark.asyncio
async def test_swot_risk_agent_rejects_empty_idea():
    """Empty or whitespace idea should raise ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        await run_swot_risk_agent("   ")


@pytest.mark.asyncio
async def test_swot_risk_agent_handles_none_context():
    """Agent should operate safely when market and competitor context are None."""
    idea = "Decentralized micro-grid solar energy sharing platform for suburban neighborhoods"
    result = await run_swot_risk_agent(idea=idea, market_analysis=None, competitor_analysis=None, search_results=None)

    assert "swot_analysis" in result
    assert "risk_analysis" in result
    SWOTAnalysis(**result["swot_analysis"])
    for r in result["risk_analysis"]:
        RiskItem(**r)


@pytest.mark.asyncio
async def test_orchestrator_integrates_swot_and_risk():
    """Verify that run_orchestrator executes end-to-end and returns swot_analysis and risk_analysis."""
    idea = "Autonomous AI fleet dispatch and route optimization for municipal electric waste trucks"
    result = await run_orchestrator(idea=idea)

    assert isinstance(result, dict)
    assert "swot_analysis" in result
    assert "risk_analysis" in result
    assert result["swot_analysis"] is not None
    assert len(result["risk_analysis"]) > 0

    # Ensure final payload validates against the complete ValidationResponse model
    validated = ValidationResponse(**result)
    assert validated.swot_analysis is not None
    assert len(validated.swot_analysis.strengths) > 0
    assert len(validated.risk_analysis) > 0
