"""
NEXUS-ISB7 — Market Analysis & Customer Segmentation Agent Test Suite
Role: Member 2 — Market Opportunity & Customer Segmentation

Covers:
- Pydantic schema validation (MarketAnalysis, CustomerSegment)
- Evidence grounding with web research context
- Thin-evidence honesty caveat (<3 search results)
- Seed persona reuse from Milestone 1 target audience discovery
- Multi-industry taxonomy classification
- Gemini LLM mocking & JSON sanitization
- Graceful deterministic fallback on network or API failures
- Integration with Member 1 Multi-Agent Orchestrator
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from server.agents.market_analysis_agent import (
    THIN_EVIDENCE_NOTE,
    THIN_EVIDENCE_THRESHOLD,
    _detect_industry,
    _extract_seed_audiences,
    run_market_analysis_agent,
)
from server.models.validation import CustomerSegment, MarketAnalysis, ValidationResponse


@pytest.mark.asyncio
async def test_market_analysis_contract_conformance():
    """Verify that market analysis produces output conforming to MarketAnalysis model."""
    idea = "AI powered fitness coaching platform with automated posture feedback"
    search_results = [
        {
            "title": "Connected Fitness Market Report 2026",
            "url": "https://example.com/fitness-report",
            "target_audience": "Fitness Enthusiasts & Gymgoers",
            "content": "Rising demand for real-time form correction and personalized AI workouts."
        },
        {
            "title": "Digital Health and Wellness Platform Trends",
            "url": "https://example.com/digital-health",
            "target_audience": "Personal Trainers",
            "content": "Trainers adopt mobile-first tools to retain clients remotely."
        },
        {
            "title": "Wearable AI Fitness Sensors",
            "url": "https://example.com/wearables",
            "target_audience": "Athletes",
            "content": "Computer vision posture guidance reduces workout injury rates."
        }
    ]

    result = await run_market_analysis_agent(idea=idea, search_results=search_results)

    assert isinstance(result, dict)
    assert "industry" in result
    assert "market_opportunity" in result
    assert "market_trends" in result
    assert "customer_segments" in result
    assert "growth_drivers" in result
    assert "market_challenges" in result

    # Validate with strict Pydantic model
    validated = MarketAnalysis(**result)
    assert "Health" in validated.industry or "Fitness" in validated.industry
    assert len(validated.market_trends) >= 1
    assert len(validated.customer_segments) >= 1
    assert len(validated.growth_drivers) >= 1
    assert len(validated.market_challenges) >= 1

    # Verify nested customer segment structure
    first_segment = validated.customer_segments[0]
    assert isinstance(first_segment, CustomerSegment)
    assert len(first_segment.segment) > 0
    assert len(first_segment.needs) >= 1
    assert len(first_segment.pain_points) >= 1


@pytest.mark.asyncio
async def test_market_analysis_seed_persona_propagation():
    """Verify target_audience seeds from Milestone 1 are extracted and seeded into personas."""
    search_results = [
        {
            "title": "Hospital Logistics Solutions",
            "url": "https://example.com/hospital",
            "target_audience": "Hospital Procurement Officers",
            "content": "Medical inventory delays cost hospitals millions."
        },
        {
            "title": "Surgical Supply Distribution",
            "url": "https://example.com/surgical",
            "target_audience": "Chief Medical Officers",
            "content": "Just-in-time sterilization tracking software."
        }
    ]

    seeds = _extract_seed_audiences(search_results)
    assert "Hospital Procurement Officers" in seeds
    assert "Chief Medical Officers" in seeds

    result = await run_market_analysis_agent(
        idea="SaaS inventory management for hospital sterile supply chains",
        search_results=search_results
    )
    segments = result["customer_segments"]
    assert any("Hospital Procurement" in s["segment"] or "Chief Medical" in s["segment"] or "Procurement" in s["segment"] for s in segments)


@pytest.mark.asyncio
async def test_market_analysis_thin_evidence_caveat():
    """Verify that fewer than 3 search results triggers the explicit thin-evidence caveat."""
    idea = "Quantum encryption key manager for local credit unions"
    # Only 1 search result (< THIN_EVIDENCE_THRESHOLD)
    search_results = [
        {
            "title": "Credit Union Cybersecurity",
            "url": "https://example.com/cu-sec",
            "target_audience": "IT Directors",
            "content": "Financial institutions face post-quantum crypto challenges."
        }
    ]

    result = await run_market_analysis_agent(idea=idea, search_results=search_results)

    assert THIN_EVIDENCE_NOTE in result["market_opportunity"]


@pytest.mark.asyncio
async def test_market_analysis_empty_search_results():
    """Verify robust execution when search results list is completely empty."""
    idea = "Marketplace for upcycled vintage denim jackets and clothing repair"

    result = await run_market_analysis_agent(idea=idea, search_results=[])

    assert isinstance(result, dict)
    validated = MarketAnalysis(**result)
    assert validated.industry != ""
    assert THIN_EVIDENCE_NOTE in validated.market_opportunity
    assert len(validated.customer_segments) >= 1


@pytest.mark.asyncio
async def test_market_analysis_domain_override():
    """Verify user-supplied domain overrides automatic classification."""
    idea = "Platform for booking local fitness coaches and personal chefs"

    result = await run_market_analysis_agent(
        idea=idea,
        search_results=[],
        domain="Hospitality & Lifestyle Services"
    )

    assert result["industry"] == "Hospitality & Lifestyle Services"


def test_detect_industry_taxonomy():
    """Verify taxonomy matching across diverse startup domains."""
    assert _detect_industry("solar panel recycling and carbon credits") == "CleanTech & Sustainability"
    assert _detect_industry("micro-lending and credit score underwriting") == "FinTech & Financial Services"
    assert _detect_industry("last-mile courier dispatch and delivery route pooling") == "Logistics & Supply Chain"
    assert _detect_industry("crm and team workflow project management platform") == "Enterprise SaaS & Productivity"
    assert _detect_industry("automated code review bot for developers") == "Artificial Intelligence & Automation"
    assert _detect_industry("interactive college lecture summaries and flashcard generator") == "EdTech & Learning Technology"



@pytest.mark.asyncio
async def test_market_analysis_gemini_mocked_success():
    """Verify parsing and validation when Gemini responds successfully."""
    mock_gemini_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": (
                                '{\n'
                                '  "industry": "EdTech & Learning Technology",\n'
                                '  "market_opportunity": "High commercial runway in higher-ed AI learning tools with rapid student adoption.",\n'
                                '  "market_trends": [\n'
                                '    "Generative AI adoption in university lecture study workflows",\n'
                                '    "Demand for verifiable flashcard recall systems"\n'
                                '  ],\n'
                                '  "customer_segments": [\n'
                                '    {\n'
                                '      "segment": "Undergraduate STEM Students",\n'
                                '      "needs": ["Instant lecture summarization", "Practice quiz generation"],\n'
                                '      "pain_points": ["Information overload in 90-minute lectures", "High textbook costs"]\n'
                                '    }\n'
                                '  ],\n'
                                '  "growth_drivers": ["Proactive AI learning tools", "Expanding digital campus adoption"],\n'
                                '  "market_challenges": ["Institutional compliance scrutiny", "Student retention past exam cycles"]\n'
                                '}'
                            )
                        }
                    ]
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_gemini_response

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        with patch.dict("os.environ", {"GEMINI_API_KEY": "fake-test-key"}):
            result = await run_market_analysis_agent(
                idea="AI lecture summarizer and quiz generator",
                search_results=[
                    {"title": "EdTech 1", "url": "https://ed1.com", "target_audience": "Students", "content": "Evidence 1"},
                    {"title": "EdTech 2", "url": "https://ed2.com", "target_audience": "Professors", "content": "Evidence 2"},
                    {"title": "EdTech 3", "url": "https://ed3.com", "target_audience": "Tutors", "content": "Evidence 3"}
                ]
            )

    assert result["industry"] == "EdTech & Learning Technology"
    assert "Undergraduate STEM Students" in result["customer_segments"][0]["segment"]
    validated = MarketAnalysis(**result)
    assert len(validated.market_trends) == 2


@pytest.mark.asyncio
async def test_market_analysis_gemini_fallback_on_error():
    """Verify that network or API failures fall back cleanly to the heuristic engine without raising."""
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = ConnectionError("Google API unreachable")
        with patch.dict("os.environ", {"GEMINI_API_KEY": "fake-test-key"}):
            result = await run_market_analysis_agent(
                idea="FinTech platform for automated freelance tax deductions",
                search_results=[
                    {"title": "Tax SaaS", "url": "https://tax.example.com", "target_audience": "Freelancers", "content": "Tax filing tools."}
                ]
            )

    assert isinstance(result, dict)
    assert "industry" in result
    assert "FinTech" in result["industry"]
    validated = MarketAnalysis(**result)
    assert len(validated.customer_segments) >= 1


@pytest.mark.asyncio
async def test_orchestrator_integration_with_member2_agent():
    """Verify that orchestrator invokes Member 2's run_market_analysis_agent directly."""
    from server.agents.orchestrator import run_orchestrator

    mock_search_data = {
        "results": [
            {
                "title": "GreenRoute Logistics Network",
                "url": "https://greenroute.example.com",
                "target_audience": "E-Commerce Logistics Managers",
                "content": "Shared delivery pooling reduces urban freight emissions by 30%."
            },
            {
                "title": "Urban Delivery Route Optimization",
                "url": "https://urbanrouting.example.com",
                "target_audience": "Warehouse Dispatchers",
                "content": "Last-mile courier contracts causing margin loss."
            },
            {
                "title": "Courier Multi-Carrier Platforms",
                "url": "https://multicarrier.example.com",
                "target_audience": "Supply Chain Directors",
                "content": "Consolidated shipping platforms streamline operations."
            }
        ]
    }

    with patch("server.agents.orchestrator.run_web_search_agent", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_search_data

        idea = "AI freight pooling and route consolidation platform for e-commerce brands"
        result = await run_orchestrator(idea)

        assert isinstance(result, dict)
        assert "market_analysis" in result
        market = result["market_analysis"]
        assert "Logistics" in market["industry"] or "Supply Chain" in market["industry"]
        assert len(market["customer_segments"]) >= 1

        # Full end-to-end response conforms to ValidationResponse
        validated = ValidationResponse(**result)
        assert validated.idea == idea
        assert validated.market_analysis.industry != ""
