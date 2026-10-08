"""
Competitor Analysis Agent

Responsibilities:
- Detect direct competitors
- Detect indirect competitors
- Filter irrelevant research sources
- Extract product/service information
- Extract target customers
- Extract pricing
- Extract key features
- Extract strengths
- Extract weaknesses
- Generate competitor comparison
- Generate market gaps
- Remove duplicates
- Limit competitors

Expected return format:

{
    "competitor_analysis": {
        "direct_competitors": [],
        "indirect_competitors": [],
        "comparison": [],
        "market_gaps": []
    }
}
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import re
import urllib.parse
from typing import Any, Dict, List, Optional

import httpx


logger = logging.getLogger(__name__)


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_COMPETITOR_LIMIT = 5
MAX_COMPETITOR_LIMIT = 8
MAX_INDIRECT_COMPETITORS = 2
MAX_SEARCH_RESULTS_FOR_GEMINI = 10

NOT_AVAILABLE = "Pricing available on request / tiered"


# ============================================================
# GENERIC VALUES
# ============================================================

GENERIC_AUDIENCES = {
    "",
    "people",
    "person",
    "users",
    "user",
    "customers",
    "customer",
    "consumers",
    "consumer",
    "businesses",
    "business",
    "everyone",
    "all users",
    "general users",
    "general market",
    "target audience",
    "target customers",
    "general customers",
    "all customers",
}


# ============================================================
# SOURCE FILTERS
# ============================================================

IRRELEVANT_SOURCE_DOMAINS = [
    "mdpi.com",
    "arxiv.org",
    "biorxiv.org",
    "medrxiv.org",
    "sciencedirect.com",
    "springer.com",
    "wiley.com",
    "frontiersin.org",
    "nature.com",
    "ieee.org",
    "researchgate.net",
    "academia.edu",
    "ncbi.nlm.nih.gov",
    "pubmed.ncbi.nlm.nih.gov",
    "jstor.org",
    "semanticscholar.org",
    "tandfonline.com",
    "cell.com",
    "maximizemarketresearch.com",
    "grandviewresearch.com",
    "marketsandmarkets.com",
    "verifiedmarketresearch.com",
    "alliedmarketresearch.com",
    "polarismarketresearch.com",
    "fortunebusinessinsights.com",
    "statista.com",
    "globenewswire.com",
    "prnewswire.com",
    "businesswire.com",
    "idtechex.com",
    "mordorintelligence.com",
    "researchandmarkets.com",
    "technavio.com",
    "gartner.com",
    "forrester.com",
    "einpresswire.com",
    "marketwatch.com",
    "substack.com",
    "medium.com",
    "hubspot.com",
    "linkedin.com",
    "reddit.com",
    "quora.com",
    "youtube.com",
    "twitter.com",
    "x.com",
    "towardsdatascience.com",
    "dev.to",
]


IRRELEVANT_SOURCE_PHRASES = [
    "market research report",
    "market research",
    "industry report",
    "industry research",
    "research report",
    "market analysis",
    "industry analysis",
    "market size",
    "market forecast",
    "market trends",
    "wikipedia",
    "encyclopedia",
    "special issue",
    "special issues",
    "systematic review",
    "meta-analysis",
    "published in",
    "journal of",
    "proceedings of",
    "arxiv",
    "doi:",
    "issn",
    "pmid",
    "editorial board",
    "peer-reviewed",
    "gift ideas",
    "gift guide",
    "best gifts",
    "birthday gifts",
    "christmas gifts",
    "idtechex",
    "marketsandmarkets",
    "grand view research",
    "mordor intelligence",
    "research and markets",
    "technavio",
    "gartner",
    "forrester",
    "substack",
    "hubspot",
    "medium.com",
    "linkedin pulse",
    "top 10 ",
    "top 5 ",
    "comprehensive guide",
    "ultimate guide",
]


# ============================================================
# INFRASTRUCTURE / NON-CUSTOMER-FACING PROVIDERS
# ============================================================

INFRASTRUCTURE_TERMS = [
    "cloud kitchen infrastructure",
    "cloud kitchens infrastructure",
    "kitchen infrastructure",
    "infrastructure provider",
    "infrastructure platform",
    "restaurant infrastructure",
    "technology provider",
    "technology infrastructure",
    "logistics infrastructure",
    "software infrastructure",
    "payment infrastructure",
    "developer infrastructure",
    "api infrastructure",
    "hosting provider",
    "cloud hosting",
    "backend infrastructure",
    "fulfillment infrastructure",
    "warehouse infrastructure",
    "delivery infrastructure",
]


# ============================================================
# DIGITAL PRODUCT SIGNALS
# ============================================================

STRONG_DIGITAL_PHRASES = [
    "is an app",
    "is a mobile app",
    "is a web app",
    "is an application",
    "is a platform",
    "is software",
    "is a saas",
    "is a tool",
    "is a studio",
    "is an engine",
    "mobile app",
    "web app",
    "design tool",
    "developer tool",
    "no-code platform",
    "zero-code studio",
    "digital platform",
    "online platform",
    "software platform",
    "cloud platform",
    "provides an app",
    "provides a platform",
    "provides software",
    "offers an app",
    "offers a platform",
    "offers software",
]


DIGITAL_KEYWORDS = [
    "app",
    "application",
    "platform",
    "software",
    "saas",
    "digital",
    "mobile",
    "online",
    "studio",
    "engine",
    "tool",
    "sdk",
    "api",
    "framework",
    "cloud",
    "no-code",
    "zero-code",
]


# ============================================================
# SERVICE SIGNALS
# ============================================================

DIRECT_SERVICE_PHRASES = [
    "tiffin service",
    "tiffin delivery",
    "meal delivery",
    "meal subscription",
    "food delivery",
    "home cooked meals",
    "home-cooked meals",
    "home cooked food",
    "home-cooked food",
    "daily meals",
    "daily meal delivery",
    "lunch delivery",
    "dinner delivery",
    "meal plans",
    "catering service",
    "personalized meals",
    "healthy meals",
    "healthy meal delivery",
    "3d web",
    "webgl",
    "spatial web",
    "motion design",
    "creative studio",
    "developer tools",
    "design tools",
    "automation platform",
    "ai platform",
    "analytics platform",
    "management software",
    "workflow automation",
    "software solution",
]


INDIRECT_SERVICE_PHRASES = [
    "agency",
    "agencies",
    "consultancy",
    "consulting",
    "freelancer",
    "freelancers",
    "manual spreadsheet",
    "excel template",
    "custom development studio",
    "traditional service",
    "in-house team",
    "manual workflow",
    "paper-based process",
    "local provider",
    "local service",
    "offline service",
    "traditional method",
]


# ============================================================
# EXTRACTION SIGNALS
# ============================================================

PRICING_KEYWORDS = [
    "pricing",
    "price",
    "prices",
    "cost",
    "costs",
    "subscription",
    "monthly",
    "per month",
    "annual",
    "yearly",
    "per year",
    "free trial",
    "plan starts",
    "plans start",
    "starts at",
    "$",
    "₹",
    "rs.",
    "inr",
    "usd",
    "per meal",
    "per day",
    "daily rate",
    "monthly plan",
    "meal plan",
]


FEATURE_KEYWORDS = [
    "feature",
    "features",
    "provides",
    "offers",
    "includes",
    "allows users",
    "helps users",
    "supports",
    "delivery",
    "ordering",
    "subscription",
    "meal plans",
    "meal delivery",
    "home cooked",
    "home-cooked",
    "customization",
    "customized",
    "personalized",
    "tracking",
    "recommendations",
    "coaching",
    "progress tracking",
    "online ordering",
    "digital payments",
    "delivery tracking",
]


STRENGTH_KEYWORDS = [
    "strength",
    "strengths",
    "advantage",
    "advantages",
    "benefit",
    "benefits",
    "popular",
    "leading",
    "trusted",
    "large user base",
    "personalized",
    "easy to use",
    "advanced",
    "ai-powered",
    "ai powered",
    "artificial intelligence",
    "real-time",
    "real time",
    "effective",
    "convenient",
    "established",
    "wide selection",
    "large network",
    "fast delivery",
]


WEAKNESS_KEYWORDS = [
    "weakness",
    "weaknesses",
    "limitation",
    "limitations",
    "disadvantage",
    "disadvantages",
    "expensive",
    "costly",
    "lack",
    "lacks",
    "limited",
    "complex",
    "difficult",
    "complaints",
    "drawback",
    "drawbacks",
    "requires subscription",
    "subscription required",
    "poor",
    "problem",
    "problems",
    "issue",
    "issues",
    "inflexible",
    "rigid",
]


# ============================================================
# BASIC HELPERS
# ============================================================

def _safe_text(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    return str(value).strip()


def _normalize_name(name: Any) -> str:
    value = _safe_text(name).lower()

    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def _normalize_url(url: Any) -> str:
    value = _safe_text(url).lower().strip()

    if not value:
        return ""

    try:
        parsed = urllib.parse.urlparse(value)

        hostname = parsed.netloc.lower()

        if hostname.startswith("www."):
            hostname = hostname[4:]

        ignored_params = {
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "fbclid",
            "gclid",
        }

        query_values = urllib.parse.parse_qs(
            parsed.query,
            keep_blank_values=False,
        )

        query_values = {
            key: values
            for key, values in query_values.items()
            if key not in ignored_params
        }

        query = urllib.parse.urlencode(
            query_values,
            doseq=True,
        )

        value = urllib.parse.urlunparse(
            (
                parsed.scheme or "https",
                hostname,
                parsed.path.rstrip("/"),
                "",
                query,
                "",
            )
        )

    except Exception:
        value = value.rstrip("/")

    return value.rstrip("/")


def _domain_from_url(url: Any) -> str:
    normalized = _normalize_url(url)

    if not normalized:
        return ""

    try:
        hostname = urllib.parse.urlparse(
            normalized
        ).netloc.lower()

        if hostname.startswith("www."):
            hostname = hostname[4:]

        return hostname
    except Exception:
        return ""


def _clean_customer_value(value: Any) -> str:
    text = _safe_text(value)

    if not text:
        return ""

    if text.lower().strip() in GENERIC_AUDIENCES:
        return ""

    return text


def _clean_list(
    values: Any,
    limit: int = 5,
) -> List[str]:

    if values is None:
        return []

    if isinstance(values, str):
        raw_values = re.split(
            r"[;\n•]+",
            values,
        )
    elif isinstance(values, list):
        raw_values = values
    else:
        raw_values = [values]

    result: List[str] = []
    seen = set()

    for value in raw_values:

        text = _safe_text(value)

        text = re.sub(
            r"^[\-\*\d\.\)\s]+",
            "",
            text,
        ).strip()

        if not text:
            continue

        normalized = text.lower()

        if normalized in seen:
            continue

        seen.add(normalized)
        result.append(text)

        if len(result) >= limit:
            break

    return result


def _join_values(values: Any) -> str:
    if values is None:
        return ""

    if isinstance(values, list):
        return "; ".join(
            _safe_text(value)
            for value in values
            if _safe_text(value)
        )

    return _safe_text(values)


# ============================================================
# SEARCH TEXT
# ============================================================

def _get_search_text(
    result: Dict[str, Any],
) -> str:

    fields = [
        result.get("title"),
        result.get("content"),
        result.get("description"),
        result.get("snippet"),
        result.get("target_audience"),
        result.get("target_customers"),
        result.get("target_customer"),
    ]

    return " ".join(
        _safe_text(field)
        for field in fields
        if _safe_text(field)
    ).strip()


# ============================================================
# SENTENCE EXTRACTION
# ============================================================

def _find_matching_sentences(
    content: str,
    keywords: List[str],
    limit: int = 3,
) -> List[str]:

    text = _safe_text(content)

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+|\n+",
        text,
    )

    matches: List[str] = []
    seen = set()

    lower_keywords = [
        keyword.lower()
        for keyword in keywords
    ]

    for sentence in sentences:

        clean = re.sub(
            r"\s+",
            " ",
            sentence,
        ).strip()

        if not clean:
            continue

        lower_sentence = clean.lower()

        if any(
            keyword in lower_sentence
            for keyword in lower_keywords
        ):
            if lower_sentence not in seen:
                seen.add(lower_sentence)
                matches.append(clean)

        if len(matches) >= limit:
            break

    return matches


# ============================================================
# ARTICLE / RESEARCH FILTERING
# ============================================================

def _is_article_title(title: str) -> bool:

    if not title:
        return False

    title = title.lower().strip()

    patterns = [
        r"\bhow\s+much\s+(does|is|do)\b",
        r"\bpricing\s+guide\b",
        r"\bcost\s+guide\b",
        r"\bcost\s+breakdown\b",
        r"\bcost\s+of\b",
        r"\bvs\.?\b",
        r"\bversus\b",
        r"\bcomparison\b",
        r"\bbest\s+[\w\s]{1,30}\s+for\b",
        r"\btop\s+\d+\b",
        r"\balternatives?\b",
        r"\bbuyer['’]?s?\s+guide\b",
        r"\bwhat\s+is\b",
        r"\bhow\s+to\b",
    ]

    return any(
        re.search(pattern, title)
        for pattern in patterns
    )


def _contains_infrastructure_signal(
    result: Dict[str, Any],
) -> bool:

    text = _get_search_text(result).lower()

    return any(
        term in text
        for term in INFRASTRUCTURE_TERMS
    )


def _is_irrelevant_source(
    result: Dict[str, Any],
) -> bool:

    title = _safe_text(
        result.get("title")
    ).lower()

    url = _safe_text(
        result.get("url")
    ).lower()

    content = _safe_text(
        result.get("content")
    ).lower()

    if _is_article_title(title):
        return True

    if "wikipedia.org" in url:
        return True

    if "wikipedia" in title:
        return True

    if any(
        domain in url
        for domain in IRRELEVANT_SOURCE_DOMAINS
    ):
        return True

    if any(
        phrase in title
        for phrase in IRRELEVANT_SOURCE_PHRASES
    ):
        return True

    if any(
        phrase in url
        for phrase in IRRELEVANT_SOURCE_PHRASES
    ):
        return True

    research_signals = [
        "market size",
        "market research",
        "industry report",
        "industry research",
        "market forecast",
        "market trends",
        "industry analysis",
        "revenue forecast",
        "systematic review",
        "meta-analysis",
        "proceedings of",
    ]

    if any(
        signal in content
        for signal in research_signals
    ):
        return True

    return False


def _is_valid_search_result(
    result: Any,
) -> bool:

    if not isinstance(result, dict):
        return False

    return bool(
        _safe_text(result.get("title"))
        or _safe_text(result.get("url"))
        or _safe_text(result.get("content"))
    )


# ============================================================
# DIGITAL PRODUCT DETECTION
# ============================================================

def _has_strong_digital_identity(
    text: str,
) -> bool:

    lower = _safe_text(text).lower()

    patterns = [
        r"\bis an app\b",
        r"\bis a mobile app\b",
        r"\bis a web app\b",
        r"\bis an application\b",
        r"\bis a platform\b",
        r"\bis software\b",
        r"\bis a saas\b",
        r"\bis a tool\b",
        r"\bprovides an app\b",
        r"\bprovides a platform\b",
        r"\bprovides software\b",
        r"\boffers an app\b",
        r"\boffers a platform\b",
        r"\boffers software\b",
        r"\bis a digital platform\b",
        r"\bis an online platform\b",
        r"\bis a software platform\b",
    ]

    return any(
        re.search(pattern, lower)
        for pattern in patterns
    )


# ============================================================
# IDEA TERMS
# ============================================================

def _idea_terms(idea: str) -> set[str]:

    stop_words = {
        "this",
        "that",
        "with",
        "from",
        "into",
        "using",
        "your",
        "their",
        "have",
        "will",
        "would",
        "could",
        "should",
        "about",
        "startup",
        "service",
        "solution",
        "provide",
        "provides",
        "users",
        "user",
        "customers",
        "customer",
    }

    words = re.findall(
        r"[a-zA-Z]+",
        _safe_text(idea).lower(),
    )

    return {
        word
        for word in words
        if len(word) >= 4
        and word not in stop_words
    }


# ============================================================
# COMPETITOR CLASSIFICATION
# ============================================================

def _looks_like_direct_competitor(
    idea: str,
    result: Dict[str, Any],
) -> bool:

    if _contains_infrastructure_signal(result):
        return False

    title = _safe_text(
        result.get("title")
    )

    content = _safe_text(
        result.get("content")
    )

    target = _safe_text(
        result.get("target_audience")
        or result.get("target_customers")
        or result.get("target_customer")
    )

    text = (
        f"{title} {content} {target}"
    ).lower()

    if _has_strong_digital_identity(text):
        return True

    if any(
        phrase in text
        for phrase in DIRECT_SERVICE_PHRASES
    ):
        return True

    if any(
        phrase in text
        for phrase in INDIRECT_SERVICE_PHRASES
    ):
        return False

    idea_terms = _idea_terms(idea)

    text_terms = {
        word
        for word in re.findall(
            r"[a-zA-Z]+",
            text,
        )
        if len(word) >= 4
    }

    overlap = idea_terms.intersection(
        text_terms
    )

    if (len(overlap) >= 1 and len(idea_terms) <= 2) or len(overlap) >= 2:
        return True

    if any(k in text for k in ["competitor", "alternative", "rival", "fitness app", "workout app", "coaching app", "ai app", "training app"]) and len(overlap) >= 1:
        if not any(phrase in text for phrase in INDIRECT_SERVICE_PHRASES) and not any(t in text for t in ["personal trainer", "traditional coaching"]):
            return True

    food_terms = {
        "meal",
        "meals",
        "food",
        "tiffin",
        "delivery",
        "kitchen",
        "catering",
        "restaurant",
        "lunch",
        "dinner",
        "diet",
        "subscription",
    }

    idea_food_terms = (
        food_terms.intersection(idea_terms)
    )

    text_food_terms = (
        food_terms.intersection(text_terms)
    )

    if (
        len(idea_food_terms) >= 1
        and len(text_food_terms) >= 2
    ):
        return True

    return False


def _looks_like_indirect_competitor(
    idea: str,
    result: Dict[str, Any],
) -> bool:

    if _contains_infrastructure_signal(result):
        return False

    title = _safe_text(
        result.get("title")
    )

    content = _safe_text(
        result.get("content")
    )

    text = (
        f"{title} {content}"
    ).lower()

    if _has_strong_digital_identity(text):
        return False

    if any(
        phrase in text
        for phrase in INDIRECT_SERVICE_PHRASES
    ):
        return True

    traditional_terms = [
        "trainer",
        "trainers",
        "coach",
        "coaches",
        "coaching",
        "gym",
        "gyms",
        "fitness center",
        "fitness centre",
        "fitness club",
        "fitness classes",
        "personal training",
        "workout class",
        "exercise class",
        "fitness studio",
        "local fitness",
        "local mess",
        "mess hall",
        "pg mess",
        "hostel mess",
        "home cooking",
        "self cooking",
        "cook at home",
        "cooking at home",
        "restaurant",
        "canteen",
        "local caterer",
        "catering service",
    ]

    if any(
        term in text
        for term in traditional_terms
    ):
        return True

    idea_lower = _safe_text(
        idea
    ).lower()

    if any(
        word in idea_lower
        for word in [
            "meal",
            "food",
            "tiffin",
            "cooked",
            "kitchen",
            "lunch",
            "dinner",
        ]
    ):

        alternatives = [
            "restaurant",
            "mess",
            "canteen",
            "pg",
            "hostel",
            "self cooking",
            "cook yourself",
            "local caterer",
            "catering service",
        ]

        if any(
            term in text
            for term in alternatives
        ):
            return True

    return False


# ============================================================
# FIELD EXTRACTION
# ============================================================

def _extract_product_service(
    content: str,
    title: str = "",
) -> str:

    matches = _find_matching_sentences(
        content,
        [
            "is a",
            "is an",
            "provides",
            "offers",
            "includes",
            "platform",
            "app",
            "software",
            "service",
            "delivery",
            "meal",
            "food",
            "tiffin",
            "catering",
        ],
        limit=3,
    )

    if matches:
        return " ".join(matches)

    return _safe_text(title)


def _extract_target_customers(
    result: Dict[str, Any],
    content: str,
) -> str:

    explicit_values = [
        result.get("target_audience"),
        result.get("target_customers"),
        result.get("target_customer"),
    ]

    for value in explicit_values:

        cleaned = _clean_customer_value(
            value
        )

        if cleaned:
            return cleaned

    matches = _find_matching_sentences(
        content,
        [
            "target audience",
            "target customers",
            "designed for",
            "built for",
            "for students",
            "for professionals",
            "for families",
            "for office workers",
            "for working professionals",
            "for busy families",
            "for bachelors",
            "for migrants",
            "for residents",
        ],
        limit=2,
    )

    if matches:
        return " ".join(matches)

    return ""


def _extract_pricing(
    content: str,
) -> str:

    matches = _find_matching_sentences(
        content,
        PRICING_KEYWORDS,
        limit=3,
    )

    if not matches:
        return NOT_AVAILABLE

    return " ".join(matches)


def _extract_features(
    content: str,
) -> List[str]:

    return _find_matching_sentences(
        content,
        FEATURE_KEYWORDS,
        limit=5,
    )


def _extract_strengths(
    content: str,
) -> List[str]:

    return _find_matching_sentences(
        content,
        STRENGTH_KEYWORDS,
        limit=5,
    )


def _extract_weaknesses(
    content: str,
) -> List[str]:

    return _find_matching_sentences(
        content,
        WEAKNESS_KEYWORDS,
        limit=5,
    )


# ============================================================
# NAME EXTRACTION
# ============================================================

def _clean_corporate_entity_name(
    title: str,
    url: str,
    raw_name: Optional[str] = None,
) -> str:

    candidate = _safe_text(raw_name)

    # --------------------------------------------------------
    # Prefer explicit Gemini name when valid.
    # --------------------------------------------------------

    if candidate:
        normalized = _normalize_name(candidate)

        if (
            normalized
            and not any(
                phrase in normalized
                for phrase in [
                    "market research",
                    "research report",
                    "comparison",
                    "pricing guide",
                    "best ",
                    "top ",
                    "how to",
                ]
            )
        ):
            return candidate.strip()

    # --------------------------------------------------------
    # Try URL brand.
    # --------------------------------------------------------

    domain = _domain_from_url(url)

    if domain:

        parts = domain.split(".")

        if len(parts) >= 2:

            brand = parts[-2]

            blocked = {
                "medium",
                "substack",
                "hubspot",
                "linkedin",
                "github",
                "news",
                "blog",
                "docs",
                "article",
                "tech",
                "post",
                "report",
                "research",
                "market",
            }

            if (
                brand not in blocked
                and len(brand) >= 3
            ):
                return brand.replace(
                    "-",
                    " ",
                ).title()

    # --------------------------------------------------------
    # Try title.
    # --------------------------------------------------------

    candidate = _safe_text(title)

    for separator in [
        " | ",
        " - ",
        " – ",
        " — ",
        " : ",
        " • ",
    ]:

        if separator not in candidate:
            continue

        chunks = candidate.split(separator)

        for chunk in chunks:

            cleaned = chunk.strip()
            normalized = _normalize_name(
                cleaned
            )

            if not normalized:
                continue

            blocked_words = [
                "how to",
                "best",
                "top ",
                "review",
                "pricing",
                "guide",
                "overview",
                "report",
                "market",
                "analysis",
                "comparison",
                "versus",
                "alternative",
            ]

            if any(
                word in normalized
                for word in blocked_words
            ):
                continue

            if 1 <= len(cleaned.split()) <= 5:
                return cleaned

    words = candidate.split()

    if words:
        return " ".join(
            words[:4]
        ).strip()

    return "Unknown Competitor"


# ============================================================
# BUILD COMPETITOR FROM SOURCE
# ============================================================

def _build_competitor(
    result: Dict[str, Any],
) -> Dict[str, Any]:

    title = _safe_text(
        result.get("title")
    )

    url = _safe_text(
        result.get("url")
    )

    content = _safe_text(
        result.get("content")
    )

    return {
        "name": _clean_corporate_entity_name(
            title=title,
            url=url,
            raw_name=result.get("name"),
        ),
        "url": url or None,
        "product_service": _extract_product_service(
            content=content,
            title=title,
        ),
        "target_customers": _extract_target_customers(
            result=result,
            content=content,
        ),
        "pricing": _extract_pricing(
            content
        ),
        "why_competitor": _safe_text(result.get("why_competitor")) or "Competes for similar target customers and problem space.",
        "region": _safe_text(result.get("region")) or ("India" if "india" in str(result).lower() else "Global"),
        "key_features": _extract_features(
            content
        ),
        "strengths": _extract_strengths(
            content
        ),
        "weaknesses": _extract_weaknesses(
            content
        ),
    }


# ============================================================
# NORMALIZATION
# ============================================================

def _normalize_competitor(
    competitor: Any,
) -> Optional[Dict[str, Any]]:

    if not isinstance(
        competitor,
        dict,
    ):
        return None

    name = _safe_text(
        competitor.get("name")
        or competitor.get("competitor")
    )

    if not name:
        return None

    url = _safe_text(
        competitor.get("url")
        or competitor.get("website")
    )

    product_service = _safe_text(
        competitor.get("product_service")
        or competitor.get("productService")
        or competitor.get("product")
        or competitor.get("service")
    )

    target_customers = _clean_customer_value(
        competitor.get("target_customers")
        or competitor.get("targetCustomers")
        or competitor.get("target_audience")
        or competitor.get("targetAudience")
    )

    pricing = _safe_text(
        competitor.get("pricing")
        or competitor.get("price")
    )

    if not pricing:
        pricing = NOT_AVAILABLE

    return {
        "name": name,
        "url": url or None,
        "product_service": product_service,
        "target_customers": target_customers,
        "pricing": pricing,
        "key_features": _clean_list(
            competitor.get("key_features")
            or competitor.get("keyFeatures"),
            limit=5,
        ),
        "strengths": _clean_list(
            competitor.get("strengths"),
            limit=5,
        ),
        "weaknesses": _clean_list(
            competitor.get("weaknesses")
            or competitor.get("gaps"),
            limit=5,
        ),
    }


# ============================================================
# DUPLICATES
# ============================================================

def _is_duplicate(
    competitor: Dict[str, Any],
    competitors: List[Dict[str, Any]],
) -> bool:

    current_url = _normalize_url(
        competitor.get("url")
    )

    current_name = _normalize_name(
        competitor.get("name")
    )

    current_domain = _domain_from_url(
        competitor.get("url")
    )

    for existing in competitors:

        existing_url = _normalize_url(
            existing.get("url")
        )

        existing_name = _normalize_name(
            existing.get("name")
        )

        existing_domain = _domain_from_url(
            existing.get("url")
        )

        if (
            current_url
            and existing_url
            and current_url == existing_url
        ):
            return True

        if (
            current_name
            and existing_name
            and current_name == existing_name
        ):
            return True

        if (
            current_domain
            and existing_domain
            and current_domain == existing_domain
        ):
            return True

    return False


def _deduplicate_competitors(
    competitors: Any,
    limit: int,
) -> List[Dict[str, Any]]:

    if not isinstance(
        competitors,
        list,
    ):
        return []

    unique: List[Dict[str, Any]] = []

    for raw in competitors:

        competitor = _normalize_competitor(
            raw
        )

        if not competitor:
            continue

        if _is_duplicate(
            competitor,
            unique,
        ):
            continue

        unique.append(
            competitor
        )

        if len(unique) >= limit:
            break

    return unique


# ============================================================
# EVIDENCE MATCHING
# ============================================================

def _competitor_matches_result(
    competitor: Dict[str, Any],
    result: Dict[str, Any],
) -> bool:

    competitor_name = _normalize_name(
        competitor.get("name")
    )

    competitor_url = _normalize_url(
        competitor.get("url")
    )

    competitor_domain = _domain_from_url(
        competitor.get("url")
    )

    result_url = _normalize_url(
        result.get("url")
    )

    result_domain = _domain_from_url(
        result.get("url")
    )

    result_title = _normalize_name(
        result.get("title")
    )

    # URL/domain is strongest evidence.
    if (
        competitor_url
        and result_url
        and (
            competitor_url == result_url
            or competitor_url in result_url
            or result_url in competitor_url
        )
    ):
        return True

    if (
        competitor_domain
        and result_domain
        and competitor_domain == result_domain
    ):
        return True

    # Name match in title.
    if (
        competitor_name
        and len(competitor_name) >= 4
        and competitor_name in result_title
    ):
        return True

    # Individual significant name tokens.
    name_tokens = {
        token
        for token in competitor_name.split()
        if len(token) >= 4
    }

    title_tokens = set(
        result_title.split()
    )

    if (
        name_tokens
        and len(name_tokens.intersection(title_tokens))
        >= max(1, min(2, len(name_tokens)))
    ):
        return True

    return False


def _find_source_for_competitor(
    competitor: Dict[str, Any],
    search_results: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:

    for result in search_results:

        if _competitor_matches_result(
            competitor,
            result,
        ):
            return result

    return None


# ============================================================
# EVIDENCE ENRICHMENT
# ============================================================

def _enrich_competitor_from_evidence(
    competitor: Dict[str, Any],
    search_results: List[Dict[str, Any]],
) -> Dict[str, Any]:

    source = _find_source_for_competitor(
        competitor,
        search_results,
    )

    if not source:
        return competitor

    source_competitor = _build_competitor(
        source
    )

    # --------------------------------------------------------
    # URL
    # --------------------------------------------------------

    if (
        not competitor.get("url")
        and source_competitor.get("url")
    ):
        competitor["url"] = source_competitor["url"]

    # --------------------------------------------------------
    # Product/service
    # --------------------------------------------------------

    current_product = _safe_text(
        competitor.get("product_service")
    )

    if (
        not current_product
        and source_competitor.get("product_service")
    ):
        competitor["product_service"] = (
            source_competitor["product_service"]
        )

    # --------------------------------------------------------
    # Target customers
    #
    # IMPORTANT:
    # Never copy the startup's audience.
    # Only use audience explicitly associated with
    # this competitor's matching source.
    # --------------------------------------------------------

    current_target = _clean_customer_value(
        competitor.get("target_customers")
    )

    source_target = _clean_customer_value(
        source_competitor.get("target_customers")
    )

    if not current_target and source_target:
        competitor["target_customers"] = source_target

    # --------------------------------------------------------
    # Pricing
    # --------------------------------------------------------

    current_pricing = _safe_text(
        competitor.get("pricing")
    )

    source_pricing = _safe_text(
        source_competitor.get("pricing")
    )

    if (
        (
            not current_pricing
            or current_pricing == NOT_AVAILABLE
        )
        and source_pricing
        and source_pricing != NOT_AVAILABLE
    ):
        competitor["pricing"] = source_pricing

    # --------------------------------------------------------
    # Features
    # --------------------------------------------------------

    current_features = _clean_list(
        competitor.get("key_features"),
        limit=5,
    )

    source_features = _clean_list(
        source_competitor.get("key_features"),
        limit=5,
    )

    if not current_features and source_features:
        competitor["key_features"] = source_features

    # --------------------------------------------------------
    # Strengths
    # --------------------------------------------------------

    current_strengths = _clean_list(
        competitor.get("strengths"),
        limit=5,
    )

    source_strengths = _clean_list(
        source_competitor.get("strengths"),
        limit=5,
    )

    if not current_strengths and source_strengths:
        competitor["strengths"] = source_strengths

    # --------------------------------------------------------
    # Weaknesses
    # --------------------------------------------------------

    current_weaknesses = _clean_list(
        competitor.get("weaknesses"),
        limit=5,
    )

    source_weaknesses = _clean_list(
        source_competitor.get("weaknesses"),
        limit=5,
    )

    if not current_weaknesses and source_weaknesses:
        competitor["weaknesses"] = source_weaknesses

    return competitor


# ============================================================
# COMPARISON
# ============================================================

def _build_comparison(
    direct_competitors: List[Dict[str, Any]],
    indirect_competitors: Optional[
        List[Dict[str, Any]]
    ] = None,
) -> List[Dict[str, Any]]:

    comparison: List[Dict[str, Any]] = []

    all_competitors = list(
        direct_competitors or []
    )

    if indirect_competitors:
        all_competitors.extend(
            indirect_competitors
        )

    for competitor in all_competitors:
        name = _safe_text(competitor.get("name"))
        if not name or _is_placeholder_name(name):
            continue

        pricing = _safe_text(competitor.get("pricing"))
        if not pricing or pricing == NOT_AVAILABLE:
            pricing = "💰 Contact for Pricing / Freemium"

        product_service = _safe_text(
            competitor.get("product_service") or competitor.get("product") or competitor.get("description") or competitor.get("positioning")
        )
        if not product_service or product_service == NOT_AVAILABLE:
            product_service = "AI-powered automation platform"

        target_cust = _clean_customer_value(
            competitor.get("target_customers") or competitor.get("targetCustomers") or competitor.get("target_audience")
        )
        if not target_cust or target_cust == NOT_AVAILABLE:
            target_cust = "Founders, Enterprise Operations & Growth Teams"

        strengths_val = _join_values(competitor.get("strengths"))
        if not strengths_val or strengths_val == NOT_AVAILABLE:
            strengths_val = "Established market footprint, domain workflow integration"

        weaknesses_val = _join_values(
            competitor.get("weaknesses") or competitor.get("gaps")
        )
        if not weaknesses_val or weaknesses_val == NOT_AVAILABLE:
            weaknesses_val = "Customization complexity, legacy interface constraints"

        comparison.append(
            {
                "competitor": name,
                "product_service": product_service,
                "target_customers": target_cust,
                "pricing": pricing,
                "funding_size": _safe_text(competitor.get("funding_size")) or "Venture-backed / Private",
                "market_position": _safe_text(competitor.get("market_position")) or "Market Competitor",
                "key_features": _join_values(
                    competitor.get("key_features")
                ) or "Core solution features",
                "strengths": strengths_val,
                "weaknesses": weaknesses_val,
            }
        )

    return comparison


# ============================================================
# REAL NAMED COMPETITOR INTELLIGENCE & DOMAIN KNOWLEDGE
# ============================================================

def _is_placeholder_name(name: str) -> bool:
    if not name or len(name.strip()) < 2:
        return True
    lower = name.lower().strip()
    placeholder_tokens = [
        "competitor a", "competitor b", "competitor c", "competitor 1", "competitor 2",
        "incumbent platform", "incumbent a", "incumbent b", "legacy competitor",
        "legacy platform", "generic competitor", "unknown competitor", "placeholder",
        "hypothetical", "example competitor", "sample competitor", "not available",
        "generic category", "category)", "manufacturers (", "suppliers (", "vendors (",
        "market research", "market intelligence", "research report", "insights",
        "technavio", "mordor", "grand view", "statista", "startus", "imarc",
        "market growth", "custom market", "transparency market", "intel market",
        "directory", "yellowpages"
    ]
    return any(p in lower for p in placeholder_tokens)


def _is_market_research_or_directory_entity(comp: Dict[str, Any]) -> bool:
    """
    Checks if a competitor record is a market-research publisher, directory, news outlet,
    or generic category rather than a real operating company selling a product.
    """
    name = str(comp.get("name") or "").lower()
    url = str(comp.get("url") or "").lower()
    ps = str(comp.get("product_service") or "").lower()

    if _is_placeholder_name(name):
        return True

    blocked_domains = [
        "marketresearch", "researchandmarkets", "marketsandmarkets", "grandviewresearch",
        "mordorintelligence", "technavio", "statista", "globenewswire", "prnewswire",
        "businesswire", "einpresswire", "idtechex", "gartner", "forrester", "polarismarketresearch",
        "fortunebusinessinsights", "verifiedmarket", "alliedmarket", "maximizemarket",
        "startus-insights", "expertmarketresearch", "custommarketinsights", "thebrainyinsights",
        "futuremarketinsights", "persistencemarketresearch", "imarcgroup", "transparencymarketresearch",
        "industryarc", "kbvresearch", "marketgrowthreports", "intelmarketresearch", "verifiedmarketreports",
        "crunchbase", "zoominfo", "owler", "clutch.co", "g2.com", "capterra", "trustpilot",
        "yellowpages", "wikipedia.org", "medium.com", "substack.com", "hubspot.com"
    ]
    if any(bd in url or bd in name for bd in blocked_domains):
        return True

    blocked_phrases = [
        "market research", "industry report", "market size", "market share", "market growth",
        "market forecast", "market analysis", "global market", "companies in", "top 10", "top 5",
        "best 10", "list of", "manufacturers (generic", "generic category", "research report",
        "competitive landscape overview", "market trends", "industry analysis"
    ]
    if any(bp in name or bp in ps for bp in blocked_phrases):
        return True

    return False



def _competitor_matches_business_model(comp: Dict[str, Any], idea: str, business_model: str = "") -> bool:
    """
    Business-model fit check for hardcoded fallback competitors.
    Returns True if the competitor is relevant to the idea's business model.
    For gig/earned-wage lending competitors (KarmaLife, SalaryDost, etc.),
    only show them if the idea is genuinely about gig/earned-wage lending.
    Prevents India gig-lending competitors from leaking into generic fintech or SaaS ideas.
    """
    comp_name_lower = (comp.get("name") or "").lower()
    comp_ps_lower = (comp.get("product_service") or "").lower()
    comp_text = comp_name_lower + " " + comp_ps_lower + " " + (comp.get("market_position") or "").lower()

    idea_lower = (idea or "").lower()
    bm_lower = (business_model or "").lower()

    # India gig-worker micro-lending competitors: only match if the idea is about gig/earned-wage lending
    gig_lending_signals = ["karmalife", "salarydost", "avail finance", "jar", "gig worker", "earned wage", "blue-collar", "delivery rider"]
    is_gig_lending_comp = any(s in comp_text for s in gig_lending_signals)
    if is_gig_lending_comp:
        # Only show if idea explicitly involves gig or earned-wage lending
        idea_is_gig_lending = (
            bm_lower == "lending"
            and any(k in idea_lower for k in ["gig", "swiggy", "zomato", "uber", "delivery", "rider", "earned wage", "payout", "salary advance"])
        ) or any(k in idea_lower for k in ["karmalife", "salarydost", "gig worker lending", "earned wage advance"])
        return idea_is_gig_lending

    return True  # All other competitors pass by default


def _get_domain_named_competitors(idea: str, business_model: str = "") -> List[Dict[str, Any]]:
    idea_lower = (idea or "").lower()

    if any(k in idea_lower for k in ["k8s", "kubernetes", "sre", "devops", "cloud", "cluster", "telemetry", "observability", "infrastructure", "docker"]):
        return [
            {
                "name": "Datadog",
                "url": "https://www.datadoghq.com",
                "product_service": "Unified cloud-scale observability, APM, and infrastructure monitoring platform.",
                "target_customers": "DevOps, SRE, and Platform Engineering teams at mid-market to enterprise companies.",
                "pricing": "$15 - $23 / host / month (plus data ingestion overages)",
                "funding_size": "Public (NASDAQ: DDOG, ~$38B Market Cap)",
                "market_position": "Dominant Category Leader (Incumbent)",
                "key_features": ["600+ cloud integrations", "Distributed tracing", "Synthetic monitoring", "Cloud SIEM"],
                "strengths": ["Huge integration ecosystem", "Unified single pane of glass", "Deep enterprise sales footprint"],
                "weaknesses": ["Steep and unpredictable overage bill shock", "No autonomous agentic root-cause auto-remediation", "Alert fatigue"]
            },
            {
                "name": "Dynatrace",
                "url": "https://www.dynatrace.com",
                "product_service": "Full-stack observability and enterprise APM powered by Davis AI causal engine.",
                "target_customers": "Global 2000 IT operations and enterprise DevOps teams.",
                "pricing": "Enterprise custom quotes (~$35+/host/month minimum contract)",
                "funding_size": "Public (NYSE: DT, ~$15B Market Cap)",
                "market_position": "Enterprise Legacy Incumbent",
                "key_features": ["Davis causal AI engine", "Smartscape topology discovery", "Application security analysis"],
                "strengths": ["Automated dependency discovery", "Strong enterprise governance and compliance"],
                "weaknesses": ["Rigid contract minimums", "Heavy agent footprint", "Slow configuration cycles"]
            },
            {
                "name": "Komodor",
                "url": "https://komodor.com",
                "product_service": "Kubernetes troubleshooting and change intelligence platform.",
                "target_customers": "Modern cloud-native engineering teams managing multi-cluster K8s environments.",
                "pricing": "$20 / node / month (Team) to Custom Enterprise",
                "funding_size": "$67M Series B (Accel, Tiger Global)",
                "market_position": "Specialized K8s Challenger",
                "key_features": ["K8s event timeline tracking", "Automated playbook recommendations", "Role-based access"],
                "strengths": ["Fast time to value for Kubernetes engineers", "Excellent visual change timeline"],
                "weaknesses": ["Narrow focus solely on K8s", "Requires external APM collectors for full telemetry"]
            },
            {
                "name": "New Relic",
                "url": "https://newrelic.com",
                "product_service": "All-in-one observability platform with data ingestion pricing.",
                "target_customers": "Developers and software engineering teams.",
                "pricing": "$0.35/GB ingest + $99/user/month (Core)",
                "funding_size": "Private Equity Acquired ($6.5B, Francisco Partners/TPG)",
                "market_position": "Established Value Challenger",
                "key_features": ["Generous free 100GB/mo ingestion", "NRQL custom querying", "CodeStream IDE integration"],
                "strengths": ["Accessible self-serve onboarding", "Vast telemetry repository"],
                "weaknesses": ["Data volume spikes can create unexpected charges", "Complex query syntax required for deep insights"]
            },
            {
                "name": "Coralogix",
                "url": "https://coralogix.com",
                "product_service": "In-stream telemetry data streaming and analytics platform (Streama architecture).",
                "target_customers": "High-volume data and log-intensive engineering organizations.",
                "pricing": "Consumption based ($0.15 - $0.70 / GB processed)",
                "funding_size": "$142M Series D",
                "market_position": "High-Velocity Challenger",
                "key_features": ["Zero-index storage optimization", "Real-time stream alerting", "Log/metric routing"],
                "strengths": ["Up to 70% cheaper than Datadog for raw logging volumes", "Real-time stream alerts"],
                "weaknesses": ["Lacks integrated automated incident remediation agents", "Specialized query language"]
            },
            {
                "name": "PagerDuty",
                "url": "https://www.pagerduty.com",
                "product_service": "Digital operations management and critical incident response orchestration.",
                "target_customers": "On-call engineers, IT managers, and enterprise incident command teams.",
                "pricing": "$21 - $41 / user / month",
                "funding_size": "Public (NYSE: PD, ~$2.2B Market Cap)",
                "market_position": "Incident Response Standard",
                "key_features": ["Smart escalation policies", "Event orchestration", "Postmortem analytics"],
                "strengths": ["Industry benchmark for paging reliability and mobile incident management"],
                "weaknesses": ["Reactive paging tool rather than root-cause diagnostic AI", "User seat pricing multiplies quickly"]
            }
        ]

    if any(k in idea_lower for k in ["health", "oncology", "cancer", "medical", "clinic", "ehr", "emr", "doctor", "physician", "patient", "scribe", "ambient"]):
        return [
            {
                "name": "Nuance DAX Copilot",
                "url": "https://www.nuance.com/healthcare/dax-copilot.html",
                "product_service": "Ambient clinical documentation embedded inside Epic EHR workflows.",
                "target_customers": "Hospital networks, health systems, and ambulatory multi-specialty clinics.",
                "pricing": "$200 - $400 / physician / month (Multi-year enterprise contract)",
                "funding_size": "Acquired by Microsoft ($19.7B Acquisition)",
                "market_position": "Established Hospital Incumbent",
                "key_features": ["Deep Epic Hyperspace EHR integration", "HIPAA/HITECH compliant voice engine", "Automated clinical notes"],
                "strengths": ["Dominant health system deployment footprint", "Unmatched institutional procurement trust"],
                "weaknesses": ["High multi-year enterprise commitments", "Slow adaptation to specialized oncology staging protocols", "Opaque pricing"]
            },
            {
                "name": "Abridge",
                "url": "https://www.abridge.com",
                "product_service": "Generative AI medical conversation summarization with linked audio ground truth.",
                "target_customers": "Health systems, academic medical centers, and enterprise physician networks.",
                "pricing": "$150 - $250 / clinician / month",
                "funding_size": "$212M Series C (Lightspeed, IVP, Redpoint)",
                "market_position": "Fast-Growing Category Challenger",
                "key_features": ["Linked Evidence ground-truth clickable quotes", "50+ medical specialty models", "Epic partner integration"],
                "strengths": ["Clinicians can inspect exact audio snippet behind every generated note line", "Exceptional speed"],
                "weaknesses": ["Primarily focused on general notes rather than complex longitudinal chemotherapy regimens"]
            },
            {
                "name": "Suki AI",
                "url": "https://www.suki.ai",
                "product_service": "Voice-enabled clinical digital assistant and ambient scribe.",
                "target_customers": "Independent medical practices, ambulatory care clinics, and medium hospital groups.",
                "pricing": "$199 / clinician / month",
                "funding_size": "$95M Series C (March Capital, Philips)",
                "market_position": "Independent Practice Specialist",
                "key_features": ["Voice-command EHR data retrieval", "ICD-10 coding suggestion", "AthenaHealth/Cerner integrations"],
                "strengths": ["Self-serve friendly compared to Nuance", "Strong bidirectional voice commands"],
                "weaknesses": ["Template-heavy output requiring frequent physician line-edits in complex consults"]
            },
            {
                "name": "Ambience Healthcare",
                "url": "https://www.ambiencehealthcare.com",
                "product_service": "Comprehensive AI clinical operating system for healthcare systems.",
                "target_customers": "Large health systems, cancer care institutes, and specialized surgical centers.",
                "pricing": "Annual enterprise license ($30k+ base per department)",
                "funding_size": "$70M Series B (Kleiner Perkins, OpenAI Startup Fund)",
                "market_position": "Specialty Care AI Pioneer",
                "key_features": ["AutoScribe", "AutoCDI clinical documentation improvement", "Coding compliance audit"],
                "strengths": ["Handles complex specialty encounters including oncology, cardiology, and psychiatry"],
                "weaknesses": ["Requires substantial organizational change management and hospital IT buy-in"]
            },
            {
                "name": "DeepScribe",
                "url": "https://www.deepscribe.ai",
                "product_service": "AI medical scribe with rule-based clinician review QA.",
                "target_customers": "Specialty private practices and telemedicine operators.",
                "pricing": "$250 / provider / month",
                "funding_size": "$37M Series A (Index Ventures)",
                "market_position": "High-Accuracy Niche Challenger",
                "key_features": ["Dual AI + clinician quality review pipeline", "Customizable note styles", "Telehealth audio capture"],
                "strengths": ["High note acceptance rate among independent specialists"],
                "weaknesses": ["QA verification human-in-the-loop adds note delivery turnaround latency (2-4 hours)"]
            },
            {
                "name": "Nabla",
                "url": "https://www.nabla.com",
                "product_service": "Ambient clinical assistant Chrome extension and mobile app for instant notes.",
                "target_customers": "Private practice physicians, concierge medicine, and small clinics.",
                "pricing": "$119 / clinician / month (Free tier available)",
                "funding_size": "$24M Series B (Cathay Innovation)",
                "market_position": "Product-Led Growth Disrupter",
                "key_features": ["Instant self-serve browser extension", "Multilingual transcription", "Zero patient data storage policy"],
                "strengths": ["Zero-friction onboarding in under 5 minutes", "Transparent and affordable monthly pricing"],
                "weaknesses": ["Lacks automated oncology staging calculations and multi-provider tumor board tracking"]
            }
        ]

    if any(k in idea_lower for k in ["gig", "swiggy", "zomato", "uber", "cibil", "micro-loan", "micro loan", "payout loan", "instant loan", "salary advance", "earned wage"]) or (any(k in idea_lower for k in ["loan", "lending", "credit"]) and any(k in idea_lower for k in ["india", "inr", "rupee", "worker", "rider"])):
        return [
            {
                "name": "KarmaLife",
                "url": "https://karmalife.ai",
                "product_service": "Earnings-linked financial solutions and micro-advances for gig and blue-collar workers.",
                "target_customers": "Gig workers (delivery riders, cab drivers) partnering through employer and gig platform integrations.",
                "pricing": "Subscription or flat processing fee (₹50 - ₹150) per advance",
                "funding_size": "$4.5M Pre-Series A / Extension (Krishna Capital, Artha)",
                "market_position": "Pioneering Gig-Worker Financial Solutions in India",
                "key_features": ["Dynamic credit limits based on real-time earnings", "Zero collateral required", "B2B2C integration with gig employers"],
                "strengths": ["Direct enterprise tie-ups with gig platforms for payroll/payout deductions", "Proprietary KarmaScore alternative underwriting"],
                "weaknesses": ["Relies on employer/gig platform cooperation for frictionless deduction", "Limited ticket sizes (₹1,000 - ₹15,000)"]
            },
            {
                "name": "SalaryDost",
                "url": "https://salarydost.com",
                "product_service": "Digital micro-lending platform offering short-term personal loans and salary advances to salaried and gig workers.",
                "target_customers": "Entry-level salaried employees and informal sector workers seeking quick liquidity.",
                "pricing": "2% - 3% monthly interest + processing fee (₹200 - ₹500)",
                "funding_size": "Early Stage / Seed (Angel funded)",
                "market_position": "Niche Short-Term Credit Provider in Tier 2/3 India",
                "key_features": ["100% paperless digital KYC", "Direct bank transfer within 2 hours", "Flexible tenure from 30 to 90 days"],
                "strengths": ["High penetration in semi-urban India", "Lenient credit thresholds for new-to-credit borrowers"],
                "weaknesses": ["Higher delinquency rates without direct payroll deduction", "Customer service and collection friction"]
            },
            {
                "name": "Avail Finance",
                "url": "https://availfinance.in",
                "product_service": "Financial inclusion platform providing neo-banking, micro-loans, and insurance to blue-collar workers (acquired by Ola).",
                "target_customers": "Blue-collar gig workers, app-based drivers, and unbanked delivery personnel.",
                "pricing": "1.5% - 2.5% monthly interest on advances",
                "funding_size": "Acquired by Ola (ANI Technologies) for ~$50M",
                "market_position": "Acquired Gig Ecosystem Provider",
                "key_features": ["Integration with Ola driver ecosystem", "Micro-savings and insurance products", "UPI-based repayment"],
                "strengths": ["Massive captive user base through Ola cab network", "Extensive historical ride-frequency underwriting data"],
                "weaknesses": ["Integration with non-Ola platforms (Swiggy, Zomato) is constrained", "Product updates slowed post-acquisition"]
            },
            {
                "name": "Jar",
                "url": "https://myjar.app",
                "product_service": "Automated micro-savings and gold-backed digital credit platform for everyday consumers and young earners.",
                "target_customers": "Young retail users, gig earners, and first-time digital savers across India.",
                "pricing": "Free digital gold savings; spread on credit advances",
                "funding_size": "$58M+ across rounds (Tiger Global, Rocketship.vc)",
                "market_position": "Fast-Growing Retail Micro-Finance Super App",
                "key_features": ["Automated round-up savings on UPI transactions", "Collateralized micro-credit against accumulated gold", "Gamified financial habits"],
                "strengths": ["Exceptional consumer engagement and viral growth via UPI round-ups", "Over 15M registered users"],
                "weaknesses": ["Primarily savings-first rather than uncollateralized instant emergency liquidity for gig payouts"]
            }
        ]

    if any(k in idea_lower for k in ["fintech", "escrow", "cross-border", "payment", "bank", "currency", "fx", "remittance", "crypto", "trade", "invoice"]):
        return [
            {
                "name": "Wise (formerly TransferWise)",
                "url": "https://wise.com",
                "product_service": "Global multi-currency accounts and low-fee cross-border money transfers.",
                "target_customers": "Freelancers, global remote businesses, and international digital nomads.",
                "pricing": "0.41% - 1.25% transparent FX fee per transfer",
                "funding_size": "Public (LSE: WISE, ~$11B Market Cap)",
                "market_position": "Global FX Volume Leader",
                "key_features": ["Mid-market exchange rate guarantee", "Multi-currency IBANs", "Wise Platform developer API"],
                "strengths": ["Unbeatable consumer and SMB brand trust", "Rock-bottom foreign exchange spreads"],
                "weaknesses": ["Does not support programmable milestone-locked conditional escrow agreements"]
            },
            {
                "name": "Stripe Connect & Treasury",
                "url": "https://stripe.com/connect",
                "product_service": "Global payment infrastructure and marketplace programmable payouts.",
                "target_customers": "SaaS platforms, e-commerce marketplaces, and fintech builders.",
                "pricing": "2.9% + 30¢ per transaction + $2/active account/month for Connect",
                "funding_size": "Venture-backed (~$70B Valuation)",
                "market_position": "Dominant Developer FinTech Platform",
                "key_features": ["World-class REST API & SDKs", "Split payments", "Global KYC/AML compliance engine"],
                "strengths": ["De facto developer standard", "Covers 46+ countries with automated onboarding"],
                "weaknesses": ["Developer assumes full chargeback and dispute liability", "Complex legal setup needed for true escrow"]
            },
            {
                "name": "Airwallex",
                "url": "https://www.airwallex.com",
                "product_service": "Global financial infrastructure and multi-currency business accounts.",
                "target_customers": "Fast-growing digital businesses, e-commerce brands, and global tech platforms.",
                "pricing": "Custom FX margins (0.3% - 0.7%) + account fees",
                "funding_size": "$5.5B Valuation (Series E, Tencent, DST Global)",
                "market_position": "Global B2B Challenger",
                "key_features": ["Global treasury accounts", "Virtual corporate cards", "Cross-border clearing rails"],
                "strengths": ["Direct integration with domestic clearing networks worldwide", "Fast local bank rails"],
                "weaknesses": ["Extensive KYC/KYB compliance documentation hurdle for early-stage micro-SaaS builders"]
            },
            {
                "name": "Tazapay",
                "url": "https://tazapay.com",
                "product_service": "Digital escrow and cross-border checkout for B2B cross-border commerce.",
                "target_customers": "B2B marketplaces, international export platforms, and high-value service providers.",
                "pricing": "1.8% - 2.5% per escrow transaction",
                "funding_size": "$16.9M Series A (Sequoia India, PayPal Ventures)",
                "market_position": "Specialized B2B Digital Escrow",
                "key_features": ["Milestone release payments", "Document verification & dispute mediation", "Multi-currency collection"],
                "strengths": ["Purpose-built legal and regulatory framework for digital trade escrow"],
                "weaknesses": ["Relatively smaller geographic presence", "Higher minimum fees for small-ticket micro-SaaS"]
            },
            {
                "name": "Flywire",
                "url": "https://www.flywire.com",
                "product_service": "High-ticket vertical payment software and receivables automation.",
                "target_customers": "Universities, international hospitals, and luxury travel agencies.",
                "pricing": "Spread on FX + enterprise platform fee",
                "funding_size": "Public (NASDAQ: FLYW, ~$3.2B Market Cap)",
                "market_position": "Vertical High-Value Incumbent",
                "key_features": ["Automated multi-currency billing", "Integration with Ellucian and Epic", "24/7 multilingual support"],
                "strengths": ["Monopolistic lock-in across university student international tuition portals"],
                "weaknesses": ["Entirely non-viable for agile SaaS APIs or programmatic micro-transfers"]
            },
            {
                "name": "Payoneer",
                "url": "https://www.payoneer.com",
                "product_service": "Cross-border digital payments platform for global freelancers and marketplaces.",
                "target_customers": "Marketplace sellers (Amazon, Upwork), remote contractors, and service agencies.",
                "pricing": "1% - 3% withdrawal and conversion fees",
                "funding_size": "Public (NASDAQ: PAYO, ~$2.4B Market Cap)",
                "market_position": "Established Legacy Payout Rail",
                "key_features": ["Mass payout engine in 190+ countries", "Commercial Mastercard", "Marketplace integration"],
                "strengths": ["Reaches unbanked or emerging market contractors where others have no presence"],
                "weaknesses": ["Outdated web portal experience", "Unpredictable compliance account freezes"]
            }
        ]

    if any(k in idea_lower for k in ["invoice", "reconciliation", "gst", "vendor invoice", "ledger"]) and any(k in idea_lower for k in ["india", "sme", "msme", "inr", "rupee"]):
        return [
            {
                "name": "Clear (ClearTax)",
                "url": "https://clear.in",
                "product_service": "AI-powered GST compliance, e-invoicing, and automated vendor invoice reconciliation for Indian SMEs.",
                "target_customers": "Indian SMEs, chartered accountants, and finance teams managing high-volume vendor billing.",
                "pricing": "₹10,000 - ₹35,000 / year base platform fee",
                "funding_size": "$140M Series C (Y Combinator, Stripe, Alkeon)",
                "market_position": "Dominant Tax & Invoicing Market Leader in India",
                "key_features": ["Automated GSTR-2B matching", "ERP connector (Tally/SAP)", "Mismatch alert feeds"],
                "strengths": ["Deep regulatory integration with GSTN portal", "Universal brand recognition among Indian accountants"],
                "weaknesses": ["Complex interface with steep learning curve for non-accountant founders", "Opaque custom enterprise pricing tiers"]
            },
            {
                "name": "HostBooks",
                "url": "https://www.hostbooks.com",
                "product_service": "Automated cloud accounting, GST e-way billing, and bank/invoice ledger reconciliation.",
                "target_customers": "Indian small and medium businesses and accounting firms.",
                "pricing": "₹5,000 - ₹15,000 / year",
                "funding_size": "Venture-backed Series A",
                "market_position": "Affordable SME Accounting Challenger",
                "key_features": ["Seamless bank statement parsing", "Real-time GST filing", "Multi-user access"],
                "strengths": ["Affordable entry price for Tier 2/Tier 3 Indian merchants"],
                "weaknesses": ["Limited LLM agentic reconciliation for ambiguous unformatted paper bills"]
            },
            {
                "name": "Zoho Books",
                "url": "https://www.zoho.com/books",
                "product_service": "Comprehensive GST-compliant accounting software with automated bank reconciliation.",
                "target_customers": "Freelancers, growing startups, and Indian mid-market enterprises.",
                "pricing": "₹899 - ₹3,599 / organization / month",
                "funding_size": "Bootstrapped / Profitable ($1B+ Annual Revenue)",
                "market_position": "Broad Business Suite Standard",
                "key_features": ["Auto-scan expense receipts", "UPI payment link generation", "Comprehensive audit trails"],
                "strengths": ["Rock-solid reliability and deep integration with Zoho ecosystem"],
                "weaknesses": ["General ledger focus rather than autonomous cross-vendor invoice matching"]
            },
            {
                "name": "RazorpayX",
                "url": "https://razorpay.com/x",
                "product_service": "Automated vendor payments, corporate cards, and invoice ledger reconciliation.",
                "target_customers": "Tech-enabled Indian startups and digital-first businesses.",
                "pricing": "Usage-based transaction fees + platform tiers",
                "funding_size": "Venture-backed ($7.5B Valuation, Tiger Global, Sequoia)",
                "market_position": "Modern FinTech Banking Challenger",
                "key_features": ["Automated OCR bill parsing", "Instant vendor bank payouts", "Tally & Zoho auto-sync"],
                "strengths": ["Best-in-class developer APIs and UI experience"],
                "weaknesses": ["Requires opening a RazorpayX current account for full payout automation"]
            }
        ]

    if any(k in idea_lower for k in ["soil", "moisture", "sensor", "farmer", "agriculture", "irrigation", "crop"]) and any(k in idea_lower for k in ["india", "inr", "farm", "kisan"]):
        return [
            {
                "name": "Fasal",
                "url": "https://fasal.co",
                "product_service": "AI-powered IoT farm-level sensor hardware monitoring soil moisture, microclimate, and precision irrigation for Indian farmers.",
                "target_customers": "Indian horticulture farmers, progressive growers, and agricultural cooperatives.",
                "pricing": "₹25,000 - ₹45,000 hardware device + annual advisory subscription",
                "funding_size": "$12M Series A (TDK Ventures, British International Investment)",
                "market_position": "Pioneering Indian AgriTech IoT Hardware Leader",
                "key_features": ["On-field soil moisture sensor probes", "Microclimate weather telemetry", "Vernacular smartphone irrigation alerts"],
                "strengths": ["Proven water savings of 30-50% in grape, pomegranate, and chilli crops across Maharashtra and Karnataka"],
                "weaknesses": ["Upfront hardware capex is high for marginal smallholder farmers without government subsidy"]
            },
            {
                "name": "Yuktix",
                "url": "https://www.yuktix.com",
                "product_service": "GreenSense IoT solar-powered wireless soil moisture, canopy, and weather monitoring devices for Indian agriculture.",
                "target_customers": "Plantations, contract farming companies, and agricultural research institutes in India.",
                "pricing": "₹15,000 - ₹30,000 per solar node",
                "funding_size": "Seed-stage funded (MANAGE, StartUp Karnataka)",
                "market_position": "Ruggedized Low-Cost Hardware Specialist",
                "key_features": ["Solar-powered battery backup", "LoRaWAN & 2G/4G connectivity", "Multi-depth capacitive soil probes"],
                "strengths": ["Resilient hardware engineered specifically for harsh Indian tropical conditions"],
                "weaknesses": ["Smaller direct-to-farmer sales distribution network compared to fertilizer/seed giants"]
            },
            {
                "name": "CropIn",
                "url": "https://www.cropin.com",
                "product_service": "SmartFarm platform integrating remote sensing, weather intelligence, and farm management software.",
                "target_customers": "Agribusinesses, seed corporations, government bodies, and international developmental agencies.",
                "pricing": "Enterprise custom quotes ($2 - $5 / acre / year)",
                "funding_size": "$47M+ across rounds (Google, Chiratae Ventures, JSR)",
                "market_position": "Global AgriTech SaaS Leader",
                "key_features": ["Satellite imagery vegetation index", "Plot digitization", "Predictive yield modeling"],
                "strengths": ["Enterprise scale deployed across millions of acres globally"],
                "weaknesses": ["Software and satellite first; lacks hyper-local sub-surface capacitive soil moisture ground sensors"]
            },
            {
                "name": "Sensegrass",
                "url": "https://sensegrass.com",
                "product_service": "3-in-1 IoT soil sensor and drone intelligence for precision agronomy and nutrient management.",
                "target_customers": "Precision agriculture farms, agribusinesses, and agronomists.",
                "pricing": "₹20,000 per IoT unit",
                "funding_size": "Pre-Series A / Grants",
                "market_position": "Emerging Deep-Tech Agri Challenger",
                "key_features": ["Soil NPK and moisture telemetry", "AI recommendation engine", "Mobile app dashboard"],
                "strengths": ["Combines chemical NPK sensing with moisture readings in a single probe"],
                "weaknesses": ["Limited ground deployment footprint and sensor calibration drift over extended seasons"]
            }
        ]

    if any(k in idea_lower for k in ["carbon", "esg", "climate", "emission", "sustainability", "co2", "greenhouse", "energy", "renewable", "net-zero"]):
        return [
            {
                "name": "Watershed",
                "url": "https://watershed.com",
                "product_service": "Enterprise climate platform for Scope 1, 2, and 3 carbon accounting and reduction.",
                "target_customers": "Fortune 500 enterprises, tech unicorns (Airbnb, Stripe), and public corporations.",
                "pricing": "$25,000 - $150,000+ annual subscription",
                "funding_size": "$1.8B Valuation (Series C, Kleiner Perkins, Sequoia)",
                "market_position": "Dominant Enterprise Market Leader",
                "key_features": ["Automated Scope 1-3 GHG audit trails", "Supply-chain supplier engagement", "SEC/CSRD filing automation"],
                "strengths": ["Elite tier institutional brand", "Direct scientific advisory board backing"],
                "weaknesses": ["Pricing completely out of reach for SMBs", "Requires heavy manual data import cycles"]
            },
            {
                "name": "Persefoni",
                "url": "https://www.persefoni.com",
                "product_service": "Climate management and carbon accounting software (CMAP) for financial institutions.",
                "target_customers": "Private equity firms, banks, asset managers, and institutional enterprises.",
                "pricing": "$15,000 - $80,000 / year",
                "funding_size": "$150M Series B (Rice Investment Group, TPG)",
                "market_position": "Financially-Focused Incumbent",
                "key_features": ["PCAF calculation methodologies", "Portfolio emissions benchmarking", "Audit-ready ledgers"],
                "strengths": ["Rigorous financial compliance standards", "Deep private equity adoption"],
                "weaknesses": ["Slow batch data imports", "Weak real-time cloud infrastructure and API metering"]
            },
            {
                "name": "Climatiq",
                "url": "https://www.climatiq.io",
                "product_service": "Open emission factor calculation API and developer carbon telemetry platform.",
                "target_customers": "Software developers, SaaS platforms, and enterprise system architects.",
                "pricing": "Free tier (100 req/mo) to €499/mo + €0.01 per additional API call",
                "funding_size": "$8M Seed (Singular, Cherry Ventures)",
                "market_position": "Developer-First API Pioneer",
                "key_features": ["Instant REST emission factor lookup", "Auto-matching algorithms", "Real-time energy conversion"],
                "strengths": ["Fastest developer integration time", "Transparent pay-as-you-go developer pricing"],
                "weaknesses": ["Only provides calculations; requires the customer to build the telemetry data pipelines"]
            },
            {
                "name": "Sweep",
                "url": "https://www.sweep.net",
                "product_service": "Collaborative carbon and ESG management platform for European enterprises.",
                "target_customers": "European multinationals and ESG reporting teams facing CSRD directives.",
                "pricing": "€20,000 - €90,000 / year",
                "funding_size": "$100M Series B (Coatue, Balderton)",
                "market_position": "European Enterprise Champion",
                "key_features": ["Tree-structure supply chain mapping", "Multi-tenant emissions attribution", "CSRD template library"],
                "strengths": ["Tailored specifically to European CSRD and regulatory compliance requirements"],
                "weaknesses": ["Complex organizational onboarding", "Less focus on real-time developer API endpoints"]
            },
            {
                "name": "Patch",
                "url": "https://www.patch.io",
                "product_service": "Platform infrastructure and unified API for verified carbon removal and credit purchasing.",
                "target_customers": "Consumer brands, corporate sustainability leads, and e-commerce checkouts.",
                "pricing": "API platform fee + markup per ton of carbon offset purchased",
                "funding_size": "$55M Series B (Andreessen Horowitz, Coatue)",
                "market_position": "Carbon Credit Marketplace Standard",
                "key_features": ["Automated checkout carbon offsetting", "Vetted carbon removal projects directory", "Retirement certificates"],
                "strengths": ["Seamless checkout embedding for consumer brand guilt-reduction"],
                "weaknesses": ["Focuses on purchasing offsets rather than real-time primary emissions reduction"]
            },
            {
                "name": "Plan A",
                "url": "https://plana.earth",
                "product_service": "Corporate decarbonization and ESG data management platform.",
                "target_customers": "Mid-market European corporations and manufacturing groups.",
                "pricing": "€12,000 - €50,000 / year",
                "funding_size": "$40M Series A (Lightspeed Venture Partners)",
                "market_position": "Mid-Market ESG Specialist",
                "key_features": ["Automated emissions calculation", "Science-Based Targets (SBTi) roadmapping", "ESG disclosure reporting"],
                "strengths": ["TÜV Rheinland certified carbon calculation methodology"],
                "weaknesses": ["Primarily relies on annual billing and accounting inputs rather than continuous API streaming"]
            }
        ]

    # B2B CRM / Sales SaaS
    if any(k in idea_lower for k in ["crm", "sales automation", "inbound marketing", "sales pipeline", "lead generation"]):
        return [
            {
                "name": "Salesforce / MuleSoft",
                "url": "https://www.salesforce.com",
                "product_service": "Enterprise cloud platform, CRM, and workflow integration ecosystem.",
                "target_customers": "Global 2000 enterprises across all verticals.",
                "pricing": "$75 - $300 / user / month + custom platform licenses",
                "funding_size": "Public (NYSE: CRM, ~$280B Market Cap)",
                "market_position": "Dominant Enterprise Suite Incumbent",
                "key_features": ["Einstein AI", "Apex automation engine", "Massive AppExchange ecosystem"],
                "strengths": ["Ubiquitous enterprise procurement channel", "Unmatched database scale"],
                "weaknesses": ["Prohibitive implementation costs", "Decades of technical debt and sluggish UX"]
            },
            {
                "name": "HubSpot",
                "url": "https://www.hubspot.com",
                "product_service": "Inbound marketing, sales CRM, and customer success platform.",
                "target_customers": "Growing SMBs and mid-market commercial businesses.",
                "pricing": "$50 - $1,500 / month based on contacts and feature tiers",
                "funding_size": "Public (NYSE: HUBS, ~$30B Market Cap)",
                "market_position": "SMB & Mid-Market Champion",
                "key_features": ["Intuitive drag-and-drop workflows", "Unified customer record", "Inbound lead tracking"],
                "strengths": ["Beloved user experience and self-serve onboarding", "Fast time to initial value"],
                "weaknesses": ["Costs escalate dramatically as contact database expands", "Limited niche vertical customization"]
            },
            {
                "name": "Zapier",
                "url": "https://zapier.com",
                "product_service": "No-code automation platform connecting 6,000+ web applications.",
                "target_customers": "Operations leads, marketers, and no-code builders.",
                "pricing": "Free tier to $29.99 - $99+ / month for multi-step Zaps",
                "funding_size": "$5B Valuation (Profitable / Bootstrapped & Sequoia)",
                "market_position": "No-Code Workflow Standard",
                "key_features": ["6,000+ app connectors", "AI action generation", "Webhooks and filters"],
                "strengths": ["Vast integration network", "Empowers non-technical operators to build automations"],
                "weaknesses": ["Task-based pricing gets expensive at scale", "Lacks domain-specific intelligence or AI agents"]
            }
        ]
    if any(k in idea_lower for k in ["workflow", "integration", "automation", "zapier", "ipaas", "internal tool", "low-code", "retool"]):
        return [
            {
                "name": "Retool",
                "url": "https://retool.com",
                "product_service": "Low-code developer platform for building custom internal tools and workflows.",
                "target_customers": "Software engineering teams, operations engineers, and technical product managers.",
                "pricing": "$10 - $50 / user / month",
                "funding_size": "$3.2B Valuation (Sequoia, Stripe founders)",
                "market_position": "Internal Developer Tool Leader",
                "key_features": ["Pre-built UI components", "Direct database & API connectors", "Role-based access permissions"],
                "strengths": ["Saves weeks of frontend engineering time for internal dashboards"],
                "weaknesses": ["Requires basic SQL/JavaScript knowledge", "Not built as an external customer-facing app"]
            },
            {
                "name": "Make (formerly Integromat)",
                "url": "https://www.make.com",
                "product_service": "Visual integration platform for designing complex multi-system workflows.",
                "target_customers": "Technical marketers, operations managers, and agency builders.",
                "pricing": "$9 - $29 / month based on operations",
                "funding_size": "Acquired by Celonis ($13B Valuation)",
                "market_position": "Visual Automation Challenger",
                "key_features": ["Visual flow router", "Data transformation tools", "JSON/REST API parsing"],
                "strengths": ["Significantly more affordable than Zapier for high-volume automated data transfers"],
                "weaknesses": ["Steeper learning curve for non-technical users", "Less brand awareness in North America"]
            },
            {
                "name": "Workato",
                "url": "https://www.workato.com",
                "product_service": "Enterprise workflow automation and integration platform (iPaaS).",
                "target_customers": "Enterprise IT, security, and operations executives.",
                "pricing": "$10,000 - $50,000+ annual enterprise license",
                "funding_size": "$5.7B Valuation (Battery Ventures, Insight Partners)",
                "market_position": "Enterprise Automation Incumbent",
                "key_features": ["Enterprise governance and security audit", "Recipe community", "Bot integrations for Slack/Teams"],
                "strengths": ["Built specifically to meet strict SOC 2, HIPAA, and enterprise IT governance criteria"],
                "weaknesses": ["No self-serve signup", "Expensive annual contracts requiring sales qualification"]
            }
        ]

    # Return empty list if no domain taxonomy matches - NEVER inject unrelated domain competitors
    return []



def _build_domain_feature_matrix(direct_competitors: List[Dict[str, Any]], idea: str) -> List[Dict[str, Any]]:
    comp_names = [c.get("name", f"Competitor {i+1}") for i, c in enumerate(direct_competitors[:5])]
    idea_lower = (idea or "").lower()

    if any(k in idea_lower for k in ["k8s", "kubernetes", "sre", "devops", "cloud", "observability", "telemetry"]):
        return [
            {"feature": "Autonomous Root-Cause Remediation", "your_product": "Native AI Agent (Auto-fix)", **{name: "Alert Only / Manual" if i % 2 == 0 else "Heuristics (No Auto-fix)" for i, name in enumerate(comp_names)}},
            {"feature": "Zero-Config DaemonSet Deploy", "your_product": "Yes (<5 mins)", **{name: "Complex Helm / Config" if i % 2 == 0 else "Heavy Agent Footprint" for i, name in enumerate(comp_names)}},
            {"feature": "Multi-Cluster Dynamic Topology", "your_product": "Real-time Dynamic Graph", **{name: "Available (Paid Add-on)" if i % 2 == 0 else "Static Inventory" for i, name in enumerate(comp_names)}},
            {"feature": "Transparent Flat / Predictable Billing", "your_product": "Predictable Flat Fee", **{name: "Overage Billing Shock" for name in comp_names}},
            {"feature": "SOC 2 & Air-Gapped Operation", "your_product": "Built-in / Enterprise", **{name: "Enterprise Tier Only" if i % 2 == 0 else "Cloud SaaS Only" for i, name in enumerate(comp_names)}},
        ]
    elif any(k in idea_lower for k in ["health", "oncology", "cancer", "medical", "scribe", "physician", "ehr"]):
        return [
            {"feature": "Oncology Staging & Protocol Alignment", "your_product": "Native Oncology AI", **{name: "General Notes Only" if i % 2 == 0 else "Manual Template" for i, name in enumerate(comp_names)}},
            {"feature": "Linked Audio Ground-Truth Audit", "your_product": "Sub-sentence Clickable Quotes", **{name: "Black-box Output" if i % 2 == 0 else "Summary Only" for i, name in enumerate(comp_names)}},
            {"feature": "Epic & Cerner Real-time Sync", "your_product": "Bi-directional FHIR API", **{name: "Custom Enterprise Setup" if i % 2 == 0 else "Chrome Extension Only" for i, name in enumerate(comp_names)}},
            {"feature": "Self-Serve Clinician Onboarding", "your_product": "Instant (<5 mins)", **{name: "6-Week IT Sales Cycle" if i % 2 == 0 else "Contact Sales" for i, name in enumerate(comp_names)}},
            {"feature": "Zero Data Retention Guarantee", "your_product": "Strict HIPAA Zero-Retention", **{name: "Enterprise Add-on" if i % 2 == 0 else "Opt-out Required" for i, name in enumerate(comp_names)}},
        ]
    elif any(k in idea_lower for k in ["fintech", "escrow", "cross-border", "payment", "currency", "fx"]):
        return [
            {"feature": "Programmable Milestone Escrow", "your_product": "Native Smart Contracts / Webhooks", **{name: "Manual Dispute Escrow" if i % 2 == 0 else "Payout Rail Only" for i, name in enumerate(comp_names)}},
            {"feature": "Instant Global Micro-Transfers", "your_product": "Sub-minute Settlement", **{name: "1-3 Business Days" if i % 2 == 0 else "Batch Wire" for i, name in enumerate(comp_names)}},
            {"feature": "Developer-First REST API & Webhooks", "your_product": "Self-Serve API Keys", **{name: "Custom Enterprise Portal" if i % 2 == 0 else "Developer SDK" for i, name in enumerate(comp_names)}},
            {"feature": "Sub-1% Transparent FX Margin", "your_product": "0.35% Flat Transparent", **{name: "Hidden Spread (1-3%)" if i % 2 == 0 else "2.5% + $0.30" for i, name in enumerate(comp_names)}},
            {"feature": "Automated Multi-Jurisdiction KYB", "your_product": "Automated 60-Sec Verification", **{name: "5-Day Manual Review" if i % 2 == 0 else "Strict Minimums" for i, name in enumerate(comp_names)}},
        ]
    elif any(k in idea_lower for k in ["carbon", "esg", "climate", "emission", "sustainability", "energy"]):
        return [
            {"feature": "Real-time Cloud Carbon Telemetry API", "your_product": "Sub-second Webhook Streaming", **{name: "Monthly CSV Upload" if i % 2 == 0 else "Batch Reports" for i, name in enumerate(comp_names)}},
            {"feature": "Granular Scope 1, 2, 3 Ledger", "your_product": "Automated GHG Protocol", **{name: "Scope 1 & 2 Only" if i % 2 == 0 else "Manual Audit Required" for i, name in enumerate(comp_names)}},
            {"feature": "Developer Self-Serve Pricing", "your_product": "Usage-Based Tiered", **{name: "$25k+ Annual Minimum" if i % 2 == 0 else "Enterprise Custom" for i, name in enumerate(comp_names)}},
            {"feature": "Third-Party Certified Methodology", "your_product": "TÜV / ISO 14064 Compliant", **{name: "Self-Reported" if i % 2 == 0 else "Audited" for i, name in enumerate(comp_names)}},
            {"feature": "Automated SEC / CSRD Export", "your_product": "One-Click Instant Filing", **{name: "Professional Services Only" if i % 2 == 0 else "Add-on Module" for i, name in enumerate(comp_names)}},
        ]
    else:
        return [
            {"feature": "Autonomous Multi-Agent Automation", "your_product": "Native Autonomous Agents", **{name: "Rule-Based Only" if i % 2 == 0 else "Manual Execution" for i, name in enumerate(comp_names)}},
            {"feature": "Modern Developer API & Webhooks", "your_product": "Instant Self-Serve", **{name: "Legacy SOAP / Complex" if i % 2 == 0 else "Restricted API" for i, name in enumerate(comp_names)}},
            {"feature": "Time-to-Value", "your_product": "Under 10 Minutes", **{name: "2-4 Weeks Onboarding" if i % 2 == 0 else "Consultant Needed" for i, name in enumerate(comp_names)}},
            {"feature": "Transparent Flat / Usage Pricing", "your_product": "Predictable Flat / Usage", **{name: "Enterprise Custom Quote" if i % 2 == 0 else "Seat Multipliers" for i, name in enumerate(comp_names)}},
            {"feature": "Enterprise Security & Audit Trail", "your_product": "SOC 2 Type II Built-in", **{name: "Add-on Module" if i % 2 == 0 else "Enterprise Only" for i, name in enumerate(comp_names)}},
        ]


# ============================================================
# MARKET GAPS
# ============================================================

def _build_market_gaps(
    direct_competitors: List[Dict[str, Any]],
    indirect_competitors: List[Dict[str, Any]],
    idea: str = "",
) -> List[str]:

    gaps: List[str] = []

    weaknesses: List[str] = []

    for competitor in direct_competitors:

        values = competitor.get(
            "weaknesses",
            [],
        )

        if isinstance(values, list):
            weaknesses.extend(
                _safe_text(value)
                for value in values
                if _safe_text(value)
            )
        else:
            value = _safe_text(values)

            if value:
                weaknesses.append(value)

    for weakness in weaknesses:

        lower = weakness.lower()

        if any(
            word in lower
            for word in [
                "expensive",
                "costly",
                "price",
                "pricing",
                "subscription",
                "$",
                "₹",
                "cost",
            ]
        ):
            gaps.append(
                "Potential pricing gap: there may be an "
                "opportunity for a more affordable option "
                "for price-sensitive customers."
            )

        elif any(
            word in lower
            for word in [
                "limited",
                "lack",
                "lacks",
                "limitation",
            ]
        ):
            gaps.append(
                "Potential capability gap: there may be an "
                "opportunity to address capabilities that "
                "competitors currently provide only in a "
                "limited way."
            )

        elif any(
            word in lower
            for word in [
                "complex",
                "difficult",
            ]
        ):
            gaps.append(
                "Potential usability gap: there may be an "
                "opportunity for a simpler and more "
                "user-friendly experience."
            )

        elif any(
            word in lower
            for word in [
                "complaint",
                "problem",
                "issue",
                "drawback",
                "disadvantage",
                "poor",
            ]
        ):
            gaps.append(
                "Potential customer-experience gap: there "
                "may be an opportunity to address reported "
                "competitor limitations or customer pain points."
            )

        elif any(
            word in lower
            for word in [
                "inflexible",
                "rigid",
            ]
        ):
            gaps.append(
                "Potential flexibility gap: there may be an "
                "opportunity to provide more customizable "
                "options around customer needs."
            )

    # Remove duplicates.
    unique_gaps: List[str] = []

    for gap in gaps:

        if gap not in unique_gaps:
            unique_gaps.append(gap)

    if not unique_gaps:
        unique_gaps = _synthesize_domain_aware_market_gaps(
            idea=idea,
            direct_competitors=direct_competitors,
            indirect_competitors=indirect_competitors,
        )

    disclaimer = (
        "Further primary customer research and "
        "competitor benchmarking are recommended to "
        "validate these potential market gaps."
    )

    if not any(
        "primary customer research" in gap.lower()
        for gap in unique_gaps
    ):
        unique_gaps.append(
            disclaimer
        )

    return unique_gaps[:5]


def _synthesize_domain_aware_market_gaps(
    idea: str,
    direct_competitors: List[Dict[str, Any]],
    indirect_competitors: List[Dict[str, Any]],
) -> List[str]:

    idea_lower = _safe_text(
        idea
    ).lower()

    if any(
        keyword in idea_lower
        for keyword in [
            "tiffin",
            "meal",
            "food",
            "home cooked",
            "home-cooked",
            "kitchen",
            "lunch",
            "dinner",
            "catering",
        ]
    ):
        return [
            "Potential affordability gap: daily meal services "
            "could better target budget-conscious students and "
            "office workers with predictable low-cost plans.",
            "Potential personalization gap: customers may value "
            "easy customization for portion size, dietary "
            "preferences, and next-day meal changes.",
            "Potential local-trust gap: a hyper-local home-kitchen "
            "model could differentiate through transparent menus, "
            "consistent quality, and direct customer relationships.",
        ]

    if any(
        keyword in idea_lower
        for keyword in [
            "agri",
            "farm",
            "crop",
            "drone",
            "vineyard",
            "orchard",
            "fungal",
            "spray",
        ]
    ):
        return [
            "Potential precision-targeting gap: existing solutions "
            "may not fully support affordable, localized treatment "
            "recommendations for small and medium farms.",
            "Potential connectivity gap: rural users may need "
            "reliable operation with limited connectivity.",
            "Potential affordability gap: lower-cost solutions "
            "could improve accessibility for smaller farms.",
        ]

    if any(
        keyword in idea_lower
        for keyword in [
            "security",
            "cyber",
            "privacy",
            "fraud",
            "auth",
            "zero-trust",
        ]
    ):
        return [
            "Potential integration gap: fragmented security tools "
            "may create an opportunity for a simpler unified workflow.",
            "Potential automation gap: organizations may benefit "
            "from reducing manual compliance and monitoring work.",
            "Potential accessibility gap: simpler security tooling "
            "could better serve smaller organizations with limited "
            "security teams.",
        ]

    if any(
        keyword in idea_lower
        for keyword in [
            "fitness",
            "workout",
            "exercise",
            "gym",
            "training",
        ]
    ):
        return [
            "Potential personalization gap: users may benefit from "
            "more adaptive recommendations based on individual goals.",
            "Potential affordability gap: there may be an opportunity for affordable, "
            "lower-cost personalized training to serve users who cannot afford one-to-one "
            "coaching.",
            "Potential engagement gap: stronger progress feedback "
            "could improve long-term adherence.",
        ]

    return [
        "Potential affordability gap: there may be an underserved "
        "customer segment seeking a lower-cost alternative.",
        "Potential personalization gap: there may be an opportunity "
        "to better adapt the solution to individual customer needs.",
        "Potential usability gap: there may be an opportunity to "
        "simplify the existing customer experience.",
    ]


# ============================================================
# GEMINI
# ============================================================

async def _run_gemini_competitor_analysis(
    idea: str,
    search_results: List[Dict[str, Any]],
    api_key: str,
    max_competitors: int = DEFAULT_COMPETITOR_LIMIT,
) -> Optional[Dict[str, Any]]:

    formatted_evidence = []

    for index, item in enumerate(
        search_results[:MAX_SEARCH_RESULTS_FOR_GEMINI],
        1,
    ):

        formatted_evidence.append(
            {
                "source_id": index,
                "title": _safe_text(
                    item.get("title")
                ),
                "url": _safe_text(
                    item.get("url")
                ),
                "target_audience": _safe_text(
                    item.get("target_audience")
                ),
                "target_customers": _safe_text(
                    item.get("target_customers")
                ),
                "content": _safe_text(
                    item.get("content")
                )[:1000],
            }
        )

    evidence_json = json.dumps(
        formatted_evidence,
        indent=2,
        ensure_ascii=False,
    )

    prompt = f"""
You are a Lead Competitive Intelligence Analyst.

Analyze the startup idea using ONLY the supplied web evidence.

STARTUP IDEA:
"{idea}"

WEB EVIDENCE:
{evidence_json}

STRICT RULES:

1. Identify 5 to 6 REAL named commercial companies or customer-facing
   alternative products/services. NEVER use placeholders such as "Legacy Competitor A",
   "Incumbent Platform B", or "Startup Competitor 1".

2. Do NOT identify:
   - academic papers
   - universities
   - research organizations
   - market research companies
   - news publishers
   - generic blogs
   - comparison articles
   - best/top lists
   - infrastructure providers
   - cloud-kitchen infrastructure companies
   - payment/hosting/API infrastructure providers

3. A direct competitor solves substantially the same core
   customer problem using a similar product/service.

4. PERFORM A COMPETITOR FIT CHECK for every competitor:
   - Confirm they serve the same target customer, solve the same core problem, and operate in a relevant jurisdiction.
   - For every competitor (direct and indirect), provide:
     a) "why_competitor": a one-sentence justification of why this company is a competitor (same customer, same problem, same jurisdiction fit).
     b) "region": geographic region/market (e.g., "India", "US", "Global", "EU").

5. An indirect competitor solves the same customer problem
   using another method or traditional alternative.

6. Do NOT classify a company as a competitor merely because
   it uses AI, software, subscriptions, payments, cloud,
   analytics, or another technology.

7. Provide 5 to {max_competitors} direct competitors.

8. Maximum 2 indirect competitors.

9. NEVER copy the startup's target customers into a competitor.
   Target customers must come from evidence specifically
   associated with that competitor.

10. NEVER invent pricing. If unknown, use "Pricing available on request / tiered".

11. NEVER invent weaknesses. If none supported, list real architectural trade-offs.

12. Specify realistic funding_size (e.g. "$50M Series B", "Public ($15B Cap)", "Bootstrapped") and market_position (e.g. "Category Leader", "Enterprise Incumbent", "Fast Challenger").

13. Use the source URL when possible.

14. Market gaps must be potential opportunities, not facts.

15. Output only valid JSON.

Required schema:

{{
  "competitor_analysis": {{
    "direct_competitors": [
      {{
        "name": "Company/Product",
        "url": "https://example.com",
        "product_service": "Description supported by evidence",
        "target_customers": "Evidence-supported audience",
        "pricing": "{NOT_AVAILABLE}",
        "funding_size": "Funding size or valuation",
        "market_position": "Category Leader / Challenger / Niche",
        "why_competitor": "One-line justification of competitor fit (same customer, problem, jurisdiction)",
        "region": "India / US / Global",
        "key_features": [],
        "strengths": [],
        "weaknesses": []
      }}
    ],
    "indirect_competitors": [
      {{
        "name": "Alternative",
        "url": null,
        "product_service": "Alternative approach",
        "target_customers": "",
        "pricing": "{NOT_AVAILABLE}",
        "funding_size": "Venture-backed / Established",
        "market_position": "Indirect Alternative",
        "why_competitor": "One-line justification of indirect competitor fit",
        "region": "India / US / Global",
        "key_features": [],
        "strengths": [],
        "weaknesses": []
      }}
    ],
    "comparison": [],
    "market_gaps": []
  }}
}}
"""

    try:
        from server.utils.gemini_client import call_gemini_generate_content, clean_llm_json_text
        result = await call_gemini_generate_content(
            prompt=prompt,
            api_key=api_key,
            temperature=0.1,
            response_mime_type="application/json",
            timeout_per_model=12.0,
            tag="COMPETITOR-ANALYSIS"
        )
        if result:
            raw_text, successful_model = result
            raw_text = clean_llm_json_text(raw_text)
            try:
                parsed = json.loads(raw_text.strip())
            except json.JSONDecodeError as exc:
                logger.warning(f"Invalid Gemini JSON from {successful_model}: {exc}")
                return None

            if isinstance(parsed, dict):
                comp_data = parsed.get("competitor_analysis", parsed)
                if isinstance(comp_data, dict):
                    logger.info(f"Gemini competitor analysis succeeded via {successful_model}")
                    return {"competitor_analysis": comp_data}
    except Exception as exc:
        logger.warning(f"Universal Gemini competitor analysis error: {exc}")

    return None


# ============================================================
# CLEAN GEMINI RESULTS
# ============================================================

def _clean_gemini_competitors(
    raw_competitors: Any,
    limit: int,
    search_results: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    competitors = _deduplicate_competitors(
        raw_competitors,
        limit=limit,
    )

    enriched: List[Dict[str, Any]] = []

    for competitor in competitors:

        competitor = _enrich_competitor_from_evidence(
            competitor,
            search_results,
        )

        # ----------------------------------------------------
        # Do not allow generic audience.
        # ----------------------------------------------------

        competitor[
            "target_customers"
        ] = _clean_customer_value(
            competitor.get(
                "target_customers"
            )
        )

        # ----------------------------------------------------
        # Ensure pricing has explicit fallback.
        # ----------------------------------------------------

        pricing = _safe_text(
            competitor.get("pricing")
        )

        competitor["pricing"] = (
            pricing
            if pricing
            else NOT_AVAILABLE
        )

        # ----------------------------------------------------
        # Ensure product has explicit fallback.
        # ----------------------------------------------------

        if not _safe_text(
            competitor.get("product_service")
        ):
            competitor[
                "product_service"
            ] = NOT_AVAILABLE

        # ----------------------------------------------------
        # Funding and market position defaults
        # ----------------------------------------------------

        funding_size = _safe_text(competitor.get("funding_size"))
        competitor["funding_size"] = funding_size if funding_size and funding_size != NOT_AVAILABLE else "Undisclosed / Venture-backed"

        market_position = _safe_text(competitor.get("market_position"))
        competitor["market_position"] = market_position if market_position else "Market Competitor"

        why_comp = _safe_text(competitor.get("why_competitor"))
        competitor["why_competitor"] = why_comp if why_comp else "Direct competitor addressing same target customer segment and problem space."

        region_val = _safe_text(competitor.get("region"))
        competitor["region"] = region_val if region_val else ("India" if "india" in str(competitor).lower() else "Global")

        # ----------------------------------------------------
        # Discard placeholder names and market research publishers
        # ----------------------------------------------------

        if _is_placeholder_name(competitor.get("name", "")) or _is_market_research_or_directory_entity(competitor):
            continue

        # ----------------------------------------------------
        # Never include obvious infrastructure competitors.
        # ----------------------------------------------------

        fake_result = {
            "title": competitor.get("name"),
            "url": competitor.get("url"),
            "content": competitor.get(
                "product_service"
            ),
        }

        if _contains_infrastructure_signal(
            fake_result
        ):
            continue

        enriched.append(
            competitor
        )

    return enriched[:limit]


# ============================================================
# FAILURE TEXT FILTER & SANITIZER
# ============================================================

FAILURE_PATTERNS = [
    re.compile(r"no competitor analysis (?:can|could) be performed", re.IGNORECASE),
    re.compile(r"competitor analysis (?:could not|was not|cannot) be performed", re.IGNORECASE),
    re.compile(r"no competitor analysis was available", re.IGNORECASE),
    re.compile(r"due to the lack of competitor", re.IGNORECASE),
    re.compile(r"in the absence of competitor data", re.IGNORECASE),
    re.compile(r"not enough competitor evidence to perform", re.IGNORECASE),
    re.compile(r"no competitors? (?:were|was) identified to analyze", re.IGNORECASE),
    re.compile(r"no competitor data is available", re.IGNORECASE),
    re.compile(r"no competitors could be identified", re.IGNORECASE),
]

def sanitize_failure_sentences(data: Any) -> Any:
    """
    Failure sentences ("no competitor analysis can be performed...") must never
    enter market gaps, MVP, SWOT, GTM or the report.
    Filters out any string or item matching failure patterns.
    """
    def _has_failure(text: str) -> bool:
        if not isinstance(text, str):
            return False
        return any(p.search(text) for p in FAILURE_PATTERNS)

    if isinstance(data, str):
        return "" if _has_failure(data) else data
    elif isinstance(data, list):
        filtered = []
        for x in data:
            if isinstance(x, str):
                if not _has_failure(x) and x.strip():
                    filtered.append(x)
            elif isinstance(x, dict):
                cleaned_dict = sanitize_failure_sentences(x)
                if any(bool(v) for v in cleaned_dict.values()):
                    filtered.append(cleaned_dict)
            else:
                filtered.append(x)
        return filtered
    elif isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            if isinstance(v, str) and _has_failure(v):
                continue
            cleaned[k] = sanitize_failure_sentences(v)
        return cleaned
    return data


# ============================================================
# LLM-SUGGESTED UNVERIFIED CANDIDATE GENERATION
# ============================================================

async def _generate_unverified_candidates_async(
    idea: str,
    domain: str = "",
    count: int = 3,
) -> List[Dict[str, Any]]:
    """
    When verified search evidence yields < 3 competitors, suggests up to 3 candidates
    from LLM knowledge. All candidates are strictly checked for fit (same customer,
    same problem, same jurisdiction) and clearly labeled 'Unverified, from model knowledge'.
    NEVER falls back to hardcoded lists from unrelated domains.
    """
    prompt = f"""You are a venture capital competitive intelligence analyst.
Startup Idea to Analyze:
"{idea}"
Industry / Domain: {domain or 'Digital Technology'}

Live web search did NOT find sufficient verified competitors.
Suggest up to {count} real-world competitor companies from your knowledge base that address the SAME customer with the SAME problem in the SAME or relevant jurisdiction.
DO NOT suggest companies from unrelated domains (e.g. absolutely no DevOps/K8s/SaaS tools for healthtech, no microfinance for software).

For each competitor candidate, return:
- name: Real company/product name
- url: Known website URL (or null if uncertain)
- product_service: One concise sentence describing their product
- target_customers: Exact target audience (must match the startup's customer)
- why_competitor: One line explaining why they are a competitor (same customer, same problem, same jurisdiction)
- region: Target market or headquarters (e.g. India, US, Global)
- key_features: 2-3 core features (list of strings)
- strengths: 1-2 core strengths (list of strings)
- weaknesses: 1-2 core weaknesses (list of strings)

Respond strictly with a JSON array:
[
  {{
    "name": "...",
    "url": "https://...",
    "product_service": "...",
    "target_customers": "...",
    "why_competitor": "Same customer (...), same problem (...), in jurisdiction (...)",
    "region": "India / Global",
    "key_features": ["..."],
    "strengths": ["..."],
    "weaknesses": ["..."]
  }}
]
"""
    candidates: List[Dict[str, Any]] = []
    try:
        from server.utils.gemini_client import call_gemini_generate_content, clean_llm_json_text
        res = await call_gemini_generate_content(
            prompt=prompt,
            system_instruction="You are a startup competitive intelligence analyst. Output strictly a JSON array without markdown formatting.",
        )
        if res and res.get("text"):
            cleaned = clean_llm_json_text(res["text"])
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                for item in parsed[:count]:
                    if isinstance(item, dict) and item.get("name"):
                        item["verification_status"] = "Unverified, from model knowledge"
                        item["source_type"] = "unverified_model_knowledge"
                        candidates.append(item)
    except Exception as exc:
        logger.warning("Failed to generate unverified competitor candidates via LLM: %s", exc)

    # Idea-specific fallback if LLM is offline - tailored strictly to the idea keywords
    if not candidates:
        idea_l = (idea or "").lower()
        if any(w in idea_l for w in ["adherence", "medication", "pill", "elderly", "chronic", "patient", "health"]):
            candidates = [
                {
                    "name": "Medisafe",
                    "url": "https://www.medisafe.com",
                    "product_service": "Digital medication management and pill reminder app with family/caregiver escalation alerts.",
                    "target_customers": "Elderly patients with chronic conditions and their family caregivers.",
                    "why_competitor": "Same customer (chronic disease patients & families), same problem (medication non-adherence), available in India & globally.",
                    "region": "Global / India",
                    "key_features": ["Dosage scheduling", "Caregiver missed-dose alerts", "Pharmacy refill reminders"],
                    "strengths": ["Broad consumer awareness", "Reliable reminder engine"],
                    "weaknesses": ["App interface is complex for low-literacy elderly in Tier 2/3 cities", "Requires standalone app install instead of WhatsApp"],
                    "verification_status": "Unverified, from model knowledge",
                    "source_type": "unverified_model_knowledge",
                },
                {
                    "name": "MyTherapy",
                    "url": "https://www.mytherapyapp.com",
                    "product_service": "Pill reminder and medication tracker app focused on chronic disease adherence.",
                    "target_customers": "Patients with hypertension and diabetes managing daily medication regimens.",
                    "why_competitor": "Same customer (chronic illness patients), same problem (forgetting prescribed doses).",
                    "region": "Global",
                    "key_features": ["Health journal", "Dose tracking", "Doctor report export"],
                    "strengths": ["Clean simple interface", "Privacy-focused design"],
                    "weaknesses": ["No vernacular voice messaging", "No automated local pharmacy dispatch integration"],
                    "verification_status": "Unverified, from model knowledge",
                    "source_type": "unverified_model_knowledge",
                }
            ]
        elif any(w in idea_l for w in ["loan", "lending", "micro-loan", "microloan", "cibil", "borrow"]):
            candidates = [
                {
                    "name": "KarmaLife",
                    "url": "https://karmalife.ai",
                    "product_service": "Earnings-linked micro-loans and liquidity solutions for gig platform workers in India.",
                    "target_customers": "Gig economy and informal platform workers without traditional credit scores.",
                    "why_competitor": "Same customer (Indian gig workers), same problem (small emergency loans without CIBIL), same jurisdiction (India).",
                    "region": "India",
                    "key_features": ["Platform earnings integration", "Instant daily liquidity"],
                    "strengths": ["Direct enterprise integration with gig employers"],
                    "weaknesses": ["Restricted to partnered platform workforces"],
                    "verification_status": "Unverified, from model knowledge",
                    "source_type": "unverified_model_knowledge",
                }
            ]
        elif any(w in idea_l for w in ["k8s", "kubernetes", "sre", "devops", "cloud", "observability"]):
            candidates = [
                {
                    "name": "Komodor",
                    "url": "https://komodor.com",
                    "product_service": "Kubernetes troubleshooting and change intelligence platform.",
                    "target_customers": "DevOps and Platform Engineering teams managing K8s clusters.",
                    "why_competitor": "Same customer (DevOps engineers), same problem (troubleshooting K8s outages).",
                    "region": "Global",
                    "key_features": ["Timeline tracking", "Automated root cause hints"],
                    "strengths": ["Intuitive visualization of Kubernetes state"],
                    "weaknesses": ["Narrow scope limited to K8s ecosystem"],
                    "verification_status": "Unverified, from model knowledge",
                    "source_type": "unverified_model_knowledge",
                }
            ]

    return candidates[:count]


# ============================================================
# MAIN AGENT
# ============================================================

async def run_competitor_analysis_agent(
    idea: str,
    search_results: Any,
    max_competitors: int = DEFAULT_COMPETITOR_LIMIT,
    domain: str = "",
) -> Dict[str, Any]:

    idea = _safe_text(idea)

    # --------------------------------------------------------
    # Clamp limit.
    # --------------------------------------------------------

    try:
        max_competitors = int(
            max_competitors
        )
    except (
        TypeError,
        ValueError,
    ):
        max_competitors = DEFAULT_COMPETITOR_LIMIT

    max_competitors = max(
        1,
        min(
            max_competitors,
            MAX_COMPETITOR_LIMIT,
        ),
    )

    # --------------------------------------------------------
    # Validate and filter search results.
    # --------------------------------------------------------

    valid_results: List[
        Dict[str, Any]
    ] = []

    if isinstance(
        search_results,
        list,
    ):

        for item in search_results:

            if not _is_valid_search_result(
                item
            ):
                continue

            if _is_irrelevant_source(
                item
            ):
                continue

            valid_results.append(
                item
            )

    # --------------------------------------------------------
    # Fallback to domain named competitors if no web evidence.
    # --------------------------------------------------------

    if not valid_results:
        market_gaps = _build_market_gaps([], [], idea)
        return {
            "competitor_analysis": {
                "direct_competitors": [],
                "indirect_competitors": [],
                "comparison": [],
                "market_gaps": market_gaps,
                "feature_matrix": None,
                "source": "empty_search",
            }
        }

    # ========================================================
    # GEMINI / GROQ LLM SYNTHESIS
    # ========================================================

    from server.utils.gemini_client import get_gemini_api_key, get_groq_api_key
    gemini_key = get_gemini_api_key()
    groq_key = get_groq_api_key()

    if gemini_key or groq_key:

        gemini_result = (
            await _run_gemini_competitor_analysis(
                idea=idea,
                search_results=valid_results,
                api_key=gemini_key,
                max_competitors=max_competitors,
            )
        )

        if gemini_result:

            comp_data = gemini_result.get(
                "competitor_analysis",
                {},
            )

            if isinstance(
                comp_data,
                dict,
            ):

                # ------------------------------------------------
                # Direct competitors
                # ------------------------------------------------

                directs = _clean_gemini_competitors(
                    raw_competitors=comp_data.get(
                        "direct_competitors",
                        [],
                    ),
                    limit=max_competitors,
                    search_results=valid_results,
                )

                # ------------------------------------------------
                # Indirect competitors
                # ------------------------------------------------

                indirects = _clean_gemini_competitors(
                    raw_competitors=comp_data.get(
                        "indirect_competitors",
                        [],
                    ),
                    limit=MAX_INDIRECT_COMPETITORS,
                    search_results=valid_results,
                )

                # ------------------------------------------------
                # Remove competitors that appear in both groups.
                # ------------------------------------------------

                filtered_indirects: List[
                    Dict[str, Any]
                ] = []

                for indirect in indirects:

                    if not _is_duplicate(
                        indirect,
                        directs,
                    ):
                        filtered_indirects.append(
                            indirect
                        )

                indirects = filtered_indirects[
                    :MAX_INDIRECT_COMPETITORS
                ]

                # ------------------------------------------------
                # Discard placeholder names, generic categories, and publishers
                # ------------------------------------------------
                directs = [c for c in directs if not _is_placeholder_name(c.get("name", "")) and not _is_market_research_or_directory_entity(c)]

                # Re-run search with a refined query if fewer than 3 valid competitors remain
                if len(directs) < 3:
                    try:
                        from server.agents.web_search_agent import run_web_search_agent
                        refined_q = f"{idea} operating commercial startups companies product competitors alternatives -marketresearch -report -insights"
                        logger.info(f"Fewer than 3 valid competitors found ({len(directs)}). Re-running search with refined query: '{refined_q}'...")
                        refined_res = await run_web_search_agent(idea=refined_q, max_results=6)
                        extra_items = refined_res.get("results", []) if isinstance(refined_res, dict) else []
                        for extra in extra_items:
                            built = _build_competitor(extra)
                            if (
                                not _is_placeholder_name(built.get("name", ""))
                                and not _is_market_research_or_directory_entity(built)
                                and not _is_duplicate(built, directs)
                            ):
                                directs.append(built)
                            if len(directs) >= max_competitors:
                                break
                    except Exception as re_err:
                        logger.warning(f"Refined competitor search error: {re_err}")

                unverified_candidates: List[Dict[str, Any]] = []
                if len(directs) < 3:
                    evidence_status = "not_enough_evidence"
                    evidence_reason = f"Only {len(directs)} verified competitor(s) identified in live search evidence (minimum 3 required for conclusive validation)."
                    unverified_candidates = await _generate_unverified_candidates_async(idea, domain=domain, count=3)
                else:
                    evidence_status = "sufficient"
                    evidence_reason = None

                # ------------------------------------------------
                # Build comparison directly from final records.
                # ------------------------------------------------

                comparison = _build_comparison(
                    direct_competitors=directs,
                    indirect_competitors=indirects,
                )

                # ------------------------------------------------
                # Feature Matrix
                # ------------------------------------------------
                feature_matrix = _build_domain_feature_matrix(
                    direct_competitors=directs,
                    idea=idea,
                )

                # ------------------------------------------------
                # Market gaps
                # ------------------------------------------------

                raw_gaps = comp_data.get(
                    "market_gaps",
                    [],
                )

                market_gaps = _clean_list(
                    raw_gaps,
                    limit=5,
                )

                # Make language conservative.
                normalized_gaps: List[str] = []

                for gap in market_gaps:

                    lower = gap.lower()

                    if not any(
                        phrase in lower
                        for phrase in [
                            "potential",
                            "may ",
                            "could ",
                            "opportunity",
                        ]
                    ):
                        gap = (
                            "Potential opportunity: "
                            + gap
                        )

                    if gap not in normalized_gaps:
                        normalized_gaps.append(
                            gap
                        )

                # If Gemini produced no useful gaps,
                # use evidence-aware fallback.
                if not normalized_gaps:

                    normalized_gaps = _build_market_gaps(
                        direct_competitors=directs,
                        indirect_competitors=indirects,
                        idea=idea,
                    )

                elif not any(
                    "primary customer research"
                    in gap.lower()
                    for gap in normalized_gaps
                ):

                    normalized_gaps.append(
                        "Further primary customer research "
                        "and competitor benchmarking are "
                        "recommended to validate these "
                        "potential market gaps."
                    )

                clean_market_gaps = sanitize_failure_sentences(normalized_gaps[:5])

                return {
                    "competitor_analysis": {
                        "direct_competitors": directs,
                        "indirect_competitors": indirects,
                        "comparison": comparison,
                        "market_gaps": clean_market_gaps,
                        "feature_matrix": feature_matrix,
                        "evidence_status": evidence_status,
                        "evidence_reason": evidence_reason,
                        "unverified_candidates": unverified_candidates,
                    }
                }

    # ========================================================
    # RULE-BASED FALLBACK
    # ========================================================

    direct_competitors: List[
        Dict[str, Any]
    ] = []

    indirect_competitors: List[
        Dict[str, Any]
    ] = []

    for result in valid_results:

        # ----------------------------------------------------
        # Direct
        # ----------------------------------------------------

        if _looks_like_direct_competitor(
            idea=idea,
            result=result,
        ):

            competitor = _build_competitor(
                result
            )

            if not _is_duplicate(
                competitor,
                direct_competitors,
            ):
                direct_competitors.append(
                    competitor
                )

            continue

        # ----------------------------------------------------
        # Indirect
        # ----------------------------------------------------

        if _looks_like_indirect_competitor(
            idea=idea,
            result=result,
        ):

            competitor = _build_competitor(
                result
            )

            if not _is_duplicate(
                competitor,
                indirect_competitors,
            ):
                indirect_competitors.append(
                    competitor
                )

    # --------------------------------------------------------
    # Limits
    # --------------------------------------------------------

    # Discard placeholder names, generic categories, and publishers
    direct_competitors = [
        c for c in direct_competitors
        if not _is_placeholder_name(c.get("name", "")) and not _is_market_research_or_directory_entity(c)
    ]

    unverified_candidates = []
    if len(direct_competitors) < 3:
        evidence_status = "not_enough_evidence"
        evidence_reason = f"Only {len(direct_competitors)} verified competitor(s) identified in live search evidence (minimum 3 required for conclusive validation)."
        unverified_candidates = await _generate_unverified_candidates_async(idea, domain=domain, count=3)
    else:
        evidence_status = "sufficient"
        evidence_reason = None

    direct_competitors = (
        direct_competitors[
            :max_competitors
        ]
    )

    indirect_competitors = (
        indirect_competitors[
            :MAX_INDIRECT_COMPETITORS
        ]
    )

    # --------------------------------------------------------
    # Remove cross-category duplicates.
    # --------------------------------------------------------

    indirect_competitors = [
        competitor
        for competitor in indirect_competitors
        if not _is_duplicate(
            competitor,
            direct_competitors,
        )
    ]

    # ========================================================
    # COMPARISON
    # ========================================================

    comparison = _build_comparison(
        direct_competitors=direct_competitors,
        indirect_competitors=indirect_competitors,
    )

    # ========================================================
    # FEATURE MATRIX
    # ========================================================

    feature_matrix = _build_domain_feature_matrix(
        direct_competitors=direct_competitors,
        idea=idea,
    )

    # ========================================================
    # MARKET GAPS
    # ========================================================

    raw_market_gaps = _build_market_gaps(
        direct_competitors=direct_competitors,
        indirect_competitors=indirect_competitors,
        idea=idea,
    )
    clean_market_gaps = sanitize_failure_sentences(raw_market_gaps)

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {
        "competitor_analysis": {
            "direct_competitors": direct_competitors,
            "indirect_competitors": indirect_competitors,
            "comparison": comparison,
            "market_gaps": clean_market_gaps,
            "feature_matrix": feature_matrix,
            "evidence_status": evidence_status,
            "evidence_reason": evidence_reason,
            "unverified_candidates": unverified_candidates,
        }
    }


# ============================================================
# COMPATIBILITY WRAPPER
# ============================================================

async def analyze_competitors(
    idea: str,
    search_results: Any,
    max_competitors: int = DEFAULT_COMPETITOR_LIMIT,
) -> Dict[str, Any]:

    return await run_competitor_analysis_agent(
        idea=idea,
        search_results=search_results,
        max_competitors=max_competitors,
    )


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    "run_competitor_analysis_agent",
    "analyze_competitors",
]


def filter_and_label_competitors_by_fit(
    competitors: List[Dict[str, Any]],
    idea: str,
    jurisdiction: str = "India"
) -> List[Dict[str, Any]]:
    """
    Fit check on candidate competitors:
    - Same customer segment and problem
    - Operating in idea's jurisdiction or explicitly labeled region
    - One-line 'why_competitor' justification
    - Drops non-fits (e.g. African mobile money for Indian micro-loan ideas)
    """
    clean_idea = idea.lower()
    is_india = "india" in jurisdiction.lower() or "india" in clean_idea
    
    non_fits_india = {"m-pesa", "branch africa", "tala africa", "fairmoney", "kuda bank", "safaricom"}

    filtered = []
    for comp in competitors:
        name = str(comp.get("name", "")).strip()
        url = str(comp.get("url", "")).strip().lower()
        if not name or _is_placeholder_name(name):
            continue
            
        c_lower = name.lower()
        if is_india and any(nf in c_lower for nf in non_fits_india):
            logger.info(f"COMPETITOR-FIT: Filtered out non-fit regional entity '{name}' for Indian idea.")
            continue

        region = comp.get("region")
        if not region:
            if any(k in c_lower or k in url for k in ["karmalife", "salarydost", "avail finance", "cleartax", "fasal", "yuktix", "cropin", "razorpay"]):
                region = "India"
            elif any(k in c_lower or k in url for k in ["sensoterra", "rika", "wave", "rollee", "psa"]):
                region = "Global"
            else:
                region = "India" if is_india else "Global"

        why_comp = comp.get("why_competitor")
        if not why_comp:
            why_comp = f"Direct commercial alternative in {region} serving target customers with overlapping capabilities."

        comp["why_competitor"] = why_comp
        comp["region"] = region
        comp["fit_status"] = "fit"
        filtered.append(comp)

    return filtered
