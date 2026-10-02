"""
NEXUS-ISB7 — MVP Recommendation Agent Test Suite

Role: Member 2 — MVP Feature Recommendation

Covers:
- MVP category completeness
- Feature schema validation
- Customer needs and pain points
- Customer segment usage
- Competitor feature usage
- Market gap usage
- SWOT usage
- Risk usage
- Feature prioritization
- Priority consistency
- Duplicate prevention
- Context-specific recommendations
- Graceful handling of missing context
- Input validation
- Different startup ideas
- Structured JSON output
"""

import pytest

from server.agents.mvp_recommendation_agent import (
    run_mvp_recommendation_agent
)

from server.models.validation import (
    MVPFeature,
    MVPRecommendations,
)


# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------

def get_all_features(mvp: MVPRecommendations):
    """Return all MVP features from all four categories."""
    return (
        mvp.must_have
        + mvp.should_have
        + mvp.could_have
        + mvp.future_features
    )


def get_feature_text(mvp: MVPRecommendations):
    """Return all feature names, reasons and priorities as lowercase text."""
    features = get_all_features(mvp)

    return " ".join(
        (
            f"{feature.feature} "
            f"{feature.reason} "
            f"{feature.priority}"
        ).lower()
        for feature in features
    )


def get_feature_names(mvp: MVPRecommendations):
    """Return normalized feature names."""
    return [
        feature.feature.strip().lower()
        for feature in get_all_features(mvp)
    ]


# -------------------------------------------------------------------
# 1. Basic category completeness
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_recommendation_category_completeness():
    """
    Verify that the MVP agent returns all four feature categories.
    """

    idea = (
        "AI platform for personalized meal planning "
        "and nutrition tracking"
    )

    market_context = {
        "industry": "Health and Fitness",

        "customer_segments": [
            "Busy professionals",
            "Health-conscious users"
        ],

        "customer_needs": [
            "Personalized meal plans",
            "Easy nutrition tracking"
        ],

        "pain_points": [
            "Difficulty planning healthy meals",
            "Lack of personalized nutrition guidance"
        ]
    }

    competitor_context = {
        "direct_competitors": [
            {
                "name": "MyFitnessPal",
                "key_features": [
                    "Calorie tracking",
                    "Food database"
                ]
            }
        ],

        "market_gaps": [
            "Limited personalized meal planning"
        ]
    }

    result = await run_mvp_recommendation_agent(
        idea=idea,
        market_analysis=market_context,
        competitor_analysis=competitor_context,
    )

    assert isinstance(result, dict)
    assert "mvp_recommendations" in result

    mvp = MVPRecommendations(
        **result["mvp_recommendations"]
    )

    assert mvp.must_have
    assert mvp.should_have
    assert mvp.could_have
    assert mvp.future_features


# -------------------------------------------------------------------
# 2. Feature schema validation
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_feature_schema():
    """
    Verify that every recommended feature follows the expected schema.
    """

    idea = (
        "AI fitness coaching platform for busy "
        "working professionals"
    )

    result = await run_mvp_recommendation_agent(
        idea=idea
    )

    mvp = MVPRecommendations(
        **result["mvp_recommendations"]
    )

    all_features = get_all_features(mvp)

    assert len(all_features) > 0

    for feature in all_features:

        assert isinstance(feature, MVPFeature)

        assert feature.feature.strip() != ""
        assert feature.priority.strip() != ""
        assert feature.reason.strip() != ""
        assert feature.customer_value.strip() != ""
        assert feature.complexity.strip() != ""


# -------------------------------------------------------------------
# 3. Market context usage
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_recommendation_uses_market_context():
    """
    Verify that customer needs and pain points can
    influence recommendations.
    """

    idea = "AI learning platform for college students"

    market_context = {
        "industry": "Education Technology",

        "customer_segments": [
            "College students"
        ],

        "customer_needs": [
            "Personalized learning"
        ],

        "pain_points": [
            "Difficulty creating personalized study plans"
        ]
    }

    result = await run_mvp_recommendation_agent(
        idea=idea,
        market_analysis=market_context
    )

    assert "mvp_recommendations" in result

    mvp = MVPRecommendations(
        **result["mvp_recommendations"]
    )

    assert len(mvp.must_have) > 0

    text = get_feature_text(mvp)

    # The exact wording can differ, but the recommendation
    # should show awareness of the supplied customer problem.
    assert (
        "personalized" in text
        or "study" in text
        or "learning" in text
        or "pain" in text
    )


# -------------------------------------------------------------------
# 4. Customer pain-point usage
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_recommendation_uses_customer_pain_points():
    """
    A strong MVP should directly address customer pain points.
    """

    idea = "Online platform for small business accounting"

    market_context = {
        "customer_segments": [
            "Small business owners"
        ],

        "customer_needs": [
            "Simple accounting"
        ],

        "pain_points": [
            "Complex accounting software",
            "Difficulty tracking expenses"
        ]
    }

    result = await run_mvp_recommendation_agent(
        idea=idea,
        market_analysis=market_context
    )

    mvp = MVPRecommendations(
        **result["mvp_recommendations"]
    )

    text = get_feature_text(mvp)

    assert (
        "account" in text
        or "expense" in text
        or "simple" in text
        or "pain" in text
    )


# -------------------------------------------------------------------
# 5. Customer segment usage
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_recommendation_uses_customer_segments():
    """
    Verify that customer segment information is considered.
    """

    idea = "AI career guidance platform"

    market_context = {
        "customer_segments": [
            "Final-year college students",
            "Recent graduates"
        ],

        "customer_needs": [
            "Career recommendations",
            "Job preparation"
        ],

        "pain_points": [
            "Uncertainty about suitable careers"
        ]
    }

    result = await run_mvp_recommendation_agent(
        idea=idea,
        market_analysis=market_context
    )

    mvp = MVPRecommendations(
        **result["mvp_recommendations"]
    )

    assert len(mvp.must_have) > 0

    text = get_feature_text(mvp)

    assert (
        "career" in text
        or "job" in text
        or "profile" in text
        or "customer" in text
    )


# -------------------------------------------------------------------
# 6. Competitor context usage
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_recommendation_uses_competitor_context():
    """
    Verify that competitor information influences recommendations.
    """

    idea = "AI meal planning application"

    competitor_context = {
        "direct_competitors": [
            {
                "name": "CompetitorA",
                "key_features": [
                    "Calorie tracking",
                    "Food database"
                ],
                "strengths": [
                    "Large food database"
                ],
                "weaknesses": [
                    "Limited personalized meal plans"
                ]
            }
        ],

        "market_gaps": [
            "Limited personalized meal planning"
        ]
    }

    result = await run_mvp_recommendation_agent(
        idea=idea,
        competitor_analysis=competitor_context
    )

    mvp = MVPRecommendations(
        **result["mvp_recommendations"]
    )

    text = get_feature_text(mvp)

    assert (
        "competitor" in text
        or "comparison" in text
        or "market gap" in text
        or "personalized" in text
        or "differenti" in text
    )


# -------------------------------------------------------------------
# 7. Market gap usage
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_recommendation_uses_market_gaps():
    """
    Verify that identified market gaps influence MVP features.
    """

    idea = "AI platform for local grocery delivery"

    competitor_context = {
        "market_gaps": [
            "Lack of same-day delivery in smaller towns",
            "Limited local-store availability"
        ],

        "direct_competitors": [
            {
                "name": "Existing Grocery App",
                "key_features": [
                    "Online ordering",
                    "Scheduled delivery"
                ]
            }
        ]
    }

    result = await run_mvp_recommendation_agent(
        idea=idea,
        competitor_analysis=competitor_context
    )

    mvp = MVPRecommendations(
        **result["mvp_recommendations"]
    )

    text = get_feature_text(mvp)

    assert (
        "gap" in text
        or "delivery" in text
        or "local" in text
        or "differenti" in text
    )


# -------------------------------------------------------------------
# 8. SWOT usage
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_recommendation_uses_swot_context():
    """
    Verify that SWOT opportunities/weaknesses can
    influence MVP recommendations.
    """

    idea = "AI platform for remote employee productivity"

    swot_context = {
        "strengths": [
            "Strong AI-based task analysis"
        ],

        "weaknesses": [
            "Limited user feedback mechanisms"
        ],

        "opportunities": [
            "Growing remote workforce"
        ],

        "threats": [
            "Strong competition from established productivity tools"
        ]
    }

    result = await run_mvp_recommendation_agent(
        idea=idea,
        swot_analysis=swot_context
    )

    mvp = MVPRecommendations(
        **result["mvp_recommendations"]
    )

    assert len(get_all_features(mvp)) > 0

    text = get_feature_text(mvp)

    assert (
        "opportun" in text
        or "feedback" in text
        or "competition" in text
        or "differenti" in text
        or "ai" in text
    )


# -------------------------------------------------------------------
# 9. Risk usage
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_recommendation_uses_risk_context():
    """
    Verify that important risks can result in
    risk-mitigation features.
    """

    idea = "Online healthcare appointment platform"

    risk_context = {
        "risks": [
            {
                "risk": "Unauthorized access to user information",
                "severity": "High",
                "impact": "Privacy and security issues",
                "mitigation": "Authentication and access control"
            }
        ]
    }

    result = await run_mvp_recommendation_agent(
        idea=idea,
        risk_analysis=risk_context
    )

    mvp = MVPRecommendations(
        **result["mvp_recommendations"]
    )

    assert len(get_all_features(mvp)) > 0

    text = get_feature_text(mvp)

    assert (
        "security" in text
        or "authentication" in text
        or "access" in text
        or "risk" in text
    )


# -------------------------------------------------------------------
# 10. Feature prioritization
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_recommendation_prioritizes_features():
    """
    Verify that features are distributed across priority categories.
    """

    idea = "AI fitness coaching application"

    result = await run_mvp_recommendation_agent(
        idea=idea
    )

    mvp = MVPRecommendations(
        **result["mvp_recommendations"]
    )

    assert len(mvp.must_have) > 0
    assert len(mvp.should_have) > 0
    assert len(mvp.could_have) > 0
    assert len(mvp.future_features) > 0


# -------------------------------------------------------------------
# 11. Priority labels should match their category
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_priority_labels_are_consistent():
    """
    Verify that each feature's priority matches the category
    in which the feature was returned.
    """

    idea = "AI shopping assistant for online customers"

    result = await run_mvp_recommendation_agent(
        idea=idea
    )

    mvp = MVPRecommendations(
        **result["mvp_recommendations"]
    )

    for feature in mvp.must_have:
        assert feature.priority.lower() == "must have"

    for feature in mvp.should_have:
        assert feature.priority.lower() == "should have"

    for feature in mvp.could_have:
        assert feature.priority.lower() == "could have"

    for feature in mvp.future_features:
        assert feature.priority.lower() == "future features"


# -------------------------------------------------------------------
# 12. No duplicate features
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_recommendation_has_no_duplicate_features():
    """
    Verify that the same feature is not recommended multiple times.
    """

    idea = "AI education platform for students"

    market_context = {
        "customer_segments": [
            "College students"
        ],

        "customer_needs": [
            "Personalized learning",
            "Personalized study plans"
        ],

        "pain_points": [
            "Difficulty studying efficiently",
            "Difficulty creating study plans"
        ]
    }

    competitor_context = {
        "direct_competitors": [
            {
                "name": "LearningApp",
                "key_features": [
                    "Study plans",
                    "Progress tracking"
                ]
            }
        ],

        "market_gaps": [
            "Limited personalization"
        ]
    }

    result = await run_mvp_recommendation_agent(
        idea=idea,
        market_analysis=market_context,
        competitor_analysis=competitor_context
    )

    mvp = MVPRecommendations(
        **result["mvp_recommendations"]
    )

    names = get_feature_names(mvp)

    assert len(names) == len(set(names))


# -------------------------------------------------------------------
# 13. Reasons should be meaningful
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_recommendation_reasons_are_meaningful():
    """
    Verify that recommendations contain useful explanations,
    not just empty/generic text.
    """

    idea = "AI platform for personalized financial education"

    market_context = {
        "customer_needs": [
            "Simple financial education"
        ],

        "pain_points": [
            "Users find financial concepts difficult"
        ]
    }

    result = await run_mvp_recommendation_agent(
        idea=idea,
        market_analysis=market_context
    )

    mvp = MVPRecommendations(
        **result["mvp_recommendations"]
    )

    for feature in get_all_features(mvp):

        assert len(feature.reason.strip()) >= 15

        # Reason should not simply repeat the feature name.
        assert feature.reason.strip().lower() != (
            feature.feature.strip().lower()
        )


# -------------------------------------------------------------------
# 14. Customer value validation
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_customer_value_values_are_valid():
    """
    Verify allowed customer value levels.
    """

    idea = "AI travel planning platform"

    result = await run_mvp_recommendation_agent(
        idea=idea
    )

    mvp = MVPRecommendations(
        **result["mvp_recommendations"]
    )

    allowed_values = {
        "high",
        "medium",
        "low"
    }

    for feature in get_all_features(mvp):

        assert feature.customer_value.strip().lower() in allowed_values


# -------------------------------------------------------------------
# 15. Complexity validation
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_complexity_values_are_valid():
    """
    Verify allowed implementation complexity levels.
    """

    idea = "AI recruitment platform"

    result = await run_mvp_recommendation_agent(
        idea=idea
    )

    mvp = MVPRecommendations(
        **result["mvp_recommendations"]
    )

    allowed_complexities = {
        "high",
        "medium",
        "low"
    }

    for feature in get_all_features(mvp):

        assert feature.complexity.strip().lower() in allowed_complexities


# -------------------------------------------------------------------
# 16. Missing context handling
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_recommendation_handles_missing_context():
    """
    Agent should work even when previous agent outputs are missing.
    """

    idea = (
        "Decentralized solar energy sharing "
        "platform for neighborhoods"
    )

    result = await run_mvp_recommendation_agent(
        idea=idea,
        market_analysis=None,
        competitor_analysis=None,
        swot_analysis=None,
        risk_analysis=None,
    )

    assert "mvp_recommendations" in result

    MVPRecommendations(
        **result["mvp_recommendations"]
    )


# -------------------------------------------------------------------
# 17. Empty dictionaries should be handled
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_recommendation_handles_empty_context():
    """
    Empty dictionaries should not crash the agent.
    """

    idea = "AI productivity application for students"

    result = await run_mvp_recommendation_agent(
        idea=idea,
        market_analysis={},
        competitor_analysis={},
        swot_analysis={},
        risk_analysis={},
    )

    assert "mvp_recommendations" in result

    mvp = MVPRecommendations(
        **result["mvp_recommendations"]
    )

    assert len(get_all_features(mvp)) > 0


# -------------------------------------------------------------------
# 18. Different startup ideas should produce valid results
# -------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "idea",
    [
        "AI platform for personalized education",
        "Smart agriculture monitoring system",
        "Electric vehicle charging marketplace",
        "AI-powered legal document assistant",
        "Online mental wellness journaling application",
    ]
)
async def test_mvp_agent_supports_different_startup_domains(idea):
    """
    Verify that the agent works across different startup domains.
    """

    result = await run_mvp_recommendation_agent(
        idea=idea
    )

    assert "mvp_recommendations" in result

    mvp = MVPRecommendations(
        **result["mvp_recommendations"]
    )

    assert len(get_all_features(mvp)) > 0


# -------------------------------------------------------------------
# 19. Structured output validation
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_output_is_structured_json():
    """
    Verify that the returned structure can be directly
    converted into the Pydantic MVPRecommendations model.
    """

    idea = "AI platform for small business marketing"

    result = await run_mvp_recommendation_agent(
        idea=idea
    )

    assert isinstance(result, dict)

    assert isinstance(
        result["mvp_recommendations"],
        dict
    )

    mvp = MVPRecommendations(
        **result["mvp_recommendations"]
    )

    assert isinstance(mvp, MVPRecommendations)


# -------------------------------------------------------------------
# 20. Empty idea validation
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_recommendation_rejects_empty_idea():
    """
    Empty or whitespace-only ideas should be rejected.
    """

    with pytest.raises(
        ValueError,
        match="cannot be empty"
    ):
        await run_mvp_recommendation_agent("   ")


# -------------------------------------------------------------------
# 21. Short idea validation
# -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mvp_recommendation_rejects_short_idea():
    """
    Very short ideas should be rejected.
    """

    with pytest.raises(
        ValueError,
        match="too short"
    ):
        await run_mvp_recommendation_agent("AI app")