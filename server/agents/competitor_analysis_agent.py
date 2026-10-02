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
MAX_COMPETITOR_LIMIT = 5
MAX_INDIRECT_COMPETITORS = 2
MAX_SEARCH_RESULTS_FOR_GEMINI = 8

NOT_AVAILABLE = "Not available in retrieved sources"


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

    if len(overlap) >= 3:
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
        direct_competitors
    )

    if indirect_competitors:
        all_competitors.extend(
            indirect_competitors
        )

    for competitor in all_competitors:

        pricing = _safe_text(
            competitor.get("pricing")
        )

        if not pricing:
            pricing = NOT_AVAILABLE

        comparison.append(
            {
                "competitor": _safe_text(
                    competitor.get("name")
                ),
                "product_service": _safe_text(
                    competitor.get("product_service")
                ) or NOT_AVAILABLE,
                "target_customers": _clean_customer_value(
                    competitor.get("target_customers")
                ),
                "pricing": pricing,
                "key_features": _join_values(
                    competitor.get("key_features")
                ) or NOT_AVAILABLE,
                "strengths": _join_values(
                    competitor.get("strengths")
                ) or NOT_AVAILABLE,
                "weaknesses": _join_values(
                    competitor.get("weaknesses")
                ) or NOT_AVAILABLE,
            }
        )

    return comparison


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
            "Potential affordability gap: lower-cost personalized "
            "training could serve users who cannot afford one-to-one "
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

1. Identify REAL commercial competitors or customer-facing
   alternative services.

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

4. An indirect competitor solves the same customer problem
   using another method or traditional alternative.

5. Do NOT classify a company as a competitor merely because
   it uses AI, software, subscriptions, payments, cloud,
   analytics, or another technology.

6. Maximum {max_competitors} direct competitors.

7. Maximum 2 indirect competitors.

8. NEVER copy the startup's target customers into a competitor.
   Target customers must come from evidence specifically
   associated with that competitor.

9. NEVER invent pricing.

10. If pricing is not explicitly supported by the evidence,
    use:
    "{NOT_AVAILABLE}"

11. NEVER invent weaknesses.

12. If no weakness is supported, use an empty list.

13. NEVER invent target customers.

14. If target customers are not supported by evidence,
    use an empty string.

15. Use the source URL when possible.

16. Market gaps must be potential opportunities, not facts.

17. Output only valid JSON.

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

    models = [
        "gemini-3.6-flash",
        "gemini-3-flash-preview",
        "gemini-flash-lite-latest",
        "gemini-2.5-flash",
    ]

    for model in models:

        url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{model}:generateContent"
            f"?key={api_key.strip()}"
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
            },
        }

        for attempt in range(3):

            try:

                timeout = httpx.Timeout(
                    30.0,
                    connect=5.0,
                )

                async with httpx.AsyncClient(
                    timeout=timeout
                ) as client:

                    response = await client.post(
                        url,
                        json=payload,
                    )

                if response.status_code == 200:

                    data = response.json()

                    candidates = data.get(
                        "candidates",
                        [],
                    )

                    if not candidates:
                        break

                    parts = (
                        candidates[0]
                        .get("content", {})
                        .get("parts", [])
                    )

                    if not parts:
                        break

                    raw_text = _safe_text(
                        parts[0].get("text")
                    )

                    if not raw_text:
                        break

                    raw_text = re.sub(
                        r"^```(?:json)?\s*",
                        "",
                        raw_text,
                        flags=re.IGNORECASE,
                    )

                    raw_text = re.sub(
                        r"\s*```$",
                        "",
                        raw_text,
                    )

                    try:
                        parsed = json.loads(
                            raw_text.strip()
                        )
                    except json.JSONDecodeError as exc:

                        logger.warning(
                            "Invalid Gemini JSON from %s: %s",
                            model,
                            exc,
                        )

                        break

                    if not isinstance(
                        parsed,
                        dict,
                    ):
                        break

                    comp_data = parsed.get(
                        "competitor_analysis",
                        parsed,
                    )

                    if not isinstance(
                        comp_data,
                        dict,
                    ):
                        break

                    return {
                        "competitor_analysis": comp_data
                    }

                if response.status_code in (
                    400,
                    401,
                    403,
                ):
                    logger.warning(
                        "Gemini HTTP %s. "
                        "Stopping Gemini analysis.",
                        response.status_code,
                    )
                    return None

                if response.status_code == 404:
                    logger.warning(
                        "Gemini model %s unavailable.",
                        model,
                    )
                    break

                if response.status_code in (
                    429,
                    500,
                    502,
                    503,
                    504,
                ):

                    delay = (
                        0.5 * (2 ** attempt)
                    ) + random.uniform(
                        0.1,
                        0.3,
                    )

                    await asyncio.sleep(
                        delay
                    )

                    continue

                logger.warning(
                    "Gemini model %s returned HTTP %s.",
                    model,
                    response.status_code,
                )

                break

            except (
                httpx.ConnectError,
                httpx.ConnectTimeout,
                httpx.NetworkError,
            ) as exc:

                logger.warning(
                    "Gemini connection error: %s",
                    exc,
                )

                break

            except httpx.TimeoutException:

                if attempt < 2:
                    await asyncio.sleep(
                        1.0
                    )
                    continue

                break

            except Exception as exc:

                logger.warning(
                    "Gemini call failed: %s",
                    exc,
                )

                break

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
# MAIN AGENT
# ============================================================

async def run_competitor_analysis_agent(
    idea: str,
    search_results: Any,
    max_competitors: int = DEFAULT_COMPETITOR_LIMIT,
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
    # No usable evidence.
    # --------------------------------------------------------

    if not valid_results:

        return {
            "competitor_analysis": {
                "direct_competitors": [],
                "indirect_competitors": [],
                "comparison": [],
                "market_gaps": [
                    "Potential competitor white-space could "
                    "not be established from the retrieved "
                    "evidence. Further primary and web research "
                    "is recommended."
                ],
            }
        }

    # ========================================================
    # GEMINI
    # ========================================================

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if api_key and api_key.strip():

        gemini_result = (
            await _run_gemini_competitor_analysis(
                idea=idea,
                search_results=valid_results,
                api_key=api_key.strip(),
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
                # Build comparison directly from final records.
                # ------------------------------------------------

                comparison = _build_comparison(
                    direct_competitors=directs,
                    indirect_competitors=indirects,
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

                return {
                    "competitor_analysis": {
                        "direct_competitors": directs,
                        "indirect_competitors": indirects,
                        "comparison": comparison,
                        "market_gaps": normalized_gaps[:5],
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
    # MARKET GAPS
    # ========================================================

    market_gaps = _build_market_gaps(
        direct_competitors=direct_competitors,
        indirect_competitors=indirect_competitors,
        idea=idea,
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {
        "competitor_analysis": {
            "direct_competitors": direct_competitors,
            "indirect_competitors": indirect_competitors,
            "comparison": comparison,
            "market_gaps": market_gaps,
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