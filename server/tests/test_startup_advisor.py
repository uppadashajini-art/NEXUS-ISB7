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
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    result = await run_startup_advisor(
        question="What should my MVP contain?",
        validation_context=MOCK_VALIDATION_CONTEXT
    )
    assert "answer" in result
    ans = result["answer"]
    assert "MVP" in ans or "Scope" in ans
    # Verifies context grounding
    assert "Busy Corporate Professionals" in ans or "Seamless automated nutrition" in ans
    assert "suggested_followups" in result
    assert len(result["suggested_followups"]) > 0


@pytest.mark.asyncio
async def test_startup_advisor_competitors_question_offline(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
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
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    result = await run_startup_advisor(
        question="What are the biggest risks?",
        validation_context=MOCK_VALIDATION_CONTEXT
    )
    assert "answer" in result
    ans = result["answer"]
    assert "acquisition" in ans.lower() or "churn" in ans.lower() or "risk" in ans.lower()


@pytest.mark.asyncio
async def test_startup_advisor_differentiation_question_offline(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
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
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
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

