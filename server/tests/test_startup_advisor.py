"""
Tests for Member 3 Conversational Startup Advisor Agent
"""

import pytest
from server.agents.startup_advisor_agent import run_startup_advisor, _match_intent


MOCK_VALIDATION_CONTEXT = {
    "idea": "AI-powered personalized nutrition and fitness platform",
    "market_analysis": {
        "industry": "HealthTech",
        "market_opportunity": "Global digital wellness expansion",
        "customer_segments": [
            {
                "segment": "Busy Corporate Professionals",
                "needs": ["Automated meal plans", "Quick 20-min home workouts"],
                "pain_points": ["Severe lack of time", "Inconsistent coaching"]
            }
        ],
        "market_challenges": [
            "High customer acquisition costs on Meta and Google",
            "User churn after 30 days"
        ]
    },
    "competitor_analysis": {
        "direct_competitors": [
            {
                "name": "FitMaster AI",
                "pricing": "$29/mo",
                "strengths": ["Massive workout library"],
                "weaknesses": ["No personalized nutrition support"]
            }
        ],
        "market_gaps": [
            "Seamless automated nutrition coaching with biometric integration"
        ]
    },
    "gtm_strategy": {
        "pricing_strategy": "Freemium with $19/mo Pro Tier and $99/yr Annual Pass"
    }
}


def test_intent_matcher():
    assert _match_intent("What should my MVP contain?") == "mvp"
    assert _match_intent("Who are my main competitors?") == "competitors"
    assert _match_intent("What are the biggest risks?") == "risks"
    assert _match_intent("Who should I target first?") == "target_customer"
    assert _match_intent("How can I launch my product?") == "launch"
    assert _match_intent("How is my idea different from existing products?") == "differentiation"
    assert _match_intent("What should my pricing be?") == "pricing"


@pytest.mark.asyncio
async def test_startup_advisor_mvp_question_offline(monkeypatch):
    monkeypatch.setattr("server.utils.gemini_client.get_gemini_api_key", lambda: "")
    monkeypatch.setattr("server.utils.gemini_client.get_groq_api_key", lambda: "")
    result = await run_startup_advisor(
        question="What should my MVP contain?",
        validation_context=MOCK_VALIDATION_CONTEXT
    )
    assert "answer" in result
    ans = result["answer"]
    assert "MVP" in ans or "Scope" in ans
    # Verifies context grounding
    assert "busy corporate professionals" in ans.lower() or "seamless automated nutrition" in ans.lower()
    assert "suggested_followups" in result
    assert len(result["suggested_followups"]) > 0


@pytest.mark.asyncio
async def test_startup_advisor_competitors_question_offline(monkeypatch):
    monkeypatch.setattr("server.utils.gemini_client.get_gemini_api_key", lambda: "")
    monkeypatch.setattr("server.utils.gemini_client.get_groq_api_key", lambda: "")
    result = await run_startup_advisor(
        question="Who are my main competitors?",
        validation_context=MOCK_VALIDATION_CONTEXT
    )
    assert "answer" in result
    ans = result["answer"]
    # Verifies competitor name from context is mentioned
    assert "FitMaster AI" in ans


@pytest.mark.asyncio
async def test_startup_advisor_risks_question_offline(monkeypatch):
    monkeypatch.setattr("server.utils.gemini_client.get_gemini_api_key", lambda: "")
    monkeypatch.setattr("server.utils.gemini_client.get_groq_api_key", lambda: "")
    result = await run_startup_advisor(
        question="What are the biggest risks?",
        validation_context=MOCK_VALIDATION_CONTEXT
    )
    assert "answer" in result
    ans = result["answer"]
    assert "acquisition" in ans.lower() or "churn" in ans.lower() or "risk" in ans.lower()


@pytest.mark.asyncio
async def test_startup_advisor_differentiation_question_offline(monkeypatch):
    monkeypatch.setattr("server.utils.gemini_client.get_gemini_api_key", lambda: "")
    monkeypatch.setattr("server.utils.gemini_client.get_groq_api_key", lambda: "")
    result = await run_startup_advisor(
        question="How is my idea different from existing products?",
        validation_context=MOCK_VALIDATION_CONTEXT
    )
    assert "answer" in result
    ans = result["answer"]
    assert "advantage" in ans.lower() or "gap" in ans.lower() or "fitmaster" in ans.lower()


@pytest.mark.asyncio
async def test_startup_advisor_empty_context(monkeypatch):
    # Should not crash if validation_context is None or empty
    monkeypatch.setattr("server.utils.gemini_client.get_gemini_api_key", lambda: "")
    monkeypatch.setattr("server.utils.gemini_client.get_groq_api_key", lambda: "")
    result = await run_startup_advisor(
        question="Who should I target first?",
        validation_context=None
    )
    assert "answer" in result
    assert len(result["answer"]) > 20


@pytest.mark.asyncio
async def test_universal_model_waterfall_ordering():
    from server.utils.gemini_client import get_all_viable_models, MASTER_MODELS_WATERFALL
    models = await get_all_viable_models()
    assert len(models) >= 20
    # Tier 1 models must be ranked first
    assert models[0].startswith("gemini-3") or models[0].startswith("gemini-2")
    # Non-text modalities must be excluded
    for m in models:
        for forbidden in ("tts", "transcribe", "lyria", "clip"):
            assert forbidden not in m.lower(), f"Forbidden modality in models: {m}"


def test_extract_advisor_signals_and_prompt_builder():
    from server.agents.startup_advisor_agent import extract_advisor_signals, _build_advisor_prompt
    rich_context = {
        "idea": "Autonomous AI Inventory Drone for Warehouses",
        "domain": "Logistics & Supply Chain",
        "target_customer": "Enterprise Warehouse Directors",
        "market_analysis": {
            "industry": "Logistics & Automation",
            "market_opportunity": "Global warehouse automation boom reaching $41B",
            "market_trends": ["Autonomous flight regulations loosening", "Labor shortages in 3PL"],
            "growth_drivers": ["Demand for same-day delivery"],
            "market_challenges": ["High capital expenditure hurdles"],
            "customer_segments": [
                {
                    "segment": "Tier-1 3PL Operators",
                    "needs": ["Real-time inventory reconciliation"],
                    "pain_points": ["Manual stocktaking takes 3 days and shuts down operations"]
                }
            ]
        },
        "competitor_analysis": {
            "direct_competitors": [
                {
                    "name": "FlyScan Systems",
                    "pricing": "$5,000/mo per facility",
                    "strengths": ["Proprietary indoor lidar"],
                    "weaknesses": ["Slow battery recharge and manual swap required"]
                }
            ],
            "market_gaps": ["Autonomous wireless inductive recharging pads without human intervention"],
            "competitive_advantage": "Continuous 24/7 scanning with self-docking wireless recharging"
        },
        "swot_analysis": {
            "strengths": ["Patent-pending computer vision barcode scanning at 20km/h"],
            "weaknesses": ["Hardware supply chain lead times"],
            "opportunities": ["Expansion into cold-storage facilities"],
            "threats": ["Incumbent robotics vendors adding drone attachments"]
        },
        "risk_analysis": [
            {
                "risk": "Collision with warehouse racking or personnel",
                "category": "Operational",
                "severity": "High",
                "impact": "Facility shutdown and legal liability",
                "mitigation": "Quad-redundant optical flow sensors and geo-fenced safety kill switches"
            }
        ],
        "mvp_recommendations": {
            "must_have": [
                {
                    "feature": "Automated Aisle Flight Path Navigation",
                    "customer_value": "High",
                    "complexity": "High",
                    "reason": "Core functionality needed to navigate 40ft aisles safely"
                }
            ],
            "should_have": [
                {"feature": "Integration with SAP EWM"}
            ],
            "future_features": [
                {"feature": "Automated physical box manipulation robotic arm"}
            ]
        },
        "gtm_strategy": {
            "pricing_strategy": "Robotics-as-a-Service (RaaS) at $3,500/month per facility",
            "marketing_channels": [
                {"channel": "ProMat Trade Show", "category": "Direct Event", "tactics": "Live flight demo booth"}
            ],
            "customer_acquisition": ["Free 7-day single-aisle proof-of-concept audit"],
            "launch_strategy": [
                {"phase": "Pilot", "objective": "3 paid pilot facilities in Midwest"}
            ]
        },
        "technical_feasibility": {
            "score": 8.5,
            "feasibility_rating": "Feasible",
            "recommended_tech_stack": ["ROS 2", "C++", "Python", "FastAPI", "WebSockets"],
            "key_barriers": ["Indoor GPS denial requiring optical SLAM"]
        },
        "scientific_validation": {
            "scientific_credibility_score": 9.0
        },
        "regulatory_risk": {
            "risk_level": "Low",
            "fda_classification": "FAA Part 107 Indoor Exemption"
        },
        "search_results": [
            {
                "title": "Warehouse Robotics Market Surges Past 2026 Forecasts",
                "url": "https://logisticsreport.example.com",
                "snippet": "Supply chain operators are accelerating autonomous indoor drone adoption."
            }
        ]
    }

    signals = extract_advisor_signals(rich_context)
    assert signals["idea"] == "Autonomous AI Inventory Drone for Warehouses"
    assert signals["industry"] == "Logistics & Automation"
    assert "FlyScan Systems" in signals["competitor_names"]
    assert len(signals["swot"]["strengths"]) > 0
    assert len(signals["risk_items"]) > 0

    prompt = _build_advisor_prompt(
        question="How should I price this against FlyScan and what is the biggest technical obstacle?",
        signals=signals
    )

    # Verifies all generated reports and founder idea are deeply embedded in LLM prompt
    assert "Autonomous AI Inventory Drone for Warehouses" in prompt
    assert "FlyScan Systems" in prompt
    assert "$5,000/mo" in prompt
    assert "Indoor GPS denial requiring optical SLAM" in prompt
    assert "Collision with warehouse racking" in prompt
    assert "Robotics-as-a-Service (RaaS)" in prompt
    assert "Quad-redundant optical flow sensors" in prompt
    assert "Warehouse Robotics Market Surges" in prompt


