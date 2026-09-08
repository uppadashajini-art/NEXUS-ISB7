"""
NEXUS-ISB7 — Multi-Agent Orchestrator

Role: Member 1 — Agent Orchestration & System Integration

Coordinates the multi-agent execution pipeline for Milestone 2:

1. Validates the startup idea.
2. Invokes Web Search Agent to retrieve real-time market/competitor evidence.
3. Passes search results as context to the Market Analysis Agent (Member 2).
4. Passes search results as context to the Competitor Analysis Agent (Member 3).
5. Aggregates and validates results against the unified ValidationResponse schema.
6. Returns structured data to FastAPI and the React UI.
"""

import asyncio
import logging
import re
import urllib.parse
from typing import Any, Dict, List, Optional

from server.models.validation import (
    ComparisonRow,
    Competitor,
    CompetitorAnalysis,
    CustomerSegment,
    MarketAnalysis,
    ValidationResponse,
)

logger = logging.getLogger(__name__)

try:
    from server.agents.web_search_agent import run_web_search_agent
except ImportError:
    logger.warning("web_search_agent not found via direct import")

    async def run_web_search_agent(
        idea: str, **kwargs
    ) -> Dict[str, Any]:
        return {"results": []}


async def _dispatch_market_analysis(
    idea: str,
    search_results: List[Dict[str, Any]],
    domain: Optional[str] = None,
) -> Dict[str, Any]:

    try:
        from server.agents.market_analysis_agent import (
            run_market_analysis_agent
        )

        result = await run_market_analysis_agent(
            idea=idea,
            search_results=search_results,
            domain=domain,
        )

        if isinstance(result, dict) and "market_analysis" in result:
            return result["market_analysis"]

        if isinstance(result, dict) and "industry" in result:
            return result

    except (ImportError, AttributeError):
        logger.info(
            "Market Analysis Agent not available; "
            "using fallback analyzer"
        )

    except Exception as exc:
        logger.warning(
            f"Market Analysis Agent failed: {exc}; "
            "using fallback analyzer"
        )

    return _generate_fallback_market_analysis(
        idea,
        search_results,
        domain,
    )


async def _dispatch_competitor_analysis(
    idea: str,
    search_results: List[Dict[str, Any]],
) -> Dict[str, Any]:

    try:
        from server.agents.competitor_analysis_agent import (
            run_competitor_analysis_agent
        )

        result = await run_competitor_analysis_agent(
            idea=idea,
            search_results=search_results,
        )

        if isinstance(result, dict) and "competitor_analysis" in result:
            return result["competitor_analysis"]

        if isinstance(result, dict) and "direct_competitors" in result:
            return result

    except (ImportError, AttributeError):
        logger.info(
            "Competitor Analysis Agent not available; "
            "using fallback analyzer"
        )

    except Exception as exc:
        logger.warning(
            f"Competitor Analysis Agent failed: {exc}; "
            "using fallback analyzer"
        )

    return _generate_fallback_competitor_analysis(
        idea,
        search_results,
    )


def _detect_industry(
    idea: str,
    domain: Optional[str] = None,
) -> str:

    if domain and domain.strip():
        return domain.strip().title()

    lower = idea.lower()

    if any(
        w in lower
        for w in [
            "fitness",
            "workout",
            "gym",
            "health",
            "diet",
            "nutrition",
            "wellness",
            "medical",
        ]
    ):
        return "HealthTech & Fitness Technology"

    if any(
        w in lower
        for w in [
            "finance",
            "fintech",
            "banking",
            "crypto",
            "invest",
            "payment",
            "money",
            "budget",
        ]
    ):
        return "FinTech & Financial Services"

    if any(
        w in lower
        for w in [
            "education",
            "edtech",
            "student",
            "school",
            "course",
            "learn",
            "lecture",
            "quiz",
        ]
    ):
        return "EdTech & Educational Technology"

    if any(
        w in lower
        for w in [
            "ecommerce",
            "e-commerce",
            "retail",
            "shop",
            "store",
            "product",
            "cart",
        ]
    ):
        return "E-Commerce & Digital Commerce"

    if any(
        w in lower
        for w in [
            "productivity",
            "task",
            "workflow",
            "collaboration",
            "saas",
            "crm",
            "project",
        ]
    ):
        return "Enterprise SaaS & Productivity"

    if any(
        w in lower
        for w in [
            "ai",
            "machine learning",
            "automation",
            "agent",
            "bot",
        ]
    ):
        return "Artificial Intelligence & Automation"

    return "Technology & Digital Services"


def _generate_fallback_market_analysis(
    idea: str,
    search_results: List[Dict[str, Any]],
    domain: Optional[str] = None,
) -> Dict[str, Any]:

    industry = _detect_industry(idea, domain)

    snippets = [
        r.get("title", "")
        for r in search_results
        if r.get("title")
    ]

    trends = [
        f"Rapid acceleration of AI-powered personalization in {industry}",
        "Increasing user preference for mobile-first platforms",
        "Growing integration of analytics and real-time feedback",
        "Shift toward unified end-to-end ecosystems",
    ]

    if snippets:
        trends.insert(
            0,
            f"Recent development: {snippets[0][:60]}..."
        )

    customer_segments = [
        CustomerSegment(
            segment="Tech-Forward Early Adopters & Professionals",
            needs=[
                "Automated workflows",
                "Personalized recommendations",
                "Seamless integration",
            ],
            pain_points=[
                "High manual effort",
                "Generic solutions",
                "Poor long-term consistency",
            ],
        ),
        CustomerSegment(
            segment="Small Teams, Students & Independent Creators",
            needs=[
                "Affordable pricing",
                "Quick onboarding",
                "Progress visualization",
            ],
            pain_points=[
                "High subscription costs",
                "Steep learning curves",
                "Limited support",
            ],
        ),
    ]

    return MarketAnalysis(
        industry=industry,
        market_opportunity=(
            f"Significant commercial opportunity in the "
            f"{industry} sector."
        ),
        market_trends=trends[:4],
        customer_segments=customer_segments,
        growth_drivers=[
            "Growing digital transformation",
            "Self-service adoption",
            "Social and collaborative growth",
        ],
        market_challenges=[
            "High customer acquisition costs",
            "User retention",
            "Data privacy and security",
        ],
    ).model_dump()


def _clean_competitor_name(
    title: str,
    url: str,
) -> str:

    if url:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.replace("www.", "")

        if netloc:
            parts = netloc.split(".")
            if parts:
                return parts[0].capitalize()

    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", title)
    words = cleaned.split()

    return " ".join(words[:2]).title() if words else "Market Player"


def _generate_fallback_competitor_analysis(
    idea: str,
    search_results: List[Dict[str, Any]],
) -> Dict[str, Any]:

    direct_competitors: List[Competitor] = []
    comparison_rows: List[ComparisonRow] = []

    seen_names = set()

    for item in search_results:

        raw_title = item.get("title", "")
        raw_url = item.get("url", "")

        if not raw_title:
            continue

        comp_name = _clean_competitor_name(
            raw_title,
            raw_url,
        )

        if comp_name.lower() in seen_names:
            continue

        seen_names.add(comp_name.lower())

        target = (
            item.get("target_audience")
            or "Broad Market / Digital Users"
        )

        direct_competitors.append(
            Competitor(
                name=comp_name,
                url=raw_url or None,
                product_service=raw_title[:80],
                target_customers=target,
                key_features=[
                    "Core platform functionality",
                    "Web & mobile interface",
                    "Automated features",
                ],
                pricing="Freemium / Paid Tier available",
                strengths=[
                    "Established presence",
                    "Active user base",
                ],
                weaknesses=[
                    "Generic positioning",
                    "Limited personalization",
                ],
            )
        )

        comparison_rows.append(
            ComparisonRow(
                competitor=comp_name,
                target_customers=target,
                key_features="General industry solution",
                strengths="Established presence",
                weaknesses="Less specialized",
            )
        )

        if len(direct_competitors) >= 3:
            break

    if not direct_competitors:
        direct_competitors = [
            Competitor(
                name="Incumbent Player",
                url=None,
                product_service="Established industry solution",
                target_customers="Large organizations",
                key_features=["Established feature set"],
                pricing="Paid subscription",
                strengths=["Recognized brand"],
                weaknesses=["Higher cost"],
            )
        ]

        comparison_rows = [
            ComparisonRow(
                competitor="Incumbent Player",
                target_customers="Large organizations",
                key_features="Established feature set",
                strengths="Recognized brand",
                weaknesses="Higher cost",
            )
        ]

    indirect_competitors = [
        Competitor(
            name="Manual / Spreadsheet Workarounds",
            product_service="Spreadsheets and templates",
            target_customers="Budget-conscious users",
            key_features=[
                "Flexible",
                "Low cost",
            ],
            pricing="Free / Low cost",
            strengths=[
                "Customizable",
                "Low cost",
            ],
            weaknesses=[
                "Manual effort",
                "Error-prone",
            ],
        ),
        Competitor(
            name="Traditional Consultancies / Agencies",
            product_service="Human consulting services",
            target_customers="High-budget clients",
            key_features=[
                "Human expertise",
            ],
            pricing="Hourly / Retainer",
            strengths=[
                "Domain expertise",
            ],
            weaknesses=[
                "Expensive",
                "Not scalable",
            ],
        ),
    ]

    return CompetitorAnalysis(
        direct_competitors=direct_competitors,
        indirect_competitors=indirect_competitors,
        comparison=comparison_rows,
        market_gaps=[
            "Affordable pricing",
            "Automated AI-driven workflows",
            "Recommendations backed by live evidence",
            "Unified all-in-one experience",
        ],
    ).model_dump()


async def run_orchestrator(
    idea: str,
    domain: Optional[str] = None,
) -> Dict[str, Any]:

    if not idea or not isinstance(idea, str):
        raise ValueError("Startup idea cannot be empty")

    cleaned_idea = idea.strip()

    if not cleaned_idea:
        raise ValueError("Startup idea cannot be empty")

    if len(cleaned_idea) < 10:
        raise ValueError(
            "Startup idea is too short to analyze meaningfully"
        )

    logger.info(
        f"Orchestrator initiated for idea: "
        f"'{cleaned_idea[:50]}...'"
    )

    try:
        search_payload = await run_web_search_agent(
            idea=cleaned_idea,
            domain=domain,
        )

        search_results = (
            search_payload.get("results", [])
            if isinstance(search_payload, dict)
            else []
        )

    except Exception as exc:
        logger.error(
            f"Web Search Agent failed: {exc}"
        )
        search_results = []

    market_task = _dispatch_market_analysis(
        cleaned_idea,
        search_results,
        domain,
    )

    competitor_task = _dispatch_competitor_analysis(
        cleaned_idea,
        search_results,
    )

    market_data, competitor_data = await asyncio.gather(
        market_task,
        competitor_task,
    )

    validated_response = ValidationResponse(
        idea=cleaned_idea,
        market_analysis=market_data,
        competitor_analysis=competitor_data,
    )

    return validated_response.model_dump()


if __name__ == "__main__":
    test_idea = (
        "AI powered platform for personalized "
        "fitness plans and meal tracking"
    )

    result = asyncio.run(
        run_orchestrator(test_idea)
    )

    import json

    print(json.dumps(result, indent=2))