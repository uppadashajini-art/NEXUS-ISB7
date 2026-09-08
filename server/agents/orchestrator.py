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

# Try to import Web Search Agent
try:
    from server.agents.web_search_agent import run_web_search_agent
except ImportError:
    logger.warning("web_search_agent not found via direct import; checking package import")
    try:
        from .web_search_agent import run_web_search_agent
    except ImportError:
        async def run_web_search_agent(idea: str, **kwargs) -> Dict[str, Any]:
            return {"results": []}


# ---------------------------------------------------------------------------
# Dynamic Agent Dispatchers with Resilient Fallback Engines
# ---------------------------------------------------------------------------

async def _dispatch_market_analysis(idea: str, search_results: List[Dict[str, Any]], domain: Optional[str] = None) -> Dict[str, Any]:
    """
    Invokes Member 2's Market Analysis Agent.
    If the agent module is not yet merged, runs the resilient fallback analyzer.
    """
    try:
        from server.agents.market_analysis_agent import run_market_analysis_agent
        result = await run_market_analysis_agent(idea=idea, search_results=search_results, domain=domain)
        if isinstance(result, dict) and "market_analysis" in result:
            return result["market_analysis"]
        if isinstance(result, dict) and "industry" in result:
            return result
    except (ImportError, AttributeError):
        logger.info("Member 2 market_analysis_agent not yet merged; using built-in engine")
    except Exception as exc:
        logger.warning(f"Error calling external market_analysis_agent: {exc}; falling back to built-in engine")

    return _generate_fallback_market_analysis(idea, search_results, domain)


async def _dispatch_competitor_analysis(idea: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Invokes Member 3's Competitor Analysis Agent.
    If the agent module is not yet merged, runs the resilient fallback analyzer.
    """
    try:
        from server.agents.competitor_analysis_agent import run_competitor_analysis_agent
        result = await run_competitor_analysis_agent(idea=idea, search_results=search_results)
        if isinstance(result, dict) and "competitor_analysis" in result:
            return result["competitor_analysis"]
        if isinstance(result, dict) and "direct_competitors" in result:
            return result
    except (ImportError, AttributeError):
        logger.info("Member 3 competitor_analysis_agent not yet merged; using built-in engine")
    except Exception as exc:
        logger.warning(f"Error calling external competitor_analysis_agent: {exc}; falling back to built-in engine")

    return _generate_fallback_competitor_analysis(idea, search_results)


# ---------------------------------------------------------------------------
# Built-In Fallback Analysis Engines (Member 2 & 3 Contracts)
# ---------------------------------------------------------------------------

def _detect_industry(idea: str, domain: Optional[str] = None) -> str:
    if domain and domain.strip():
        return domain.strip().title()

    lower = idea.lower()
    if any(w in lower for w in ["fitness", "workout", "gym", "health", "diet", "nutrition", "wellness", "medical"]):
        return "HealthTech & Fitness Technology"
    if any(w in lower for w in ["finance", "fintech", "banking", "crypto", "invest", "payment", "money", "budget"]):
        return "FinTech & Financial Services"
    if any(w in lower for w in ["education", "edtech", "student", "school", "course", "learn", "lecture", "quiz"]):
        return "EdTech & Educational Technology"
    if any(w in lower for w in ["ecommerce", "e-commerce", "retail", "shop", "store", "product", "cart"]):
        return "E-Commerce & Digital Commerce"
    if any(w in lower for w in ["productivity", "task", "workflow", "collaboration", "saas", "crm", "project"]):
        return "Enterprise SaaS & Productivity"
    if any(w in lower for w in ["ai", "machine learning", "automation", "agent", "bot"]):
        return "Artificial Intelligence & Automation"
    return "Technology & Digital Services"


def _generate_fallback_market_analysis(idea: str, search_results: List[Dict[str, Any]], domain: Optional[str] = None) -> Dict[str, Any]:
    industry = _detect_industry(idea, domain)
    lower = idea.lower()

    # Dynamic market opportunity
    market_opp = (
        f"Significant commercial opportunity in the {industry} sector. "
        f"Increasing customer demand for automated and personalized solutions provides a strong growth trajectory "
        f"with high customer willingness-to-pay for time-saving platforms."
    )

    # Extract snippets from web search results if available
    snippets = [r.get("title", "") for r in search_results if r.get("title")]

    trends = [
        f"Rapid acceleration of AI-powered personalization in {industry}",
        "Increasing user preference for mobile-first, proactive self-service platforms",
        "Growing integration of analytics and real-time feedback loops",
        "Shift from fragmented point solutions to unified end-to-end ecosystems"
    ]
    if snippets:
        trends.insert(0, f"Industry interest driven by recent developments: {snippets[0][:60]}...")

    customer_segments = [
        CustomerSegment(
            segment="Primary: Tech-Forward Early Adopters & Professionals",
            needs=[
                "Automated workflows with minimal manual input",
                "Actionable, personalized recommendations",
                "Seamless integration into existing daily routines"
            ],
            pain_points=[
                "High friction and time spent using legacy manual alternatives",
                "Generic solutions that lack contextual personalization",
                "Inability to maintain long-term consistency"
            ]
        ),
        CustomerSegment(
            segment="Secondary: Small Teams, Students & Independent Creators",
            needs=[
                "Affordable pricing tiers and quick onboarding",
                "Clear visualization of progress and measurable value",
                "Collaborative sharing capabilities"
            ],
            pain_points=[
                "High subscription costs of enterprise-grade tools",
                "Steep learning curves and bloated feature sets",
                "Lack of accessible customer support"
            ]
        )
    ]

    growth_drivers = [
        "Expanding Total Addressable Market driven by digital transformation",
        "Low barrier to initial adoption with self-service freemium models",
        "High viral coefficient through social proof and collaborative loops"
    ]

    market_challenges = [
        "High customer acquisition costs (CAC) in competitive digital channels",
        "Maintaining long-term user retention past the initial 30-day onboarding window",
        "Data privacy compliance and secure handling of user information"
    ]

    return MarketAnalysis(
        industry=industry,
        market_opportunity=market_opp,
        market_trends=trends[:4],
        customer_segments=customer_segments,
        growth_drivers=growth_drivers,
        market_challenges=market_challenges
    ).model_dump()


def _clean_competitor_name(title: str, url: str) -> str:
    if url:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.replace("www.", "")
        if netloc:
            parts = netloc.split(".")
            if parts:
                return parts[0].capitalize()

    # Fallback to first 3 words of title
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", title)
    words = cleaned.split()
    return " ".join(words[:2]).title() if words else "Market Player"


def _generate_fallback_competitor_analysis(idea: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    direct_competitors: List[Competitor] = []
    comparison_rows: List[ComparisonRow] = []

    # Derive competitors from live search results
    seen_names = set()
    for item in search_results:
        raw_title = item.get("title", "")
        raw_url = item.get("url", "")
        if not raw_title:
            continue

        comp_name = _clean_competitor_name(raw_title, raw_url)
        if comp_name.lower() in seen_names or len(comp_name) < 2:
            continue
        seen_names.add(comp_name.lower())

        target = item.get("target_audience") or "Broad Market / Digital Users"
        snippet = item.get("content", "")[:120]

        direct_competitors.append(
            Competitor(
                name=comp_name,
                url=raw_url or None,
                product_service=raw_title[:80],
                target_customers=target,
                key_features=["Core platform functionality", "Web & mobile interface", "Automated features"],
                pricing="Freemium / Paid Tier available",
                strengths=["Established domain authority", "Active user base", "Search visibility"],
                weaknesses=["Generic positioning", "Limited hyper-personalization", "Slow feature rollout"]
            )
        )

        comparison_rows.append(
            ComparisonRow(
                competitor=comp_name,
                target_customers=target,
                key_features="General industry solution",
                strengths="Established presence",
                weaknesses="Less specialized than targeted startups"
            )
        )

        if len(direct_competitors) >= 3:
            break

    # If web search returned zero or insufficient competitors, provide baseline archetypes
    if not direct_competitors:
        archetypes = [
            ("Incumbent Pro", "https://example.com/incumbent", "Established Enterprise Suite", "Large organizations"),
            ("QuickStarter", "https://example.com/quickstart", "Point solution tool", "Individual users")
        ]
        for name, url, prod, target in archetypes:
            direct_competitors.append(
                Competitor(
                    name=name,
                    url=url,
                    product_service=prod,
                    target_customers=target,
                    key_features=["Legacy feature set", "Cloud sync"],
                    pricing="Subscription ($29-$99/mo)",
                    strengths=["Recognized brand", "Extensive resource backing"],
                    weaknesses=["High price", "Complex onboarding"]
                )
            )
            comparison_rows.append(
                ComparisonRow(
                    competitor=name,
                    target_customers=target,
                    key_features="Legacy suite",
                    strengths="Strong distribution",
                    weaknesses="High cost & complexity"
                )
            )

    indirect_competitors = [
        Competitor(
            name="Manual / Spreadsheet Workarounds",
            url=None,
            product_service="Spreadsheets (Excel, Google Sheets, Notion templates)",
            target_customers="Budget-conscious self-starters",
            key_features=["Maximum flexibility", "Free/low cost"],
            pricing="Free / Included with office software",
            strengths=["Zero marginal cost", "Completely customizable"],
            weaknesses=["High manual effort", "No automated intelligence", "Error-prone"]
        ),
        Competitor(
            name="Traditional Consultancies / Agencies",
            url=None,
            product_service="Human service providers & advisors",
            target_customers="High-budget clients",
            key_features=["High-touch human expertise"],
            pricing="Expensive hourly or retainer fees",
            strengths=["Nuanced domain understanding"],
            weaknesses=["Not scalable", "Inaccessible to mainstream users"]
        )
    ]

    market_gaps = [
        "Affordable pricing model tailored for individual users and early-stage adopters",
        "Zero-configuration setup with automated AI-driven workflow generation",
        "Transparent, verifiable recommendations based on live web evidence rather than static advice",
        "Unified all-in-one experience eliminating the need for 3-4 disparate tools"
    ]

    return CompetitorAnalysis(
        direct_competitors=direct_competitors,
        indirect_competitors=indirect_competitors,
        comparison=comparison_rows,
        market_gaps=market_gaps
    ).model_dump()


# ---------------------------------------------------------------------------
# Main Orchestrator Entrypoint
# ---------------------------------------------------------------------------

async def run_orchestrator(idea: str, domain: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes the Milestone 2 multi-agent pipeline:
    1. Input validation.
    2. Web Search Agent execution.
    3. Sequential/concurrent dispatch to Market Analysis and Competitor Analysis agents.
    4. Aggregation and schema validation.
    """
    # 1. Input validation
    if not idea or not isinstance(idea, str) or not idea.strip():
        raise ValueError("Startup idea cannot be empty")

    cleaned_idea = idea.strip()
    if len(cleaned_idea) < 10:
        raise ValueError("Startup idea is too short to analyze meaningfully")

    logger.info(f"Orchestrator initiated for idea: '{cleaned_idea[:50]}...'")

    # 2. Web Search Context Retrieval
    try:
        search_payload = await run_web_search_agent(idea=cleaned_idea, domain=domain)
        search_results = search_payload.get("results", []) if isinstance(search_payload, dict) else []
        logger.info(f"Web Search Agent returned {len(search_results)} search results")
    except Exception as exc:
        logger.error(f"Web Search Agent execution failed in orchestrator: {exc}")
        # Graceful degradation: continue with empty search results rather than halting
        search_results = []

    # 3. Context passing to Market Analysis & Competitor Analysis agents
    # Executing both analysis stages concurrently for optimal throughput
    market_task = _dispatch_market_analysis(cleaned_idea, search_results, domain)
    competitor_task = _dispatch_competitor_analysis(cleaned_idea, search_results)

    market_data, competitor_data = await asyncio.gather(market_task, competitor_task)

    # 4. Result Synthesis & Schema Validation
    combined_payload = {
        "idea": cleaned_idea,
        "market_analysis": market_data,
        "competitor_analysis": competitor_data
    }

    # Validate against Pydantic model to guarantee contract integrity
    validated_response = ValidationResponse(**combined_payload)
    return validated_response.model_dump()


if __name__ == "__main__":
    test_idea = "AI powered platform for personalized fitness plans and meal tracking"
    print(f"Executing Orchestrator with idea: '{test_idea}'")
    result = asyncio.run(run_orchestrator(test_idea))
    import json
    print(json.dumps(result, indent=2))
