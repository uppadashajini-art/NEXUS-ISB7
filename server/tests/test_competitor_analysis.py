import pytest

from server.agents.competitor_analysis_agent import (
    run_competitor_analysis_agent,
)


# ============================================================================
# BASIC OUTPUT CONTRACT
# ============================================================================

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


# ============================================================================
# EMPTY INPUT
# ============================================================================

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

    # Even without evidence, the agent should return a useful
    # market-gap message rather than crashing.
    assert len(analysis["market_gaps"]) > 0


# ============================================================================
# INVALID INPUT
# ============================================================================

@pytest.mark.asyncio
async def test_invalid_search_result_is_ignored():
    search_results = [
        None,
        "invalid",
        {},
        123,
        [],
    ]

    result = await run_competitor_analysis_agent(
        idea="AI platform for personalized fitness plans",
        search_results=search_results,
    )

    assert "competitor_analysis" in result

    analysis = result["competitor_analysis"]

    assert isinstance(
        analysis["direct_competitors"],
        list,
    )

    assert isinstance(
        analysis["indirect_competitors"],
        list,
    )


# ============================================================================
# DIRECT COMPETITOR DETECTION
# ============================================================================

@pytest.mark.asyncio
async def test_direct_competitor_is_detected():
    search_results = [
        {
            "title": "Fitbod - Personalized Workout Plans",
            "url": "https://fitbod.me",
            "target_audience": "Fitness Users",
            "content": (
                "Fitbod is a fitness app and platform that "
                "provides personalized workout plans. "
                "It offers personalized recommendations, "
                "workout tracking and analytics."
            ),
        }
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

    assert len(all_competitors) >= 1

    names = [
        competitor["name"].lower()
        for competitor in all_competitors
    ]

    assert any(
        "fitbod" in name
        for name in names
    )


# ============================================================================
# MULTIPLE DIRECT COMPETITORS
# ============================================================================

@pytest.mark.asyncio
async def test_multiple_direct_competitors_are_detected():
    search_results = [
        {
            "title": "Fitbod Personalized Workout App",
            "url": "https://fitbod.me",
            "target_audience": "Fitness Users",
            "content": (
                "Fitbod is a fitness app that provides "
                "personalized workout plans and recommendations."
            ),
        },
        {
            "title": "FitnessAI Personalized Training App",
            "url": "https://fitnessai.com",
            "target_audience": "Fitness Enthusiasts",
            "content": (
                "FitnessAI provides personalized workout "
                "plans and AI recommendations based on "
                "user goals and performance."
            ),
        },
        {
            "title": "Freeletics AI Fitness Coach",
            "url": "https://freeletics.com",
            "target_audience": "Fitness Users",
            "content": (
                "Freeletics is an AI fitness platform that "
                "provides personalized training plans and "
                "coaching recommendations."
            ),
        },
    ]

    result = await run_competitor_analysis_agent(
        idea="AI platform for personalized fitness plans",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    assert len(
        analysis["direct_competitors"]
    ) >= 3


# ============================================================================
# INDIRECT COMPETITOR DETECTION
# ============================================================================

@pytest.mark.asyncio
async def test_indirect_competitor_is_detected():
    search_results = [
        {
            "title": "Personal Trainer Coaching Services",
            "url": "https://example.com/personal-trainer",
            "target_audience": "Fitness Enthusiasts",
            "content": (
                "Personal trainers provide individualized "
                "workout coaching and fitness guidance. "
                "Traditional coaching is an alternative "
                "to fitness apps and can be expensive."
            ),
        }
    ]

    result = await run_competitor_analysis_agent(
        idea="AI platform for personalized fitness plans",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    assert len(
        analysis["indirect_competitors"]
    ) >= 1


# ============================================================================
# RESEARCH REPORT FILTERING
# ============================================================================

@pytest.mark.asyncio
async def test_market_research_report_is_not_competitor():
    search_results = [
        {
            "title": "AI Fitness Market Size and Trends 2035",
            "url": "https://example.com/market-report",
            "target_audience": "Fitness Businesses",
            "content": (
                "The AI fitness market research report "
                "provides market size, revenue forecasts, "
                "industry analysis and market trends."
            ),
        }
    ]

    result = await run_competitor_analysis_agent(
        idea="AI platform for personalized fitness plans",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    assert analysis["direct_competitors"] == []
    assert analysis["indirect_competitors"] == []


# ============================================================================
# WIKIPEDIA FILTERING
# ============================================================================

@pytest.mark.asyncio
async def test_wikipedia_is_not_competitor():
    search_results = [
        {
            "title": "Fitness App",
            "url": "https://en.wikipedia.org/wiki/Fitness",
            "target_audience": "General Users",
            "content": (
                "This page describes fitness applications "
                "and digital fitness services."
            ),
        }
    ]

    result = await run_competitor_analysis_agent(
        idea="AI fitness platform",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    assert analysis["direct_competitors"] == []
    assert analysis["indirect_competitors"] == []


# ============================================================================
# GIFT / IRRELEVANT PAGE FILTERING
# ============================================================================

@pytest.mark.asyncio
async def test_gift_page_is_not_competitor():
    search_results = [
        {
            "title": "Best Fitness Gifts for Christmas",
            "url": "https://example.com/fitness-gifts",
            "content": (
                "Here are the best fitness gifts and gift "
                "cards for Christmas and birthdays."
            ),
        }
    ]

    result = await run_competitor_analysis_agent(
        idea="AI fitness platform",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    assert analysis["direct_competitors"] == []
    assert analysis["indirect_competitors"] == []


# ============================================================================
# FEATURE EXTRACTION
# ============================================================================

@pytest.mark.asyncio
async def test_competitor_features_are_extracted():
    search_results = [
        {
            "title": "Fitbod Personalized Workout App",
            "url": "https://fitbod.me",
            "target_audience": "Fitness Users",
            "content": (
                "Fitbod provides personalized workout plans. "
                "The app supports workout tracking and "
                "personalized recommendations. "
                "It also provides progress monitoring."
            ),
        }
    ]

    result = await run_competitor_analysis_agent(
        idea="AI fitness platform",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    competitors = analysis["direct_competitors"]

    assert len(competitors) >= 1

    competitor = competitors[0]

    assert "key_features" in competitor
    assert isinstance(
        competitor["key_features"],
        list,
    )

    assert len(
        competitor["key_features"]
    ) > 0


# ============================================================================
# PRICING EXTRACTION
# ============================================================================

@pytest.mark.asyncio
async def test_competitor_pricing_is_extracted():
    search_results = [
        {
            "title": "Fitbod Pricing and Personalized Workout Plans",
            "url": "https://fitbod.me/pricing",
            "target_audience": "Fitness Users",
            "content": (
                "Fitbod provides personalized workout plans "
                "and workout tracking. The premium subscription "
                "costs $9.99 per month."
            ),
        }
    ]

    result = await run_competitor_analysis_agent(
        idea="AI fitness platform",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    competitors = analysis["direct_competitors"]

    assert len(competitors) >= 1

    competitor = competitors[0]

    assert competitor.get("pricing") is not None

    assert (
        "$9.99" in competitor["pricing"]
        or "9.99" in competitor["pricing"]
    )


# ============================================================================
# TARGET CUSTOMER EXTRACTION
# ============================================================================

@pytest.mark.asyncio
async def test_competitor_target_customer_is_preserved():
    search_results = [
        {
            "title": "Fitbod Personalized Workout App",
            "url": "https://fitbod.me",
            "target_audience": "Fitness Enthusiasts",
            "content": (
                "Fitbod provides personalized workout plans "
                "for fitness users."
            ),
        }
    ]

    result = await run_competitor_analysis_agent(
        idea="AI fitness platform",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    competitors = analysis["direct_competitors"]

    assert len(competitors) >= 1

    competitor = competitors[0]

    assert (
        competitor["target_customers"]
        == "Fitness Enthusiasts"
    )


# ============================================================================
# STRENGTH EXTRACTION
# ============================================================================

@pytest.mark.asyncio
async def test_competitor_strengths_are_extracted():
    search_results = [
        {
            "title": "Fitbod Advanced Personalized Fitness Platform",
            "url": "https://fitbod.me",
            "target_audience": "Fitness Users",
            "content": (
                "Fitbod is a popular and powerful fitness "
                "platform. It provides advanced personalized "
                "recommendations and comprehensive workout "
                "tracking."
            ),
        }
    ]

    result = await run_competitor_analysis_agent(
        idea="AI fitness platform",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    competitors = analysis["direct_competitors"]

    assert len(competitors) >= 1

    competitor = competitors[0]

    assert "strengths" in competitor
    assert isinstance(
        competitor["strengths"],
        list,
    )

    assert len(
        competitor["strengths"]
    ) > 0


# ============================================================================
# WEAKNESS EXTRACTION
# ============================================================================

@pytest.mark.asyncio
async def test_competitor_weaknesses_are_extracted():
    search_results = [
        {
            "title": "Fitness App Review",
            "url": "https://example.com/fitness-app-review",
            "target_audience": "Fitness Users",
            "content": (
                "The fitness app provides personalized "
                "workouts but the premium plan is expensive "
                "and some users report a complex interface."
            ),
        }
    ]

    result = await run_competitor_analysis_agent(
        idea="AI fitness platform",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    competitors = analysis["direct_competitors"]

    assert len(competitors) >= 1

    competitor = competitors[0]

    assert "weaknesses" in competitor
    assert isinstance(
        competitor["weaknesses"],
        list,
    )

    assert len(
        competitor["weaknesses"]
    ) > 0


# ============================================================================
# COMPARISON GENERATION
# ============================================================================

@pytest.mark.asyncio
async def test_competitor_comparison_is_generated():
    search_results = [
        {
            "title": "Fitbod Personalized Workout App",
            "url": "https://fitbod.me",
            "target_audience": "Fitness Users",
            "content": (
                "Fitbod provides personalized workout plans "
                "and advanced analytics. The platform is "
                "popular among fitness users."
            ),
        },
        {
            "title": "FitnessAI Personalized Training",
            "url": "https://fitnessai.com",
            "target_audience": "Fitness Enthusiasts",
            "content": (
                "FitnessAI provides personalized workout "
                "recommendations and progress tracking."
            ),
        },
    ]

    result = await run_competitor_analysis_agent(
        idea="AI fitness platform",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    assert len(
        analysis["comparison"]
    ) > 0

    row = analysis["comparison"][0]

    assert "competitor" in row
    assert "target_customers" in row
    assert "key_features" in row
    assert "strengths" in row
    assert "weaknesses" in row


# ============================================================================
# MARKET GAP GENERATION
# ============================================================================

@pytest.mark.asyncio
async def test_market_gap_is_generated_from_weaknesses():
    search_results = [
        {
            "title": "Fitness App Review",
            "url": "https://example.com/fitness-review",
            "target_audience": "Fitness Users",
            "content": (
                "The fitness app provides personalized "
                "workouts but the service is expensive "
                "and the interface is complex for beginners."
            ),
        }
    ]

    result = await run_competitor_analysis_agent(
        idea="Affordable AI fitness platform",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    assert len(
        analysis["market_gaps"]
    ) > 0

    gap_text = " ".join(
        analysis["market_gaps"]
    ).lower()

    assert (
        "affordable" in gap_text
        or "pricing" in gap_text
        or "simpl" in gap_text
        or "opportunity" in gap_text
    )


# ============================================================================
# NO-EVIDENCE MARKET GAP
# ============================================================================

@pytest.mark.asyncio
async def test_market_gap_is_conservative_without_weakness_evidence():
    search_results = [
        {
            "title": "Fitbod Personalized Workout App",
            "url": "https://fitbod.me",
            "target_audience": "Fitness Users",
            "content": (
                "Fitbod provides personalized workout plans "
                "and workout tracking."
            ),
        }
    ]

    result = await run_competitor_analysis_agent(
        idea="AI fitness platform",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    assert len(
        analysis["market_gaps"]
    ) > 0

    # The agent should not claim that a specific gap has
    # definitely been proven when evidence is unavailable.
    gap_text = " ".join(
        analysis["market_gaps"]
    ).lower()

    assert (
        "potential" in gap_text
        or "further" in gap_text
        or "validated" in gap_text
        or "no explicit" in gap_text
    )


# ============================================================================
# DUPLICATE URL REMOVAL
# ============================================================================

@pytest.mark.asyncio
async def test_duplicate_urls_are_removed():
    search_results = [
        {
            "title": "Fitness Platform",
            "url": "https://example.com",
            "target_audience": "Fitness Users",
            "content": (
                "This platform provides personalized "
                "workouts and advanced analytics."
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


# ============================================================================
# DUPLICATE NAME REMOVAL
# ============================================================================

@pytest.mark.asyncio
async def test_duplicate_competitor_names_are_removed():
    search_results = [
        {
            "title": "Fitbod Review",
            "url": "https://fitbod.me/review",
            "target_audience": "Fitness Users",
            "content": (
                "Fitbod provides personalized workout plans "
                "and workout tracking."
            ),
        },
        {
            "title": "Fitbod Pricing",
            "url": "https://fitbod.me/pricing",
            "target_audience": "Fitness Users",
            "content": (
                "Fitbod offers personalized workouts and "
                "subscription pricing."
            ),
        },
    ]

    result = await run_competitor_analysis_agent(
        idea="AI fitness platform",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    all_competitors = (
        analysis["direct_competitors"]
        + analysis["indirect_competitors"]
    )

    names = [
        competitor["name"].lower()
        for competitor in all_competitors
    ]

    assert len(names) == len(set(names))


# ============================================================================
# COMPETITOR LIMIT
# ============================================================================

@pytest.mark.asyncio
async def test_competitor_limit_is_respected():
    search_results = []

    for index in range(10):
        search_results.append(
            {
                "title": f"Fitness App {index}",
                "url": f"https://fitness{index}.com",
                "target_audience": "Fitness Users",
                "content": (
                    "This fitness app provides personalized "
                    "workout plans and tracking."
                ),
            }
        )

    result = await run_competitor_analysis_agent(
        idea="AI fitness platform",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    assert len(
        analysis["direct_competitors"]
    ) <= 5

    assert len(
        analysis["indirect_competitors"]
    ) <= 5


# ============================================================================
# RESULT STRUCTURE
# ============================================================================

@pytest.mark.asyncio
async def test_competitor_object_contains_expected_fields():
    search_results = [
        {
            "title": "Fitbod Personalized Workout App",
            "url": "https://fitbod.me",
            "target_audience": "Fitness Users",
            "content": (
                "Fitbod provides personalized workout plans "
                "and fitness tracking."
            ),
        }
    ]

    result = await run_competitor_analysis_agent(
        idea="AI fitness platform",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    all_competitors = (
        analysis["direct_competitors"]
        + analysis["indirect_competitors"]
    )

    assert len(all_competitors) >= 1

    competitor = all_competitors[0]

    expected_fields = [
        "name",
        "url",
        "product_service",
        "target_customers",
        "key_features",
        "pricing",
        "strengths",
        "weaknesses",
    ]

    for field in expected_fields:
        assert field in competitor


# ============================================================================
# RESULT URLs ARE VALID / PRESERVED
# ============================================================================

@pytest.mark.asyncio
async def test_competitor_url_is_preserved():
    search_results = [
        {
            "title": "Fitbod Personalized Workout App",
            "url": "https://fitbod.me",
            "target_audience": "Fitness Users",
            "content": (
                "Fitbod provides personalized workout plans."
            ),
        }
    ]

    result = await run_competitor_analysis_agent(
        idea="AI fitness platform",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    all_competitors = (
        analysis["direct_competitors"]
        + analysis["indirect_competitors"]
    )

    assert len(all_competitors) >= 1

    competitor = all_competitors[0]

    assert competitor["url"] == "https://fitbod.me"


# ============================================================================
# NON-LIST SEARCH RESULTS
# ============================================================================

@pytest.mark.asyncio
async def test_non_list_search_results_are_handled():
    result = await run_competitor_analysis_agent(
        idea="AI fitness platform",
        search_results=None,
    )

    assert "competitor_analysis" in result

    analysis = result["competitor_analysis"]

    assert analysis["direct_competitors"] == []
    assert analysis["indirect_competitors"] == []
    assert analysis["comparison"] == []
    assert len(analysis["market_gaps"]) > 0


# ============================================================================
# RESEARCH SOURCE + REAL PRODUCT MIX
# ============================================================================

@pytest.mark.asyncio
async def test_research_sources_are_filtered_but_products_are_kept():
    search_results = [
        {
            "title": "AI Fitness Market Size and Trends 2035",
            "url": "https://example.com/market-report",
            "content": (
                "The market research report provides "
                "market size, revenue forecasts, industry "
                "analysis and market trends."
            ),
        },
        {
            "title": "Fitbod Personalized Workout App",
            "url": "https://fitbod.me",
            "target_audience": "Fitness Users",
            "content": (
                "Fitbod provides personalized workout plans "
                "and workout tracking."
            ),
        },
    ]

    result = await run_competitor_analysis_agent(
        idea="AI fitness platform",
        search_results=search_results,
    )

    analysis = result["competitor_analysis"]

    assert len(
        analysis["direct_competitors"]
    ) >= 1

    competitor_names = [
        competitor["name"].lower()
        for competitor in analysis["direct_competitors"]
    ]

    assert any(
        "fitbod" in name
        for name in competitor_names
    )

    assert not any(
        "market size" in name
        or "market research" in name
        for name in competitor_names
    )

