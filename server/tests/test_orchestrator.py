"""
NEXUS-ISB7 — Multi-Agent Orchestrator Test Suite
Role: Member 1 — Agent Orchestration & System Integration

Covers:
- Pipeline execution & context passing
- Input validation (empty, short ideas)
- Resilience against web search failures
- Resilience against downstream agent failures
- Response structure conformance with ValidationResponse
"""

import pytest
from unittest.mock import patch, AsyncMock
from server.agents.orchestrator import run_orchestrator
from server.models.validation import ValidationResponse


@pytest.mark.asyncio
async def test_orchestrator_pipeline_success():
    """Verify that orchestrator executes end-to-end and returns a valid schema."""
    idea = "AI platform for personalized meal planning and nutrition tracking"
    result = await run_orchestrator(idea)

    assert isinstance(result, dict)
    assert result["idea"] == idea
    assert "market_analysis" in result
    assert "competitor_analysis" in result

    # Validate against strict Pydantic model
    validated = ValidationResponse(**result)
    assert validated.idea == idea
    assert validated.market_analysis.industry != ""
    assert len(validated.market_analysis.customer_segments) >= 1
    assert len(validated.competitor_analysis.direct_competitors) >= 1
    assert len(validated.competitor_analysis.market_gaps) >= 1


@pytest.mark.asyncio
async def test_orchestrator_rejects_empty_idea():
    """Empty idea should raise ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        await run_orchestrator("   ")


@pytest.mark.asyncio
async def test_orchestrator_rejects_short_idea():
    """Idea shorter than 10 characters should raise ValueError."""
    with pytest.raises(ValueError, match="too short"):
        await run_orchestrator("AI app")


@pytest.mark.asyncio
async def test_orchestrator_resilience_on_search_failure():
    """If the Web Search Agent raises an exception, the orchestrator should degrade gracefully."""
    with patch("server.agents.orchestrator.run_web_search_agent", new_callable=AsyncMock) as mock_search:
        mock_search.side_effect = ConnectionError("Tavily API unreachable")

        idea = "Blockchain based decentralized identity verification for freelancers"
        result = await run_orchestrator(idea)

        assert isinstance(result, dict)
        assert result["idea"] == idea
        assert "market_analysis" in result
        assert "competitor_analysis" in result
        # ValidationResponse should still parse without errors
        validated = ValidationResponse(**result)
        assert validated.market_analysis.industry != ""


@pytest.mark.asyncio
async def test_orchestrator_context_passing():
    """Verify that web search results are forwarded into the analysis agents."""
    mock_search_data = {
        "results": [
            {
                "title": "FitTech Pro Competitor",
                "url": "https://fittechpro.example.com",
                "target_audience": "Fitness enthusiasts",
                "content": "Leading AI personalized fitness app for workouts."
            }
        ]
    }

    with patch("server.agents.orchestrator.run_web_search_agent", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_search_data

        idea = "AI driven fitness coaching for busy tech professionals"
        result = await run_orchestrator(idea)

        # The competitor analysis should extract FitTech Pro from the search results
        competitors = result["competitor_analysis"]["direct_competitors"]
        assert any("fittech" in c["name"].lower() or "example" in (c["url"] or "").lower() for c in competitors)
