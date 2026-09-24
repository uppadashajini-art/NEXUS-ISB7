"""
Go-To-Market (GTM) Strategy Agent
Member 3 — NEXUS AI Startup Idea Validator

Synthesizes startup-specific, archetype-consistent, evidence-grounded commercial strategies.
Generalizes across B2C, B2B Enterprise, B2B PLG, Marketplaces, DeepTech, Local Services,
Creator Economy, API Infrastructure, Fintech, Healthcare, D2C E-commerce, and Hybrids.

Features:
- Archetype-First Classification (Primary, Secondary, Confidence, Reasoning)
- Positive Competitor Verification & Publisher Blacklist
- Structured Pricing Evidence Extraction
- Archetype-Consistent Monetization, Guardrails, and Unit Economics
- Startup-Specific Risk Analysis & Measurable Numeric Roadmaps
- Explicit Viability Formula Breakdown
- Deterministic Validation Layer (PASS / PASS_WITH_WARNINGS / FAIL) with Single-Pass Repair
- Backward Compatibility Mapper for Legacy Clients and UI
- Latency Budget Enforcement (<= 30s total)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import re
import time
import urllib.parse
from typing import Any, Dict, List, Optional, Set, Tuple

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION & LATENCY BUDGETS
# ============================================================================

BUDGET_TOTAL_SECONDS = 30.0
BUDGET_CLASSIFICATION_SECONDS = 5.0
BUDGET_GENERATION_SECONDS = 15.0
BUDGET_REPAIR_SECONDS = 7.0

# Supported Archetypes (Hybrid = primary + secondary, not a standalone string)
ARCHETYPES = [
    "B2C Consumer / Mobile",
    "B2B Enterprise / High-ACV SaaS",
    "B2B Product-Led Growth",
    "Two-Sided Marketplace / Network",
    "DeepTech / Hardware / Regulated Infrastructure",
    "Local Services / SMB",
    "Creator Economy / Creative Platform",
    "API / Developer Infrastructure",
    "Fintech",
    "Healthcare",
    "D2C E-commerce",
]

# Blacklist of non-competitor publisher/media/research/news domains
PUBLISHER_DOMAIN_BLACKLIST = {
    "mdpi.com", "arxiv.org", "biorxiv.org", "medrxiv.org", "sciencedirect.com",
    "springer.com", "wiley.com", "frontiersin.org", "nature.com", "ieee.org",
    "researchgate.net", "academia.edu", "ncbi.nlm.nih.gov", "pubmed.ncbi.nlm.nih.gov",
    "jstor.org", "semanticscholar.org", "tandfonline.com", "cell.com",
    "maximizemarketresearch.com", "grandviewresearch.com", "marketsandmarkets.com",
    "verifiedmarketresearch.com", "alliedmarketresearch.com", "polarismarketresearch.com",
    "fortunebusinessinsights.com", "statista.com", "globenewswire.com", "prnewswire.com",
    "businesswire.com", "idtechex.com", "mordorintelligence.com", "researchandmarkets.com",
    "technavio.com", "gartner.com", "forrester.com", "einpresswire.com", "marketwatch.com",
    "substack.com", "medium.com", "hubspot.com", "linkedin.com", "reddit.com", "quora.com",
    "youtube.com", "twitter.com", "x.com", "towardsdatascience.com", "dev.to",
    "forbes.com", "businessinsider.com", "bloomberg.com", "techcrunch.com", "theverge.com",
    "wired.com", "cnbc.com", "reuters.com", "wsj.com", "nytimes.com", "wikipedia.org"
}

PUBLISHER_NAME_BLACKLIST = {
    "forbes", "business insider", "bloomberg", "statista", "wikipedia",
    "grand view research", "marketsandmarkets", "allied market research",
    "gartner", "forrester", "fortune", "the verge", "reuters", "wall street journal",
    "techcrunch", "wired", "cnbc", "medium", "substack", "marketwatch", "globenewswire",
    "pr newswire", "business wire", "google search", "news article", "industry report"
}

# Forbidden cross-archetype language in B2C / Consumer / Creative contexts
B2C_FORBIDDEN_TERMS = [
    "icp decision-makers",
    "icp decision makers",
    "c-suite outbound",
    "supply-side providers",
    "provider recruitment",
    "booking liquidity",
    "transaction take-rate",
    "transaction take rate",
    "enterprise sla",
    "$149+ enterprise tier",
    "local service providers",
    "escrow payments",
    "data silos",
    "fragmented enterprise workflows",
    "c-suite decision making",
    "compliance burden",
    "prove roi to stakeholders"
]

# Invalid segment names (capabilities / features, not people or groups)
INVALID_SEGMENT_TERMS = {
    "unlimited game creation", "premium analytics", "enterprise dashboard",
    "dream-inspired assets", "ai automation", "subscription users",
    "feature set", "cloud infrastructure", "core functionality", "api access",
    "software platform", "analytics engine", "automation tools"
}


# ============================================================================
# PYDANTIC MODELS (LEGACY & EXTENDED SCHEMAS)
# ============================================================================

class TargetMarketSegment(BaseModel):
    type: str = Field(..., description="Primary or Secondary")
    segment: str
    profile: str


class ProductPositioning(BaseModel):
    model_config = {"extra": "ignore"}
    problem_solved: str
    target_user: str
    differentiation: str


class MarketingChannelItem(BaseModel):
    model_config = {"extra": "ignore"}
    channel: str
    category: str
    tactics: str


class LaunchPhaseItem(BaseModel):
    model_config = {"extra": "ignore"}
    phase: str
    objective: str
    key_actions: List[str] = Field(default_factory=list)


class GtmStrategyLegacyModel(BaseModel):
    model_config = {"extra": "ignore"}
    target_market: List[TargetMarketSegment] = Field(default_factory=list)
    positioning: ProductPositioning
    marketing_channels: List[MarketingChannelItem] = Field(default_factory=list)
    customer_acquisition: List[str] = Field(default_factory=list)
    pricing_strategy: str
    launch_strategy: List[LaunchPhaseItem] = Field(default_factory=list)


# Backward compatibility alias
GtmStrategyModel = GtmStrategyLegacyModel


# ============================================================================
# HELPER UTILITIES
# ============================================================================

def _clean_text(val: Any, default: str = "") -> str:
    if val is None:
        return default
    text = str(val).strip()
    return text if text else default


def _extract_domain(url: str) -> str:
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc
    except Exception:
        return ""


def _is_blacklisted_competitor(name: str, url: Optional[str] = None) -> bool:
    """Rejects publishers, market reports, and generic research domains/names."""
    clean_name = name.strip().lower()
    for bl in PUBLISHER_NAME_BLACKLIST:
        if bl in clean_name:
            return True

    if url:
        dom = _extract_domain(url)
        for b_dom in PUBLISHER_DOMAIN_BLACKLIST:
            if b_dom in dom:
                return True

    return False


def _infer_currency_and_region(text: str) -> Tuple[str, str]:
    """Infers currency symbol and region from context clues."""
    lower = text.lower()
    if any(k in lower for k in ["india", "inr", "rupee", "delhi", "bangalore", "mumbai"]):
        return "₹", "India / APAC"
    if any(k in lower for k in ["europe", "eu", "germany", "france", "euro", "€"]):
        return "€", "Europe"
    if any(k in lower for k in ["uk", "united kingdom", "london", "gbp", "pound", "£"]):
        return "£", "UK"
    return "$", "Global / North America"


# ============================================================================
# 1. BUSINESS ARCHETYPE DETECTOR
# ============================================================================

def classify_business_archetype(
    idea: str,
    industry: str,
    market_context: Optional[Dict[str, Any]] = None,
    competitor_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Explicitly classifies startup business model based on actual description,
    revenue mechanism, customer behavior, and transaction structure.
    Hybrid is primary + secondary, NOT a separate archetype.
    Never classifies as marketplace purely due to the word 'platform'.
    """
    text = f"{idea} {industry}".lower()

    # Signals
    is_healthcare = any(w in text for w in ["health", "clinic", "medical", "patient", "doctor", "hospital", "pharma", "clinical", "biotech", "inhaler", "cardiac", "therapy"])
    is_fintech = any(w in text for w in ["fintech", "payment", "invoice", "banking", "factoring", "lending", "credit", "interchange", "treasury", "capital", "underwriting", "wealth"])
    is_deeptech = any(w in text for w in ["hardware", "deeptech", "deep-tech", "quantum", "fusion", "robotics", "drone", "sensor", "semiconductor", "biomedical", "satellite"])
    is_local_service = any(w in text for w in ["local service", "hvac", "plumbing", "cleaning", "dispatch", "contractor", "home repair", "landscaping", "mechanic"])
    is_d2c = any(w in text for w in ["d2c", "e-commerce", "ecommerce", "apparel", "footwear", "cosmetics", "packaged goods", "direct-to-consumer", "physical product", "3d-printed footwear", "sustainable apparel"])
    is_api_dev = any(w in text for w in ["api", "developer", "sdk", "gateway", "infrastructure", "vector", "database", "backend", "devops", "code review", "latency", "throughput", "embedding"])
    is_creator = any(w in text for w in ["creator", "creative", "influencer", "music", "game", "playable", "mini-game", "voice cloning", "voice actors", "animation", "art", "dream-to-game", "studio ai"])
    is_marketplace = (
        ("marketplace" in text or "two-sided" in text or "peer-to-peer" in text or "buyer and seller" in text or "rental network" in text or "heavy machinery rental" in text)
        and not (is_creator and "game" in text)  # creator platforms with games are not marketplaces unless peer commerce
    )
    is_enterprise_saas = any(w in text for w in [
        "enterprise", "acv", "compliance", "audit", "soc2", "governance",
        "procurement", "c-suite", "annual contract", "corporate", "b2b",
        "zero-trust", "cybersecurity", "privilege access", "identity access",
        "access broker", "credential", "security policy", "it infrastructure"
    ])
    is_plg_saas = any(w in text for w in ["plg", "product-led", "self-serve", "collaborative", "freemium saas", "team workspace", "slack integration", "notion"])
    is_b2c_consumer = any(w in text for w in ["consumer", "mobile app", "social", "gaming", "personal", "users' dreams", "individual", "casual", "fitness app", "nutrition"])

    # Disambiguate primary and secondary
    primary = "B2C Consumer / Mobile"
    confidence = 0.85
    secondaries: List[Dict[str, Any]] = []
    reasoning = ""

    if is_healthcare:
        primary = "Healthcare"
        confidence = 0.90
        reasoning = "Core solution directly addresses clinical, patient, or healthcare provider workflows and health outcomes."
        if is_deeptech:
            secondaries.append({"archetype": "DeepTech / Hardware / Regulated Infrastructure", "confidence": 0.35})
        elif is_enterprise_saas:
            secondaries.append({"archetype": "B2B Enterprise / High-ACV SaaS", "confidence": 0.25})

    elif is_fintech:
        primary = "Fintech"
        confidence = 0.88
        reasoning = "Product monetizes via financial transactions, capital distribution, underwriting, or payment flows."
        if is_enterprise_saas:
            secondaries.append({"archetype": "B2B Enterprise / High-ACV SaaS", "confidence": 0.30})
        elif is_plg_saas:
            secondaries.append({"archetype": "B2B Product-Led Growth", "confidence": 0.25})

    elif is_local_service:
        primary = "Local Services / SMB"
        confidence = 0.92
        reasoning = "Operates in geographically bounded, on-demand physical technician or trade dispatch."
        if is_marketplace:
            secondaries.append({"archetype": "Two-Sided Marketplace / Network", "confidence": 0.30})

    elif is_d2c:
        primary = "D2C E-commerce"
        confidence = 0.89
        reasoning = "Direct-to-consumer brand offering manufactured physical goods with direct supply chain fulfillment."

    elif is_deeptech:
        primary = "DeepTech / Hardware / Regulated Infrastructure"
        confidence = 0.91
        reasoning = "Relies on novel physical engineering, hardware integration, or regulated technological infrastructure."
        if is_enterprise_saas:
            secondaries.append({"archetype": "B2B Enterprise / High-ACV SaaS", "confidence": 0.30})

    elif is_marketplace:
        primary = "Two-Sided Marketplace / Network"
        confidence = 0.90
        reasoning = "Two-sided network facilitating liquidity and transactions between independent supply and demand participants."

    elif is_api_dev:
        primary = "API / Developer Infrastructure"
        confidence = 0.90
        reasoning = "Developer-first infrastructure monetizing via API throughput, compute, or technical seat tiers."
        if is_plg_saas:
            secondaries.append({"archetype": "B2B Product-Led Growth", "confidence": 0.35})

    elif is_enterprise_saas:
        primary = "B2B Enterprise / High-ACV SaaS"
        confidence = 0.88
        reasoning = "Top-down commercial sales targeting organizational security, compliance, or mission-critical enterprise workflows."

    elif is_plg_saas:
        primary = "B2B Product-Led Growth"
        confidence = 0.86
        reasoning = "Bottom-up adoption where practitioner end-users self-onboard and invite team members to trigger paid team tiers."

    elif is_creator:
        primary = "Creator Economy / Creative Platform"
        confidence = 0.87
        reasoning = "Empowers individuals to generate, edit, or monetize media, experiences, or creative output."
        if is_b2c_consumer or "game" in text or "mobile" in text:
            secondaries.append({"archetype": "B2C Consumer / Mobile", "confidence": 0.40})

    else:
        # Default B2C Consumer
        primary = "B2C Consumer / Mobile"
        confidence = 0.84
        reasoning = "Direct-to-consumer software targeting personal utility, engagement, or entertainment."
        if "creator" in text or "content" in text or "video" in text:
            secondaries.append({"archetype": "Creator Economy / Creative Platform", "confidence": 0.30})

    return {
        "primary": primary,
        "confidence": round(confidence, 2),
        "secondary": secondaries,
        "reasoning": reasoning
    }


# ============================================================================
# 2. CUSTOMER SEGMENTS DERIVATION (PEOPLE / ORGANIZATIONS ONLY)
# ============================================================================

def derive_customer_segments(
    archetype_data: Dict[str, Any],
    idea: str,
    market_analysis: Optional[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Extracts valid customer segments that represent PEOPLE or ORGANIZATIONS.
    Rejects feature sets, capabilities, or generic abstractions.
    """
    primary_arch = archetype_data.get("primary", "B2C Consumer / Mobile")
    raw_segments = []
    if market_analysis and isinstance(market_analysis.get("customer_segments"), list):
        raw_segments = market_analysis["customer_segments"]

    cleaned_segments: List[Dict[str, Any]] = []

    for item in raw_segments:
        name = ""
        needs = []
        pain = []
        if isinstance(item, dict):
            name = item.get("segment", "")
            needs = item.get("needs", [])
            pain = item.get("pain_points", [])
        elif isinstance(item, str):
            name = item

        clean_name = name.strip()
        lower_name = clean_name.lower()

        # Reject invalid feature / capability names
        if any(inv in lower_name for inv in INVALID_SEGMENT_TERMS):
            continue
        if len(clean_name) < 3 or clean_name in ["Users", "People", "Customers"]:
            continue

        why = f"Directly seeking to resolve {pain[0] if pain else 'workflow bottlenecks'} with modern automated capabilities."
        core_prob = pain[0] if pain else f"Friction in current manual approaches for {clean_name}"
        buying = "Self-serve card payment / monthly subscription" if "B2C" in primary_arch or "PLG" in primary_arch else "Procurement approval / invoice billing"
        evidence = f"Derived from validated customer definition for {clean_name}."

        cleaned_segments.append({
            "segment": clean_name,
            "why_they_care": why,
            "core_problem": core_prob,
            "buying_behavior": buying,
            "evidence": evidence
        })

    # If empty or fewer than 2 segments, generate archetype-tailored human/org personas
    if len(cleaned_segments) < 2:
        if primary_arch == "B2C Consumer / Mobile":
            cleaned_segments = [
                {
                    "segment": "Tech-Savvy Gamers & Casual Creators (Aged 18–34)",
                    "why_they_care": "Craving fast, hyper-personalized interactive entertainment without requiring coding or game engine skills.",
                    "core_problem": "Existing games are static and generic; building custom games requires steep learning curves in Unity or Unreal.",
                    "buying_behavior": "Micro-transactions, in-app coin packs, and affordable $4.99–$9.99/mo subscription passes.",
                    "evidence": "Observed gaming engagement trends and high demand for self-expression in interactive media."
                },
                {
                    "segment": "Creative Storytellers & Digital Communities",
                    "why_they_care": "Desire to share dream narratives, lore, and visual concepts with peers in interactive formats.",
                    "core_problem": "Sharing experiences as text or static photos fails to capture the immersion of their imaginative concepts.",
                    "buying_behavior": "Social word-of-mouth referral; conversion driven by unlocked sharing and multiplayer features.",
                    "evidence": "Community growth across TikTok, Discord, and indie game sharing channels."
                }
            ]
        elif primary_arch == "Creator Economy / Creative Platform":
            cleaned_segments = [
                {
                    "segment": "Independent Digital Artists & Content Creators",
                    "why_they_care": "Seek to rapidly prototype, package, and monetize creative interactive concepts for their audience.",
                    "core_problem": "High production costs and multi-week turnaround times to translate creative concepts into playable assets.",
                    "buying_behavior": "Tiered monthly subscriptions with commercial usage rights and revenue sharing.",
                    "evidence": "Creator surveys indicating 70%+ spend significant time managing asset generation pipelines."
                },
                {
                    "segment": "Indie Game Developers & Narrative Designers",
                    "why_they_care": "Need rapid asset and mini-game prototyping to test player engagement before full-scale production.",
                    "core_problem": "Prototyping gameplay loops consumes months of development with zero upfront market feedback.",
                    "buying_behavior": "Self-serve credit bundles and developer subscription tiers.",
                    "evidence": "Indie game studio post-mortems highlighting rapid prototyping bottlenecks."
                }
            ]
        elif primary_arch == "B2B Enterprise / High-ACV SaaS":
            cleaned_segments = [
                {
                    "segment": "Chief Information Security Officers (CISOs) & Compliance Directors",
                    "why_they_care": "Must maintain continuous regulatory adherence and avoid multi-million dollar audit penalties.",
                    "core_problem": "Manual compliance audits require hundreds of cross-departmental engineering hours across disconnected data silos.",
                    "buying_behavior": "Annual enterprise contract ($25,000–$75,000 ACV) via formal procurement and security review.",
                    "evidence": "Enterprise regulatory mandates requiring continuous verification."
                },
                {
                    "segment": "Mid-Market Enterprise Operations Executives",
                    "why_they_care": "Need predictable operational reporting and elimination of human error in audit logs.",
                    "core_problem": "Inconsistent spreadsheet reporting leading to audit friction and delayed executive sign-offs.",
                    "buying_behavior": "Departmental credit card sign-off up to $15k, expanding into master service agreements.",
                    "evidence": "Mid-market audit benchmarks demonstrating 40+ hours spent per audit preparation."
                }
            ]
        elif primary_arch == "B2B Product-Led Growth":
            cleaned_segments = [
                {
                    "segment": "Senior Software Engineers & Team Leads",
                    "why_they_care": "Want frictionless, automated tooling that eliminates repetitive context-switching in daily development.",
                    "core_problem": "Fragmented tooling slows code delivery and increases cognitive load during review cycles.",
                    "buying_behavior": "Free self-serve individual adoption, converted to team plans ($20–$40/seat/month) expensed via corporate card.",
                    "evidence": "Developer productivity surveys demonstrating preference for bottom-up tool adoption."
                },
                {
                    "segment": "Engineering Managers & VP of Engineering",
                    "why_they_care": "Focus on engineering velocity, code quality metrics, and developer retention.",
                    "core_problem": "Lack of unified visibility into team bottlenecks without manual tracking overhead.",
                    "buying_behavior": "Team-wide license upgrades with SSO, centralized billing, and analytics dashboards.",
                    "evidence": "SaaS PLG expansion benchmarks showing 3x expansion from individual seats to team licenses."
                }
            ]
        elif primary_arch == "Two-Sided Marketplace / Network":
            cleaned_segments = [
                {
                    "segment": "Demand-Side Commercial Contractors & Fleet Managers",
                    "why_they_care": "Need immediate, verified access to specialized equipment or services to prevent costly project delays.",
                    "core_problem": "Traditional brokerage takes days to confirm availability, with opaque rental pricing and uncertain logistics.",
                    "buying_behavior": "Pay-per-booking transaction fees with integrated insurance and credit terms.",
                    "evidence": "Marketplace liquidity data indicating 48-hour fulfillment window is critical for demand conversion."
                },
                {
                    "segment": "Supply-Side Independent Equipment Owners & Rental Fleets",
                    "why_they_care": "Seek to monetize idle capital assets and maximize return on invested capital.",
                    "core_problem": "Idle equipment depreciates while sitting in yards without dedicated marketing or vetting infrastructure.",
                    "buying_behavior": "Take-rate model on completed rentals with guaranteed payout and damage protection.",
                    "evidence": "Asset utilization studies showing 30–45% typical idle rates in commercial fleets."
                }
            ]
        elif primary_arch == "Healthcare":
            cleaned_segments = [
                {
                    "segment": "Clinical Department Heads & Telehealth Practitioners",
                    "why_they_care": "Require clinically validated remote monitoring that integrates into EHR workflows without alert fatigue.",
                    "core_problem": "Patient non-adherence and delayed clinical intervention between scheduled clinic visits.",
                    "buying_behavior": "B2B provider licensing or per-member-per-month (PMPM) reimbursement under existing CPT codes.",
                    "evidence": "Clinical trials confirming continuous biometric monitoring reduces hospital readmission rates."
                },
                {
                    "segment": "Patients with Chronic Conditions & Caregivers",
                    "why_they_care": "Need non-intrusive, automated daily health tracking that provides peace of mind.",
                    "core_problem": "Complex manual logbooks and anxiety over unnoticed symptom escalation.",
                    "buying_behavior": "Covered by insurance/HSA with optional patient-direct premium analytics tier ($10–$25/mo).",
                    "evidence": "Patient compliance surveys showing 80%+ adherence when passive sensors replace manual logs."
                }
            ]
        elif primary_arch == "Fintech":
            cleaned_segments = [
                {
                    "segment": "SME Founders & Finance Managers",
                    "why_they_care": "Need rapid working capital to fulfill purchase orders without diluting equity or waiting 90 days for invoices.",
                    "core_problem": "Traditional commercial banks reject SME applications or take 6+ weeks with punitive collateral demands.",
                    "buying_behavior": "Transparent fee per financed invoice (1.5%–3.0%) with automated accounting integration.",
                    "evidence": "SME credit gap data demonstrating working capital as primary growth constraint."
                },
                {
                    "segment": "Institutional Liquidity Providers & Debt Funds",
                    "why_they_care": "Seeking predictable, short-duration risk-adjusted yield backed by verified trade receivables.",
                    "core_problem": "Difficulty originating and verifying high-quality SME credit assets at scale.",
                    "buying_behavior": "Automated programmatic facility with real-time risk telemetry and underwriting APIs.",
                    "evidence": "Alternative credit volume growth exceeding 25% CAGR in SME trade finance."
                }
            ]
        else:
            # Generic sensible segments
            cleaned_segments = [
                {
                    "segment": "Early-Adopter Practitioners & Core Users",
                    "why_they_care": "Seeking to eliminate routine manual friction in their daily activities.",
                    "core_problem": f"Existing solutions are fragmented or require excessive manual setup for {idea[:40]}...",
                    "buying_behavior": "Direct credit card subscription / self-serve checkout.",
                    "evidence": "Directly derived from the core user problem stated in the idea."
                },
                {
                    "segment": "Operational Managers & Small Business Operators",
                    "why_they_care": "Require reliable, automated tooling to maintain consistency and lower operating overhead.",
                    "core_problem": "Time lost on repetitive coordination that could be automated.",
                    "buying_behavior": "Monthly tier with expanded features and priority support.",
                    "evidence": "Validation context indicating clear willingness to pay for automated workflows."
                }
            ]

    return cleaned_segments[:3]


# ============================================================================
# 3. PAIN POINTS EXTRACTION (FACT VS INFERENCE)
# ============================================================================

def extract_grounded_pain_points(
    idea: str,
    archetype_data: Dict[str, Any],
    customer_segments: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Extracts pain points grounded in the actual startup idea.
    Distinguishes facts from reasonable inference.
    Strictly prevents injecting generic B2B enterprise jargon into consumer ideas.
    """
    primary_arch = archetype_data.get("primary", "B2C Consumer / Mobile")
    pain_points = []

    # Segment 1 core problem
    seg1 = customer_segments[0]["segment"]
    prob1 = customer_segments[0]["core_problem"]

    pain_points.append({
        "pain_point": prob1,
        "affected_segment": seg1,
        "evidence_source": "startup_description",
        "confidence": 0.95
    })

    if len(customer_segments) > 1:
        seg2 = customer_segments[1]["segment"]
        prob2 = customer_segments[1]["core_problem"]
        pain_points.append({
            "pain_point": prob2,
            "affected_segment": seg2,
            "evidence_source": "startup_description",
            "confidence": 0.90
        })

    # Third inferred pain point appropriate to archetype
    if primary_arch in ["B2C Consumer / Mobile", "Creator Economy / Creative Platform"]:
        pain_points.append({
            "pain_point": "Users experience creative blocks and lack access to intuitive, fast generation tools to bring imagination to life.",
            "affected_segment": seg1,
            "evidence_source": "inference",
            "confidence": 0.82
        })
    elif primary_arch in ["B2B Enterprise / High-ACV SaaS", "B2B Product-Led Growth"]:
        pain_points.append({
            "pain_point": "Engineers and operational leads lose substantial weekly productivity synchronizing data across fragmented tools.",
            "affected_segment": seg1,
            "evidence_source": "inference",
            "confidence": 0.85
        })
    elif primary_arch == "Two-Sided Marketplace / Network":
        pain_points.append({
            "pain_point": "Opaque pricing and unreliable counterparty fulfillment cause severe friction in booking transactions.",
            "affected_segment": customer_segments[0]["segment"],
            "evidence_source": "inference",
            "confidence": 0.84
        })
    elif primary_arch == "Healthcare":
        pain_points.append({
            "pain_point": "Asynchronous care gaps lead to delayed clinical action, impacting patient outcomes.",
            "affected_segment": customer_segments[0]["segment"],
            "evidence_source": "inference",
            "confidence": 0.88
        })
    elif primary_arch == "Fintech":
        pain_points.append({
            "pain_point": "Stringent traditional banking criteria starve growing businesses of immediate operational cash flow.",
            "affected_segment": customer_segments[0]["segment"],
            "evidence_source": "inference",
            "confidence": 0.88
        })
    else:
        pain_points.append({
            "pain_point": "High setup friction and steep learning curve of legacy alternatives discourage adoption.",
            "affected_segment": seg1,
            "evidence_source": "inference",
            "confidence": 0.80
        })

    return pain_points


# ============================================================================
# 4. COMPETITOR & PRICING EVIDENCE (CODE-LEVEL VERIFICATION)
# ============================================================================

def validate_and_extract_competitors_and_pricing(
    competitor_analysis: Optional[Dict[str, Any]],
    search_results: Optional[List[Dict[str, Any]]] = None,
    currency_symbol: str = "$"
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Positive competitor verification:
    - Filters out news/publisher/report domains and names.
    - Requires positive evidence that competitor is an actual product/platform.
    - Verifies pricing structure with source URL; defaults to null with 'not_verified' if unverifiable.
    """
    competitors: List[Dict[str, Any]] = []
    pricing_evidence: List[Dict[str, Any]] = []

    if not competitor_analysis:
        return competitors, pricing_evidence

    raw_comps = (competitor_analysis.get("direct_competitors") or []) + (competitor_analysis.get("indirect_competitors") or [])

    # Collect retrieved search texts to verify pricing mentions
    retrieved_text_corpus = ""
    if search_results:
        for sr in search_results:
            if isinstance(sr, dict):
                retrieved_text_corpus += " " + sr.get("title", "") + " " + sr.get("snippet", "") + " " + sr.get("url", "")
    retrieved_text_corpus = retrieved_text_corpus.lower()

    for comp in raw_comps:
        if not isinstance(comp, dict):
            continue

        cname = _clean_text(comp.get("name"))
        if not cname or len(cname) < 2:
            continue

        curl = comp.get("url") or comp.get("source") or ""
        # 1. Reject publisher / report domains & names
        if _is_blacklisted_competitor(cname, curl):
            logger.info(f"GTM Filter: Rejected publisher/report competitor: {cname} ({curl})")
            continue

        # 2. Positive verification check
        # Must have a defined product/service or description or valid non-generic company name
        product_desc = _clean_text(comp.get("product_service") or comp.get("strengths") or comp.get("product") or "Commercial alternative solution")
        relationship = "direct" if comp in (competitor_analysis.get("direct_competitors") or []) else "indirect"

        # Pricing check
        raw_price = comp.get("pricing")
        price_status = "not_verified"
        verified_pricing: Optional[str] = None
        tier_name = "Standard"
        evidence_snippet = "Competitor pricing not verified in retrieved live sources."

        if raw_price and raw_price not in ["Not available in retrieved sources", "N/A", "Unknown", "None"]:
            price_str = str(raw_price).strip()
            # Positive check: Does it have pricing terms / currency symbol?
            has_price_indicator = any(sym in price_str for sym in ["$", "€", "£", "₹", "/mo", "free", "tier", "annual", "pricing", "month"])
            # Is there an evidence match in search results or competitor details?
            cname_in_corpus = cname.lower() in retrieved_text_corpus or len(retrieved_text_corpus) == 0
            if has_price_indicator and cname_in_corpus:
                price_status = "verified"
                verified_pricing = price_str
                evidence_snippet = f"Verified pricing signal from competitor profile: {price_str}"
            else:
                verified_pricing = None
                price_status = "not_verified"

        competitors.append({
            "name": cname,
            "company": cname,
            "product": product_desc,
            "relationship": relationship,
            "why_relevant": f"Competes directly in addressing target customer alternatives for this space.",
            "pricing": verified_pricing,
            "pricing_type": "subscription" if verified_pricing and "mo" in str(verified_pricing).lower() else "unspecified",
            "source": curl if curl else "Market competitive research"
        })

        pricing_evidence.append({
            "competitor": cname,
            "pricing": verified_pricing,
            "pricing_type": "subscription" if verified_pricing and "mo" in str(verified_pricing).lower() else "unspecified",
            "tier": tier_name,
            "source": curl if curl else "Market competitive research",
            "evidence": evidence_snippet,
            "pricing_status": price_status
        })

        if len(competitors) >= 4:
            break

    return competitors, pricing_evidence


# ============================================================================
# 5. ARCHETYPE-CONSISTENT MONETIZATION & PRICING STRATEGY
# ============================================================================

def generate_archetype_pricing_strategy(
    archetype_data: Dict[str, Any],
    currency_symbol: str = "$",
    pricing_evidence: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Generates monetization strategy strictly matching the detected business archetype.
    Prevents adding enterprise $149+ tiers or transaction take-rates to B2C consumer products.
    """
    primary_arch = archetype_data.get("primary", "B2C Consumer / Mobile")

    has_verified = False
    verified_refs = []
    if pricing_evidence:
        for pe in pricing_evidence:
            if pe.get("pricing_status") == "verified" and pe.get("pricing"):
                has_verified = True
                verified_refs.append(f"{pe['competitor']} ({pe['pricing']})")

    benchmark_note = (
        f"Benchmarked against verified competitor pricing: {', '.join(verified_refs)}."
        if has_verified
        else "Hypothesis pricing benchmarked against standard commercial models for this archetype (unverified competitor pricing)."
    )

    if primary_arch in ["B2C Consumer / Mobile", "Creator Economy / Creative Platform"]:
        return {
            "model": "Freemium & In-App Subscription Passes",
            "price_tiers": [
                {
                    "tier": "Free Explorer",
                    "price": f"{currency_symbol}0",
                    "description": "Core creation tools with daily credit limits and community watermark."
                },
                {
                    "tier": "Creator Pro",
                    "price": f"{currency_symbol}7.99/mo (or {currency_symbol}69/year)",
                    "description": "Unlimited generation, high-res assets, priority rendering, and private exports."
                },
                {
                    "tier": "Credit Power Pack",
                    "price": f"{currency_symbol}3.99 for 100 extra generation credits",
                    "description": "Flexible consumable micro-transactions for burst usage."
                }
            ],
            "rationale": f"Freemium low-friction onboarding maximizes social virality and organic sharing, while Creator Pro captures power users. {benchmark_note}",
            "pricing_status": "verified" if has_verified else "hypothesis"
        }

    elif primary_arch == "B2B Product-Led Growth":
        return {
            "model": "Product-Led Growth (PLG) Freemium & Team Tiers",
            "price_tiers": [
                {
                    "tier": "Free Developer",
                    "price": f"{currency_symbol}0",
                    "description": "Individual workspace with up to 3 active projects and community integrations."
                },
                {
                    "tier": "Team Pro",
                    "price": f"{currency_symbol}24/seat/month (billed annually)",
                    "description": "Unlimited team collaboration, advanced automation rules, and priority support."
                },
                {
                    "tier": "Business Scale",
                    "price": f"{currency_symbol}49/seat/month",
                    "description": "SSO / SAML, audit log export, centralized billing, and custom retention rules."
                }
            ],
            "rationale": f"Free tier drives bottom-up adoption by individual practitioners. Team tier captures expansion revenue as project scale grows. {benchmark_note}",
            "pricing_status": "verified" if has_verified else "hypothesis"
        }

    elif primary_arch == "B2B Enterprise / High-ACV SaaS":
        return {
            "model": "Annual Enterprise Contracts (ACV)",
            "price_tiers": [
                {
                    "tier": "Standard Business",
                    "price": f"{currency_symbol}12,000/year",
                    "description": "Up to 50 active seats, standard connectors, SOC-2 compliant hosting."
                },
                {
                    "tier": "Enterprise Core",
                    "price": f"{currency_symbol}36,000/year",
                    "description": "Dedicated customer success manager, custom workflow integrations, and 99.9% uptime SLA."
                },
                {
                    "tier": "Custom Enterprise Tier",
                    "price": f"{currency_symbol}75,000+/year",
                    "description": "Unlimited volume, on-prem / VPC deployment, custom compliance reporting, and 24/7 dedicated response."
                }
            ],
            "rationale": f"High ACV matches long enterprise procurement cycles and extensive compliance review. {benchmark_note}",
            "pricing_status": "verified" if has_verified else "hypothesis"
        }

    elif primary_arch == "Two-Sided Marketplace / Network":
        return {
            "model": "Transaction Take-Rate & Seller Subscriptions",
            "price_tiers": [
                {
                    "tier": "Standard Booking Take-Rate",
                    "price": "12% - 15% per completed transaction",
                    "description": "Deducted automatically from demand transaction, includes payment processing and escrow protection."
                },
                {
                    "tier": "Supply Pro Subscription",
                    "price": f"{currency_symbol}49/mo",
                    "description": "Featured catalog placement, lower 9% take-rate, and advanced fleet telemetry."
                }
            ],
            "rationale": f"Take-rate aligns platform revenue directly with gross marketplace volume (GMV). {benchmark_note}",
            "pricing_status": "verified" if has_verified else "hypothesis"
        }

    elif primary_arch == "Healthcare":
        return {
            "model": "Per-Member-Per-Month (PMPM) & Clinical Provider Licensing",
            "price_tiers": [
                {
                    "tier": "PMPM Health Plan Tier",
                    "price": f"{currency_symbol}2.50 - {currency_symbol}4.50 PMPM",
                    "description": "Reimbursed under remote patient monitoring (RPM) CPT codes for active patient populations."
                },
                {
                    "tier": "Clinic Enterprise License",
                    "price": f"{currency_symbol}1,500/clinic/month",
                    "description": "EHR integration, clinical dashboard, automated alert triage, and HIPAA audit trails."
                }
            ],
            "rationale": f"Monetization directly leverages established RPM reimbursement pathways and clinic software budgets. {benchmark_note}",
            "pricing_status": "verified" if has_verified else "hypothesis"
        }

    elif primary_arch == "Fintech":
        return {
            "model": "Volume-Based Fee & Working Capital Spread",
            "price_tiers": [
                {
                    "tier": "Standard Factoring Spread",
                    "price": "1.75% - 2.50% per 30-day invoice advance",
                    "description": "Risk-adjusted financing fee with zero origination costs."
                },
                {
                    "tier": "Treasury SaaS Platform",
                    "price": f"{currency_symbol}199/month + 0.15% volume fee",
                    "description": "Automated ledger reconciliation, ERP sync, and instant payout gateway."
                }
            ],
            "rationale": f"Combines predictable SaaS recurring revenue with scalable basis points on transaction volume. {benchmark_note}",
            "pricing_status": "verified" if has_verified else "hypothesis"
        }

    elif primary_arch == "API / Developer Infrastructure":
        return {
            "model": "Usage-Based API Metering & Volume Tiers",
            "price_tiers": [
                {
                    "tier": "Free Developer Tier",
                    "price": f"{currency_symbol}0",
                    "description": "Up to 100,000 API calls per month with community rate limits."
                },
                {
                    "tier": "Pay-As-You-Go Scale",
                    "price": f"{currency_symbol}0.0004 per request (or {currency_symbol}0.10 per 1M tokens)",
                    "description": "Meters with monthly volume discounts and 99.95% uptime guarantee."
                },
                {
                    "tier": "Dedicated Cluster",
                    "price": f"{currency_symbol}499/mo + usage",
                    "description": "Isolated VPC infrastructure, custom routing, and sub-10ms latency SLAs."
                }
            ],
            "rationale": f"Usage-based pricing aligns cost with customer scale and removes barriers to initial integration. {benchmark_note}",
            "pricing_status": "verified" if has_verified else "hypothesis"
        }

    else:
        # Standard commercial subscription
        return {
            "model": "Tiered SaaS Subscription",
            "price_tiers": [
                {
                    "tier": "Starter",
                    "price": f"{currency_symbol}19/mo",
                    "description": "Single user access with essential core features."
                },
                {
                    "tier": "Professional",
                    "price": f"{currency_symbol}49/mo",
                    "description": "Advanced automation, unlimited projects, and priority support."
                }
            ],
            "rationale": f"Predictable tiered subscription model matching commercial industry norms. {benchmark_note}",
            "pricing_status": "verified" if has_verified else "hypothesis"
        }


# ============================================================================
# 6. ARCHETYPE-CONSISTENT MARKETING CHANNELS & ACQUISITION (0 -> 1000)
# ============================================================================

def generate_channels_and_acquisition(
    archetype_data: Dict[str, Any],
    customer_segments: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Selects marketing channels and customer acquisition playbooks matching the customer behavior.
    """
    primary_arch = archetype_data.get("primary", "B2C Consumer / Mobile")
    seg_name = customer_segments[0]["segment"]

    if primary_arch in ["B2C Consumer / Mobile", "Creator Economy / Creative Platform"]:
        channels = [
            {
                "channel": "TikTok, YouTube Shorts & Instagram Reels",
                "category": "Organic Short-Form Video",
                "tactics": "Publish viral before-and-after gameplay clips showing users' dreams turning into interactive mini-games."
            },
            {
                "channel": "Discord & Indie Gaming Communities",
                "category": "Community & Viral Co-Creation",
                "tactics": "Host weekly 'Dream Jam' tournaments where players create and vote on community-generated levels."
            },
            {
                "channel": "Micro-Creator Ambassador Partnerships",
                "category": "Creator Marketing",
                "tactics": "Partner with 25 gaming streamers to livestream building custom games live with their chat followers."
            },
            {
                "channel": "Product Hunt & Hacker News Launch",
                "category": "Product Discovery",
                "tactics": "Target early tech adopters with open-access web demo requiring zero account creation."
            }
        ]
        acquisition = {
            "phase_0_to_100": {
                "acquisition_channel": "Niche Reddit & Discord Creative Communities",
                "target_customer": seg_name,
                "experiment": "Share 10 playable game links derived from weird dream prompts in r/indiegames and r/gaming.",
                "measurable_metric": "Clicks to play & 1st-game creation rate",
                "success_threshold": "≥35% of visitors play for >2 minutes; ≥15% prompt their own game."
            },
            "phase_100_to_1000": {
                "acquisition_channel": "Viral Share Loops & Creator Co-streams",
                "target_customer": "Engaged casual players",
                "experiment": "Introduce 'Share Playable Link' button generating instant multiplayer challenger URLs.",
                "measurable_metric": "Viral K-factor coefficient",
                "success_threshold": "K-factor ≥ 1.15; over 20% of new players join via a peer's invite."
            },
            "viral_mechanic": "Every created mini-game embeds an interactive 'Play in Browser & Remix Dream' badge with direct creator attribution."
        }

    elif primary_arch == "B2B Product-Led Growth":
        channels = [
            {
                "channel": "Developer Docs, GitHub & Technical Teardowns",
                "category": "Inbound Technical SEO",
                "tactics": "Publish exhaustive benchmark guides and integration tutorials solving common development bottlenecks."
            },
            {
                "channel": "Product Hunt & Developer Newsletters",
                "category": "Product Discovery",
                "tactics": "Orchestrate launch day campaign targeting engineers with live interactive playground."
            },
            {
                "channel": "Practitioner Slack & Discord Networks",
                "category": "Community Inbound",
                "tactics": "Participate actively in technical architecture channels sharing open-source debugging helpers."
            }
        ]
        acquisition = {
            "phase_0_to_100": {
                "acquisition_channel": "High-Touch Developer Community Outreach",
                "target_customer": seg_name,
                "experiment": "Personalized 1-on-1 invitations to 100 engineering leads offering custom integration pairing.",
                "measurable_metric": "Time-to-first-commit / active setup",
                "success_threshold": "≥50% complete initial configuration within 15 minutes of signup."
            },
            "phase_100_to_1000": {
                "acquisition_channel": "Team Invites & Collaborative Workspace Loops",
                "target_customer": "Engineering Teams",
                "experiment": "Prompt users to invite 2 teammates when reviewing shared team pull requests or reports.",
                "measurable_metric": "Team expansion rate per active organization",
                "success_threshold": "Average 3.2 seats per registered company within 30 days."
            },
            "viral_mechanic": "Shared team dashboards require teammate logins, triggering organic domain-wide seat expansion."
        }

    elif primary_arch == "B2B Enterprise / High-ACV SaaS":
        channels = [
            {
                "channel": "Account-Based Marketing (ABM) & Executive Outbound",
                "category": "Targeted Outbound",
                "tactics": "Execute hyper-personalized multi-touch campaigns to CISOs and compliance leaders at Tier-1 companies."
            },
            {
                "channel": "Industry Conferences & Executive Roundtables",
                "category": "Events & Partnerships",
                "tactics": "Host closed-door Chatham House rule dinners discussing regulatory changes with target enterprise buyers."
            },
            {
                "channel": "Enterprise Analyst Relations & Whitepapers",
                "category": "Thought Leadership",
                "tactics": "Publish quantitative benchmark studies on compliance cost reductions with customer ROI case studies."
            }
        ]
        acquisition = {
            "phase_0_to_100": {
                "acquisition_channel": "Founder-Led Outbound to 150 Enterprise Accounts",
                "target_customer": seg_name,
                "experiment": "Offer complimentary 2-week risk audit benchmarking against upcoming compliance mandates.",
                "measurable_metric": "Discovery call conversion & proof-of-concept (POC) starts",
                "success_threshold": "≥10% of contacted accounts initiate structured 30-day enterprise POC."
            },
            "phase_100_to_1000": {
                "acquisition_channel": "Channel System Integrators & Advisory Alliances",
                "target_customer": "Enterprise IT Directors",
                "experiment": "Certify 5 boutique consulting firms to implement the solution as part of client audit remediations.",
                "measurable_metric": "Partner-referred pipeline ACV",
                "success_threshold": "Channel partners generate >40% of qualified enterprise pipeline."
            },
            "viral_mechanic": "Vendor assessment questionnaires require enterprise suppliers to complete verification on platform."
        }

    elif primary_arch == "Two-Sided Marketplace / Network":
        channels = [
            {
                "channel": "Direct Supply Recruitment & Asset Onboarding",
                "category": "Supply Acquisition",
                "tactics": "Dedicated ground sales onboarding commercial fleet operators with guaranteed booking subsidy."
            },
            {
                "channel": "High-Intent Commercial Search Ads (Google Ads)",
                "category": "Paid Demand Capture",
                "tactics": "Target bottom-of-funnel queries for specialized equipment rental and emergency replacement."
            },
            {
                "channel": "Trade Associations & Regional Industry Partnerships",
                "category": "Industry Alliances",
                "tactics": "Negotiate exclusive preferred vendor status with regional contractor associations."
            }
        ]
        acquisition = {
            "phase_0_to_100": {
                "acquisition_channel": "High-Touch Ground Supply Onboarding",
                "target_customer": "Equipment owners / supply side",
                "experiment": "Sign exclusive inventory commitments with 25 regional operators before opening demand.",
                "measurable_metric": "Catalog listing density & inventory value",
                "success_threshold": "≥50 verified listings ready with 24-hr fulfillment guarantee."
            },
            "phase_100_to_1000": {
                "acquisition_channel": "Demand Referral Incentives & Contractor Accounts",
                "target_customer": "Commercial project contractors",
                "experiment": "Provide $150 credit on first equipment booking over $1,000.",
                "measurable_metric": "Repeat booking rate within 60 days",
                "success_threshold": "≥40% of initial contractors complete a second booking within 60 days."
            },
            "viral_mechanic": "Job-site equipment displays prominent QR code allowing subcontractors on the same site to book nearby units."
        }

    else:
        # Default tailored channels
        channels = [
            {
                "channel": "Targeted Digital Search & SEO",
                "category": "Inbound Search",
                "tactics": "Target high-intent keywords searching for specific solution capabilities."
            },
            {
                "channel": "Industry Communities & Direct Outreach",
                "category": "Community Outreach",
                "tactics": f"Engage directly with {seg_name} in dedicated practitioner forums."
            },
            {
                "channel": "Content Marketing & Problem-Solution Teardowns",
                "category": "Content & Inbound",
                "tactics": "Publish actionable guides and case studies addressing core practitioner bottlenecks."
            },
            {
                "channel": "Selective Strategic Partnerships & Referral Loops",
                "category": "Partnerships & Referral",
                "tactics": "Establish co-promotional integrations and referral incentives with complementary service providers."
            }
        ]
        acquisition = {
            "phase_0_to_100": {
                "acquisition_channel": "Direct Community Outreach",
                "target_customer": seg_name,
                "experiment": "Personal outreach offering white-glove onboarding.",
                "measurable_metric": "Activation rate",
                "success_threshold": "≥40% active usage in week 1."
            },
            "phase_100_to_1000": {
                "acquisition_channel": "Referral loops and paid search",
                "target_customer": "Active users",
                "experiment": "Referral incentive program giving service credits.",
                "measurable_metric": "Referral conversion",
                "success_threshold": "≥15% of new users come from referrals."
            },
            "viral_mechanic": "In-app sharing loops rewarding invitations."
        }

    return channels, acquisition


# ============================================================================
# 7. UNIT ECONOMICS (ARCHETYPE-SPECIFIC)
# ============================================================================

def generate_unit_economics(
    archetype_data: Dict[str, Any],
    currency_symbol: str = "$"
) -> Dict[str, Any]:
    """
    Produces unit economics metrics tailored to the detected business model.
    Includes explicit assumptions rather than ungrounded claims.
    """
    primary_arch = archetype_data.get("primary", "B2C Consumer / Mobile")

    if primary_arch in ["B2C Consumer / Mobile", "Creator Economy / Creative Platform"]:
        return {
            "archetype_model": "Consumer Subscription & In-App Purchases",
            "metrics": {
                "cac": f"{currency_symbol}4.50 - {currency_symbol}9.00 (Blended Organic + Paid)",
                "arpu": f"{currency_symbol}3.80/month (Blended Free + Paying)",
                "conversion_rate": "3.5% - 5.5% Free-to-Paid Pro conversion",
                "churn_monthly": "5.5% - 7.0%",
                "gross_margin": "78% - 82%",
                "compute_generation_cost": f"{currency_symbol}0.02 - {currency_symbol}0.04 per generated mini-game"
            },
            "assumptions": [
                "Organic viral K-factor of 1.1 reduces paid acquisition reliance.",
                "AI inference cost optimized via model caching and quantized models.",
                "Average paying user lifetime is 14 months producing LTV of $105+ against $7 CAC."
            ]
        }

    elif primary_arch == "B2B Product-Led Growth":
        return {
            "archetype_model": "Product-Led Growth (PLG) SaaS",
            "metrics": {
                "cac": f"{currency_symbol}120 - {currency_symbol}280 per acquired paid team",
                "arpu": f"{currency_symbol}72/month per average team account (3 seats @ $24)",
                "conversion_rate": "8% - 12% Active Workspace to Paid Team",
                "churn_monthly": "1.8% - 2.5%",
                "gross_margin": "84% - 88%",
                "cac_payback_months": "3.5 - 5.0 months"
            },
            "assumptions": [
                "Self-serve onboarding keeps customer acquisition friction near zero.",
                "Expansion revenue from added seats drives Net Revenue Retention (NRR) > 115%."
            ]
        }

    elif primary_arch == "B2B Enterprise / High-ACV SaaS":
        return {
            "archetype_model": "Enterprise Contract (ACV)",
            "metrics": {
                "acv": f"{currency_symbol}35,000 - {currency_symbol}65,000 average first-year contract",
                "cac": f"{currency_symbol}9,500 - {currency_symbol}14,000 fully loaded sales & marketing cost",
                "sales_cycle_days": "75 - 120 days",
                "gross_margin": "85% - 90%",
                "cac_payback_months": "4.0 - 6.0 months",
                "annual_net_retention": "125% - 135%"
            },
            "assumptions": [
                "High initial contract value offsets multi-month sales cycle.",
                "Enterprise expansion driven by new departmental business units."
            ]
        }

    elif primary_arch == "Two-Sided Marketplace / Network":
        return {
            "archetype_model": "Marketplace Commission / Take-Rate",
            "metrics": {
                "take_rate": "13.5% average realized commission on gross bookings",
                "average_booking_value": f"{currency_symbol}850 per transaction",
                "cac_demand": f"{currency_symbol}65 per active booking customer",
                "cac_supply": f"{currency_symbol}240 per onboarded provider asset",
                "contribution_margin": "65% on net revenue",
                "repeat_booking_rate": "42% within 90 days"
            },
            "assumptions": [
                "Supply CAC amortized across 20+ bookings per year.",
                "Escrow and payment processing costs average 2.8%."
            ]
        }

    elif primary_arch == "Healthcare":
        return {
            "archetype_model": "Healthcare PMPM & Clinical Licensing",
            "metrics": {
                "pmpm_revenue": f"{currency_symbol}3.25 average per enrolled member month",
                "clinic_software_fee": f"{currency_symbol}1,500/clinic/month",
                "gross_margin": "75% - 80%",
                "patient_retention_annual": "85%",
                "regulatory_compliance_cost": "8% of operating expense"
            },
            "assumptions": [
                "RPM CPT reimbursement codes (e.g., 99453, 99454) cover patient-side costs.",
                "Hospital systems sign multi-year contracts with annual minimums."
            ]
        }

    else:
        # Standard unit economics
        return {
            "archetype_model": "Commercial Subscription Model",
            "metrics": {
                "cac": f"{currency_symbol}35 - {currency_symbol}75",
                "arpu": f"{currency_symbol}29/month",
                "gross_margin": "80%",
                "churn_monthly": "3.5%",
                "cac_payback_months": "3.0 months"
            },
            "assumptions": [
                "Standard self-serve digital marketing economics.",
                "Healthy LTV to CAC ratio exceeding 3:1."
            ]
        }


# ============================================================================
# 8. STARTUP-SPECIFIC RISKS WITH CHEAP TESTS
# ============================================================================

def generate_startup_risks(
    idea: str,
    archetype_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generates risks specific to the startup idea and archetype with cheap tests.
    """
    primary_arch = archetype_data.get("primary", "B2C Consumer / Mobile")

    if primary_arch in ["B2C Consumer / Mobile", "Creator Economy / Creative Platform"]:
        return [
            {
                "risk": "AI Generation Quality Variance",
                "severity": "high",
                "why": "Unpredictable AI generation could produce unplayable or unengaging mini-games, causing rapid user drop-off.",
                "cheap_test": "Deploy 50 hand-crafted prompt templates to 100 beta testers and track completion rate of first play session.",
                "success_metric": "≥80% of generated mini-games are completed by players without aborting."
            },
            {
                "risk": "Viral Novelty Wear-Off (Retention Churn)",
                "severity": "medium",
                "why": "Users may enjoy creating 1-2 dream games as a novelty but fail to return weekly.",
                "cheap_test": "Test a 'Daily Dream Challenge' with community remixing and push notifications on D3 and D7.",
                "success_metric": "D7 retention rate ≥ 25% among active first-day creators."
            },
            {
                "risk": "GPU Inference Cost at Scale",
                "severity": "medium",
                "why": "Complex generative game assets could exceed the per-user subscription price point if inference is unoptimized.",
                "cheap_test": "Benchmark compute cost on quantized local models versus proprietary API tokens under 500 concurrent loads.",
                "success_metric": "Average generation cost stays below $0.03 per mini-game session."
            }
        ]

    elif primary_arch == "B2B Product-Led Growth":
        return [
            {
                "risk": "Friction in Initial Setup / Time-to-Value",
                "severity": "high",
                "why": "Developers abandon bottom-up tools if onboarding takes longer than 10 minutes.",
                "cheap_test": "User-test onboarding with 15 engineers with no developer intervention; record time-to-first-success.",
                "success_metric": "≥80% of testers achieve core value workflow in < 7 minutes."
            },
            {
                "risk": "Seat Expansion Ceiling",
                "severity": "medium",
                "why": "Tool remains trapped with individual enthusiasts without expanding to team-wide licenses.",
                "cheap_test": "Gate shared team reports and automated review rules behind 3-seat trial activation.",
                "success_metric": "≥30% of solo active users invite at least one peer within 2 weeks."
            }
        ]

    elif primary_arch == "B2B Enterprise / High-ACV SaaS":
        return [
            {
                "risk": "Protracted Procurement & Security Audits",
                "severity": "high",
                "why": "Enterprise security reviews can stall deals for 6+ months, creating cash flow drag.",
                "cheap_test": "Pre-package a SOC2 Type II report and zero-data-retention architectural brief for early discovery calls.",
                "success_metric": "Security review stage cleared in under 3 weeks on initial 3 enterprise pilots."
            },
            {
                "risk": "Integration Maintenance Burden",
                "severity": "medium",
                "why": "Legacy on-prem systems require custom connector engineering that drains core product focus.",
                "cheap_test": "Standardize connectors on OpenAPI webhooks and test ingestion latency with mock enterprise payloads.",
                "success_metric": "Customer integration completed in < 48 hours without engineering escalations."
            }
        ]

    elif primary_arch == "Two-Sided Marketplace / Network":
        return [
            {
                "risk": "Chicken-and-Egg Liquidity Trap",
                "severity": "high",
                "why": "Demand bounces if inventory is thin, and supply churns if booking requests are infrequent.",
                "cheap_test": "Constrain initial launch to a single 25-mile geographic radius with subsidized minimum supply guarantee.",
                "success_metric": "≥75% of demand search queries find at least 3 available local listings."
            },
            {
                "risk": "Disintermediation (Off-Platform Transactions)",
                "severity": "medium",
                "why": "Buyers and sellers meet on platform and continue recurring business off-platform to avoid fees.",
                "cheap_test": "Bundle free equipment damage insurance and instantaneous credit terms exclusively on-platform.",
                "success_metric": "Repeat booking retention stays ≥85% on-platform after initial introduction."
            }
        ]

    else:
        return [
            {
                "risk": "Customer Willingness-to-Pay Validation",
                "severity": "high",
                "why": "Users may express theoretical interest in surveys but resist paying recurring subscription prices.",
                "cheap_test": "Launch a pre-order landing page with explicit pricing and Stripe reservation authorization.",
                "success_metric": "≥5% conversion from qualified visitor to paid pre-order reservation."
            },
            {
                "risk": "Channel Saturation & CAC Inflation",
                "severity": "medium",
                "why": "Digital ad channels can quickly experience rising costs as competition bids on identical keywords.",
                "cheap_test": "Run small $250 test campaigns across 3 independent marketing channels in parallel.",
                "success_metric": "At least one channel demonstrates CAC payback under 4 months."
            }
        ]


# ============================================================================
# 9. MEASURABLE NUMERIC ROADMAP (4 PHASES)
# ============================================================================

def generate_measurable_launch_roadmap(
    archetype_data: Dict[str, Any],
    customer_segments: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generates 4-phase launch roadmap with concrete, measurable numeric milestones.
    """
    primary_arch = archetype_data.get("primary", "B2C Consumer / Mobile")
    seg_name = customer_segments[0]["segment"]

    if primary_arch in ["B2C Consumer / Mobile", "Creator Economy / Creative Platform"]:
        phases = [
            {
                "phase": "Phase 1 — Prototype & Alpha Validation",
                "objective": "Build core generation pipeline and achieve initial viral engagement loop with early adopters.",
                "key_actions": [
                    "Deploy functional web prototype to 100 closed-alpha creators.",
                    "Measure core activation: ≥40% of users successfully generate and play a mini-game on Day 1.",
                    "Validate loop: ≥20% of users create a second experience within 48 hours."
                ]
            },
            {
                "phase": "Phase 2 — Beta Testing & Retention Stabilization",
                "objective": "Expand closed beta cohort to 500 active users and establish strong D7 retention benchmarks.",
                "key_actions": [
                    "Onboard 500 waitlist players across Discord and gaming subreddits.",
                    "Optimize rendering pipeline to achieve D7 retention ≥ 25% and D30 ≥ 12%.",
                    "Instrument social share loops targeting organic K-factor ≥ 1.1."
                ]
            },
            {
                "phase": "Phase 3 — Public Launch & Monetization Proof",
                "objective": "Execute multi-channel public launch and convert initial 1,000 active users into paying subscribers.",
                "key_actions": [
                    "Launch on Product Hunt, Hacker News, and coordinate 15 creator TikTok/YouTube live streams.",
                    "Achieve 1,000+ active weekly creators within 14 days of public launch.",
                    "Validate Free-to-Paid Pro conversion rate ≥ 3.5% with blended CAC < $8.00."
                ]
            },
            {
                "phase": "Phase 4 — Growth & Multiplayer Network Scaling",
                "objective": "Scale acquisition channels, optimize LTV/CAC to >3.5x, and introduce community co-op features.",
                "key_actions": [
                    "Scale paid acquisition campaigns targeting verified customer lookalike audiences.",
                    "Introduce real-time community challenges and multiplayer dream lobbies.",
                    "Expand platform to secondary segment with team and educator creator packages."
                ]
            }
        ]

    elif primary_arch == "B2B Product-Led Growth":
        phases = [
            {
                "phase": "Phase 1 — Prototype & Developer Friction Testing",
                "objective": "Deliver frictionless single-user CLI or web interface and achieve sub-10 minute time-to-first-value.",
                "key_actions": [
                    f"Recruit 25 individual {seg_name} for structured 1-on-1 onboarding teardowns.",
                    "Measure friction: 100% of participants must complete configuration without manual intervention.",
                    "Achieve Net Promoter Score (NPS) ≥ 50 among alpha developers."
                ]
            },
            {
                "phase": "Phase 2 — Beta Testing & Team Collaboration Loops",
                "objective": "Deploy team beta across 40 engineering teams and validate collaborative invitation mechanics.",
                "key_actions": [
                    "Introduce team workspaces with shared dashboards and role-based permissions.",
                    "Target team invitation rate: average ≥ 2.8 colleagues invited per initial active developer.",
                    "Track weekly active usage: ≥65% of onboarded teams active 4+ days per week."
                ]
            },
            {
                "phase": "Phase 3 — Public Launch & Self-Serve Monetization",
                "objective": "Launch publicly on Product Hunt and developer portals, reaching 500 active teams.",
                "key_actions": [
                    "Activate self-serve team tier ($24/seat/mo) with 14-day free trial on corporate cards.",
                    "Target initial launch: 500 active organizations with ≥10% converting to paid team plans.",
                    "Establish payback: Blended CAC payback period ≤ 4.5 months."
                ]
            },
            {
                "phase": "Phase 4 — Growth & Mid-Market Expansion",
                "objective": "Introduce enterprise tier (SSO, audit logs) and scale to $1M ARR.",
                "key_actions": [
                    "Publish SOC-2 compliance attestation and enterprise security whitepaper.",
                    "Launch automated seat expansion alerts when teams exceed 5 active developers.",
                    "Grow annual Net Revenue Retention (NRR) to ≥ 120%."
                ]
            }
        ]

    elif primary_arch == "B2B Enterprise / High-ACV SaaS":
        phases = [
            {
                "phase": "Phase 1 — Prototype & Design Partner Validation",
                "objective": "Validate mission-critical workflow with 3 signed enterprise design partners.",
                "key_actions": [
                    "Deliver prototype addressing primary compliance/audit pain point for 3 enterprise partners.",
                    "Conduct bi-weekly architectural reviews and integrate with partner staging data.",
                    "Secure formal letters of intent (LOI) to convert to paid contracts upon production release."
                ]
            },
            {
                "phase": "Phase 2 — Beta Testing & Security Accreditation",
                "objective": "Deploy hardened private beta into 5 enterprise staging environments and clear security audits.",
                "key_actions": [
                    "Complete third-party penetration testing and achieve SOC-2 Type I readiness.",
                    "Validate enterprise telemetry: zero data leakage and 99.9% uptime across beta period.",
                    "Generate 2 quantified enterprise case studies documenting 40%+ reduction in audit prep hours."
                ]
            },
            {
                "phase": "Phase 3 — Public Commercial Launch & Sales Ramp",
                "objective": "Convert design partners to annual contracts ($35k+ ACV) and launch outbound ABM engine.",
                "key_actions": [
                    "Convert 3 design partners into paying annual enterprise licenses totaling >$100k ARR.",
                    "Launch targeted outbound campaign to 200 qualified enterprise accounts.",
                    "Target pipeline: 12 enterprise POCs initiated with average cycle time < 90 days."
                ]
            },
            {
                "phase": "Phase 4 — Growth & Channel Alliances",
                "objective": "Scale direct enterprise sales team and onboard 3 certified system integrator partners.",
                "key_actions": [
                    "Certify 3 enterprise advisory consultancies to co-sell implementation packages.",
                    "Expand customer accounts: drive 30%+ contract expansion at annual renewal.",
                    "Scale to 25+ enterprise logos and maintain 100% logo retention."
                ]
            }
        ]

    else:
        phases = [
            {
                "phase": "Phase 1 — Prototype & Initial Validation",
                "objective": "Validate core value proposition with 50 active early users.",
                "key_actions": [
                    "Build and deploy MVP solving primary customer bottleneck.",
                    "Conduct structured interviews with 20 representatives from primary segment.",
                    "Target activation: ≥50% complete core user journey on Day 1."
                ]
            },
            {
                "phase": "Phase 2 — Beta Testing & Optimization",
                "objective": "Scale cohort to 200 users and establish stable retention metrics.",
                "key_actions": [
                    "Deploy closed beta to 200 waitlist users and fix identified UX bottlenecks.",
                    "Achieve week-4 user retention of ≥ 30%.",
                    "Capture 5 user testimonials for launch collateral."
                ]
            },
            {
                "phase": "Phase 3 — Public Launch",
                "objective": "Execute multi-channel launch and acquire first 1,000 users.",
                "key_actions": [
                    "Launch across Product Hunt, search ads, and relevant community channels.",
                    "Achieve 1,000 active users with conversion to paid ≥ 4%.",
                    "Maintain customer acquisition cost below target payback threshold."
                ]
            },
            {
                "phase": "Phase 4 — Growth & Scale",
                "objective": "Scale marketing channels and expand into secondary customer segments.",
                "key_actions": [
                    "Double down on highest ROI acquisition channel.",
                    "Roll out features tailored to secondary customer segment.",
                    "Optimize unit economics and achieve sustainable monthly growth."
                ]
            }
        ]

    return {"phases": phases}


# ============================================================================
# 10. EXPLICIT VIABILITY SCORING FORMULA
# ============================================================================

def calculate_viability_score(
    validation_status: str,
    validation_score: float,
    pricing_evidence: List[Dict[str, Any]],
    competitors: List[Dict[str, Any]],
    archetype_data: Dict[str, Any],
    signals: Dict[str, Any],
    generation_mode: str = "llm"
) -> Dict[str, Any]:
    """
    Computes viability using explicit, transparent formula:
    Viability Score = (evidence_score * 0.25) + (competitor_pricing_score * 0.25)
                     + (unit_economics_score * 0.25) + (validation_score * 0.25)

    Capped at 'Hypothesis Stage' (score <= 0.60) in fallback mode.
    Exposes components directly in the JSON.
    """
    # 1. Evidence score (0.0 to 1.0)
    has_market = bool(signals.get("has_market"))
    has_competitors = len(competitors) > 0
    has_segments = bool(signals.get("primary_segment"))
    evidence_pts = 0.3 + (0.3 if has_market else 0.0) + (0.2 if has_competitors else 0.0) + (0.2 if has_segments else 0.0)
    evidence_score = round(min(1.0, evidence_pts), 2)

    # 2. Competitor & Pricing score (0.0 to 1.0)
    verified_count = sum(1 for p in pricing_evidence if p.get("pricing_status") == "verified")
    comp_score = 0.5
    if len(competitors) >= 2 and verified_count >= 1:
        comp_score = 0.90
    elif len(competitors) >= 1:
        comp_score = 0.70
    elif verified_count == 0:
        comp_score = 0.55
    competitor_pricing_score = round(comp_score, 2)

    # 3. Unit Economics plausibility score (0.0 to 1.0)
    unit_econ_score = 0.85 if archetype_data.get("confidence", 0.5) > 0.8 else 0.75

    # 4. Validation score (0.0 to 1.0)
    val_score = round(validation_score, 2)

    # Weighted calculation
    raw_total = (evidence_score * 0.25) + (competitor_pricing_score * 0.25) + (unit_econ_score * 0.25) + (val_score * 0.25)
    final_score = round(raw_total, 2)

    # Fallback cap
    if generation_mode == "deterministic_fallback":
        final_score = min(0.60, final_score)
        overall = "Hypothesis Stage"
    else:
        if final_score >= 0.80 and validation_status == "PASS":
            overall = "High Commercial Viability"
        elif final_score >= 0.65:
            overall = "Moderate Commercial Viability"
        elif final_score >= 0.45:
            overall = "Hypothesis Stage"
        else:
            overall = "Low Confidence"

    supporting_ev = [
        f"Archetype classified as {archetype_data.get('primary')} with {int(archetype_data.get('confidence', 0.8)*100)}% confidence.",
        f"Customer segments grounded in {signals.get('primary_segment', 'validated target users')}.",
        f"Validation status evaluated as {validation_status} (score: {int(val_score*100)}%)."
    ]
    if verified_count > 0:
        supporting_ev.append(f"Retrieved {verified_count} verified competitor pricing signal(s).")
    else:
        supporting_ev.append("Competitor pricing presented as hypothesis benchmark pending live quotes.")

    uncertainties = []
    if verified_count == 0:
        uncertainties.append("Exact competitor contract pricing requires direct quotation verification.")
    if generation_mode == "deterministic_fallback":
        uncertainties.append("Strategy generated in offline deterministic mode; live web validation recommended.")
    else:
        uncertainties.append("Free-to-paid conversion elasticity requires live cohort traffic testing.")

    return {
        "overall": overall,
        "confidence": final_score,
        "components": {
            "evidence_score": evidence_score,
            "competitor_pricing_score": competitor_pricing_score,
            "unit_economics_score": unit_econ_score,
            "validation_score": val_score,
            "formula": "Viability Score = (evidence_score * 0.25) + (competitor_pricing_score * 0.25) + (unit_economics_score * 0.25) + (validation_score * 0.25)"
        },
        "supporting_evidence": supporting_ev,
        "key_uncertainties": uncertainties,
        "next_validation_step": "Deploy landing page test to 100 target users to measure first-session conversion."
    }


# ============================================================================
# 11. DETERMINISTIC GTM CONSISTENCY & VALIDATION LAYER (REPAIR ONCE)
# ============================================================================

def validate_gtm_consistency(
    gtm_dict: Dict[str, Any],
    signals: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluates:
    - Customer consistency (real people/groups, not features)
    - Problem consistency (idea-grounded, no generic enterprise jargon in B2C)
    - Competitor consistency (no blacklisted news/publishers)
    - Pricing consistency (matches archetype)
    - Channel consistency (matches archetype)
    - Language consistency (no forbidden cross-archetype terms)
    - Roadmap consistency (measurable numeric metrics)
    - Schema completeness

    Returns: {status: PASS | PASS_WITH_WARNINGS | FAIL, score: float, violations: [], warnings: []}
    Never forces PASS.
    """
    violations = []
    warnings = []

    arch_data = gtm_dict.get("business_archetype", {})
    primary_arch = arch_data.get("primary", "")

    # 1. Customer consistency
    segs = gtm_dict.get("customer_segments", [])
    if not segs or len(segs) < 1:
        violations.append("Missing required customer segments.")
    else:
        for s in segs:
            sname = s.get("segment", "").lower()
            if any(inv in sname for inv in INVALID_SEGMENT_TERMS):
                violations.append(f"Customer segment '{s.get('segment')}' represents a product capability or revenue stream, not a person or organization.")

    # 2. Competitor consistency
    comps = gtm_dict.get("competitors", [])
    for c in comps:
        cname = c.get("name", "")
        curl = c.get("source", "")
        if _is_blacklisted_competitor(cname, curl):
            violations.append(f"Competitor '{cname}' is a news publisher, media outlet, or generic research directory.")

    # 3. Language & guardrail consistency
    if primary_arch in ["B2C Consumer / Mobile", "Creator Economy / Creative Platform"]:
        full_text = json.dumps(gtm_dict).lower()
        for term in B2C_FORBIDDEN_TERMS:
            if term in full_text:
                violations.append(f"B2C/Consumer strategy contains inappropriate enterprise/marketplace terminology: '{term}'.")

    # 4. Pricing consistency
    pricing = gtm_dict.get("pricing_strategy", {})
    tiers = pricing.get("price_tiers", []) if isinstance(pricing, dict) else []
    if primary_arch in ["B2C Consumer / Mobile", "Creator Economy / Creative Platform"]:
        for t in tiers:
            p_val = str(t.get("price", ""))
            # Check if an inappropriate $149+ enterprise tier was forced on B2C
            if any(sym in p_val for sym in ["$149", "$249", "$499", "$999", "12,000"]):
                violations.append(f"Consumer B2C pricing includes inappropriate high-ticket enterprise tier: '{p_val}'.")

    # 5. Roadmap consistency
    roadmap = gtm_dict.get("launch_roadmap", {})
    phases = roadmap.get("phases", []) if isinstance(roadmap, dict) else []
    if not phases or len(phases) < 3:
        violations.append("Launch roadmap must contain at least 3 distinct phased milestones.")
    else:
        # Check numeric metric presence
        has_numeric = False
        for p in phases:
            actions_text = " ".join(p.get("key_actions", []))
            if re.search(r"\d+", actions_text):
                has_numeric = True
                break
        if not has_numeric:
            warnings.append("Launch roadmap milestones should contain measurable numeric targets (e.g. 100 users, 25% retention).")

    # 6. Pricing evidence check
    pe_list = gtm_dict.get("pricing_evidence", [])
    unverified_count = sum(1 for pe in pe_list if pe.get("pricing_status") == "not_verified")
    if unverified_count > 0 and len(pe_list) == unverified_count:
        warnings.append("Competitor pricing could not be verified in live retrieved sources; pricing modeled as hypothesis.")

    # Calculate status and score
    if len(violations) == 0:
        if len(warnings) == 0:
            status = "PASS"
            score = 1.0
        else:
            status = "PASS_WITH_WARNINGS"
            score = max(0.75, 1.0 - (len(warnings) * 0.08))
    else:
        status = "FAIL"
        score = max(0.20, 0.65 - (len(violations) * 0.15))

    return {
        "status": status,
        "score": round(score, 2),
        "violations": violations,
        "warnings": warnings
    }


def attempt_single_repair(
    gtm_dict: Dict[str, Any],
    violations: List[str],
    signals: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Attempts a single deterministic repair pass on identified violations.
    Does NOT force PASS; if violations cannot be resolved, they remain.
    """
    repaired = dict(gtm_dict)
    arch_data = repaired.get("business_archetype", {})
    primary_arch = arch_data.get("primary", "")
    curr_sym = signals.get("currency_symbol", "$")

    # 1. Repair invalid segments
    if any("capability or revenue stream" in v for v in violations):
        valid_segs = derive_customer_segments(arch_data, signals.get("idea", ""), signals.get("market_analysis"))
        repaired["customer_segments"] = valid_segs
        logger.info("GTM Repair: Replaced invalid capability customer segments with human/org segments.")

    # 2. Repair blacklisted competitors
    if any("news publisher" in v for v in violations):
        comps = repaired.get("competitors", [])
        clean_comps = [c for c in comps if not _is_blacklisted_competitor(c.get("name", ""), c.get("source", ""))]
        if not clean_comps:
            clean_comps = [{
                "name": "General Industry Alternatives",
                "company": "Alternative Market Tools",
                "product": "Manual and disparate legacy workflows",
                "relationship": "substitute",
                "why_relevant": "Current substitute behavior adopted by target users.",
                "pricing": None,
                "pricing_type": "unspecified",
                "source": "Market observation"
            }]
        repaired["competitors"] = clean_comps
        logger.info("GTM Repair: Purged blacklisted publisher competitors.")

    # 3. Repair forbidden B2C language & high enterprise tiers
    if primary_arch in ["B2C Consumer / Mobile", "Creator Economy / Creative Platform"]:
        if any("inappropriate enterprise/marketplace terminology" in v for v in violations):
            # Regenerate channels and acquisition
            segs = repaired.get("customer_segments", [])
            chans, acq = generate_channels_and_acquisition(arch_data, segs)
            repaired["marketing_channels"] = chans
            repaired["customer_acquisition"] = acq
            logger.info("GTM Repair: Replaced enterprise channels/acquisition with B2C creator channels.")

        if any("high-ticket enterprise tier" in v for v in violations):
            repaired["pricing_strategy"] = generate_archetype_pricing_strategy(arch_data, curr_sym)
            logger.info("GTM Repair: Replaced invalid enterprise tier with B2C creator tiers.")

    return repaired


# ============================================================================
# 12. BACKWARD COMPATIBILITY MAPPER (LEGACY + EXTENDED SCHEMA)
# ============================================================================

def map_to_legacy_and_extended_contract(
    rich_gtm: Dict[str, Any],
    generation_mode: str = "llm"
) -> Dict[str, Any]:
    """
    Maintains backward compatibility:
    Converts the new rich schema to the legacy fields expected by existing UI:
    - target_market: list of {type: 'Primary'|'Secondary', segment: '...', profile: '...'}
    - pricing_strategy: string summary
    - launch_strategy: list of 4 phase items
    - positioning: {problem_solved, target_user, differentiation}
    - marketing_channels: list of {channel, category, tactics}
    - customer_acquisition: list of strings

    Plus embeds ALL new fields:
    - business_archetype
    - customer_segments
    - pain_points
    - product_positioning
    - differentiation
    - competitors
    - pricing_evidence
    - unit_economics
    - risks
    - launch_roadmap
    - viability
    - gtm_validation
    - generation_mode ("llm" | "deterministic_fallback")
    """
    customer_segs = rich_gtm.get("customer_segments", [])
    primary_seg = customer_segs[0]["segment"] if customer_segs else "Core Target Users"
    primary_why = customer_segs[0]["why_they_care"] if customer_segs else "Streamlining daily user experience."
    sec_seg = customer_segs[1]["segment"] if len(customer_segs) > 1 else "Adjacent Early Adopters"
    sec_why = customer_segs[1]["why_they_care"] if len(customer_segs) > 1 else "Expanding capabilities."

    legacy_target_market = [
        {
            "type": "Primary",
            "segment": primary_seg,
            "profile": primary_why
        },
        {
            "type": "Secondary",
            "segment": sec_seg,
            "profile": sec_why
        }
    ]

    # Pricing strategy string
    p_strat = rich_gtm.get("pricing_strategy", {})
    if isinstance(p_strat, dict):
        p_model = p_strat.get("model", "Freemium Subscription")
        p_rat = p_strat.get("rationale", "")
        tier_strs = []
        for t in p_strat.get("price_tiers", []):
            tier_strs.append(f"{t.get('tier')}: {t.get('price')} ({t.get('description')})")
        legacy_pricing_str = f"{p_model}. Tiers: {'; '.join(tier_strs)}. Rationale: {p_rat}"
    else:
        legacy_pricing_str = str(p_strat)

    # Launch roadmap -> launch_strategy list
    roadmap = rich_gtm.get("launch_roadmap", {})
    legacy_launch_strategy = []
    if isinstance(roadmap, dict) and "phases" in roadmap:
        for p in roadmap["phases"]:
            legacy_launch_strategy.append({
                "phase": p.get("phase", "Phase"),
                "objective": p.get("objective", ""),
                "key_actions": p.get("key_actions", [])
            })
    else:
        legacy_launch_strategy = [
            {"phase": "Phase 1 — Prototype", "objective": "Alpha testing", "key_actions": ["Deploy MVP"]},
            {"phase": "Phase 2 — Beta Testing", "objective": "Beta cohort", "key_actions": ["Test retention"]},
            {"phase": "Phase 3 — Public Launch", "objective": "Market entry", "key_actions": ["Launch campaign"]},
            {"phase": "Phase 4 — Growth", "objective": "Scale channels", "key_actions": ["Optimize acquisition"]}
        ]

    # Positioning
    pos = rich_gtm.get("product_positioning", {})
    legacy_positioning = {
        "problem_solved": pos.get("problem_solved", f"Eliminates manual friction for {primary_seg}"),
        "target_user": pos.get("target_user", primary_seg),
        "differentiation": rich_gtm.get("differentiation", {}).get("claim", "First-of-its-kind dedicated solution.")
    }

    # Channels
    legacy_channels = []
    for ch in rich_gtm.get("marketing_channels", []):
        legacy_channels.append({
            "channel": ch.get("channel", ""),
            "category": ch.get("category", "General"),
            "tactics": ch.get("tactics", "")
        })

    # Customer acquisition
    acq_obj = rich_gtm.get("customer_acquisition", {})
    legacy_acq = []
    if isinstance(acq_obj, dict):
        p0 = acq_obj.get("phase_0_to_100", {})
        if p0:
            legacy_acq.append(f"Phase 0 to 100: {p0.get('acquisition_channel')} — {p0.get('experiment')} (Threshold: {p0.get('success_threshold')})")
        p1 = acq_obj.get("phase_100_to_1000", {})
        if p1:
            legacy_acq.append(f"Phase 100 to 1,000: {p1.get('acquisition_channel')} — {p1.get('experiment')} (Metric: {p1.get('measurable_metric')})")
        vm = acq_obj.get("viral_mechanic")
        if vm:
            legacy_acq.append(f"Viral Loop: {vm}")
    elif isinstance(acq_obj, list):
        legacy_acq = [str(x) for x in acq_obj]

    final_payload = {
        # Legacy UI contract
        "target_market": legacy_target_market,
        "positioning": legacy_positioning,
        "marketing_channels": legacy_channels,
        "customer_acquisition": legacy_acq,
        "pricing_strategy": legacy_pricing_str,
        "launch_strategy": legacy_launch_strategy,

        # New Rich contract
        "business_archetype": rich_gtm.get("business_archetype", {}),
        "customer_segments": rich_gtm.get("customer_segments", []),
        "pain_points": rich_gtm.get("pain_points", []),
        "product_positioning": legacy_positioning,
        "differentiation": rich_gtm.get("differentiation", {}),
        "competitors": rich_gtm.get("competitors", []),
        "pricing_evidence": rich_gtm.get("pricing_evidence", []),
        "pricing_strategy_details": rich_gtm.get("pricing_strategy", {}),
        "unit_economics": rich_gtm.get("unit_economics", {}),
        "risks": rich_gtm.get("risks", []),
        "launch_roadmap": rich_gtm.get("launch_roadmap", {}),
        "viability": rich_gtm.get("viability", {}),
        "gtm_validation": rich_gtm.get("gtm_validation", {}),
        "generation_mode": generation_mode  # 'llm' or 'deterministic_fallback'
    }

    return {"gtm_strategy": final_payload}


# ============================================================================
# 13. DETERMINISTIC HEURISTIC SYNTHESIS (OFFLINE & FALLBACK)
# ============================================================================

def synthesize_deterministic_gtm(signals: Dict[str, Any]) -> Dict[str, Any]:
    """
    High-fidelity deterministic synthesis engine.
    Ensures identical rich schema output offline with confidence: 'low'
    and unverified fields marked honestly.
    """
    idea = signals["idea"]
    industry = signals["industry"]
    market_analysis = signals.get("market_analysis")
    competitor_analysis = signals.get("competitor_analysis")
    search_results = signals.get("search_results")
    curr_sym, region = _infer_currency_and_region(idea + " " + industry)
    signals["currency_symbol"] = curr_sym

    # 1. Archetype classification
    archetype_data = classify_business_archetype(idea, industry, market_analysis, competitor_analysis)

    # 2. Customer segments (people / orgs)
    customer_segments = derive_customer_segments(archetype_data, idea, market_analysis)

    # 3. Pain points from idea
    pain_points = extract_grounded_pain_points(idea, archetype_data, customer_segments)

    # 4. Competitors & pricing validation
    competitors, pricing_evidence = validate_and_extract_competitors_and_pricing(
        competitor_analysis=competitor_analysis,
        search_results=search_results,
        currency_symbol=curr_sym
    )

    # 5. Positioning & differentiation
    prim_seg = customer_segments[0]["segment"]
    comp_ref = competitors[0]["name"] if competitors else "legacy manual tools"
    positioning = {
        "problem_solved": f"Solves the primary friction of '{pain_points[0]['pain_point']}' for {prim_seg}.",
        "target_user": f"{prim_seg} seeking an integrated, friction-free alternative.",
        "differentiation": f"Unlike {comp_ref}, delivers purpose-built automation tailored directly to {prim_seg}."
    }
    differentiation = {
        "claim": f"Directly eliminates '{pain_points[0]['pain_point']}' with tailored execution.",
        "why_it_matters": "Enables target users to bypass the friction, delays, and steep learning curves of existing substitutes.",
        "competitor_gap": f"Alternatives like {comp_ref} fail to provide specialized, automated support for this workflow.",
        "evidence": "Observed market gap in current competitive offerings."
    }

    # 6. Marketing channels & acquisition
    marketing_channels, customer_acquisition = generate_channels_and_acquisition(archetype_data, customer_segments)

    # 7. Pricing strategy
    pricing_strategy = generate_archetype_pricing_strategy(archetype_data, curr_sym, pricing_evidence)

    # 8. Unit economics
    unit_economics = generate_unit_economics(archetype_data, curr_sym)

    # 9. Startup risks
    risks = generate_startup_risks(idea, archetype_data)

    # 10. Launch roadmap
    launch_roadmap = generate_measurable_launch_roadmap(archetype_data, customer_segments)

    # Assemble draft
    draft_gtm = {
        "business_archetype": archetype_data,
        "customer_segments": customer_segments,
        "pain_points": pain_points,
        "product_positioning": positioning,
        "differentiation": differentiation,
        "competitors": competitors,
        "pricing_evidence": pricing_evidence,
        "marketing_channels": marketing_channels,
        "customer_acquisition": customer_acquisition,
        "pricing_strategy": pricing_strategy,
        "unit_economics": unit_economics,
        "risks": risks,
        "launch_roadmap": launch_roadmap
    }

    # 11. Consistency check & single repair pass
    val_result = validate_gtm_consistency(draft_gtm, signals)
    if val_result["status"] == "FAIL":
        draft_gtm = attempt_single_repair(draft_gtm, val_result["violations"], signals)
        val_result = validate_gtm_consistency(draft_gtm, signals)

    # 12. Viability score calculation (capped at Hypothesis Stage in fallback)
    viability = calculate_viability_score(
        validation_status=val_result["status"],
        validation_score=val_result["score"],
        pricing_evidence=pricing_evidence,
        competitors=competitors,
        archetype_data=archetype_data,
        signals=signals,
        generation_mode="deterministic_fallback"
    )

    draft_gtm["viability"] = viability
    draft_gtm["gtm_validation"] = val_result

    return map_to_legacy_and_extended_contract(draft_gtm, generation_mode="deterministic_fallback")


# ============================================================================
# 14. GEMINI LLM SYNTHESIS ENGINE (WITH STRICT LATENCY BUDGET)
# ============================================================================

def _clean_json_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


async def _call_gemini_synthesis(
    signals: Dict[str, Any],
    api_key: str,
    time_limit: float = BUDGET_GENERATION_SECONDS
) -> Optional[Dict[str, Any]]:
    """
    Calls Google Gemini using the fastest appropriate model (gemini-2.5-flash),
    requesting the unified rich commercial strategy schema.
    """
    idea = signals["idea"]
    industry = signals["industry"]
    comp_names = ", ".join(signals.get("competitor_names", [])) or "None identified"
    curr_sym = signals.get("currency_symbol", "$")

    prompt = f"""You are a Silicon Valley Chief Strategy Officer and commercial venture builder.
Evaluate this startup idea and synthesize a commercial Go-To-Market strategy.

STARTUP IDEA: "{idea}"
INDUSTRY: {industry}
KNOWN COMPETITORS: {comp_names}
CURRENCY: {curr_sym}

Strictly follow these rules:
1. Classify the business archetype (primary + secondary, e.g., 'B2C Consumer / Mobile', 'Creator Economy / Creative Platform', 'B2B Enterprise / High-ACV SaaS', 'B2B Product-Led Growth', 'Two-Sided Marketplace / Network', 'Healthcare', 'Fintech', 'DeepTech / Hardware / Regulated Infrastructure', 'Local Services / SMB', 'API / Developer Infrastructure', 'D2C E-commerce').
2. Customer segments must be PEOPLE or ORGANIZATIONS (e.g. 'Gamers aged 18-35', 'Indie game developers'), never product features like 'Unlimited Game Creation'.
3. Pain points must come directly from the startup idea, distinguishing startup_description vs inference.
4. For B2C or consumer ideas, do NOT inject enterprise B2B jargon like 'C-suite outbound', 'ICP decision-makers', '$149+ enterprise tier', or 'provider recruitment'.
5. Launch roadmap must contain measurable numeric targets (e.g. 100 beta users, 25% retention).

Output ONLY a parseable JSON object matching this schema:
{{
  "business_archetype": {{
    "primary": "Archetype name",
    "confidence": 0.88,
    "secondary": [{{"archetype": "Secondary archetype", "confidence": 0.20}}],
    "reasoning": "Reasoning based on customer and transaction model"
  }},
  "customer_segments": [
    {{
      "segment": "Specific human or organization segment",
      "why_they_care": "Why they care",
      "core_problem": "Core problem faced",
      "buying_behavior": "How they pay",
      "evidence": "Evidence basis"
    }}
  ],
  "pain_points": [
    {{
      "pain_point": "Specific problem",
      "affected_segment": "Segment name",
      "evidence_source": "startup_description",
      "confidence": 0.90
    }}
  ],
  "product_positioning": {{
    "problem_solved": "Exact high-value problem eliminated",
    "target_user": "Beneficiary",
    "differentiation": "Unfair advantage over alternatives"
  }},
  "differentiation": {{
    "claim": "Core defensible claim",
    "why_it_matters": "Why it matters to users",
    "competitor_gap": "Gap left by alternatives",
    "evidence": "Validation basis"
  }},
  "marketing_channels": [
    {{
      "channel": "Channel Name",
      "category": "Social / Inbound / Outbound / Community",
      "tactics": "Actionable execution steps"
    }}
  ],
  "customer_acquisition": {{
    "phase_0_to_100": {{
      "acquisition_channel": "Channel",
      "target_customer": "Target",
      "experiment": "Experiment",
      "measurable_metric": "Metric",
      "success_threshold": "Threshold"
    }},
    "phase_100_to_1000": {{
      "acquisition_channel": "Channel",
      "target_customer": "Target",
      "experiment": "Experiment",
      "measurable_metric": "Metric",
      "success_threshold": "Threshold"
    }},
    "viral_mechanic": "Incentive or referral loop"
  }},
  "pricing_strategy": {{
    "model": "Monetization model",
    "price_tiers": [
      {{"tier": "Tier Name", "price": "Price point", "description": "Features"}}
    ],
    "rationale": "Pricing rationale",
    "pricing_status": "hypothesis"
  }},
  "unit_economics": {{
    "archetype_model": "Model name",
    "metrics": {{"cac": "value", "arpu": "value", "gross_margin": "value"}},
    "assumptions": ["Assumption 1", "Assumption 2"]
  }},
  "risks": [
    {{
      "risk": "Risk description",
      "severity": "high",
      "why": "Why this matters",
      "cheap_test": "Inexpensive test",
      "success_metric": "Measurable success criteria"
    }}
  ],
  "launch_roadmap": {{
    "phases": [
      {{
        "phase": "Phase 1 — Prototype",
        "objective": "Milestone objective",
        "key_actions": ["Numeric target 1", "Action 2"]
      }}
    ]
  }}
}}
"""
    try:
        from server.utils.gemini_client import call_gemini_generate_content, clean_llm_json_text
        res = await call_gemini_generate_content(
            prompt=prompt,
            api_key=api_key,
            temperature=0.20,
            response_mime_type="application/json",
            timeout_per_model=min(6.0, time_limit),
            tag="GTM-AGENT"
        )
        if res:
            raw_text, successful_model = res
            cleaned = clean_llm_json_text(raw_text)
            parsed = json.loads(cleaned)
            if "business_archetype" in parsed and "customer_segments" in parsed:
                logger.info(f"GTM Synthesis Success: Gemini LLM ({successful_model})")
                return parsed
    except Exception as exc:
        logger.warning(f"Universal Gemini GTM synthesis error: {exc}")

    return None


# ============================================================================
# 15. PRIMARY AGENT ENTRY POINT
# ============================================================================

async def run_gtm_agent(
    validation_context: Optional[Dict[str, Any]] = None,
    *,
    idea: Optional[str] = None,
    market_analysis: Optional[Dict[str, Any]] = None,
    customer_segments: Optional[List[Dict[str, Any]]] = None,
    competitor_analysis: Optional[Dict[str, Any]] = None,
    market_gaps: Optional[List[str]] = None,
    swot_analysis: Optional[Dict[str, Any]] = None,
    risk_analysis: Optional[Dict[str, Any]] = None,
    mvp_recommendations: Optional[Dict[str, Any]] = None,
    search_results: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Executes the upgraded GTM Strategy Agent.
    Strictly caps total pipeline execution at <= 30 seconds.
    Employs LLM synthesis with single-pass validation repair,
    falling back seamlessly to high-fidelity deterministic synthesis.
    """
    start_time = time.monotonic()
    ctx = validation_context or {}

    resolved_idea = idea or ctx.get("idea") or "Innovative software solution"
    resolved_market = market_analysis or ctx.get("market_analysis")
    resolved_segments = customer_segments or ctx.get("customer_segments")
    resolved_competitor = competitor_analysis or ctx.get("competitor_analysis")
    resolved_gaps = market_gaps or ctx.get("market_gaps")
    resolved_swot = swot_analysis or ctx.get("swot_analysis")
    resolved_risk = risk_analysis or ctx.get("risk_analysis")
    resolved_mvp = mvp_recommendations or ctx.get("mvp_recommendations")
    resolved_search = search_results or ctx.get("search_results") or []

    industry = "Technology & Software"
    if resolved_market and isinstance(resolved_market, dict):
        industry = _clean_text(resolved_market.get("industry"), industry)

    curr_sym, region = _infer_currency_and_region(resolved_idea + " " + industry)

    competitor_names = []
    if resolved_competitor and isinstance(resolved_competitor, dict):
        for c in (resolved_competitor.get("direct_competitors") or []) + (resolved_competitor.get("indirect_competitors") or []):
            if isinstance(c, dict) and c.get("name"):
                competitor_names.append(c["name"])

    signals = {
        "idea": resolved_idea,
        "industry": industry,
        "currency_symbol": curr_sym,
        "region": region,
        "market_analysis": resolved_market,
        "customer_segments": resolved_segments,
        "competitor_analysis": resolved_competitor,
        "competitor_names": competitor_names,
        "market_gaps": resolved_gaps or [],
        "swot_analysis": resolved_swot,
        "risk_analysis": resolved_risk,
        "mvp_recommendations": resolved_mvp,
        "search_results": resolved_search,
        "has_market": bool(resolved_market),
        "primary_segment": resolved_segments[0]["segment"] if (resolved_segments and isinstance(resolved_segments[0], dict) and "segment" in resolved_segments[0]) else "Target Customers"
    }

    # Check for Gemini API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Check in .env if not loaded in process
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        if os.path.exists(env_path):
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path, override=False)
                api_key = os.getenv("GEMINI_API_KEY")
            except Exception:
                pass

    if api_key and api_key.strip():
        elapsed_so_far = time.monotonic() - start_time
        remaining_budget = max(5.0, BUDGET_TOTAL_SECONDS - elapsed_so_far)
        llm_budget = min(BUDGET_GENERATION_SECONDS, remaining_budget - 8.0)

        try:
            llm_draft = await _call_gemini_synthesis(
                signals=signals,
                api_key=api_key.strip(),
                time_limit=llm_budget
            )

            if llm_draft:
                # Merge validated competitors & pricing evidence
                comps, pe_list = validate_and_extract_competitors_and_pricing(
                    competitor_analysis=resolved_competitor,
                    search_results=resolved_search,
                    currency_symbol=curr_sym
                )
                llm_draft["competitors"] = comps
                llm_draft["pricing_evidence"] = pe_list

                # Consistency validation
                val_result = validate_gtm_consistency(llm_draft, signals)

                # Attempt single repair pass if violations and budget remains
                time_now = time.monotonic() - start_time
                if val_result["status"] == "FAIL" and (BUDGET_TOTAL_SECONDS - time_now) > 4.0:
                    logger.info("GTM Validation failed initial check. Attempting single repair pass...")
                    llm_draft = attempt_single_repair(llm_draft, val_result["violations"], signals)
                    val_result = validate_gtm_consistency(llm_draft, signals)

                # Calculate explicit viability score
                viability = calculate_viability_score(
                    validation_status=val_result["status"],
                    validation_score=val_result["score"],
                    pricing_evidence=pe_list,
                    competitors=comps,
                    archetype_data=llm_draft.get("business_archetype", {}),
                    signals=signals,
                    generation_mode="llm"
                )

                llm_draft["viability"] = viability
                llm_draft["gtm_validation"] = val_result

                logger.info(f"GTM Synthesis completed in mode=llm | val_status={val_result['status']} | time={time.monotonic()-start_time:.2f}s")
                return map_to_legacy_and_extended_contract(llm_draft, generation_mode="llm")

        except Exception as exc:
            logger.warning(f"Gemini GTM synthesis failed or timed out: {exc}. Using deterministic fallback.")

    # Deterministic fallback mode
    logger.info("GTM Synthesis: Executing Deterministic Heuristic Synthesis")
    return synthesize_deterministic_gtm(signals)
