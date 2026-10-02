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

        if isinstance(result, dict):
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

    fallback_market = _generate_fallback_market_analysis(
        idea,
        search_results,
        domain,
    )

    try:
        from server.agents.market_analysis_agent import (
            _generate_heuristic_deep_validation,
            _detect_industry,
        )
        ind = _detect_industry(idea, domain, search_results)
        deep_eval = _generate_heuristic_deep_validation(idea, domain, search_results, ind)
        return {
            "market_analysis": fallback_market,
            "technical_feasibility": deep_eval.get("technical_feasibility"),
            "scientific_validation": deep_eval.get("scientific_validation"),
            "regulatory_risk": deep_eval.get("regulatory_risk"),
            **fallback_market,
        }
    except Exception:
        return {
            "market_analysis": fallback_market,
            **fallback_market,
        }


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
        f"Rapid acceleration of enterprise automation and decision intelligence in {industry}",
        "Increasing preference for turn-key API integration over legacy monolithic software",
        "Growing integration of predictive telemetry and real-time observability",
        "Shift toward unified, multi-vendor interoperable platforms",
    ]

    if snippets:
        trends.insert(
            0,
            f"Recent industry development: {snippets[0][:70]}..."
        )

    customer_segments = [
        CustomerSegment(
            segment="Enterprise Operations & Engineering Leaders",
            needs=[
                "Automated end-to-end workflows with minimal manual configuration",
                "Deterministic SLA guarantees and zero-trust security compliance",
                "Seamless interoperability with legacy infrastructure",
            ],
            pain_points=[
                "High manual overhead and disjointed point solutions",
                "Lack of real-time visibility across heterogeneous environments",
                "Slow incident response times causing costly operational bottlenecks",
            ],
        ),
        CustomerSegment(
            segment="Mid-Market & Specialized Domain Teams",
            needs=[
                "Turn-key onboarding without high upfront engineering overhead",
                "Actionable predictive recommendations with auditable audit trails",
                "Predictable subscription pricing with clear quantifiable ROI",
            ],
            pain_points=[
                "Prohibitive enterprise licensing and inflexible multi-year contracts",
                "Fragmented data silos preventing cross-functional collaboration",
                "Limited internal engineering bandwidth for custom tool building",
            ],
        ),
    ]

    return MarketAnalysis(
        industry=industry,
        market_opportunity=(
            f"Significant commercial opportunity in the {industry} sector driven by accelerating "
            f"demand for automated, high-precision domain platforms with verifiable operational ROI."
        ),
        market_trends=trends[:4],
        customer_segments=customer_segments,
        growth_drivers=[
            f"Urgent enterprise imperative to modernize infrastructure across {industry}",
            "High willingness-to-pay for platforms eliminating costly manual operational overhead",
            "Advancements in edge AI and telemetry protocols enabling real-time optimization",
        ],
        market_challenges=[
            "Switching costs and inertia associated with entrenched legacy systems",
            "Navigating strict regulatory compliance and industry certification requirements",
            "Data integration complexity across heterogeneous customer environments",
        ],
    ).model_dump()


def _clean_competitor_name(
    title: str,
    url: str,
) -> str:
    import urllib.parse

    # 1. URL brand extraction
    if url:
        try:
            parsed = urllib.parse.urlparse(url)
            netloc = parsed.netloc.replace("www.", "").lower()
            parts = netloc.split(".")
            if parts:
                brand = parts[0]
                if brand not in {
                    "medium", "substack", "hubspot", "linkedin", "github", "news",
                    "blog", "app", "docs", "en", "marketsandmarkets", "idtechex",
                    "grandviewresearch", "mordorintelligence", "technavio"
                } and len(brand) >= 3:
                    return brand.capitalize()
        except Exception:
            pass

    # 2. Clean from title
    cleaned = title or ""
    for sep in [" | ", " - ", " – ", " — ", " : ", " • "]:
        if sep in cleaned:
            chunks = cleaned.split(sep)
            for c in chunks:
                c_clean = c.strip()
                words = c_clean.split()
                if 1 <= len(words) <= 3 and not any(
                    k in c_clean.lower() for k in [
                        "how to", "best", "top 10", "review", "pricing", "guide",
                        "overview", "report", "market", "analysis", "vs", "versus"
                    ]
                ):
                    return c_clean

    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", cleaned)
    words = cleaned.split()
    return " ".join(words[:2]).title() if words else "Enterprise Platform"


def _generate_fallback_competitor_analysis(
    idea: str,
    search_results: List[Dict[str, Any]],
) -> Dict[str, Any]:

    direct_competitors: List[Competitor] = []
    comparison_rows: List[ComparisonRow] = []

    seen_names = set()
    blacklist = {
        "marketsandmarkets", "idtechex", "grand view research", "mordor intelligence",
        "technavio", "gartner", "forrester", "substack", "hubspot", "medium", "linkedin"
    }

    for item in search_results:

        raw_title = item.get("title", "")
        raw_url = item.get("url", "")

        if not raw_title:
            continue

        comp_name = _clean_competitor_name(
            raw_title,
            raw_url,
        )

        if comp_name.lower() in seen_names or any(b in comp_name.lower() for b in blacklist):
            continue

        seen_names.add(comp_name.lower())

        target = (
            item.get("target_audience")
            or "Enterprise Operations & Specialized Teams"
        )

        direct_competitors.append(
            Competitor(
                name=comp_name,
                url=raw_url or None,
                product_service=raw_title[:80],
                target_customers=target,
                key_features=[
                    "Enterprise platform integration",
                    "Real-time telemetry and monitoring",
                    "Automated domain workflows",
                ],
                pricing="Enterprise Tier / Custom Quote",
                strengths=[
                    "Established domain market presence",
                    "Broad enterprise distribution network",
                ],
                weaknesses=[
                    "Proprietary vendor lock-in",
                    "Limited sub-second predictive intelligence",
                ],
            )
        )

        comparison_rows.append(
            ComparisonRow(
                competitor=comp_name,
                target_customers=target,
                key_features="Domain platform integration",
                strengths="Established market presence",
                weaknesses="Proprietary vendor lock-in",
            )
        )

        if len(direct_competitors) >= 3:
            break

    if not direct_competitors:
        direct_competitors = [
            Competitor(
                name="Incumbent Industry Platform",
                url=None,
                product_service="Established enterprise platform solution",
                target_customers="Tier-1 Enterprise Organizations",
                key_features=["Core domain workflow engine", "Standard reporting"],
                pricing="High-Tier Enterprise Annual Licensing",
                strengths=["Broad brand recognition", "Legacy customer base"],
                weaknesses=["Rigid architecture and slow feature iteration", "High total cost of ownership"],
            )
        ]

        comparison_rows = [
            ComparisonRow(
                competitor="Incumbent Industry Platform",
                target_customers="Tier-1 Enterprise Organizations",
                key_features="Established enterprise platform solution",
                strengths="Broad brand recognition",
                weaknesses="Rigid architecture and high TCO",
            )
        ]

    indirect_competitors = [
        Competitor(
            name="Manual Spreadsheets & Internal Scripts",
            product_service="In-house custom spreadsheets, cron jobs, and manual logging",
            target_customers="Budget-constrained operational teams",
            key_features=[
                "Zero initial licensing cost",
                "Fully customizable by internal staff",
            ],
            pricing="Zero software license (High hidden labor cost)",
            strengths=[
                "High customization flexibility",
                "Immediate accessibility without vendor approval",
            ],
            weaknesses=[
                "High cognitive overhead and error susceptibility",
                "No real-time automated synchronization or SLA guarantees",
            ],
        ),
        Competitor(
            name="Traditional Management Consultancies",
            product_service="Periodic manual audits, custom advisory, and human consulting",
            target_customers="Large corporate enterprises",
            key_features=[
                "Human domain expertise",
                "Custom boardroom audit presentations",
            ],
            pricing="Hourly / Retainer-based ($200-$500/hr)",
            strengths=[
                "Deep institutional industry expertise",
                "Executive-level strategic alignment",
            ],
            weaknesses=[
                "Prohibitive expense and zero real-time responsiveness",
                "Inability to deliver automated continuous software execution",
            ],
        ),
    ]

    idea_lower = idea.lower()
    if any(k in idea_lower for k in ["cool", "thermal", "datacenter", "liquid", "server"]):
        market_gaps = [
            "Telemetry unification across multi-vendor liquid cooling hardware (Redfish / Modbus / BACnet)",
            "Sub-second predictive thermal throttling prevention during sudden compute spikes",
            "Automated ASHRAE TC 9.9 and EU Energy Efficiency Directive compliance reporting",
            "Failsafe hardware bypass loops preventing thermal shock risk",
        ]
    elif any(k in idea_lower for k in ["agri", "farm", "crop", "drone", "spore", "vineyard"]):
        market_gaps = [
            "Real-time edge computer vision for closed-loop airborne spore detection",
            "Low-power mesh IoT ground telemetry over rolling agricultural terrain",
            "Automated FAA Part 137 and EPA FIFRA aerial dispensing compliance",
            "Precision micro-dosing eliminating blanket chemical pesticide drift",
        ]
    else:
        market_gaps = [
            "Turn-key enterprise API interoperability eliminating proprietary silos",
            "Deterministic real-time optimization with auditable decision trails",
            "Continuous compliance auditing and automated regulatory reporting",
            "Accessible mid-market deployment model with rapid time-to-value",
        ]

    return CompetitorAnalysis(
        direct_competitors=direct_competitors,
        indirect_competitors=indirect_competitors,
        comparison=comparison_rows,
        market_gaps=market_gaps,
    ).model_dump()


async def run_orchestrator(
    idea: str,
    domain: Optional[str] = None,
    audience: Optional[str] = None,
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
            audience=audience,
        )

        search_results = (
            search_payload.get("results", [])
            if isinstance(search_payload, dict)
            else []
        )

        # DIAGNOSTIC: confirm orchestrator uses run_web_search_agent's FINAL output
        _sample_title = search_results[0].get("title", "<no title>") if search_results else "<empty>"
        logger.info(
            f"ORCHESTRATOR-SEARCH-RESULTS | "
            f"count={len(search_results)} | "
            f"sample_title={_sample_title!r} | "
            f"source=run_web_search_agent() final return value"
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

    market_agent_output, competitor_data = await asyncio.gather(
        market_task,
        competitor_task,
    )

    market_data = (
        market_agent_output.get("market_analysis")
        if isinstance(market_agent_output, dict) and "market_analysis" in market_agent_output
        else market_agent_output
    )

    tech_data = (
        market_agent_output.get("technical_feasibility")
        if isinstance(market_agent_output, dict)
        else None
    )

    sci_data = (
        market_agent_output.get("scientific_validation")
        if isinstance(market_agent_output, dict)
        else None
    )

    reg_data = (
        market_agent_output.get("regulatory_risk")
        if isinstance(market_agent_output, dict)
        else None
    )

    validated_response = ValidationResponse(
        idea=cleaned_idea,
        market_analysis=market_data,
        competitor_analysis=competitor_data,
        technical_feasibility=tech_data,
        scientific_validation=sci_data,
        regulatory_risk=reg_data,
        search_results=search_results,
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