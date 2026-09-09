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


# ============================================================
# GENERIC / INVALID CUSTOMER VALUES
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
# STRONG DIGITAL PRODUCT SIGNALS
# ============================================================

STRONG_DIGITAL_PHRASES = [
    "is an app",
    "is a app",
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


# ============================================================
# DIGITAL KEYWORDS
# ============================================================

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
# DIRECT COMPETITOR SIGNALS
# ============================================================

DIRECT_SERVICE_PHRASES = [
    "3d web",
    "webgl",
    "spatial web",
    "motion design",
    "shaders",
    "creative studio",
    "developer tools",
    "design tools",
    "automation platform",
    "ai platform",
    "personalized platform",
    "analytics platform",
    "management software",
    "workflow automation",
    "cloud service",
    "software solution",
]


# ============================================================
# INDIRECT COMPETITOR SIGNALS
# ============================================================

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
# PRICING SIGNALS
# ============================================================

PRICING_KEYWORDS = [
    "price",
    "pricing",
    "cost",
    "costs",
    "subscription",
    "premium subscription",
    "monthly",
    "per month",
    "annual",
    "yearly",
    "per year",
    "free trial",
    "plan starts",
    "plans start",
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


# ============================================================
# FEATURE SIGNALS
# ============================================================

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


# ============================================================
# STRENGTH SIGNALS
# ============================================================

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


# ============================================================
# WEAKNESS SIGNALS
# ============================================================

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
# IRRELEVANT SOURCE DOMAINS
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


# ============================================================
# IRRELEVANT SOURCE PHRASES
# ============================================================

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
    "reprint",
    "mdpi books",
    "benefits of publishing",
    "special issue editors",
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
    "the future of ",
    "comprehensive guide",
    "ultimate guide",
]


# ============================================================
# BASIC HELPERS
# ============================================================

def _safe_text(value: Any) -> str:
    """Safely convert a value to a trimmed string."""
    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    return str(value).strip()


def _normalize_url(url: Any) -> str:
    """Normalize URL for duplicate detection."""
    value = _safe_text(url).lower().strip()

    if not value:
        return ""

    value = value.rstrip("/")

    # Remove common tracking parameters.
    try:
        parsed = urllib.parse.urlparse(value)

        clean_query = urllib.parse.parse_qs(
            parsed.query,
            keep_blank_values=False,
        )

        ignored_params = {
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "fbclid",
            "gclid",
        }

        clean_query = {
            key: values
            for key, values in clean_query.items()
            if key not in ignored_params
        }

        query = urllib.parse.urlencode(
            clean_query,
            doseq=True,
        )

        value = urllib.parse.urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path.rstrip("/"),
                "",
                query,
                "",
            )
        ).rstrip("/")

    except Exception:
        pass

    return value


def _normalize_name(name: Any) -> str:
    """Normalize competitor name."""
    value = _safe_text(name).lower()

    value = re.sub(
        r"[^a-z0-9]+",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def _clean_list(values: Any, limit: int = 5) -> List[str]:
    """
    Convert a list/string into a clean unique list.
    """
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

    cleaned: List[str] = []
    seen = set()

    for value in raw_values:
        text = _safe_text(value)

        if not text:
            continue

        # Remove markdown bullets.
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
        cleaned.append(text)

        if len(cleaned) >= limit:
            break

    return cleaned


def _clean_customer_value(value: Any) -> str:
    """
    Remove generic target-customer values.
    """
    text = _safe_text(value)

    if not text:
        return ""

    normalized = text.lower().strip()

    if normalized in GENERIC_AUDIENCES:
        return ""

    return text


# ============================================================
# SEARCH TEXT
# ============================================================

def _get_search_text(
    result: Dict[str, Any],
) -> str:
    """Combine useful search result fields."""

    parts = [
        _safe_text(result.get("title")),
        _safe_text(result.get("content")),
        _safe_text(result.get("description")),
        _safe_text(result.get("snippet")),
        _safe_text(result.get("target_audience")),
        _safe_text(result.get("target_customers")),
        _safe_text(result.get("target_customer")),
    ]

    return " ".join(
        part
        for part in parts
        if part
    ).strip()


# ============================================================
# SENTENCE EXTRACTION
# ============================================================

def _find_matching_sentences(
    content: str,
    keywords: List[str],
    limit: int = 3,
) -> List[str]:
    """
    Find sentences containing matching keywords.
    """

    text = _safe_text(content)

    if not text:
        return []

    # Correct sentence/newline splitting.
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
# DIGITAL PRODUCT DETECTION
# ============================================================

def _has_strong_digital_identity(
    text: str,
) -> bool:
    """
    Determine whether the result itself represents
    a digital product/platform.

    Generic mentions such as "fitness apps" are not
    sufficient evidence that the result itself is an app.
    """

    lower = _safe_text(text).lower()

    explicit_patterns = [
        r"\bis an app\b",
        r"\bis a app\b",
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

    for pattern in explicit_patterns:
        if re.search(pattern, lower):
            return True

    # Remove generic plural mentions before checking
    # broader identity phrases.
    cleaned_text = lower

    generic_mentions = [
        "fitness apps",
        "workout apps",
        "training apps",
        "fitness platforms",
        "workout platforms",
        "training platforms",
        "food delivery apps",
        "meal delivery apps",
        "restaurant apps",
        "delivery platforms",
    ]

    for phrase in generic_mentions:
        cleaned_text = cleaned_text.replace(
            phrase,
            "",
        )

    identity_phrases = [
        "fitness app",
        "workout app",
        "training app",
        "fitness platform",
        "workout platform",
        "training platform",
        "mobile app",
        "web app",
        "digital platform",
        "online platform",
        "software platform",
        "software",
        "saas",
        "meal delivery platform",
        "food delivery platform",
        "online ordering platform",
    ]

    for phrase in identity_phrases:
        if phrase in cleaned_text:
            return True

    return False


# ============================================================
# SOURCE FILTERING
# ============================================================

def _is_article_title(title: str) -> bool:
    """
    Detect generic article/list/guide titles that are not
    competitor entities.
    """

    if not title:
        return False

    t_clean = title.strip().lower()

    patterns = [
        r"\bhow\s+much\s+(does|is|do)\b",
        r"\bpricing\s+guide\b",
        r"\bcost\s+guide\b",
        r"\bcost\s+breakdown\b",
        r"\bcost\s+of\b",
        r"\bvs\.?\b|\bversus\b|\bcomparison\b",
        r"\bbest\s+[\w\s]{1,30}\s+for\b",
        r"\btop\s+\d+\b|\bbest\s+\d+\b",
        r"\balternatives?\b",
        r"\bbuyer['’]?s?\s+guide\b",
        r"\bwhat\s+is\b",
        r"\bhow\s+to\b",
    ]

    for pattern in patterns:
        if re.search(pattern, t_clean):
            return True

    return False


def _is_irrelevant_source(
    result: Dict[str, Any],
) -> bool:
    """
    Filter research/reference/article pages that are unlikely
    to represent actual commercial competitors.
    """

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

    # Wikipedia
    if "wikipedia.org" in url:
        return True

    if "wikipedia" in title:
        return True

    # Academic / research / market-report domains.
    if any(
        domain in url
        for domain in IRRELEVANT_SOURCE_DOMAINS
    ):
        return True

    # Academic identifier patterns.
    if re.search(
        r"\bdoi\b|\bmdpi\b|\barxiv\b|\bspringer\b|\bwiley\b|\bfrontiersin\b",
        title,
    ):
        return True

    if re.search(
        r"\bdoi\b|\bmdpi\b|\barxiv\b|\bspringer\b|\bwiley\b|\bfrontiersin\b",
        url,
    ):
        return True

    # Obvious irrelevant source phrases.
    for phrase in IRRELEVANT_SOURCE_PHRASES:
        if phrase in title:
            return True

        if phrase in url:
            return True

    # Research content.
    research_signals = [
        "market size",
        "market research",
        "industry report",
        "industry research",
        "market forecast",
        "market trends",
        "industry analysis",
        "revenue forecast",
        "special issue",
        "special issues",
        "systematic review",
        "meta-analysis",
        "proceedings of",
    ]

    strong_product = _has_strong_digital_identity(
        f"{title} {content}"
    )

    if (
        any(
            signal in content
            for signal in research_signals
        )
        and not strong_product
    ):
        return True

    return False


# ============================================================
# SEARCH RESULT VALIDATION
# ============================================================

def _is_valid_search_result(
    result: Any,
) -> bool:
    """Validate search result."""

    if not isinstance(result, dict):
        return False

    title = _safe_text(
        result.get("title")
    )

    url = _safe_text(
        result.get("url")
    )

    content = _safe_text(
        result.get("content")
    )

    return bool(
        title
        or url
        or content
    )


# ============================================================
# DIRECT COMPETITOR DETECTION
# ============================================================

def _looks_like_direct_competitor(
    idea: str,
    result: Dict[str, Any],
) -> bool:
    """
    Determine whether a result represents a direct competitor.
    """

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
        f"{title} "
        f"{content} "
        f"{target}"
    ).lower()

    # Strong digital product identity.
    if _has_strong_digital_identity(text):
        return True

    # Traditional/legacy services should be indirect.
    indirect_matches = sum(
        1
        for phrase in INDIRECT_SERVICE_PHRASES
        if phrase in text
    )

    if indirect_matches > 0:
        return False

    # Direct service/product phrases.
    direct_matches = sum(
        1
        for phrase in DIRECT_SERVICE_PHRASES
        if phrase in text
    )

    if direct_matches > 0:
        return True

    # --------------------------------------------------------
    # Idea overlap
    # --------------------------------------------------------

    idea_lower = _safe_text(
        idea
    ).lower()

    idea_terms = {
        word
        for word in re.findall(
            r"[a-zA-Z]+",
            idea_lower,
        )
        if len(word) >= 4
    }

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

    digital_matches = sum(
        1
        for keyword in DIGITAL_KEYWORDS
        if keyword in text
    )

    if (
        digital_matches >= 1
        and len(overlap) >= 1
    ):
        return True

    # --------------------------------------------------------
    # Domain/service overlap for non-digital businesses.
    #
    # This is important for ideas like:
    # "home cooked meal delivery".
    # --------------------------------------------------------

    idea_service_terms = {
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

    idea_service_overlap = (
        idea_service_terms.intersection(
            text_terms
        )
    )

    if len(idea_service_overlap) >= 2:
        return True

    return False


# ============================================================
# INDIRECT COMPETITOR DETECTION
# ============================================================

def _looks_like_indirect_competitor(
    idea: str,
    result: Dict[str, Any],
) -> bool:
    """
    Determine whether a result represents an indirect competitor.
    """

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
        f"{title} "
        f"{content} "
        f"{target}"
    ).lower()

    # Digital products should remain direct.
    if _has_strong_digital_identity(text):
        return False

    # Explicit indirect phrases.
    for phrase in INDIRECT_SERVICE_PHRASES:
        if phrase in text:
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
        "fitness clubs",
        "fitness class",
        "fitness classes",
        "personal training",
        "workout class",
        "workout classes",
        "exercise class",
        "exercise classes",
        "studio",
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
    ]

    for term in traditional_terms:
        if term in text:
            return True

    # Generic food alternatives.
    idea_lower = _safe_text(
        idea
    ).lower()

    if any(
        keyword in idea_lower
        for keyword in [
            "meal",
            "food",
            "tiffin",
            "cooked",
            "kitchen",
            "lunch",
            "dinner",
        ]
    ):
        alternative_terms = [
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
            for term in alternative_terms
        ):
            return True

    return False


# ============================================================
# PRODUCT / SERVICE EXTRACTION
# ============================================================

def _extract_product_service(
    content: str,
    title: str = "",
) -> str:
    """Extract product/service description."""

    text = _safe_text(content)

    if not text:
        return _safe_text(title)

    matches = _find_matching_sentences(
        text,
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
        limit=2,
    )

    if matches:
        return " ".join(matches)

    return text[:500].strip()


# ============================================================
# TARGET CUSTOMER EXTRACTION
# ============================================================

def _extract_target_customers(
    result: Dict[str, Any],
    content: str,
) -> str:
    """Extract target customer information."""

    explicit_values = [
        result.get("target_audience"),
        result.get("target_customers"),
        result.get("target_customer"),
    ]

    for value in explicit_values:
        cleaned = _clean_customer_value(value)

        if cleaned:
            return cleaned

    matches = _find_matching_sentences(
        content,
        [
            "target audience",
            "target customers",
            "designed for",
            "built for",
            "for users",
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


# ============================================================
# PRICING EXTRACTION
# ============================================================

def _extract_pricing(
    content: str,
) -> str:
    """
    Extract pricing information.

    If pricing cannot be found, return an explicit
    evidence-aware message instead of inventing a price.
    """

    matches = _find_matching_sentences(
        content,
        PRICING_KEYWORDS,
        limit=3,
    )

    if not matches:
        return "Not available in retrieved sources"

    return " ".join(matches)


# ============================================================
# FEATURE EXTRACTION
# ============================================================

def _extract_features(
    content: str,
) -> List[str]:
    """Extract key features."""

    return _find_matching_sentences(
        content,
        FEATURE_KEYWORDS,
        limit=5,
    )


# ============================================================
# STRENGTH EXTRACTION
# ============================================================

def _extract_strengths(
    content: str,
) -> List[str]:
    """Extract strengths."""

    return _find_matching_sentences(
        content,
        STRENGTH_KEYWORDS,
        limit=5,
    )


# ============================================================
# WEAKNESS EXTRACTION
# ============================================================

def _extract_weaknesses(
    content: str,
) -> List[str]:
    """Extract weaknesses."""

    return _find_matching_sentences(
        content,
        WEAKNESS_KEYWORDS,
        limit=5,
    )


# ============================================================
# CORPORATE ENTITY NAME CLEANING
# ============================================================

def _clean_corporate_entity_name(
    title: str,
    url: str,
    raw_name: Optional[str] = None,
) -> str:
    """
    Extract a clean corporate/product brand name.

    Rejects article titles and research publishers.
    """

    # --------------------------------------------------------
    # 1. URL domain
    # --------------------------------------------------------

    if url:
        try:
            parsed = urllib.parse.urlparse(url)

            netloc = (
                parsed.netloc
                .lower()
                .replace("www.", "")
            )

            parts = netloc.split(".")

            if len(parts) >= 2:
                brand = parts[0]

                blocked_brands = {
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
                    "article",
                    "tech",
                    "post",
                    "report",
                    "www",
                }

                if (
                    brand not in blocked_brands
                    and len(brand) >= 3
                ):
                    return brand.capitalize()

        except Exception:
            pass

    # --------------------------------------------------------
    # 2. Raw name / title
    # --------------------------------------------------------

    candidate = (
        _safe_text(raw_name)
        or _safe_text(title)
    )

    for separator in [
        " | ",
        " - ",
        " – ",
        " — ",
        " : ",
        " • ",
    ]:
        if separator in candidate:
            chunks = candidate.split(separator)

            for chunk in chunks:
                cleaned = chunk.strip()

                words = cleaned.split()

                if (
                    1 <= len(words) <= 4
                    and not any(
                        keyword in cleaned.lower()
                        for keyword in [
                            "how to",
                            "best",
                            "top 10",
                            "top 5",
                            "review",
                            "pricing",
                            "guide",
                            "overview",
                            "report",
                            "market",
                            "analysis",
                            "comparison",
                            "versus",
                        ]
                    )
                ):
                    return cleaned

    candidate = re.sub(
        r"^(top \d+|best \d+|the future of|how to|guide to)\s+",
        "",
        candidate,
        flags=re.IGNORECASE,
    )

    words = candidate.split()

    if words:
        return " ".join(words[:3]).title()

    return "Unknown Competitor"


# ============================================================
# BUILD COMPETITOR FROM SEARCH RESULT
# ============================================================

def _build_competitor(
    result: Dict[str, Any],
) -> Dict[str, Any]:
    """Convert search result into competitor object."""

    title = _safe_text(
        result.get("title")
    )

    url = _safe_text(
        result.get("url")
    )

    content = _safe_text(
        result.get("content")
    )

    name = _clean_corporate_entity_name(
        title=title,
        url=url,
        raw_name=result.get("name"),
    )

    return {
        "name": name,
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
# COMPETITOR NORMALIZATION
# ============================================================

def _normalize_competitor(
    competitor: Any,
) -> Optional[Dict[str, Any]]:
    """
    Normalize Gemini-generated competitor data to the
    expected schema.
    """

    if not isinstance(
        competitor,
        dict,
    ):
        return None

    name = _safe_text(
        competitor.get("name")
    )

    if not name:
        return None

    url = _safe_text(
        competitor.get("url")
        or competitor.get("website")
    )

    target_customers = _clean_customer_value(
        competitor.get("target_customers")
        or competitor.get("target_audience")
    )

    pricing = _safe_text(
        competitor.get("pricing")
    )

    if not pricing:
        pricing = "Not available in retrieved sources"

    key_features = _clean_list(
        competitor.get("key_features"),
        limit=5,
    )

    strengths = _clean_list(
        competitor.get("strengths"),
        limit=5,
    )

    weaknesses = _clean_list(
        competitor.get("weaknesses"),
        limit=5,
    )

    product_service = _safe_text(
        competitor.get("product_service")
        or competitor.get("product")
        or competitor.get("service")
    )

    return {
        "name": name,
        "url": url or None,
        "product_service": product_service,
        "target_customers": target_customers,
        "pricing": pricing,
        "key_features": key_features,
        "strengths": strengths,
        "weaknesses": weaknesses,
    }


# ============================================================
# DUPLICATE DETECTION
# ============================================================

def _is_duplicate(
    competitor: Dict[str, Any],
    competitors: List[Dict[str, Any]],
) -> bool:
    """Detect duplicate competitor by URL or name."""

    current_url = _normalize_url(
        competitor.get("url")
    )

    current_name = _normalize_name(
        competitor.get("name")
    )

    for existing in competitors:
        existing_url = _normalize_url(
            existing.get("url")
        )

        existing_name = _normalize_name(
            existing.get("name")
        )

        # Same URL.
        if (
            current_url
            and existing_url
            and current_url == existing_url
        ):
            return True

        # Same name.
        if (
            current_name
            and existing_name
            and current_name == existing_name
        ):
            return True

    return False


# ============================================================
# DEDUPLICATE COMPETITOR LIST
# ============================================================

def _deduplicate_competitors(
    competitors: Any,
    limit: int,
) -> List[Dict[str, Any]]:
    """
    Normalize and deduplicate competitors.
    """

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
# VALUE JOINING
# ============================================================

def _join_values(
    values: Any,
) -> str:
    """Convert list/string into a clean string."""

    if values is None:
        return ""

    if isinstance(
        values,
        list,
    ):
        return "; ".join(
            _safe_text(value)
            for value in values
            if _safe_text(value)
        )

    return _safe_text(values)


# ============================================================
# COMPARISON GENERATION
# ============================================================

def _build_comparison(
    direct_competitors: List[Dict[str, Any]],
    indirect_competitors: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    Generate structured competitor comparison.

    Includes pricing because pricing is an explicit
    Milestone 2 requirement.
    """

    comparison: List[Dict[str, Any]] = []

    all_competitors = list(
        direct_competitors
    )

    if indirect_competitors:
        all_competitors.extend(
            indirect_competitors
        )

    for competitor in all_competitors:
        comparison.append(
            {
                "competitor": competitor.get(
                    "name",
                    "",
                ),
                "product_service": competitor.get(
                    "product_service",
                    "",
                ),
                "target_customers": competitor.get(
                    "target_customers",
                    "",
                ),
                "pricing": competitor.get(
                    "pricing",
                    "Not available in retrieved sources",
                ),
                "key_features": _join_values(
                    competitor.get(
                        "key_features",
                        [],
                    )
                ),
                "strengths": _join_values(
                    competitor.get(
                        "strengths",
                        [],
                    )
                ),
                "weaknesses": _join_values(
                    competitor.get(
                        "weaknesses",
                        [],
                    )
                ),
            }
        )

    return comparison


# ============================================================
# MARKET GAP GENERATION
# ============================================================

def _build_market_gaps(
    direct_competitors: List[Dict[str, Any]],
    indirect_competitors: List[Dict[str, Any]],
    idea: Optional[str] = "",
) -> List[str]:
    """
    Generate conservative, evidence-aware market gaps.

    Market gaps are framed as potential opportunities,
    not guaranteed facts.
    """

    gaps: List[str] = []

    weakness_sentences: List[str] = []

    # --------------------------------------------------------
    # Collect weaknesses from direct competitors.
    # --------------------------------------------------------

    for competitor in direct_competitors:
        weaknesses = competitor.get(
            "weaknesses",
            [],
        )

        if isinstance(
            weaknesses,
            list,
        ):
            for weakness in weaknesses:
                clean = _safe_text(
                    weakness
                )

                if clean:
                    weakness_sentences.append(
                        clean
                    )

        elif weaknesses:
            clean = _safe_text(
                weaknesses
            )

            if clean:
                weakness_sentences.append(
                    clean
                )

    # --------------------------------------------------------
    # Convert evidence into potential gaps.
    # --------------------------------------------------------

    for weakness in weakness_sentences:
        lower = weakness.lower()

        # Pricing.
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

        # Limited functionality.
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

        # Complexity.
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

        # Complaints / issues.
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

        # Inflexibility.
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

    # --------------------------------------------------------
    # Remove duplicates.
    # --------------------------------------------------------

    unique_gaps: List[str] = []

    for gap in gaps:
        if gap not in unique_gaps:
            unique_gaps.append(gap)

    # --------------------------------------------------------
    # If evidence did not reveal gaps, use domain-aware
    # synthesis.
    # --------------------------------------------------------

    if not unique_gaps:
        unique_gaps = _synthesize_domain_aware_market_gaps(
            idea=idea if isinstance(idea, str) else "",
            direct_competitors=direct_competitors,
            indirect_competitors=indirect_competitors,
        )

    # --------------------------------------------------------
    # Always add validation disclaimer.
    # --------------------------------------------------------

    if not any(
        "primary research" in gap.lower()
        for gap in unique_gaps
    ):
        unique_gaps.append(
            "Further primary customer research and "
            "competitor benchmarking are recommended to "
            "validate these potential white-space opportunities."
        )

    return unique_gaps[:5]


# ============================================================
# DOMAIN-AWARE MARKET GAPS
# ============================================================

def _synthesize_domain_aware_market_gaps(
    idea: str,
    direct_competitors: List[Dict[str, Any]],
    indirect_competitors: List[Dict[str, Any]],
) -> List[str]:
    """
    Generate domain-aware fallback gaps.

    IMPORTANT:
    Avoid unrelated enterprise/technical templates.
    """

    idea_lower = (idea or "").lower()

    # --------------------------------------------------------
    # Food / tiffin / meal delivery.
    # --------------------------------------------------------

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
            "easy WhatsApp-based customization for portion size, "
            "dietary preferences, and next-day meal changes.",
            "Potential local-trust gap: a hyper-local home-kitchen "
            "model could differentiate through transparent menus, "
            "consistent quality, and direct customer relationships.",
        ]

    # --------------------------------------------------------
    # Agriculture.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Cybersecurity.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Fitness.
    # --------------------------------------------------------

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
            "training could serve users who cannot afford one-to-one coaching.",
            "Potential engagement gap: stronger progress feedback "
            "could improve long-term adherence.",
        ]

    # --------------------------------------------------------
    # Generic but domain-neutral fallback.
    # --------------------------------------------------------

    return [
        "Potential affordability gap: there may be an underserved "
        "customer segment seeking a lower-cost alternative.",
        "Potential personalization gap: there may be an opportunity "
        "to better adapt the solution to individual customer needs.",
        "Potential usability gap: there may be an opportunity to "
        "simplify the existing customer experience.",
    ]


# ============================================================
# GEMINI COMPETITOR ANALYSIS
# ============================================================

async def _run_gemini_competitor_analysis(
    idea: str,
    search_results: List[Dict[str, Any]],
    api_key: str,
    max_competitors: int = DEFAULT_COMPETITOR_LIMIT,
) -> Optional[Dict[str, Any]]:

    import random

    formatted_evidence = []

    for idx, item in enumerate(
        search_results[:MAX_SEARCH_RESULTS_FOR_GEMINI],
        1,
    ):
        formatted_evidence.append(
            {
                "source_id": idx,
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
                "snippet": _safe_text(
                    item.get("content")
                )[:500],
            }
        )

    evidence_json = (
        json.dumps(
            formatted_evidence,
            indent=2,
            ensure_ascii=False,
        )
        if formatted_evidence
        else "No search evidence available."
    )

    prompt = f"""
You are a Lead Competitive Intelligence Analyst.

Analyze the startup idea using ONLY the supplied web research evidence.

STARTUP IDEA:
"{idea}"

RETRIEVED WEB RESEARCH EVIDENCE:
{evidence_json}

IMPORTANT COMPETITOR RULES:

1. Identify REAL commercial companies, products, services,
   platforms, or traditional alternatives.

2. Do not use:
   - academic papers
   - universities
   - research papers
   - market research companies
   - blog publishers
   - news publishers
   - generic articles
   - comparison articles
   - "best X" lists
   - "top X" lists

3. The competitor name must be a clean company/product name.

4. Identify competitors based on the PRIMARY BUSINESS FUNCTION:
   what problem they solve and for whom.

5. Do not classify a company merely because it uses AI,
   subscriptions, payments, or another technology.

6. DIRECT competitors provide substantially similar products/services
   solving the same core customer problem.

7. INDIRECT competitors solve the same customer problem through
   another method, traditional service, or alternative solution.

8. Identify up to {max_competitors} direct competitors.

9. Identify no more than 2 indirect competitors.

10. Do NOT invent pricing.
    If pricing is not available in the supplied evidence,
    return:
    "Not available in retrieved sources"

11. Do NOT invent weaknesses.
    If no weakness is supported by the evidence, return
    an empty list.

12. Do NOT invent target customers.
    If the evidence does not support a specific target audience,
    return an empty string.

13. Market gaps must be phrased as POTENTIAL opportunities,
    not guaranteed facts.

14. Avoid generic white-space statements.
    Make the gaps specific to the startup idea.

OUTPUT ONLY VALID JSON.

Required schema:

{{
  "competitor_analysis": {{
    "direct_competitors": [
      {{
        "name": "Clean Company/Product Name",
        "url": "https://example.com",
        "product_service": "Brief description",
        "target_customers": "Specific target customers",
        "key_features": [
          "Feature 1",
          "Feature 2"
        ],
        "pricing": "Pricing detail or Not available in retrieved sources",
        "strengths": [
          "Evidence-supported strength"
        ],
        "weaknesses": [
          "Evidence-supported weakness"
        ]
      }}
    ],

    "indirect_competitors": [
      {{
        "name": "Alternative",
        "url": null,
        "product_service": "Alternative approach",
        "target_customers": "Specific audience",
        "key_features": [
          "Feature"
        ],
        "pricing": "Pricing detail or Not available in retrieved sources",
        "strengths": [
          "Strength"
        ],
        "weaknesses": [
          "Weakness"
        ]
      }}
    ],

    "comparison": [
      {{
        "competitor": "Company Name",
        "product_service": "Product/service",
        "target_customers": "Target audience",
        "pricing": "Pricing",
        "key_features": "Feature summary",
        "strengths": "Strength summary",
        "weaknesses": "Weakness summary"
      }}
    ],

    "market_gaps": [
      "Potential market gap 1",
      "Potential market gap 2",
      "Potential market gap 3"
    ]
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
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }

        for attempt in range(3):

            try:
                timeout_config = httpx.Timeout(
                    30.0,
                    connect=5.0,
                )

                async with httpx.AsyncClient(
                    timeout=timeout_config
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

                    # Remove accidental Markdown fences.
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
                            "Gemini returned invalid JSON "
                            "for model %s: %s",
                            model,
                            exc,
                        )
                        break

                    if not isinstance(
                        parsed,
                        dict,
                    ):
                        break

                    comp_dict = parsed.get(
                        "competitor_analysis",
                        parsed,
                    )

                    if not isinstance(
                        comp_dict,
                        dict,
                    ):
                        break

                    return {
                        "competitor_analysis": comp_dict
                    }

                elif response.status_code in (
                    400,
                    401,
                    403,
                ):
                    logger.warning(
                        "Gemini API returned HTTP %s. "
                        "Aborting Gemini retries.",
                        response.status_code,
                    )
                    return None

                elif response.status_code in (
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

                    logger.warning(
                        "Gemini model %s returned HTTP %s. "
                        "Retrying in %.2fs.",
                        model,
                        response.status_code,
                        delay,
                    )

                    await asyncio.sleep(
                        delay
                    )

                    continue

                elif response.status_code == 404:
                    logger.warning(
                        "Gemini model %s returned 404. "
                        "Trying next model.",
                        model,
                    )
                    break

                else:
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
                    "Gemini model %s connection failed: %s",
                    model,
                    exc,
                )

                break

            except httpx.TimeoutException as exc:

                if attempt < 2:
                    logger.warning(
                        "Gemini model %s timeout. "
                        "Retrying.",
                        model,
                    )

                    await asyncio.sleep(
                        1.0
                    )

                    continue

                logger.warning(
                    "Gemini model %s timed out after 3 attempts.",
                    model,
                )

                break

            except Exception as exc:

                logger.warning(
                    "Gemini call to %s failed: %s",
                    model,
                    exc,
                )

                break

    return None


# ============================================================
# MAIN AGENT
# ============================================================

async def run_competitor_analysis_agent(
    idea: str,
    search_results: Any,
    max_competitors: int = DEFAULT_COMPETITOR_LIMIT,
) -> Dict[str, Any]:
    """
    Run competitor analysis.
    """

    idea = _safe_text(
        idea
    )

    # --------------------------------------------------------
    # Clamp competitor limit.
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

    valid_results: List[Dict[str, Any]] = []

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
    # No evidence.
    # --------------------------------------------------------

    if not valid_results:
        return {
            "competitor_analysis": {
                "direct_competitors": [],
                "indirect_competitors": [],
                "comparison": [],
                "market_gaps": [
                    "Potential competitor white-space could not "
                    "be established from the retrieved evidence. "
                    "Further primary and web research is recommended."
                ],
            }
        }

    # ========================================================
    # GEMINI ANALYSIS
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
                gemini_result,
            )

            if isinstance(
                comp_data,
                dict,
            ):

                # ------------------------------------------------
                # Normalize direct competitors.
                # ------------------------------------------------

                directs = _deduplicate_competitors(
                    comp_data.get(
                        "direct_competitors",
                        [],
                    ),
                    limit=max_competitors,
                )

                # ------------------------------------------------
                # Normalize indirect competitors.
                # Requirement: maximum 2.
                # ------------------------------------------------

                indirects = _deduplicate_competitors(
                    comp_data.get(
                        "indirect_competitors",
                        [],
                    ),
                    limit=MAX_INDIRECT_COMPETITORS,
                )

                # ------------------------------------------------
                # Improve missing generic target customers using
                # source-specific matching.
                # ------------------------------------------------

                if valid_results and directs:

                    for competitor in directs:

                        current_audience = (
                            _clean_customer_value(
                                competitor.get(
                                    "target_customers"
                                )
                            )
                        )

                        if current_audience:
                            continue

                        competitor_name = (
                            _normalize_name(
                                competitor.get(
                                    "name"
                                )
                            )
                        )

                        competitor_url = (
                            _normalize_url(
                                competitor.get(
                                    "url"
                                )
                            )
                        )

                        matched_audience = ""

                        for result in valid_results:

                            result_url = (
                                _normalize_url(
                                    result.get(
                                        "url"
                                    )
                                )
                            )

                            result_title = (
                                _safe_text(
                                    result.get(
                                        "title"
                                    )
                                ).lower()
                            )

                            result_audience = (
                                _clean_customer_value(
                                    result.get(
                                        "target_audience"
                                    )
                                    or result.get(
                                        "target_customers"
                                    )
                                    or result.get(
                                        "target_customer"
                                    )
                                )
                            )

                            if not result_audience:
                                continue

                            # URL match.
                            if (
                                competitor_url
                                and result_url
                                and (
                                    competitor_url
                                    in result_url
                                    or result_url
                                    in competitor_url
                                )
                            ):
                                matched_audience = (
                                    result_audience
                                )
                                break

                            # Name in title.
                            if (
                                competitor_name
                                and len(competitor_name) > 3
                                and competitor_name
                                in result_title
                            ):
                                matched_audience = (
                                    result_audience
                                )
                                break

                        if matched_audience:
                            competitor[
                                "target_customers"
                            ] = matched_audience

                # ------------------------------------------------
                # Build comparison ourselves.
                #
                # This guarantees that pricing and all fields
                # are present even if Gemini forgets them.
                # ------------------------------------------------

                comparison = _build_comparison(
                    direct_competitors=directs,
                    indirect_competitors=indirects,
                )

                # ------------------------------------------------
                # Clean Gemini market gaps.
                # ------------------------------------------------

                raw_gaps = comp_data.get(
                    "market_gaps",
                    [],
                )

                market_gaps = _clean_list(
                    raw_gaps,
                    limit=5,
                )

                # Ensure gaps are framed conservatively.
                normalized_gaps: List[str] = []

                for gap in market_gaps:

                    lower = gap.lower()

                    if (
                        "potential" not in lower
                        and "may " not in lower
                        and "could " not in lower
                        and "opportunity" not in lower
                    ):
                        gap = (
                            "Potential opportunity: "
                            + gap
                        )

                    normalized_gaps.append(
                        gap
                    )

                if not normalized_gaps:

                    normalized_gaps = (
                        _build_market_gaps(
                            direct_competitors=directs,
                            indirect_competitors=indirects,
                            idea=idea,
                        )
                    )

                elif not any(
                    "primary research"
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
    # FALLBACK RULE-BASED ANALYSIS
    # ========================================================

    direct_competitors: List[
        Dict[str, Any]
    ] = []

    indirect_competitors: List[
        Dict[str, Any]
    ] = []

    # --------------------------------------------------------
    # Process search results.
    # --------------------------------------------------------

    for result in valid_results:

        # ----------------------------------------------------
        # DIRECT
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
        # INDIRECT
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
    # Apply limits.
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
    """
    Compatibility wrapper for other modules.
    """

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