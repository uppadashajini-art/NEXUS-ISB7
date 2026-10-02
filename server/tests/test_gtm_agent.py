"""
Tests for Member 3 Go-To-Market (GTM) Strategy Agent
"""

import pytest
from server.agents.gtm_agent import run_gtm_agent, GtmStrategyModel


@pytest.mark.asyncio
async def test_gtm_agent_with_full_context():
    validation_context = {
        "idea": "AI-powered platform for personalized fitness and nutrition plans",
        "market_analysis": {
            "industry": "HealthTech & Digital Fitness",
            "market_opportunity": "Growing global digital fitness market",
            "customer_segments": [
                {
                    "segment": "Busy Tech Professionals",
                    "needs": ["Automated workout tracking", "Time efficiency"],
                    "pain_points": ["Lack of time", "Inconsistent coaching quality"]
                },
                {
                    "segment": "Competitive Fitness Enthusiasts",
                    "needs": ["Detailed biomechanics", "Macros tracking"],
                    "pain_points": ["Generic spreadsheet tracking"]
                }
            ]
        },
        "competitor_analysis": {
            "direct_competitors": [
                {
                    "name": "FitBot AI",
                    "pricing": "$19.99/mo",
                    "strengths": ["Strong mobile app"],
                    "weaknesses": ["No meal planning"]
                }
            ],
            "indirect_competitors": [
                {
                    "name": "Gym Excel Spreadsheets",
                    "pricing": "Free",
                    "strengths": ["Customizable"],
                    "weaknesses": ["Manual entry"]
                }
            ],
            "market_gaps": [
                "Unified fitness and nutrition automation in a single subscription",
                "Frictionless onboarding with real-time biometric adjustments"
            ]
        }
    }

    result = await run_gtm_agent(validation_context=validation_context)
    assert "gtm_strategy" in result
    gtm = result["gtm_strategy"]

    # 1. Target Market
    assert "target_market" in gtm
    assert len(gtm["target_market"]) >= 2
    types = [tm["type"] for tm in gtm["target_market"]]
    assert "Primary" in types
    assert "Secondary" in types

    # 2. Product Positioning
    assert "positioning" in gtm
    pos = gtm["positioning"]
    assert "problem_solved" in pos and len(pos["problem_solved"]) > 10
    assert "target_user" in pos and len(pos["target_user"]) > 5
    assert "differentiation" in pos and len(pos["differentiation"]) > 10

    # 3. Marketing Channels
    assert "marketing_channels" in gtm
    assert len(gtm["marketing_channels"]) >= 3
    for ch in gtm["marketing_channels"]:
        assert "channel" in ch
        assert "category" in ch
        assert "tactics" in ch

    # 4. Customer Acquisition Strategy
    assert "customer_acquisition" in gtm
    assert len(gtm["customer_acquisition"]) >= 2

    # 5. Pricing Strategy
    assert "pricing_strategy" in gtm
    assert len(gtm["pricing_strategy"]) > 20

    # 6. Launch Strategy (4 Phases)
    assert "launch_strategy" in gtm
    assert len(gtm["launch_strategy"]) == 4
    phases = [lp["phase"] for lp in gtm["launch_strategy"]]
    assert any("Prototype" in p for p in phases)
    assert any("Beta" in p for p in phases)
    assert any("Public Launch" in p for p in phases)
    assert any("Growth" in p for p in phases)

    # Validates with Pydantic
    model = GtmStrategyModel(**gtm)
    assert model.positioning.problem_solved


@pytest.mark.asyncio
async def test_gtm_agent_with_minimal_context():
    # Only the idea is provided
    result = await run_gtm_agent(idea="Autonomous drone delivery network for remote healthcare clinics")
    assert "gtm_strategy" in result
    gtm = result["gtm_strategy"]

    assert len(gtm["target_market"]) >= 1
    assert "positioning" in gtm
    assert len(gtm["marketing_channels"]) >= 1
    assert len(gtm["customer_acquisition"]) >= 1
    assert len(gtm["pricing_strategy"]) > 10
    assert len(gtm["launch_strategy"]) == 4


@pytest.mark.asyncio
async def test_gtm_agent_with_optional_swot_and_risk():
    # Optional SWOT, Risk, MVP should be accepted gracefully
    result = await run_gtm_agent(
        idea="Eco-friendly packaging marketplace",
        swot_analysis={"strengths": ["High sustainability"], "weaknesses": ["Supply chain"]},
        risk_analysis={"supply_chain_risk": "High"},
        mvp_recommendations={"core_features": ["Catalog", "Checkout"]}
    )
    assert "gtm_strategy" in result
    assert result["gtm_strategy"]["positioning"]["problem_solved"]


@pytest.mark.asyncio
async def test_gtm_agent_offline_deterministic_guarantee(monkeypatch):
    # Ensure offline execution works even if GEMINI_API_KEY is not set
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    result = await run_gtm_agent(idea="Micro-SaaS bookkeeping for freelance photographers")
    assert "gtm_strategy" in result
    gtm = result["gtm_strategy"]
    assert gtm["target_market"][0]["type"] == "Primary"
    assert "launch_strategy" in gtm
    assert len(gtm["launch_strategy"]) == 4
