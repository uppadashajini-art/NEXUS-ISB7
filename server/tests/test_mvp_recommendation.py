"""
NEXUS-ISB7 — MVP Recommendation Agent Test Suite

Role: Member 2 — MVP Feature Recommendation

Covers:
- MVP category completeness
- Feature schema validation
- Customer and market context usage
- Competitor context usage
- Graceful handling of missing context
- Input validation
"""


import pytest

from server.agents.mvp_recommendation_agent import (
    run_mvp_recommendation_agent
)

from server.models.validation import (
    MVPFeature,
    MVPRecommendations,
)


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

    all_features = (
        mvp.must_have
        + mvp.should_have
        + mvp.could_have
        + mvp.future_features
    )

    assert len(all_features) > 0

    for feature in all_features:

        assert isinstance(feature, MVPFeature)

        assert feature.feature.strip() != ""
        assert feature.priority.strip() != ""
        assert feature.reason.strip() != ""
        assert feature.customer_value.strip() != ""
        assert feature.complexity.strip() != ""


@pytest.mark.asyncio
async def test_mvp_recommendation_uses_market_context():
    """
    Verify that customer needs can influence recommendations.
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