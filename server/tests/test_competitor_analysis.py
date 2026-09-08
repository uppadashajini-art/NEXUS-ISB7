import pytest

from server.agents.competitor_analysis_agent import (
    run_competitor_analysis_agent,
)


@pytest.mark.asyncio
async def test_competitor_analysis_with_search_results():

    search_results = [
        {
            "title": "Fitbod Personalized Workout App",
            "url": "https://fitbod.me",
            "target_audience": "Fitness Users",
            "content": (
                "Fitbod provides personalized workout plans "
                "and fitness tracking. The platform offers "
                "advanced analytics and subscription pricing."
            ),
        }
    ]

    result = await run_competitor_analysis_agent(
        idea="AI platform for personalized fitness plans",
        search_results=search_results,
    )

    assert "competitor_analysis" in result

    analysis = result["competitor_analysis"]

    assert "direct_competitors" in analysis
    assert "indirect_competitors" in analysis
    assert "comparison" in analysis
    assert "market_gaps" in analysis


@pytest.mark.asyncio
async def test_empty_search_results():

    result = await run_competitor_analysis_agent(
        idea="AI platform for personalized fitness plans",
        search_results=[],
    )

    assert "competitor_analysis" in result

    analysis = result["competitor_analysis"]

    assert analysis["direct_competitors"] == []
    assert analysis["indirect_competitors"] == []
    assert analysis["comparison"] == []
    assert len(analysis["market_gaps"]) > 0


@pytest.mark.asyncio
async def test_invalid_search_result_is_ignored():

    search_results = [
        None,
        "invalid",
        {},
    ]

    result = await run_competitor_analysis_agent(
        idea="AI platform for personalized fitness plans",
        search_results=search_results,
    )

    assert "competitor_analysis" in result


@pytest.mark.asyncio
async def test_duplicate_urls_are_removed():

    search_results = [
        {
            "title": "Fitness Platform",
            "url": "https://example.com",
            "target_audience": "Fitness Users",
            "content": (
                "This platform provides personalized workouts "
                "and advanced analytics."
            ),
        },
        {
            "title": "Fitness Platform Duplicate",
            "url": "https://example.com",
            "target_audience": "Fitness Users",
            "content": (
                "This platform provides personalized workouts."
            ),
        },
    ]

    result = await run_competitor_analysis_agent(
        idea="AI platform for personalized fitness plans",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    all_competitors = (
        analysis["direct_competitors"]
        + analysis["indirect_competitors"]
    )

    urls = [
        competitor["url"]
        for competitor in all_competitors
        if competitor.get("url")
    ]

    assert len(urls) == len(set(urls))