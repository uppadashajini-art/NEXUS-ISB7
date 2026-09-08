"""
NEXUS-ISB7 — Market Analysis & Customer Segmentation Agent
Role: Member 2 — Market Opportunity & Customer Segmentation

Analyzes startup ideas to produce:
1. Fine-grained industry classification.
2. Market opportunity sizing narrative with evidence-based reasoning and thin-evidence caveats.
3. Grounded emerging market trends traceable to web search results.
4. Detailed customer segments (personas, functional/emotional needs, acute pain points)
   seeded from Milestone 1 target audience discovery signals.
5. Evidence-grounded growth drivers and critical market challenges.

Guaranteed to conform to server.models.validation.MarketAnalysis.
Includes live Google Gemini synthesis with multi-model fallbacks and a resilient
deterministic heuristic fallback engine when offline or unconfigured.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

import httpx

from server.models.validation import CustomerSegment, MarketAnalysis

logger = logging.getLogger(__name__)

THIN_EVIDENCE_THRESHOLD = 3
THIN_EVIDENCE_NOTE = (
    "[Note: Low search evidence (<3 sources found). "
    "Analysis based primarily on structural industry taxonomy. "
    "Further primary customer discovery recommended.]"
)

INDUSTRY_TAXONOMY = [
    (
        "HealthTech & Digital Health",
        ["health", "fitness", "workout", "gym", "diet", "nutrition", "wellness", "medical", "patient", "clinic", "hospital", "biotech", "mental health", "therapy"]
    ),
    (
        "FinTech & Financial Services",
        ["finance", "fintech", "banking", "crypto", "invest", "payment", "money", "budget", "lending", "credit", "trading", "insurance", "insurtech", "wealth", "tax"]
    ),
    (
        "EdTech & Learning Technology",
        ["education", "edtech", "student", "school", "course", "learn", "lecture", "quiz", "university", "college", "tutor", "training", "academic", "upskilling"]
    ),
    (
        "Logistics & Supply Chain",
        ["logistics", "freight", "courier", "delivery", "shipping", "last-mile", "fleet", "warehouse", "supply chain", "cargo", "transportation", "routing", "inventory"]
    ),
    (
        "CleanTech & Sustainability",
        ["cleantech", "sustainability", "climate", "carbon", "emission", "esg", "energy", "solar", "renewable", "recycle", "waste", "green", "circular economy"]
    ),
    (
        "E-Commerce & RetailTech",
        ["ecommerce", "e-commerce", "retail", "shop", "store", "product", "cart", "checkout", "marketplace", "d2c", "merchant", "inventory"]
    ),
    (
        "Enterprise SaaS & Productivity",
        ["saas", "enterprise", "productivity", "task", "workflow", "collaboration", "crm", "project management", "automation", "b2b", "workplace"]
    ),
    (
        "CyberSecurity & Data Privacy",
        ["security", "cybersecurity", "privacy", "gdpr", "compliance", "fraud", "encryption", "threat", "vulnerability", "auth", "identity", "zero-trust"]
    ),
    (
        "PropTech & Real Estate",
        ["proptech", "real estate", "property", "tenant", "landlord", "lease", "housing", "mortgage", "broker", "facility"]
    ),
    (
        "AgriTech & FoodTech",
        ["agritech", "agriculture", "farming", "crop", "livestock", "foodtech", "restaurant", "recipe", "food delivery", "beverage"]
    ),
    (
        "LegalTech & Regulatory Compliance",
        ["legaltech", "legal", "lawyer", "contract", "compliance", "regulatory", "litigation", "paralegal"]
    ),
    (
        "HRTech & Talent Management",
        ["hr", "hrtech", "recruiting", "hiring", "talent", "payroll", "onboarding", "employee", "staffing", "retention"]
    ),
    (
        "Artificial Intelligence & Automation",
        ["ai", "machine learning", "deep learning", "llm", "agent", "automation", "robotics", "computer vision", "nlp", "bot"]
    ),
]


def _load_env_if_needed() -> None:
    """Load environment variables from .env files if not already set."""
    env_paths = [
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.getcwd(), "server", ".env"),
    ]
    for env_path in env_paths:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip(), v.strip().strip("'\""))
                break
            except Exception:
                pass


def _detect_industry(
    idea: str,
    domain: Optional[str] = None,
    search_results: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Classify the industry from an explicit domain, idea text, and web search snippets.
    """
    if domain and domain.strip():
        dom_clean = domain.strip()
        for ind_name, _ in INDUSTRY_TAXONOMY:
            if dom_clean.lower() in ind_name.lower() or ind_name.lower() in dom_clean.lower():
                return ind_name
        return dom_clean.title()

    combined_text = idea.lower()
    if search_results:
        snippets = " ".join([
            f"{r.get('title', '')} {r.get('content', '')}"
            for r in search_results[:5]
        ]).lower()
        combined_text = f"{combined_text} {snippets}"

    for industry_name, keywords in INDUSTRY_TAXONOMY:
        if any(re.search(rf"\b{re.escape(k)}\b", combined_text) for k in keywords):
            return industry_name

    return "Technology & Digital Services"


def _extract_seed_audiences(search_results: Optional[List[Dict[str, Any]]]) -> List[str]:
    """
    Reuse target audience signals tagged by the Milestone 1 Web Search Agent.
    Deduplicates and filters meaningful customer segment labels.
    """
    if not search_results:
        return []

    seen = set()
    seed_audiences: List[str] = []
    for item in search_results:
        aud = item.get("target_audience")
        if aud and isinstance(aud, str):
            clean_aud = aud.strip()
            if clean_aud and clean_aud.lower() not in seen and len(clean_aud) > 3:
                seen.add(clean_aud.lower())
                seed_audiences.append(clean_aud)

    return seed_audiences


def _build_gemini_prompt(
    idea: str,
    industry: str,
    search_results: Optional[List[Dict[str, Any]]],
    seed_audiences: List[str],
    is_thin_evidence: bool
) -> str:
    """
    Constructs a strictly constrained prompt for Gemini with evidence-grounding guardrails.
    """
    formatted_evidence = []
    if search_results:
        for idx, item in enumerate(search_results[:8], 1):
            formatted_evidence.append({
                "source_id": idx,
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "target_audience": item.get("target_audience", ""),
                "snippet": item.get("content", "")[:350]
            })

    evidence_json = json.dumps(formatted_evidence, indent=2) if formatted_evidence else "No search evidence available."
    seed_audiences_str = ", ".join(seed_audiences) if seed_audiences else "None pre-identified (extract from idea directly)."

    thin_instruction = ""
    if is_thin_evidence:
        thin_instruction = (
            f"\nIMPORTANT THIN-EVIDENCE RULE:\n"
            f"Fewer than {THIN_EVIDENCE_THRESHOLD} search results were retrieved. You MUST explicitly append this "
            f"exact disclaimer at the end of the 'market_opportunity' field:\n"
            f"\"{THIN_EVIDENCE_NOTE}\"\n"
            f"Do NOT invent unsupported confidence or pretend large empirical datasets exist.\n"
        )

    return f"""You are a Principal Market Intelligence Analyst and Startup Customer Persona Strategist.

Analyze the following startup idea and grounded web research evidence to produce a comprehensive, realistic Market Opportunity & Customer Segmentation Report.

STARTUP IDEA:
"{idea}"

IDENTIFIED INDUSTRY:
{industry}

PRE-IDENTIFIED TARGET AUDIENCE SEEDS (from prior search intelligence):
{seed_audiences_str}

RETRIEVED WEB RESEARCH EVIDENCE:
{evidence_json}
{thin_instruction}
STRICT EVIDENCE-GROUNDING & ANTI-HALLUCINATION GUARDRAILS:
1. Every 'market_trend' and 'growth_driver' MUST be directly traceable to specific evidence in the provided search_results whenever evidence is present.
2. DO NOT invent industry-wide statistics, fabricated market size figures ($B/$M), or CAGR percentages that are not explicitly corroborated by the search snippets.
3. NEVER treat general industry growth as proof of customer demand for this specific startup.
4. REUSE & REFINE TARGET AUDIENCE SEEDS: Cluster and expand the pre-identified target audience seeds into 2 to 4 distinct, rich customer segments.
5. For each customer segment, provide concrete, functional and emotional 'needs' (at least 2), and acute, tangible 'pain_points' (at least 2) reflecting current real-world frustrations.
6. Provide realistic 'market_challenges' (at least 2) covering customer inertia, technical complexity, regulatory compliance, or distribution bottlenecks.

OUTPUT FORMAT:
Return ONLY a valid JSON object matching this exact schema:
{{
  "industry": "{industry}",
  "market_opportunity": "A comprehensive, realistic narrative (2-4 sentences) evaluating the commercial potential, addressable customer demand, and adoption trajectory.{' ' + THIN_EVIDENCE_NOTE if is_thin_evidence else ''}",
  "market_trends": [
    "Evidence-backed market trend 1",
    "Evidence-backed market trend 2",
    "Evidence-backed market trend 3"
  ],
  "customer_segments": [
    {{
      "segment": "Specific Persona / Segment Title",
      "needs": [
        "Concrete functional or operational need 1",
        "Concrete functional or operational need 2"
      ],
      "pain_points": [
        "Acute pain point or workflow friction 1",
        "Acute pain point or workflow friction 2"
      ]
    }}
  ],
  "growth_drivers": [
    "Macro or market catalyst 1 directly supported by evidence",
    "Customer adoption driver 2 directly supported by evidence"
  ],
  "market_challenges": [
    "Primary market barrier, friction point, or risk 1",
    "Adoption or retention challenge 2"
  ]
}}
"""


def _generate_heuristic_market_analysis(
    idea: str,
    domain: Optional[str] = None,
    search_results: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Deterministic, robust fallback engine. Produces schema-compliant MarketAnalysis
    when Gemini API is unconfigured, rate-limited, or unreachable.
    """
    industry = _detect_industry(idea, domain, search_results)
    is_thin = not search_results or len(search_results) < THIN_EVIDENCE_THRESHOLD

    # Extract seed audiences or formulate defaults from idea
    seed_audiences = _extract_seed_audiences(search_results)
    primary_audience = seed_audiences[0] if seed_audiences else "Early Adopters & Tech-Forward Professionals"
    secondary_audience = seed_audiences[1] if len(seed_audiences) > 1 else "Operations & Management Teams"

    # Opportunity narrative with honest thin-evidence caveat
    market_opp = (
        f"Significant commercial opportunity in the {industry} sector. "
        f"Increasing customer demand for automated, personalized, and efficient solutions creates a compelling "
        f"adoption runway with high willingness-to-pay for platforms that directly reduce operational friction."
    )
    if is_thin:
        market_opp = f"{market_opp} {THIN_EVIDENCE_NOTE}"

    # Extract grounded trends from search snippets if present
    trends: List[str] = []
    if search_results:
        for r in search_results:
            title = (r.get("title") or "").strip()
            if title and len(title) > 15 and not any(t.lower() == title.lower() for t in trends):
                clean_title = re.sub(r"\s*[-|]\s*[^|]+$", "", title)
                trends.append(f"Industry momentum reflected in recent developments: {clean_title}")
                if len(trends) >= 3:
                    break

    if len(trends) < 3:
        default_trends = [
            f"Rapid acceleration of AI-powered workflows and decision intelligence across {industry}",
            "Increasing end-user preference for proactive, self-service automated interfaces",
            "Transition from fragmented point tools toward unified, interoperable platforms",
            "Rising emphasis on measurable efficiency gains, compliance verification, and transparent ROI"
        ]
        for dt in default_trends:
            if dt not in trends:
                trends.append(dt)
            if len(trends) >= 3:
                break

    # Construct customer segments
    customer_segments = [
        {
            "segment": f"Primary: {primary_audience}",
            "needs": [
                "Automated end-to-end workflows with minimal manual configuration",
                "Context-aware recommendations and reliable real-time feedback",
                "Seamless interoperability with existing tools and habits"
            ],
            "pain_points": [
                "High time expenditure and cognitive friction with legacy manual solutions",
                "Generic one-size-fits-all alternatives that fail to solve specific edge cases",
                "Inconsistent execution and difficulty sustaining long-term outcomes"
            ]
        },
        {
            "segment": f"Secondary: {secondary_audience}",
            "needs": [
                "Centralized visibility, reporting, and verifiable performance metrics",
                "Cost-effective scalability without steep onboarding overhead",
                "Reliable customer support and clear return on investment"
            ],
            "pain_points": [
                "Disjointed software stacks causing data silos and communication breakdowns",
                "Unpredictable operational costs and hidden licensing/vendor fees",
                "Difficulty proving quantifiable efficiency gains to internal stakeholders"
            ]
        }
    ]

    growth_drivers = [
        f"Expanding digital transformation and modernization demand across the {industry} landscape",
        "High economic willingness-to-pay for solutions eliminating repetitive manual overhead",
        "Advancements in AI models enabling high-accuracy personalized experiences at lower inference costs"
    ]

    market_challenges = [
        "Initial customer inertia and resistance to switching away from entrenched legacy workflows",
        "Customer retention and ongoing engagement past the initial 30 to 60 day adoption window",
        "Data integration complexity across heterogeneous third-party environments"
    ]

    return {
        "industry": industry,
        "market_opportunity": market_opp,
        "market_trends": trends,
        "customer_segments": customer_segments,
        "growth_drivers": growth_drivers,
        "market_challenges": market_challenges
    }


def _validate_and_sanitize_gemini_output(
    raw_text: str,
    fallback_data: Dict[str, Any],
    is_thin_evidence: bool
) -> Optional[Dict[str, Any]]:
    """
    Defensively parses and validates Gemini's JSON output against the MarketAnalysis schema.
    Applies the thin-evidence caveat if necessary.
    """
    try:
        text = raw_text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
            text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)

        data = json.loads(text.strip())
        if not isinstance(data, dict):
            return None

        # Enforce thin-evidence honesty caveat if applicable
        opp = str(data.get("market_opportunity", "")).strip()
        if not opp:
            opp = fallback_data["market_opportunity"]
        elif is_thin_evidence and THIN_EVIDENCE_NOTE not in opp:
            opp = f"{opp} {THIN_EVIDENCE_NOTE}"

        # Clean customer segments
        raw_segments = data.get("customer_segments", [])
        clean_segments: List[Dict[str, Any]] = []
        if isinstance(raw_segments, list):
            for s in raw_segments:
                if isinstance(s, dict) and s.get("segment"):
                    clean_segments.append({
                        "segment": str(s.get("segment")).strip(),
                        "needs": [str(n).strip() for n in s.get("needs", []) if str(n).strip()],
                        "pain_points": [str(p).strip() for p in s.get("pain_points", []) if str(p).strip()]
                    })

        if not clean_segments:
            clean_segments = fallback_data["customer_segments"]

        # Validate with strict Pydantic model
        sanitized = {
            "industry": str(data.get("industry") or fallback_data["industry"]).strip(),
            "market_opportunity": opp,
            "market_trends": [str(t).strip() for t in data.get("market_trends", []) if str(t).strip()] or fallback_data["market_trends"],
            "customer_segments": clean_segments,
            "growth_drivers": [str(g).strip() for g in data.get("growth_drivers", []) if str(g).strip()] or fallback_data["growth_drivers"],
            "market_challenges": [str(c).strip() for c in data.get("market_challenges", []) if str(c).strip()] or fallback_data["market_challenges"]
        }

        MarketAnalysis(**sanitized)
        return sanitized

    except Exception as exc:
        logger.warning(f"Error parsing Gemini Market Analysis response: {exc}")
        return None


async def _run_gemini_market_analysis(
    idea: str,
    industry: str,
    search_results: Optional[List[Dict[str, Any]]],
    seed_audiences: List[str],
    is_thin_evidence: bool,
    fallback_data: Dict[str, Any],
    api_key: str
) -> Optional[Dict[str, Any]]:
    """
    Invokes Gemini API with model fallbacks to generate grounded market analysis.
    """
    prompt = _build_gemini_prompt(
        idea=idea,
        industry=industry,
        search_results=search_results,
        seed_audiences=seed_audiences,
        is_thin_evidence=is_thin_evidence
    )

    models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.5-flash-lite"
    ]

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key.strip()}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            raw_text = parts[0].get("text", "")
                            validated = _validate_and_sanitize_gemini_output(
                                raw_text,
                                fallback_data,
                                is_thin_evidence
                            )
                            if validated:
                                return validated
                else:
                    logger.warning(f"Gemini model {model} returned HTTP {resp.status_code}")
        except Exception as exc:
            logger.warning(f"Gemini call to {model} failed: {exc}")
            continue

    return None


async def run_market_analysis_agent(
    idea: str,
    search_results: Optional[List[Dict[str, Any]]] = None,
    domain: Optional[str] = None
) -> Dict[str, Any]:
    """
    Asynchronous Market Opportunity & Customer Segmentation Agent.

    Args:
        idea: The startup idea text submitted by the user.
        search_results: Live web research results from Web Search Agent (Milestone 1).
        domain: Optional user-specified or extracted domain category.

    Returns:
        Dict conforming to server.models.validation.MarketAnalysis:
        {
            "industry": str,
            "market_opportunity": str,
            "market_trends": List[str],
            "customer_segments": List[Dict],
            "growth_drivers": List[str],
            "market_challenges": List[str]
        }
        Guaranteed never to raise unhandled exceptions.
    """
    try:
        _load_env_if_needed()

        clean_idea = (idea or "").strip()
        if not clean_idea:
            clean_idea = "Innovative technology platform"

        results_list = search_results if isinstance(search_results, list) else []
        is_thin_evidence = len(results_list) < THIN_EVIDENCE_THRESHOLD

        # Deterministic industry detection and fallback generation
        industry = _detect_industry(clean_idea, domain, results_list)
        seed_audiences = _extract_seed_audiences(results_list)
        fallback_data = _generate_heuristic_market_analysis(clean_idea, domain, results_list)

        # Attempt Gemini LLM synthesis if API key is present
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key.strip():
            gemini_result = await _run_gemini_market_analysis(
                idea=clean_idea,
                industry=industry,
                search_results=results_list,
                seed_audiences=seed_audiences,
                is_thin_evidence=is_thin_evidence,
                fallback_data=fallback_data,
                api_key=api_key.strip()
            )
            if gemini_result:
                # Provide both wrapper key and flat keys for maximum consumer compatibility
                return {
                    "market_analysis": gemini_result,
                    **gemini_result
                }

        # Return resilient fallback
        return {
            "market_analysis": fallback_data,
            **fallback_data
        }

    except Exception as exc:
        logger.error(f"Unexpected error in run_market_analysis_agent: {exc}", exc_info=True)
        # Ultimate fail-safe matching schema
        safe_fallback = _generate_heuristic_market_analysis(
            idea if isinstance(idea, str) and idea else "Technology startup",
            domain,
            search_results if isinstance(search_results, list) else []
        )
        return {
            "market_analysis": safe_fallback,
            **safe_fallback
        }
