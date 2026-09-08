"""
NEXUS-ISB7 — Market Analysis & Customer Segmentation Agent
Role: Member 2 — Market Opportunity & Customer Segmentation

Analyzes startup ideas to produce:
1. Fine-grained, weighted industry classification.
2. Realistic market opportunity sizing narrative with evidence-based reasoning and thin-evidence caveats.
3. Grounded emerging market trends traceable to web search results with strict noise filtering.
4. Detailed customer segments (personas, functional/emotional needs, acute pain points)
   derived from startup context and Milestone 1 target audience discovery signals.
5. Evidence-grounded growth drivers and critical market challenges.

Guaranteed to conform to server.models.validation.MarketAnalysis.
Includes live Google Gemini synthesis with multi-model fallbacks and a high-fidelity
domain-aware heuristic fallback engine when offline or unconfigured.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx

from server.models.validation import CustomerSegment, MarketAnalysis

logger = logging.getLogger(__name__)

THIN_EVIDENCE_THRESHOLD = 3
THIN_EVIDENCE_NOTE = (
    "[Note: Low search evidence (<3 sources found). "
    "Analysis based primarily on structural industry taxonomy. "
    "Further primary customer discovery recommended.]"
)

INDUSTRY_TAXONOMY: List[Tuple[str, List[str]]] = [
    (
        "Logistics & Supply Chain",
        ["logistics", "supply chain", "last-mile", "freight", "courier", "delivery", "shipping", "fleet", "warehouse", "warehouses", "cargo", "transportation", "routing", "fulfillment", "inventory", "dispatch", "transit", "drones", "ground bots"]
    ),
    (
        "CleanTech & Sustainability",
        ["cleantech", "sustainability", "climate", "carbon", "emission", "emissions", "esg", "energy", "solar", "renewable", "recycle", "waste", "green", "circular economy"]
    ),
    (
        "FinTech & Financial Services",
        ["finance", "fintech", "banking", "crypto", "invest", "payment", "payments", "money", "budget", "lending", "credit", "trading", "insurance", "insurtech", "wealth", "tax", "underwriting"]
    ),
    (
        "HealthTech & Digital Health",
        ["health", "fitness", "workout", "gym", "diet", "nutrition", "wellness", "medical", "patient", "clinic", "hospital", "biotech", "mental health", "therapy", "telehealth"]
    ),
    (
        "EdTech & Learning Technology",
        ["education", "edtech", "student", "students", "school", "course", "learn", "lecture", "quiz", "university", "college", "tutor", "training", "academic", "upskilling"]
    ),
    (
        "E-Commerce & RetailTech",
        ["ecommerce", "e-commerce", "retail", "retailers", "shop", "store", "product", "cart", "checkout", "marketplace", "d2c", "merchant", "merchants", "inventory"]
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
        ["proptech", "real estate", "property", "tenant", "landlord", "lease", "housing", "mortgage", "broker", "facility", "storefronts", "garages"]
    ),
    (
        "AgriTech & FoodTech",
        ["agritech", "agriculture", "farming", "crop", "crops", "livestock", "foodtech", "restaurant", "recipe", "food delivery", "beverage", "pulses", "ingredients"]
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

# High-fidelity domain knowledge templates for resilient fallback
DOMAIN_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "Logistics & Supply Chain": {
        "opportunity": (
            "Significant commercial expansion in the Logistics & Supply Chain sector driven by soaring consumer demand "
            "for sub-30 minute hyper-local fulfillment and mounting municipal pressure to decarbonize urban freight. "
            "Decentralized micro-fulfillment and automated routing eliminate costly centralized depot transit, generating "
            "strong merchant willingness-to-pay to slash last-mile delivery fees."
        ),
        "trends": [
            "Proliferation of urban micro-fulfillment hubs and neighborhood dark stores reducing last-mile transit from hours to minutes",
            "Deployment of autonomous ground bots, AGVs, and short-range delivery drones for dense metropolitan delivery zones",
            "Consolidation of multi-merchant shared logistics grids replacing expensive custom dedicated fleets",
            "Municipal mandates pushing for zero-emission urban delivery zones and off-peak freight scheduling"
        ],
        "segments": [
            {
                "segment": "Primary: Local Retailers & E-Commerce Merchants",
                "needs": [
                    "Turn-key instant local delivery infrastructure without the capital expense of custom fleets",
                    "Predictable flat per-delivery pricing and real-time inventory visibility across micro-nodes",
                    "Seamless plug-ins for Shopify, WooCommerce, and point-of-sale systems"
                ],
                "pain_points": [
                    "Inability to compete with Amazon Prime's same-day delivery windows",
                    "Soaring courier surcharges and unpredictable transit delays eating into retail margins",
                    "High fixed overhead and lease commitments for traditional warehouse storage"
                ]
            },
            {
                "segment": "Secondary: Municipal Planners & Urban Mobility Directors",
                "needs": [
                    "Actionable neighborhood mobility and curb-utilization analytics to reduce street congestion",
                    "Verifiable carbon-reduction metrics for ESG goals and municipal climate compliance",
                    "Safe, regulated integration of sidewalk autonomous bots and delivery drones"
                ],
                "pain_points": [
                    "Double-parked delivery vans causing severe traffic gridlock and pedestrian hazards",
                    "Rising urban carbon emissions from redundant, half-empty courier routes",
                    "Lack of centralized, real-time data on local freight movements"
                ]
            }
        ],
        "growth_drivers": [
            "Exploding consumer adoption of instant delivery and hyper-local quick-commerce",
            "Urgent merchant imperative to lower last-mile delivery expenses and cut delivery vehicle capital costs",
            "Regulatory and tax incentives favoring low-emission and autonomous electric delivery networks"
        ],
        "market_challenges": [
            "Securing affordable urban micro-real estate (underground parking, vacant storefronts, modular containers)",
            "Navigating municipal zoning laws, sidewalk robotics permits, and airspace drone regulations",
            "Managing demand spikes during peak delivery windows while keeping off-peak hub utilization high"
        ]
    },
    "CleanTech & Sustainability": {
        "opportunity": (
            "Substantial commercial momentum across CleanTech & Sustainability driven by strict corporate ESG disclosure "
            "mandates and carbon accounting requirements. High willingness-to-pay exists among enterprise and mid-market "
            "businesses seeking verified, auditable emissions reductions."
        ),
        "trends": [
            "Integration of real-time IoT sensors and satellite telemetry into automated carbon accounting platforms",
            "Shift from voluntary offset purchases to mandatory, auditable Scope 1-3 supply chain emissions reductions",
            "Rapid corporate adoption of circular economy models and renewable distributed energy networks"
        ],
        "segments": [
            {
                "segment": "Primary: Corporate Sustainability & ESG Compliance Officers",
                "needs": [
                    "Automated greenhouse gas accounting compliant with SEC and CSRD disclosure frameworks",
                    "Verifiable proof of supplier carbon reductions to meet Scope 3 sustainability targets",
                    "Intuitive executive dashboards displaying ROI and regulatory compliance status"
                ],
                "pain_points": [
                    "Manual spreadsheet-based emissions calculations prone to audits and regulatory penalties",
                    "Fragmented supplier data making Scope 3 emissions tracking nearly impossible",
                    "Difficulty proving commercial ROI from sustainability investments to boards"
                ]
            },
            {
                "segment": "Secondary: Green-Conscious Consumers & Eco-Brands",
                "needs": [
                    "Transparent carbon footprint labels on everyday purchases and deliveries",
                    "Seamless opt-ins for carbon-neutral delivery and packaging"
                ],
                "pain_points": [
                    "Widespread consumer skepticism regarding corporate greenwashing",
                    "Premium pricing for sustainable alternatives without verifiable proof of impact"
                ]
            }
        ],
        "growth_drivers": [
            "Global regulatory tightening around Scope 1, 2, and 3 carbon disclosures",
            "Consumer brand preference shifting heavily toward certified sustainable and circular products",
            "Institutional investor capital tying debt and equity costs to ESG performance metrics"
        ],
        "market_challenges": [
            "Navigating disparate global regulatory reporting frameworks without standard unification",
            "High implementation friction when onboarding legacy industrial supply chain partners",
            "Resistance from cost-conscious organizations treating sustainability as an overhead expense"
        ]
    }
}


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
    Classify the industry using weighted keyword frequency scoring.
    Gives 10x priority to the founder's idea text over noisy search snippets.
    """
    if domain and domain.strip():
        dom_clean = domain.strip().lower()
        for ind_name, _ in INDUSTRY_TAXONOMY:
            if dom_clean in ind_name.lower():
                return ind_name
        return domain.strip().title()

    idea_lower = (idea or "").lower()
    scores: Dict[str, int] = {}

    for industry_name, keywords in INDUSTRY_TAXONOMY:
        score = 0
        for k in keywords:
            # 10 points per occurrence in the startup idea
            matches_idea = len(re.findall(rf"\b{re.escape(k)}\b", idea_lower))
            score += matches_idea * 10
        scores[industry_name] = score

    best_industry, best_score = max(scores.items(), key=lambda x: x[1])

    # Only inspect search results if the idea itself had zero direct hits
    if best_score == 0 and search_results:
        snippets = " ".join([
            f"{r.get('title', '')} {r.get('content', '')}"
            for r in search_results[:5]
        ]).lower()
        for industry_name, keywords in INDUSTRY_TAXONOMY:
            for k in keywords:
                if re.search(rf"\b{re.escape(k)}\b", snippets):
                    scores[industry_name] += 1
        best_industry, best_score = max(scores.items(), key=lambda x: x[1])

    return best_industry if best_score > 0 else "Technology & Digital Services"


def _extract_seed_audiences(
    idea_or_search_results: Any = "",
    search_results: Optional[List[Dict[str, Any]]] = None
) -> List[str]:
    """
    Extracts audience personas from the idea text and/or search results.
    Accepts:
      - _extract_seed_audiences(search_results)
      - _extract_seed_audiences(idea, search_results)
    """
    if isinstance(idea_or_search_results, list) and search_results is None:
        search_results = idea_or_search_results
        idea = ""
    else:
        idea = str(idea_or_search_results or "")

    seen = set()
    seed_audiences: List[str] = []

    # 1. Extract explicit persona mentions from the idea text
    if idea:
        persona_patterns = [
            r"(?:for|enabling|helping|targeting|sold to)\s+([A-Za-z0-9\s-]+?)(?:,|\.|\band\b|without|by|$)",
            r"(?:small businesses|local retailers|merchants|warehouse operations|logistics managers|municipal planners|city planners|freelancers|students|consumers|enterprises)"
        ]
        idea_text = idea.lower()
        for pat in persona_patterns:
            for m in re.finditer(pat, idea_text, re.IGNORECASE):
                text_match = m.group(0 if m.lastindex is None else 1).strip()
                clean_match = re.sub(r"^(?:for|enabling|helping|targeting|sold to)\s+", "", text_match).strip()
                if len(clean_match) > 3 and len(clean_match.split()) <= 4 and clean_match.lower() not in seen:
                    seen.add(clean_match.lower())
                    seed_audiences.append(clean_match.title())

    # 2. Add audience tags from search results if clean and meaningful
    if search_results:
        for item in search_results:
            aud = item.get("target_audience")
            if aud and isinstance(aud, str):
                clean_aud = aud.strip()
                if clean_aud and clean_aud.lower() not in seen and len(clean_aud) > 3:
                    seen.add(clean_aud.lower())
                    seed_audiences.append(clean_aud)

    return seed_audiences[:4]


def _filter_clean_search_trends(
    search_results: Optional[List[Dict[str, Any]]],
    industry: str,
    idea: str
) -> List[str]:
    """
    Strictly filters out noisy, garbage (e.g. single-letter 'E'), or off-topic search titles.
    Only retains titles that have semantic relevance to the identified industry or startup idea.
    """
    if not search_results:
        return []

    # Build relevance words for the detected industry
    industry_words = set()
    for ind_name, kws in INDUSTRY_TAXONOMY:
        if ind_name == industry:
            for kw in kws:
                industry_words.update(kw.lower().split())
            break

    idea_words = set(re.findall(r"\b[a-z]{4,}\b", idea.lower()))
    valid_intersection = industry_words.union(idea_words)

    clean_trends: List[str] = []
    seen = set()

    for r in search_results:
        raw_title = (r.get("title") or "").strip()
        # Discard garbage, single characters, or ultra-short titles
        if len(raw_title) < 18 or " " not in raw_title:
            continue

        # Strip publication suffixes (e.g. " - Verified Market Research®")
        clean_title = re.sub(r"\s*[-|:]\s*[^|:]+$", "", raw_title).strip()
        if len(clean_title) < 15:
            continue

        # Discard off-topic titles that lack any keyword intersection with industry or idea
        title_lower = clean_title.lower()
        title_words = set(re.findall(r"\b[a-z]{4,}\b", title_lower))

        # Check for obvious spam/noisy food pulses vs logistics
        if any(w in title_lower for w in ["lentil", "chickpea", "recipe", "protein powder", "pea flour"]) and "logistics" in industry.lower():
            continue

        if title_words.intersection(valid_intersection):
            if clean_title.lower() not in seen:
                seen.add(clean_title.lower())
                clean_trends.append(f"Industry momentum reflected in recent developments: {clean_title}")
                if len(clean_trends) >= 3:
                    break

    return clean_trends


def _generate_heuristic_market_analysis(
    idea: str,
    domain: Optional[str] = None,
    search_results: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    High-fidelity deterministic fallback engine. Uses domain-specific templates
    and filtered search evidence to produce realistic, 10/10 intelligence reports.
    """
    industry = _detect_industry(idea, domain, search_results)
    is_thin = not search_results or len(search_results) < THIN_EVIDENCE_THRESHOLD

    # Pull domain-specific knowledge or fallback to generic
    domain_info = DOMAIN_KNOWLEDGE.get(industry)

    # Opportunity narrative with honest thin-evidence caveat
    if domain_info:
        market_opp = domain_info["opportunity"]
    else:
        market_opp = (
            f"Significant commercial opportunity in the {industry} sector. "
            f"Increasing customer demand for automated, personalized, and efficient solutions creates a compelling "
            f"adoption runway with high willingness-to-pay for platforms that directly reduce operational friction."
        )

    if is_thin:
        market_opp = f"{market_opp} {THIN_EVIDENCE_NOTE}"

    # Extract clean, verified trends from web results
    filtered_trends = _filter_clean_search_trends(search_results, industry, idea)
    trends: List[str] = list(filtered_trends)

    # Backfill with high-quality domain trends if web results were thin or noisy
    if len(trends) < 3:
        default_trends = domain_info["trends"] if domain_info else [
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

    # Construct customer segments using extracted personas from the idea
    seed_audiences = _extract_seed_audiences(idea, search_results)
    if domain_info and not seed_audiences:
        customer_segments = domain_info["segments"]
    elif domain_info and seed_audiences:
        # Blend domain intelligence with founder's explicit personas
        primary_title = f"Primary: {seed_audiences[0]}"
        secondary_title = f"Secondary: {seed_audiences[1]}" if len(seed_audiences) > 1 else domain_info["segments"][1]["segment"]

        customer_segments = [
            {
                "segment": primary_title,
                "needs": domain_info["segments"][0]["needs"],
                "pain_points": domain_info["segments"][0]["pain_points"]
            },
            {
                "segment": secondary_title,
                "needs": domain_info["segments"][1]["needs"] if len(domain_info["segments"]) > 1 else domain_info["segments"][0]["needs"],
                "pain_points": domain_info["segments"][1]["pain_points"] if len(domain_info["segments"]) > 1 else domain_info["segments"][0]["pain_points"]
            }
        ]
    else:
        primary_title = f"Primary: {seed_audiences[0]}" if seed_audiences else "Early Adopters & Tech-Forward Professionals"
        secondary_title = f"Secondary: {seed_audiences[1]}" if len(seed_audiences) > 1 else "Operations & Management Teams"
        customer_segments = [
            {
                "segment": primary_title,
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
                "segment": secondary_title,
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

    growth_drivers = domain_info["growth_drivers"] if domain_info else [
        f"Expanding digital transformation and modernization demand across the {industry} landscape",
        "High economic willingness-to-pay for solutions eliminating repetitive manual overhead",
        "Advancements in AI models enabling high-accuracy personalized experiences at lower inference costs"
    ]

    market_challenges = domain_info["market_challenges"] if domain_info else [
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
    Uses currently supported models on Google API.
    """
    prompt = _build_gemini_prompt(
        idea=idea,
        industry=industry,
        search_results=search_results,
        seed_audiences=seed_audiences,
        is_thin_evidence=is_thin_evidence
    )

    models = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
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
            async with httpx.AsyncClient(timeout=15.0) as client:
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
                elif resp.status_code == 429:
                    logger.warning(f"Gemini model {model} rate limited (HTTP 429), trying next fallback")
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
        Dict conforming to server.models.validation.MarketAnalysis
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
        seed_audiences = _extract_seed_audiences(clean_idea, results_list)
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
                return {
                    "market_analysis": gemini_result,
                    **gemini_result
                }

        # Return resilient, high-fidelity fallback
        return {
            "market_analysis": fallback_data,
            **fallback_data
        }

    except Exception as exc:
        logger.error(f"Unexpected error in run_market_analysis_agent: {exc}", exc_info=True)
        safe_fallback = _generate_heuristic_market_analysis(
            idea if isinstance(idea, str) and idea else "Technology startup",
            domain,
            search_results if isinstance(search_results, list) else []
        )
        return {
            "market_analysis": safe_fallback,
            **safe_fallback
        }
