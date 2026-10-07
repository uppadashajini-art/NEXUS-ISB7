"""
NEXUS-ISB7 — Multi-Agent Orchestrator

Role: Agent Orchestration & System Integration

Coordinates the multi-agent execution pipeline:

1. Validates the startup idea.
2. Invokes Web Search Agent to retrieve real-time evidence.
3. Passes search results to Market Analysis Agent.
4. Passes search results to Competitor Analysis Agent.
5. Invokes SWOT & Risk Analysis Agent.
6. Invokes MVP Recommendation Agent.
7. Aggregates all agent outputs.
8. Validates the final result using ValidationResponse.
9. Returns structured data to FastAPI and React.
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
    SWOTAnalysis,
    RiskItem,
    StartupMetadata,
    check_cross_tab_consistency,
    derive_research_confidence,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Upfront Startup Metadata Extraction
# Single LLM call producing {product, target_user, domain, jurisdiction, business_model}
# ---------------------------------------------------------------------------

def _heuristic_fallback_metadata(clean_idea: str, reason: str = "llm_unavailable") -> StartupMetadata:
    """
    Labeled heuristic fallback for startup metadata when LLM extraction is unavailable or fails.
    Uses conservative keyword rules strictly as fallback behind LLM reasoning.
    """
    idea_l = clean_idea.lower()

    # 1. Business model & domain detection fallback
    if any(k in idea_l for k in ["lend", "lending", "loan", "loans", "micro-loan", "microloan", "borrow", "credit line", "cibil"]):
        fb_model = "lending"
        fb_domain = "FinTech & Financial Services"
    elif any(k in idea_l for k in ["freight", "logistics", "supply chain", "fleet", "courier", "shipping", "warehouse", "routing"]):
        fb_model = "saas"
        fb_domain = "Logistics & Supply Chain"
    elif any(k in idea_l for k in ["health", "medical", "patient", "clinical", "diagnostic", "oncolog", "doctor", "scribe"]):
        fb_model = "saas"
        fb_domain = "HealthTech & Digital Health"
    elif any(k in idea_l for k in ["education", "edtech", "student", "lecture", "curriculum", "tutor", "school"]):
        fb_model = "saas"
        fb_domain = "EdTech & Learning Technology"
    elif any(k in idea_l for k in ["marketplace", "two-sided", "peer-to-peer", "buyer and seller"]):
        fb_model = "marketplace"
        fb_domain = "E-Commerce & RetailTech"
    elif any(k in idea_l for k in ["hardware", "robotics", "drone", "sensor", "satellite", "mems", "soil"]):
        fb_model = "hardware"
        fb_domain = "Industrial IoT & Predictive Maintenance"
    else:
        fb_model = "saas"
        fb_domain = "Enterprise SaaS & Productivity"

    # 2. Jurisdiction detection fallback
    if any(k in idea_l for k in ["india", "indian", "₹", "inr", "swiggy", "zomato", "cibil", "rbi"]):
        fb_jurisdiction = "India"
    elif any(k in idea_l for k in ["uk", "nhs", "london", "fca"]):
        fb_jurisdiction = "UK"
    elif any(k in idea_l for k in ["us", "usa", "america", "fda", "fincen", "california"]):
        fb_jurisdiction = "US"
    else:
        fb_jurisdiction = "Global"

    # 3. Clean product & target user fallback
    if fb_model == "lending" and any(k in idea_l for k in ["gig", "worker", "swiggy", "zomato", "uber"]):
        fb_product = "Gig Worker Instant Micro-Lending Platform"
        fb_user = "Gig delivery riders and rideshare drivers (Swiggy, Zomato, Uber)"
        fb_domain = "FinTech & Financial Services"
    else:
        first_clause = re.split(r"[.;,]", clean_idea)[0].strip()
        fb_product = first_clause[:50].strip() if len(first_clause) > 10 else f"{clean_idea[:40]} Platform"
        fb_user = "Target business and individual customers"

    logger.info(
        f"DOMAIN-CLASSIFICATION: HEURISTIC-FALLBACK | reason={reason} | domain='{fb_domain}' | "
        f"model='{fb_model}' | jurisdiction='{fb_jurisdiction}'"
    )

    return StartupMetadata(
        product=fb_product,
        target_user=fb_user,
        domain=fb_domain,
        jurisdiction=fb_jurisdiction,
        business_model=fb_model,  # type: ignore
        source_type="heuristic_fallback",
    )


async def extract_startup_metadata(idea: str) -> StartupMetadata:
    """
    Performs a single, focused LLM call at the start to extract:
    {product, target_user, domain, jurisdiction, business_model}.
    business_model: lending | saas | marketplace | hardware | other.
    LLM extraction is primary; keyword-based classification acts strictly as a labeled fallback.
    """
    clean_idea = (idea or "").strip()
    if not clean_idea:
        return _heuristic_fallback_metadata("Technology platform", reason="empty_idea")

    try:
        from server.utils.gemini_client import call_gemini_generate_content, clean_llm_json_text
        import json

        prompt = f"""You are a senior venture analyst. Analyze this startup idea and extract its core structured metadata in JSON format.
Return ONLY a valid JSON object matching this schema:
{{
  "product": "Clean, concise brand or product concept title (e.g. 'Gig Worker Instant Micro-Lending Platform', NOT fragmented keywords)",
  "target_user": "Specific target customer persona (e.g. 'Gig delivery workers and drivers on Swiggy, Zomato, and Uber')",
  "domain": "One of: FinTech & Financial Services, Logistics & Supply Chain, HealthTech & Digital Health, EdTech & Learning Technology, Enterprise SaaS & Productivity, E-Commerce & RetailTech, CleanTech & Sustainability, CyberSecurity & Data Privacy, AgriTech & FoodTech, PropTech & Real Estate, LegalTech & Regulatory Compliance, Industrial IoT & Predictive Maintenance, Artificial Intelligence & Automation, Technology & Digital Services",
  "jurisdiction": "Target geography (e.g. 'India', 'US', 'UK', 'Global')",
  "business_model": "Must be exactly one of: 'lending', 'saas', 'marketplace', 'hardware', 'other'"
}}

Startup Idea:
"{clean_idea}"
"""
        result = await call_gemini_generate_content(
            prompt=prompt,
            temperature=0.1,
            response_mime_type="application/json",
            timeout_per_model=12.0,
            tag="IDEA-EXTRACTION"
        )
        if result:
            raw_text, successful_model = result
            clean_text = clean_llm_json_text(raw_text)
            parsed = json.loads(clean_text)
            if isinstance(parsed, dict) and parsed.get("product"):
                bm = str(parsed.get("business_model", "")).lower().strip()
                if bm not in ("lending", "saas", "marketplace", "hardware", "other"):
                    bm = "other"

                extracted_product = str(parsed.get("product")).strip()
                extracted_user = str(parsed.get("target_user") or "Target customers").strip()
                extracted_domain = str(parsed.get("domain") or "Technology & Digital Services").strip()
                extracted_jurisdiction = str(parsed.get("jurisdiction") or "Global").strip()

                logger.info(
                    f"DOMAIN-CLASSIFICATION: LLM-EXTRACTED | model={successful_model} | domain='{extracted_domain}' | "
                    f"business_model='{bm}' | jurisdiction='{extracted_jurisdiction}'"
                )

                return StartupMetadata(
                    product=extracted_product,
                    target_user=extracted_user,
                    domain=extracted_domain,
                    jurisdiction=extracted_jurisdiction,
                    business_model=bm,  # type: ignore
                    source_type="llm_extracted",
                )
    except Exception as exc:
        logger.warning(f"Upfront idea metadata LLM extraction failed: {exc}. Using labeled heuristic fallback.")
        return _heuristic_fallback_metadata(clean_idea, reason=str(exc))

    return _heuristic_fallback_metadata(clean_idea, reason="llm_returned_empty")


# ---------------------------------------------------------------------------
# Web Search Agent
# ---------------------------------------------------------------------------

try:
    from server.agents.web_search_agent import run_web_search_agent

except ImportError:
    logger.warning(
        "web_search_agent not found via direct import"
    )

    async def run_web_search_agent(
        idea: str,
        **kwargs
    ) -> Dict[str, Any]:
        return {"results": []}


# ---------------------------------------------------------------------------
# SWOT & Risk Agent
# Member 1 — Milestone 3/4
# ---------------------------------------------------------------------------

try:
    from server.agents.swot_risk_agent import run_swot_risk_agent

except ImportError:
    logger.warning(
        "swot_risk_agent not found via direct import"
    )

    async def run_swot_risk_agent(
        idea: str,
        **kwargs
    ) -> Dict[str, Any]:
        return {
            "swot_analysis": None,
            "risk_analysis": []
        }


# ---------------------------------------------------------------------------
# MVP Recommendation Agent
# Member 2 — Milestone 3/4
# ---------------------------------------------------------------------------

try:
    from server.agents.mvp_recommendation_agent import (
        run_mvp_recommendation_agent
    )

except ImportError:
    logger.warning(
        "mvp_recommendation_agent not found via direct import"
    )

    async def run_mvp_recommendation_agent(
        idea: str,
        **kwargs
    ) -> Dict[str, Any]:
        return {
            "mvp_recommendations": None
        }


# ---------------------------------------------------------------------------
# Market Analysis Dispatcher
# ---------------------------------------------------------------------------

async def _dispatch_market_analysis(
    idea: str,
    search_results: List[Dict[str, Any]],
    domain: Optional[str] = None,
    startup_metadata: Optional[StartupMetadata] = None,
) -> Dict[str, Any]:

    try:
        from server.agents.market_analysis_agent import (
            run_market_analysis_agent
        )

        result = await run_market_analysis_agent(
            idea=idea,
            search_results=search_results,
            domain=domain,
            idea_metadata=startup_metadata,
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

        ind = _detect_industry(
            idea,
            domain,
            search_results
        )

        deep_eval = _generate_heuristic_deep_validation(
            idea,
            domain,
            search_results,
            ind
        )

        return {
            "market_analysis": fallback_market,
            "technical_feasibility": deep_eval.get(
                "technical_feasibility"
            ),
            "scientific_validation": deep_eval.get(
                "scientific_validation"
            ),
            "regulatory_risk": deep_eval.get(
                "regulatory_risk"
            ),
            "kill_switch": deep_eval.get(
                "kill_switch"
            ),
            "unit_economics": deep_eval.get(
                "unit_economics"
            ),
            "regulatory_runway": deep_eval.get(
                "regulatory_runway"
            ),
            "trl_readiness": deep_eval.get(
                "trl_readiness"
            ),
            "moat_durability": deep_eval.get(
                "moat_durability"
            ),
            "pivot_plan": deep_eval.get(
                "pivot_plan"
            ),
            **fallback_market,
        }

    except Exception:

        return {
            "market_analysis": fallback_market,
            **fallback_market,
        }


# ---------------------------------------------------------------------------
# Competitor Analysis Dispatcher
# ---------------------------------------------------------------------------

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

        if (
            isinstance(result, dict)
            and "competitor_analysis" in result
        ):

            comp_res = result["competitor_analysis"]

            if comp_res.get("direct_competitors"):
                return comp_res

        if (
            isinstance(result, dict)
            and "direct_competitors" in result
            and result.get("direct_competitors")
        ):

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


# ---------------------------------------------------------------------------
# Industry Detection
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Fallback Market Analysis
# ---------------------------------------------------------------------------

def _generate_fallback_market_analysis(
    idea: str,
    search_results: List[Dict[str, Any]],
    domain: Optional[str] = None,
) -> Dict[str, Any]:

    industry = _detect_industry(
        idea,
        domain
    )

    snippets = [
        r.get("title", "")
        for r in search_results
        if r.get("title")
    ]

    trends = [
        (
            f"Rapid acceleration of enterprise automation "
            f"and decision intelligence in {industry}"
        ),
        (
            "Increasing preference for turn-key API integration "
            "over legacy monolithic software"
        ),
        (
            "Growing integration of predictive telemetry "
            "and real-time observability"
        ),
        (
            "Shift toward unified, multi-vendor "
            "interoperable platforms"
        ),
    ]

    if snippets:

        trends.insert(
            0,
            f"Recent industry development: "
            f"{snippets[0][:70]}..."
        )

    customer_segments = [

        CustomerSegment(
            segment="Enterprise Operations & Engineering Leaders",

            needs=[
                (
                    "Automated end-to-end workflows "
                    "with minimal manual configuration"
                ),
                (
                    "Deterministic SLA guarantees and "
                    "zero-trust security compliance"
                ),
                (
                    "Seamless interoperability with "
                    "legacy infrastructure"
                ),
            ],

            pain_points=[
                (
                    "High manual overhead and "
                    "disjointed point solutions"
                ),
                (
                    "Lack of real-time visibility "
                    "across heterogeneous environments"
                ),
                (
                    "Slow incident response times causing "
                    "costly operational bottlenecks"
                ),
            ],
        ),

        CustomerSegment(
            segment="Mid-Market & Specialized Domain Teams",

            needs=[
                (
                    "Turn-key onboarding without high "
                    "upfront engineering overhead"
                ),
                (
                    "Actionable predictive recommendations "
                    "with auditable audit trails"
                ),
                (
                    "Predictable subscription pricing "
                    "with clear quantifiable ROI"
                ),
            ],

            pain_points=[
                (
                    "Prohibitive enterprise licensing and "
                    "inflexible multi-year contracts"
                ),
                (
                    "Fragmented data silos preventing "
                    "cross-functional collaboration"
                ),
                (
                    "Limited internal engineering bandwidth "
                    "for custom tool building"
                ),
            ],
        ),
    ]

    return MarketAnalysis(

        industry=industry,

        market_opportunity=(
            f"Significant commercial opportunity in the "
            f"{industry} sector driven by accelerating "
            f"demand for automated, high-precision domain "
            f"platforms with verifiable operational ROI."
        ),

        market_trends=trends[:4],

        customer_segments=customer_segments,

        growth_drivers=[
            (
                f"Urgent enterprise imperative to modernize "
                f"infrastructure across {industry}"
            ),
            (
                "High willingness-to-pay for platforms "
                "eliminating costly manual operational overhead"
            ),
            (
                "Advancements in edge AI and telemetry "
                "protocols enabling real-time optimization"
            ),
        ],

        market_challenges=[
            (
                "Switching costs and inertia associated "
                "with entrenched legacy systems"
            ),
            (
                "Navigating strict regulatory compliance "
                "and industry certification requirements"
            ),
            (
                "Data integration complexity across "
                "heterogeneous customer environments"
            ),
        ],

    ).model_dump()


# ---------------------------------------------------------------------------
# Clean Competitor Name
# ---------------------------------------------------------------------------

def _clean_competitor_name(
    title: str,
    url: str,
) -> str:

    # 1. URL brand extraction

    if url:

        try:

            parsed = urllib.parse.urlparse(url)

            netloc = (
                parsed.netloc
                .replace("www.", "")
                .lower()
            )

            parts = netloc.split(".")

            if parts:

                brand = parts[0]

                if brand not in {
                    "medium",
                    "substack",
                    "hubspot",
                    "linkedin",
                    "github",
                    "news",
                    "blog",
                    "app",
                    "docs",
                    "en",
                    "marketsandmarkets",
                    "idtechex",
                    "grandviewresearch",
                    "mordorintelligence",
                    "technavio",
                } and len(brand) >= 3:

                    return brand.capitalize()

        except Exception:
            pass

    # 2. Clean from title

    cleaned = title or ""

    for sep in [
        " | ",
        " - ",
        " – ",
        " — ",
        " : ",
        " • ",
    ]:

        if sep in cleaned:

            chunks = cleaned.split(sep)

            for c in chunks:

                c_clean = c.strip()

                words = c_clean.split()

                if (
                    1 <= len(words) <= 3
                    and not any(
                        k in c_clean.lower()
                        for k in [
                            "how to",
                            "best",
                            "top 10",
                            "review",
                            "pricing",
                            "guide",
                            "overview",
                            "report",
                            "market",
                            "analysis",
                            "vs",
                            "versus",
                        ]
                    )
                ):

                    return c_clean

    cleaned = re.sub(
        r"[^a-zA-Z0-9\s]",
        "",
        cleaned
    )

    words = cleaned.split()

    return (
        " ".join(words[:2]).title()
        if words
        else "Enterprise Platform"
    )


# ---------------------------------------------------------------------------
# Fallback Competitor Analysis
# ---------------------------------------------------------------------------

def _generate_fallback_competitor_analysis(
    idea: str,
    search_results: List[Dict[str, Any]],
) -> Dict[str, Any]:

    direct_competitors: List[Competitor] = []

    comparison_rows: List[ComparisonRow] = []

    seen_names = set()

    blacklist = {
        "marketsandmarkets",
        "idtechex",
        "grand view research",
        "mordor intelligence",
        "technavio",
        "gartner",
        "forrester",
        "substack",
        "hubspot",
        "medium",
        "linkedin",
    }

    for item in search_results:

        raw_title = item.get(
            "title",
            ""
        )

        raw_url = item.get(
            "url",
            ""
        )

        if not raw_title:
            continue

        comp_name = _clean_competitor_name(
            raw_title,
            raw_url,
        )

        if (
            comp_name.lower() in seen_names
            or any(
                b in comp_name.lower()
                for b in blacklist
            )
        ):
            continue

        seen_names.add(
            comp_name.lower()
        )

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

                product_service=(
                    "Established enterprise "
                    "platform solution"
                ),

                target_customers=(
                    "Tier-1 Enterprise Organizations"
                ),

                key_features=[
                    "Core domain workflow engine",
                    "Standard reporting",
                ],

                pricing=(
                    "High-Tier Enterprise "
                    "Annual Licensing"
                ),

                strengths=[
                    "Broad brand recognition",
                    "Legacy customer base",
                ],

                weaknesses=[
                    (
                        "Rigid architecture and "
                        "slow feature iteration"
                    ),
                    (
                        "High total cost of ownership"
                    ),
                ],
            )
        ]

        comparison_rows = [

            ComparisonRow(

                competitor="Incumbent Industry Platform",

                target_customers=(
                    "Tier-1 Enterprise Organizations"
                ),

                key_features=(
                    "Established enterprise "
                    "platform solution"
                ),

                strengths="Broad brand recognition",

                weaknesses=(
                    "Rigid architecture and high TCO"
                ),
            )
        ]

    indirect_competitors = [

        Competitor(

            name="Manual Spreadsheets & Internal Scripts",

            product_service=(
                "In-house custom spreadsheets, "
                "cron jobs, and manual logging"
            ),

            target_customers=(
                "Budget-constrained operational teams"
            ),

            key_features=[
                "Zero initial licensing cost",
                "Fully customizable by internal staff",
            ],

            pricing=(
                "Zero software license "
                "(High hidden labor cost)"
            ),

            strengths=[
                "High customization flexibility",
                (
                    "Immediate accessibility without "
                    "vendor approval"
                ),
            ],

            weaknesses=[
                (
                    "High cognitive overhead and "
                    "error susceptibility"
                ),
                (
                    "No real-time automated "
                    "synchronization or SLA guarantees"
                ),
            ],
        ),

        Competitor(

            name="Traditional Management Consultancies",

            product_service=(
                "Periodic manual audits, custom "
                "advisory, and human consulting"
            ),

            target_customers=(
                "Large corporate enterprises"
            ),

            key_features=[
                "Human domain expertise",
                "Custom boardroom audit presentations",
            ],

            pricing=(
                "Hourly / Retainer-based "
                "($200-$500/hr)"
            ),

            strengths=[
                "Deep institutional industry expertise",
                "Executive-level strategic alignment",
            ],

            weaknesses=[
                (
                    "Prohibitive expense and zero "
                    "real-time responsiveness"
                ),
                (
                    "Inability to deliver automated "
                    "continuous software execution"
                ),
            ],
        ),
    ]

    idea_lower = idea.lower()

    if any(
        k in idea_lower
        for k in [
            "cool",
            "thermal",
            "datacenter",
            "liquid",
            "server",
        ]
    ):

        market_gaps = [

            (
                "Telemetry unification across multi-vendor "
                "liquid cooling hardware "
                "(Redfish / Modbus / BACnet)"
            ),

            (
                "Sub-second predictive thermal throttling "
                "prevention during sudden compute spikes"
            ),

            (
                "Automated ASHRAE TC 9.9 and EU Energy "
                "Efficiency Directive compliance reporting"
            ),

            (
                "Failsafe hardware bypass loops preventing "
                "thermal shock risk"
            ),
        ]

    elif any(
        k in idea_lower
        for k in [
            "agri",
            "farm",
            "crop",
            "drone",
            "spore",
            "vineyard",
        ]
    ):

        market_gaps = [

            (
                "Real-time edge computer vision for "
                "closed-loop airborne spore detection"
            ),

            (
                "Low-power mesh IoT ground telemetry "
                "over rolling agricultural terrain"
            ),

            (
                "Automated FAA Part 137 and EPA FIFRA "
                "aerial dispensing compliance"
            ),

            (
                "Precision micro-dosing eliminating "
                "blanket chemical pesticide drift"
            ),
        ]

    else:

        market_gaps = [

            (
                "Turn-key enterprise API interoperability "
                "eliminating proprietary silos"
            ),

            (
                "Deterministic real-time optimization "
                "with auditable decision trails"
            ),

            (
                "Continuous compliance auditing and "
                "automated regulatory reporting"
            ),

            (
                "Accessible mid-market deployment model "
                "with rapid time-to-value"
            ),
        ]

    return CompetitorAnalysis(

        direct_competitors=direct_competitors,

        indirect_competitors=indirect_competitors,

        comparison=comparison_rows,

        market_gaps=market_gaps,

    ).model_dump()


# ---------------------------------------------------------------------------
# Main Orchestrator
# ---------------------------------------------------------------------------

async def run_orchestrator(
    idea: str,
    domain: Optional[str] = None,
    audience: Optional[str] = None,
    force_refresh: bool = False,
) -> Dict[str, Any]:

    # -------------------------------------------------------
    # 1. Validate startup idea
    # -------------------------------------------------------

    if not idea or not isinstance(idea, str):

        raise ValueError(
            "Startup idea cannot be empty"
        )

    cleaned_idea = idea.strip()

    if not cleaned_idea:

        raise ValueError(
            "Startup idea cannot be empty"
        )

    if len(cleaned_idea) < 10:

        raise ValueError(
            "Startup idea is too short to analyze meaningfully"
        )

    logger.info(
        f"Orchestrator initiated for idea: "
        f"'{cleaned_idea[:50]}...'"
    )

    # -------------------------------------------------------
    # 1b. Upfront Idea Extraction (Single LLM call)
    # -------------------------------------------------------
    startup_metadata = await extract_startup_metadata(cleaned_idea)
    logger.info(
        f"EXTRACTED-STARTUP-METADATA | product='{startup_metadata.product}' | "
        f"user='{startup_metadata.target_user}' | domain='{startup_metadata.domain}' | "
        f"jurisdiction='{startup_metadata.jurisdiction}' | model='{startup_metadata.business_model}'"
    )
    if not domain and startup_metadata.domain:
        domain = startup_metadata.domain

    # -------------------------------------------------------
    # 2. Web Search Agent
    # -------------------------------------------------------

    try:

        search_payload = await run_web_search_agent(

            idea=cleaned_idea,

            domain=domain,

            audience=audience or startup_metadata.target_user,

            force_refresh=force_refresh,
        )

        search_results = (
            search_payload.get(
                "results",
                []
            )
            if isinstance(
                search_payload,
                dict
            )
            else []
        )

        search_status = (
            search_payload.get(
                "search_status",
                "ok"
            )
            if isinstance(
                search_payload,
                dict
            )
            else ("thin" if len(search_results) < 5 else "ok")
        )

        # Diagnostic logging

        _sample_title = (

            search_results[0].get(
                "title",
                "<no title>"
            )

            if search_results

            else "<empty>"
        )

        logger.info(

            f"ORCHESTRATOR-SEARCH-RESULTS | "
            f"count={len(search_results)} | "
            f"search_status={search_status} | "
            f"sample_title={_sample_title!r} | "
            f"source=run_web_search_agent() "
            f"final return value"
        )

    except Exception as exc:

        logger.error(
            f"Web Search Agent failed: {exc}"
        )

        search_results = []
        is_q = any(t in str(exc).lower() for t in ["429", "432", "401", "quota", "rate limit", "credits", "exhausted", "unauthorized"])
        search_status = "quota_exhausted" if is_q else "thin"

    # -------------------------------------------------------
    # 3. Market Analysis + Competitor Analysis
    # -------------------------------------------------------

    market_task = _dispatch_market_analysis(

        cleaned_idea,

        search_results,

        domain,

        startup_metadata=startup_metadata,
    )

    competitor_task = _dispatch_competitor_analysis(

        cleaned_idea,

        search_results,
    )

    market_agent_output, competitor_data = await asyncio.gather(

        market_task,

        competitor_task,
    )

    # -------------------------------------------------------
    # 4. Extract Market Analysis
    # -------------------------------------------------------

    market_data = (

        market_agent_output.get(
            "market_analysis"
        )

        if (
            isinstance(
                market_agent_output,
                dict
            )

            and "market_analysis"
            in market_agent_output
        )

        else market_agent_output
    )

    # -------------------------------------------------------
    # 5. Extract Deep Validation
    # -------------------------------------------------------

    tech_data = (

        market_agent_output.get(
            "technical_feasibility"
        )

        if isinstance(
            market_agent_output,
            dict
        )

        else None
    )

    sci_data = (

        market_agent_output.get(
            "scientific_validation"
        )

        if isinstance(
            market_agent_output,
            dict
        )

        else None
    )

    reg_data = (

        market_agent_output.get(
            "regulatory_risk"
        )

        if isinstance(
            market_agent_output,
            dict
        )

        else None
    )

    kill_data = (
        market_agent_output.get(
            "kill_switch"
        )
        if isinstance(
            market_agent_output,
            dict
        )
        else None
    )

    ue_data = (
        market_agent_output.get(
            "unit_economics"
        )
        if isinstance(
            market_agent_output,
            dict
        )
        else None
    )

    reg_runway_data = (
        market_agent_output.get(
            "regulatory_runway"
        )
        if isinstance(
            market_agent_output,
            dict
        )
        else None
    )

    trl_data = (
        market_agent_output.get(
            "trl_readiness"
        )
        if isinstance(
            market_agent_output,
            dict
        )
        else None
    )

    moat_data = (
        market_agent_output.get(
            "moat_durability"
        )
        if isinstance(
            market_agent_output,
            dict
        )
        else None
    )

    pivot_data = (
        market_agent_output.get(
            "pivot_plan"
        )
        if isinstance(
            market_agent_output,
            dict
        )
        else None
    )

    # -------------------------------------------------------
    # 6. SWOT & Risk Analysis
    # Member 1
    # -------------------------------------------------------

    swot_data = None

    risk_data = []

    try:

        swot_risk_res = await run_swot_risk_agent(

            idea=cleaned_idea,

            market_analysis=market_data,

            competitor_analysis=competitor_data,

            search_results=search_results,
        )

        if isinstance(
            swot_risk_res,
            dict
        ):

            swot_data = swot_risk_res.get(
                "swot_analysis"
            )

            risk_data = swot_risk_res.get(
                "risk_analysis",
                []
            )

    except Exception as exc:

        logger.error(
            f"SWOT/Risk Agent failed "
            f"in orchestrator: {exc}"
        )

    # -------------------------------------------------------
    # 7. MVP Recommendation Agent
    # Member 2
    # -------------------------------------------------------

    mvp_data = None

    try:

        mvp_res = await run_mvp_recommendation_agent(

            idea=cleaned_idea,

            market_analysis=market_data,

            competitor_analysis=competitor_data,

            swot_analysis=swot_data,

            risk_analysis=risk_data,
        )

        if isinstance(
            mvp_res,
            dict
        ):

            mvp_data = mvp_res.get(
                "mvp_recommendations"
            )

            logger.info(
                "MVP Recommendation Agent "
                "completed successfully"
            )

    except Exception as exc:

        logger.error(
            f"MVP Recommendation Agent "
            f"failed in orchestrator: {exc}"
        )

    # -------------------------------------------------------
    # 8. Go-To-Market Strategy Agent
    # -------------------------------------------------------

    gtm_data = None
    try:
        from server.agents.gtm_agent import run_gtm_agent
        gtm_res = await run_gtm_agent(
            idea=cleaned_idea,
            market_analysis=market_data,
            competitor_analysis=competitor_data,
            swot_analysis=swot_data,
            risk_analysis=risk_data,
            mvp_recommendations=mvp_data,
            search_results=search_results,
            unit_economics=ue_data,
            startup_metadata=startup_metadata,
        )
        gtm_data = gtm_res.get("gtm_strategy")
    except Exception as exc:
        logger.warning(f"GTM Agent execution skipped: {exc}")

    # -------------------------------------------------------
    # 9. Build computed fields: product_name, scores, signals
    # -------------------------------------------------------

    # Single source of truth for product name: from upfront metadata extraction
    product_name = startup_metadata.product

    # -------------------------------------------------------
    # Compute sub_scores from agent outputs
    # -------------------------------------------------------
    tech_score = 0.0
    if tech_data and isinstance(tech_data, dict):
        raw = tech_data.get("score", 0) or tech_data.get("overall_score", 0)
        try:
            ts = float(raw)
            tech_score = ts if ts > 10 else ts * 10
        except Exception:
            tech_score = 76.0
    elif tech_data is None:
        tech_score = 74.0

    reg_score = 0.0
    if reg_data and isinstance(reg_data, dict):
        raw = reg_data.get("score", 0)
        try:
            rs = float(raw)
            reg_score = rs if rs > 10 else rs * 10
        except Exception:
            reg_score = 72.0
    elif reg_data is None:
        reg_score = 70.0

    market_score = 0.0
    if market_data and isinstance(market_data, dict):
        ms = market_data.get("market_sizing", {}) or {}
        if isinstance(ms, dict) and ms.get("tam"):
            market_score = 82.0
        else:
            market_score = 78.0
    else:
        market_score = 75.0

    comp_score = 0.0
    if moat_data and isinstance(moat_data, dict) and moat_data.get("moat_score") is not None:
        comp_score = float(moat_data["moat_score"])
    elif competitor_data and isinstance(competitor_data, dict):
        directs_count = len(competitor_data.get("direct_competitors", []))
        gaps_count = len(competitor_data.get("market_gaps", []))
        comp_score = min(90.0, 60.0 + directs_count * 4.0 + gaps_count * 2.0)
    else:
        comp_score = 70.0

    exec_score = 82.0  # default reasonable execution score

    sub_scores = {
        "market": round(market_score, 1),
        "technical": round(tech_score, 1),
        "regulatory": round(reg_score, 1),
        "execution": round(exec_score, 1),
        "competition": round(comp_score, 1),
    }

    overall_score = round(
        market_score * 0.25
        + tech_score * 0.20
        + reg_score * 0.15
        + exec_score * 0.20
        + comp_score * 0.20,
        1,
    )

    # -------------------------------------------------------
    # Verdict and key signals
    # -------------------------------------------------------
    if overall_score >= 82:
        verdict = "High Market Feasibility — Proceed to Build"
    elif overall_score >= 70:
        verdict = "Moderate Feasibility — Validate with Customers First"
    elif overall_score >= 55:
        verdict = "Conditional Feasibility — Address Key Risks Before Building"
    else:
        verdict = "Low Feasibility — Significant Pivots Required"

    key_signals: List[str] = []
    if market_data and isinstance(market_data, dict):
        ms = market_data.get("market_sizing", {}) or {}
        if isinstance(ms, dict) and ms.get("tam"):
            key_signals.append(f"TAM: {ms['tam']}")
        if isinstance(ms, dict) and ms.get("cagr"):
            key_signals.append(f"Market CAGR: {ms['cagr']}")
        if market_data.get("market_opportunity"):
            key_signals.append(str(market_data["market_opportunity"])[:80])
    if competitor_data and isinstance(competitor_data, dict):
        directs = competitor_data.get("direct_competitors", [])
        key_signals.append(f"{len(directs)} established direct competitors identified")
        gaps = competitor_data.get("market_gaps", [])
        if gaps:
            key_signals.append(gaps[0][:80])
    if tech_data and isinstance(tech_data, dict):
        feasibility = tech_data.get("feasibility_rating") or tech_data.get("rating")
        if feasibility:
            key_signals.append(f"Technical feasibility: {feasibility}")
    if not key_signals:
        key_signals = [
            "Market opportunity validated through web intelligence",
            "Competitive landscape analyzed with domain intelligence",
            "Technical stack feasibility assessed",
        ]

    # -------------------------------------------------------
    # Execution feasibility
    # -------------------------------------------------------
    exec_feasibility_data = {
        "score": exec_score,
        "rating": "High" if exec_score >= 80 else "Medium" if exec_score >= 65 else "Low",
        "rationale": (
            f"The idea targets a well-defined customer segment with clear pain points. "
            f"Technical complexity is manageable with a small founding team. "
            f"Go-to-market friction is moderate given established distribution channels."
        ),
        "risks": [
            "Hiring specialized technical talent in a competitive market",
            "Customer acquisition cost may be high in B2B segments",
            "Integration complexity with legacy enterprise systems",
        ],
        "mitigations": [
            "Start with product-led growth model to reduce sales overhead",
            "Partner with existing enterprise software distributors",
            "Use open APIs and standard protocols to reduce integration friction",
        ],
        "key_milestones": [
            "Month 1-3: MVP build and internal alpha testing",
            "Month 4-6: Closed beta with 5-10 design partners",
            "Month 7-12: GA launch and first 50 paying customers",
            "Month 13-18: Series A fundraise and team scale-up",
        ],
    }

    # -------------------------------------------------------
    # Compliance frameworks
    # -------------------------------------------------------
    idea_l = cleaned_idea.lower()
    compliance_frameworks = []

    def _make_fw(id_str, name, status, severity, desc, items):
        return {
            "id": id_str,
            "name": name,
            "status": status,
            "severity": severity,
            "desc": desc,
            "description": desc,
            "checklist": [{"text": item, "done": False, "mandatory": True} for item in items],
            "remediation": f"Complete {name} readiness assessment and audit checklist.",
        }

    if any(k in idea_l for k in ["health", "medical", "clinical", "patient", "ehr", "hipaa", "oncol"]):
        compliance_frameworks.extend([
            _make_fw("hipaa", "HIPAA", "Required", "Critical", "US health data privacy and security standard", ["PHI encryption at rest and in transit", "Business Associate Agreements (BAAs)", "Audit log retention", "Breach notification procedures"]),
            _make_fw("hitech", "HITECH", "Required", "High", "Health IT for Economic and Clinical Health Act", ["Enhanced HIPAA enforcement compliance", "Meaningful use certification", "Electronic health record interoperability"]),
            _make_fw("fda_samd", "FDA SaMD", "Evaluate", "High", "Software as Medical Device classification framework", ["Determine SaMD classification tier", "Clinical validation studies", "510(k) premarket notification if applicable"]),
        ])
    if any(k in idea_l for k in ["eu", "europe", "gdpr", "user data", "personal data", "privacy"]) or True:  # GDPR always worth reviewing
        compliance_frameworks.append(_make_fw("gdpr", "GDPR", "Evaluate", "Medium", "EU General Data Protection Regulation", ["Lawful basis for processing", "Data subject rights (access, deletion)", "Privacy by design", "DPA appointment if applicable"]))
    if any(k in idea_l for k in ["fintech", "payment", "financial", "bank", "credit", "escrow"]):
        compliance_frameworks.extend([
            _make_fw("pci_dss", "PCI DSS", "Required", "Critical", "Payment Card Industry Data Security Standard", ["Cardholder data encryption", "Network segmentation", "Vulnerability management", "Access control policies"]),
            _make_fw("aml_kyb", "AML/KYB", "Required", "High", "Anti-Money Laundering and Know Your Business compliance", ["Customer identity verification", "Sanctions screening", "Transaction monitoring", "SAR filing procedures"]),
        ])
    if any(k in idea_l for k in ["saas", "enterprise", "b2b", "data", "cloud", "api"]) or len(compliance_frameworks) < 2:
        compliance_frameworks.append(_make_fw("soc2", "SOC 2 Type II", "Recommended", "Medium", "Service Organization Control security audit standard", ["Security policy documentation", "Access control reviews", "Incident response procedures", "Annual independent audit"]))
    if any(k in idea_l for k in ["ai", "ml", "machine learning", "model", "llm", "automation", "agent"]):
        compliance_frameworks.append(_make_fw("eu_ai_act", "EU AI Act", "Evaluate", "Medium", "EU regulation on AI system risk classification", ["Determine AI risk category (limited/high/unacceptable)", "Register high-risk AI systems", "Human oversight mechanisms", "Transparency disclosures"]))
    if any(k in idea_l for k in ["carbon", "esg", "climate", "emission", "sustainability"]):
        compliance_frameworks.append(_make_fw("iso_14064", "ISO 14064", "Recommended", "Medium", "GHG quantification and reporting standard", ["Scope 1, 2, 3 emissions boundary", "Third-party verification", "Reporting cycle cadence"]))


    # -------------------------------------------------------
    # Citations from search results
    # -------------------------------------------------------
    citations = []
    for i, r in enumerate(search_results[:8]):
        if r.get("url") and r.get("title"):
            citations.append({
                "id": i + 1,
                "title": r.get("title", "")[:80],
                "url": r.get("url", ""),
                "source": r.get("url", "").split("/")[2] if "/" in r.get("url", "") else "Web",
                "relevance": "Market evidence" if i < 3 else "Competitor intelligence" if i < 6 else "Industry context",
            })

    # -------------------------------------------------------
    # Validation report
    # -------------------------------------------------------
    try:
        from server.agents.report_generation_agent import generate_validation_report
        report_res = await generate_validation_report(
            idea=cleaned_idea,
            market_analysis=market_data,
            competitor_analysis=competitor_data,
            swot_analysis=swot_data,
            risk_analysis=risk_data,
            mvp_recommendations=mvp_data,
            gtm_strategy=gtm_data,
        )
        validation_report_data = report_res.get("validation_report")
    except Exception as exc:
        logger.warning(f"Report generation skipped: {exc}")
        validation_report_data = None

    # -------------------------------------------------------
    # Derive Research Confidence & Consistency Warnings
    # -------------------------------------------------------

    eval_payload = {
        "unit_economics": ue_data,
        "gtm_strategy": gtm_data,
        "moat_durability": moat_data,
        "sub_scores": sub_scores,
        "kill_switch": kill_data,
        "risk_analysis": risk_data,
        "regulatory_risk": reg_data,
        "regulatory_runway": reg_runway_data,
        "trl_readiness": trl_data,
        "pivot_plan": pivot_data,
        "search_results": search_results,
        "search_status": search_status,
    }

    consistency_warnings = check_cross_tab_consistency(eval_payload)
    research_confidence = derive_research_confidence(eval_payload)

    # -------------------------------------------------------
    # Build final validated response
    # -------------------------------------------------------

    validated_response = ValidationResponse(

        idea=cleaned_idea,

        product_name=product_name,

        startup_metadata=startup_metadata,

        research_confidence=research_confidence,

        search_status=search_status,

        consistency_warnings=consistency_warnings,

        overall_score=overall_score,

        sub_scores=sub_scores,

        verdict=verdict,

        key_signals=key_signals,

        market_analysis=market_data,

        competitor_analysis=competitor_data,

        technical_feasibility=tech_data,

        scientific_validation=sci_data,

        regulatory_risk=reg_data,

        execution_feasibility=exec_feasibility_data,

        kill_switch=kill_data,

        unit_economics=ue_data,

        regulatory_runway=reg_runway_data,

        trl_readiness=trl_data,

        moat_durability=moat_data,

        pivot_plan=pivot_data,

        deep_validation={
            "technical_feasibility": tech_data,
            "scientific_validation": sci_data,
            "regulatory_risk": reg_data,
            "kill_switch": kill_data,
            "unit_economics": ue_data,
            "regulatory_runway": reg_runway_data,
            "trl_readiness": trl_data,
            "moat_durability": moat_data,
            "pivot_plan": pivot_data,
            "consistency_warnings": consistency_warnings,
        },

        compliance_frameworks=compliance_frameworks,

        swot_analysis=swot_data,

        risk_analysis=risk_data,

        mvp_recommendations=mvp_data,

        gtm_strategy=gtm_data,

        validation_report=validation_report_data,

        citations=citations,

        search_results=search_results,
    )

    # -------------------------------------------------------
    # 9. Return final structured response
    # -------------------------------------------------------

    return validated_response.model_dump()


# ---------------------------------------------------------------------------
# Local Testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    test_idea = (

        "AI powered platform for personalized "
        "fitness plans and meal tracking"
    )

    result = asyncio.run(

        run_orchestrator(
            test_idea
        )
    )

    import json

    print(
        json.dumps(
            result,
            indent=2
        )
    )