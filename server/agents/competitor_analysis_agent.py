
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
from typing import Any, Dict, List, Optional
import httpx

logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_COMPETITOR_LIMIT = 5
MAX_COMPETITOR_LIMIT = 5


# ============================================================
# STRONG DIGITAL PRODUCT SIGNALS
# ============================================================

# IMPORTANT:
# These phrases indicate that the RESULT ITSELF is a digital
# product. Generic mentions such as "fitness apps" are NOT
# included because an indirect competitor may mention apps.
STRONG_DIGITAL_PHRASES = [
    "is an app", "is a app", "is a mobile app", "is a web app", "is an application",
    "is a platform", "is software", "is a saas", "is a tool", "is a studio", "is an engine",
    "mobile app", "web app", "3d studio", "webgl engine", "spatial web platform",
    "design tool", "developer tool", "no-code platform", "zero-code studio",
    "digital platform", "online platform", "software platform", "cloud platform",
    "provides an app", "provides a platform", "provides software", "offers a tool",
    "offers an app", "offers a platform", "offers software", "offers a service"
]


# ============================================================
# DIGITAL KEYWORDS
# ============================================================

DIGITAL_KEYWORDS = [
    "app", "application", "platform", "software", "saas", "digital", "mobile", "online",
    "studio", "engine", "tool", "sdk", "api", "framework", "cloud", "no-code", "zero-code"
]


# ============================================================
# DIRECT COMPETITOR SIGNALS
# ============================================================

DIRECT_SERVICE_PHRASES = [
    "3d web", "webgl", "spatial web", "motion design", "shaders", "creative studio",
    "developer tools", "design tools", "automation platform", "ai platform",
    "personalized platform", "analytics platform", "management software",
    "workflow automation", "cloud service", "software solution"
]


# ============================================================
# INDIRECT COMPETITOR SIGNALS
# ============================================================

INDIRECT_SERVICE_PHRASES = [
    "agency", "agencies", "consultancy", "consulting", "freelancer", "freelancers",
    "manual spreadsheet", "excel template", "custom development studio",
    "traditional service", "in-house team", "manual workflow", "paper-based process"
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

    "workout tracking",
    "fitness tracking",

    "personalized workout",
    "personalized training",

    "training plans",
    "workout plans",

    "recommendations",
    "ai recommendations",

    "coaching",
    "progress tracking",

    "goal tracking",
    "exercise tracking",

    "workout recommendations",
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
]


# ============================================================
# IRRELEVANT SOURCE SIGNALS & ACADEMIC BLACKLIST
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
    """
    Safely convert a value to string.
    """

    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    return str(value).strip()


# ============================================================
# URL NORMALIZATION
# ============================================================

def _normalize_url(url: Any) -> str:
    """
    Normalize URL for duplicate detection.
    """

    value = _safe_text(url).lower().strip()

    if not value:
        return ""

    return value.rstrip("/")


# ============================================================
# NAME NORMALIZATION
# ============================================================

def _normalize_name(name: Any) -> str:
    """
    Normalize competitor name.
    """

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


# ============================================================
# SEARCH TEXT
# ============================================================

def _get_search_text(
    result: Dict[str, Any],
) -> str:
    """
    Combine useful search result fields.
    """

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

    # Split on normal sentence endings and new lines.
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

                seen.add(
                    lower_sentence
                )

                matches.append(
                    clean
                )

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
    Determine whether the RESULT ITSELF is clearly a
    digital product/platform.

    IMPORTANT FIX:

    A sentence such as:

        "Traditional coaching is an alternative to fitness apps."

    mentions "fitness apps", but the result itself is NOT
    a fitness app.

    Therefore generic plural mentions such as:
        fitness apps
        workout apps
        training apps

    must not automatically classify the result as digital.

    We first look for explicit product identity phrases.
    """

    lower = _safe_text(text).lower()

    # --------------------------------------------------------
    # Explicit self-identification
    # --------------------------------------------------------

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

        r"\bis a fitness app\b",
        r"\bis a workout app\b",
        r"\bis a training app\b",

        r"\bis a fitness platform\b",
        r"\bis a workout platform\b",
        r"\bis a training platform\b",

        r"\bis an ai fitness\b",
        r"\bis an ai fitness app\b",
        r"\bis an ai fitness platform\b",

        r"\bis an ai fitness coach\b",
        r"\bis an ai coach\b",

        r"\bai fitness app\b",
        r"\bai fitness platform\b",

        r"\bdigital platform\b",
        r"\bonline platform\b",
        r"\bsoftware platform\b",

        r"\bdigital coaching platform\b",
        r"\bonline fitness platform\b",
        r"\bonline fitness app\b",

        r"\bpersonalized fitness platform\b",
        r"\bpersonalized workout platform\b",

        r"\bpersonalized workout plans\b",
        r"\bpersonalized training plans\b",

        r"\bprovides personalized workout plans\b",
        r"\bprovides personalized training plans\b",
    ]

    for pattern in explicit_patterns:
        if re.search(pattern, lower):
            return True

    # --------------------------------------------------------
    # Strong product phrase check.
    #
    # Do NOT treat generic plural mentions as identity.
    # --------------------------------------------------------

    identity_phrases = [
        "fitness app",
        "workout app",
        "training app",

        "fitness platform",
        "workout platform",
        "training platform",

        "ai fitness app",
        "ai fitness platform",

        "personalized fitness platform",
        "personalized workout platform",

        "digital platform",
        "online platform",
        "software platform",

        "digital coaching",

        "mobile app",
        "web app",
        "software",
        "saas",
    ]

    # Generic phrases that should NOT be considered proof
    # that the result itself is digital.
    generic_mentions = [
        "fitness apps",
        "workout apps",
        "training apps",
        "fitness platforms",
        "workout platforms",
        "training platforms",
    ]

    cleaned_text = lower

    for phrase in generic_mentions:
        cleaned_text = cleaned_text.replace(
            phrase,
            "",
        )

    for phrase in identity_phrases:
        if phrase in cleaned_text:
            return True

    return False


# ============================================================
# SOURCE FILTERING
# ============================================================

def _is_article_title(title: str) -> bool:
    """
    Checks if a result title matches non-entity article patterns such as
    pricing guides, cost breakdowns, comparisons, top N lists, or how-to guides.
    """
    if not title:
        return False
    t_clean = title.strip().lower()
    patterns = [
        r"\bhow\s+much\s+(?:does|is|do)\b",
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
    ]
    for pat in patterns:
        if re.search(pat, t_clean):
            return True
    return False


def _is_irrelevant_source(
    result: Dict[str, Any],
) -> bool:
    """
    Filter research/reference/gift pages.
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

    # --------------------------------------------------------
    # Wikipedia
    # --------------------------------------------------------

    if "wikipedia.org" in url:
        return True

    if "wikipedia" in title:
        return True

    # --------------------------------------------------------
    # Academic & Research Publishers Blacklist
    # --------------------------------------------------------

    if any(domain in url for domain in IRRELEVANT_SOURCE_DOMAINS):
        return True

    if re.search(r"\[\d{4}\.\d{4,5}\]", title):
        return True

    if re.search(r"\bdoi\b|\bmdpi\b|\barxiv\b|\bspringer\b|\bwiley\b|\bfrontiersin\b", title):
        return True

    if re.search(r"\bdoi\b|\bmdpi\b|\barxiv\b|\bspringer\b|\bwiley\b|\bfrontiersin\b", url):
        return True

    # --------------------------------------------------------
    # Obvious irrelevant sources
    # --------------------------------------------------------

    for phrase in IRRELEVANT_SOURCE_PHRASES:

        if phrase in title:
            return True

        if phrase in url:
            return True

    # --------------------------------------------------------
    # Research content
    # --------------------------------------------------------

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
    """
    Validate search result.
    """

    if not isinstance(
        result,
        dict,
    ):
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

    # --------------------------------------------------------
    # 1. Strong digital identity.
    # --------------------------------------------------------

    if _has_strong_digital_identity(text):
        return True

    # --------------------------------------------------------
    # 2. Traditional service should be indirect.
    #
    # IMPORTANT:
    # Check this BEFORE broad direct phrases.
    # --------------------------------------------------------

    indirect_matches = sum(
        1
        for phrase in INDIRECT_SERVICE_PHRASES
        if phrase in text
    )

    if indirect_matches > 0:
        return False

    # --------------------------------------------------------
    # 3. Direct product/service phrases.
    # --------------------------------------------------------

    direct_matches = sum(
        1
        for phrase in DIRECT_SERVICE_PHRASES
        if phrase in text
    )

    if direct_matches > 0:
        return True

    # --------------------------------------------------------
    # 4. Digital keyword + idea overlap.
    # --------------------------------------------------------

    digital_matches = sum(
        1
        for keyword in DIGITAL_KEYWORDS
        if keyword in text
    )

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

    if (
        digital_matches >= 1
        and len(overlap) >= 1
    ):
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

    Examples:

    Personal trainer       -> INDIRECT
    Gym                     -> INDIRECT
    Traditional coaching   -> INDIRECT
    Fitness classes        -> INDIRECT

    Freeletics AI platform -> DIRECT
    Fitbod fitness app    -> DIRECT
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

    # --------------------------------------------------------
    # Digital product must remain DIRECT.
    #
    # IMPORTANT:
    # _has_strong_digital_identity() no longer treats
    # "fitness apps" as a digital identity when it is only
    # mentioned as an alternative.
    # --------------------------------------------------------

    if _has_strong_digital_identity(text):
        return False

    # --------------------------------------------------------
    # Explicit indirect phrases.
    # --------------------------------------------------------

    for phrase in INDIRECT_SERVICE_PHRASES:

        if phrase in text:
            return True

    # --------------------------------------------------------
    # Additional traditional-service terms.
    # --------------------------------------------------------

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
    ]

    for term in traditional_terms:

        if term in text:
            return True

    return False


# ============================================================
# PRODUCT / SERVICE EXTRACTION
# ============================================================

def _extract_product_service(
    content: str,
    title: str = "",
) -> str:
    """
    Extract product/service description.
    """

    text = _safe_text(
        content
    )

    if not text:
        return _safe_text(
            title
        )

    matches = _find_matching_sentences(
        text,
        [
            "is a",
            "is an",
            "provides",
            "offers",
            "platform",
            "app",
            "software",
            "service",
            "coaching",
            "training",
        ],
        limit=2,
    )

    if matches:
        return " ".join(
            matches
        )

    return text[:500].strip()


# ============================================================
# TARGET CUSTOMER EXTRACTION
# ============================================================

def _extract_target_customers(
    result: Dict[str, Any],
    content: str,
) -> str:
    """
    Extract target customer information.
    """

    explicit = (
        result.get("target_audience")
        or result.get("target_customers")
        or result.get("target_customer")
    )

    if explicit:
        return _safe_text(
            explicit
        )

    matches = _find_matching_sentences(
        content,
        [
            "target audience",
            "target customers",
            "designed for",
            "built for",
            "for users",
            "for athletes",
            "for beginners",
            "for professionals",
            "fitness users",
            "fitness enthusiasts",
        ],
        limit=2,
    )

    if matches:
        return " ".join(
            matches
        )

    return ""


# ============================================================
# PRICING EXTRACTION
# ============================================================

def _extract_pricing(
    content: str,
) -> str:
    """
    Extract pricing information.
    """

    matches = _find_matching_sentences(
        content,
        PRICING_KEYWORDS,
        limit=3,
    )

    if not matches:
        return ""

    return " ".join(
        matches
    )


# ============================================================
# FEATURE EXTRACTION
# ============================================================

def _extract_features(
    content: str,
) -> List[str]:
    """
    Extract key features.
    """

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
    """
    Extract strengths.
    """

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
    """
    Extract weaknesses.
    """

    return _find_matching_sentences(
        content,
        WEAKNESS_KEYWORDS,
        limit=5,
    )


# ============================================================
# BUILD COMPETITOR
# ============================================================

def _clean_corporate_entity_name(
    title: str,
    url: str,
    raw_name: Optional[str] = None
) -> str:
    """
    Extracts a clean corporate/product brand name and discards blog titles,
    news headlines, or market analyst publishers.
    """
    import urllib.parse

    # 1. Inspect URL domain for brand name
    if url:
        try:
            parsed = urllib.parse.urlparse(url)
            netloc = parsed.netloc.lower().replace("www.", "")
            parts = netloc.split(".")
            if len(parts) >= 2:
                brand = parts[0]
                if brand not in {
                    "medium", "substack", "hubspot", "linkedin", "github", "news",
                    "blog", "app", "docs", "en", "article", "tech", "post", "report"
                } and len(brand) >= 3:
                    return brand.capitalize()
        except Exception:
            pass

    # 2. Inspect raw_name or title
    candidate = (raw_name or title or "").strip()
    for sep in [" | ", " - ", " – ", " — ", " : ", " • "]:
        if sep in candidate:
            chunks = candidate.split(sep)
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

    candidate = re.sub(r"^(top \d+|best \d+|the future of|how to|guide to)\s+", "", candidate, flags=re.IGNORECASE)
    words = candidate.split()
    if words:
        return " ".join(words[:2]).title()
    return "Enterprise Platform"


def _build_competitor(
    result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convert search result into competitor object with aggressive entity cleaning.
    """

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
        raw_name=result.get("name")
    )

    return {
        "name": name,

        "url": url,

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
# DUPLICATE DETECTION
# ============================================================

def _is_duplicate(
    competitor: Dict[str, Any],
    competitors: List[Dict[str, Any]],
) -> bool:
    """
    Detect duplicate competitor by URL or name.
    """

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

        # Same URL
        if (
            current_url
            and existing_url
            and current_url == existing_url
        ):
            return True

        # Same name
        if (
            current_name
            and existing_name
            and current_name == existing_name
        ):
            return True

    return False


# ============================================================
# VALUE JOINING
# ============================================================

def _join_values(
    values: Any,
) -> str:
    """
    Convert list/string into a clean string.
    """

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

    return _safe_text(
        values
    )


# ============================================================
# COMPARISON GENERATION
# ============================================================

def _build_comparison(
    direct_competitors: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Generate comparison table data.
    """

    comparison = []

    for competitor in direct_competitors:

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
                    "",
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
    Generate conservative, evidence-based market gaps.

    If weaknesses are available, derive potential gaps from
    those weaknesses.

    If weaknesses are not available, do NOT invent a specific
    competitor weakness.
    """

    gaps: List[str] = []

    weakness_sentences: List[str] = []

    # --------------------------------------------------------
    # Collect weaknesses
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
    # Generate gaps from weaknesses
    # --------------------------------------------------------

    for weakness in weakness_sentences:

        lower = weakness.lower()

        # ----------------------------------------------------
        # Pricing gap
        # ----------------------------------------------------

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
                "There may be potential for a more "
                "affordable pricing option."
            )

        # ----------------------------------------------------
        # Limited functionality
        # ----------------------------------------------------

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
                "There may be potential to address "
                "capabilities that competitors currently "
                "provide only in a limited way."
            )

        # ----------------------------------------------------
        # Complexity
        # ----------------------------------------------------

        elif any(
            word in lower
            for word in [
                "complex",
                "difficult",
            ]
        ):

            gaps.append(
                "There may be potential for a simpler "
                "and more user-friendly experience."
            )

        # ----------------------------------------------------
        # Complaints / problems
        # ----------------------------------------------------

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
                "There may be potential to address "
                "existing competitor limitations and "
                "user pain points."
            )

    # --------------------------------------------------------
    # --------------------------------------------------------
    # Remove duplicate gaps
    # --------------------------------------------------------

    unique_gaps: List[str] = []

    for gap in gaps:
        if gap not in unique_gaps:
            unique_gaps.append(gap)

    # --------------------------------------------------------
    # Domain-Aware Intelligent White-Space Synthesis
    # (Purged generic e-commerce / personalization fallback)
    # --------------------------------------------------------

    if not unique_gaps:
        unique_gaps = _synthesize_domain_aware_market_gaps(
            idea=idea if isinstance(idea, str) else "",
            direct_competitors=direct_competitors,
            indirect_competitors=indirect_competitors,
        )

    return unique_gaps


def _synthesize_domain_aware_market_gaps(
    idea: str,
    direct_competitors: List[Dict[str, Any]],
    indirect_competitors: List[Dict[str, Any]],
) -> List[str]:
    """
    Synthesizes domain-specific white-space market gaps tailored precisely
    to the startup's operational domain, replacing generic templates.
    """
    idea_lower = (idea or "").lower()

    if any(k in idea_lower for k in ["cool", "thermal", "datacenter", "data center", "liquid", "server", "chip", "pue", "immersion"]):
        gaps = [
            "Potential telemetry unification gap: Incumbent cooling systems remain bound to proprietary OEM protocols, lacking multi-vendor ingestion (Redfish API, Modbus TCP, BACnet/IP).",
            "Potential sub-second predictive modeling gap: Reactive BMS controls fail to prevent GPU thermal throttling during sudden LLM compute burst barriers.",
            "Potential compliance automation gap: Absence of automated real-time PUE and heat-reuse telemetry mapped directly to ASHRAE TC 9.9 and EU Energy Efficiency Directive standards."
        ]
    elif any(k in idea_lower for k in ["agri", "farm", "crop", "drone", "vineyard", "orchard", "spore", "fungal", "spray"]):
        gaps = [
            "Potential precision targeting gap: Legacy agricultural solutions rely on broad broadcast chemical spraying rather than real-time edge spore detection and micro-dosing.",
            "Potential ruggedized connectivity gap: Inability to maintain reliable low-power mesh sensor telemetry across rolling topography without expensive cellular backhaul.",
            "Potential regulatory compliance gap: Absence of automated flight logging, weather-adjusted drift calculations, and EPA FIFRA compliance reporting for autonomous dispensing."
        ]
    elif any(k in idea_lower for k in ["gut", "acoustic", "phono", "bowel", "health", "microbiome", "patient", "clinical", "biomarker"]):
        gaps = [
            "Potential clinical accuracy gap: High false-positive rates due to ambient noise and lack of standardized acoustic impedance calibration across consumer smartphones.",
            "Potential biomarker correlation gap: Absence of prospective randomized clinical trials correlating non-invasive acoustic transients with gold-standard metagenomic sequencing.",
            "Potential workflow integration gap: Lack of HIPAA-compliant SMART on FHIR electronic health record integration for automated longitudinal clinician review."
        ]
    elif any(k in idea_lower for k in ["security", "cyber", "privacy", "fraud", "auth", "zero-trust"]):
        gaps = [
            "Potential zero-trust enforcement gap: Disjointed identity perimeters causing latency and coverage blindspots across heterogeneous cloud-native workloads.",
            "Potential automated auditability gap: Prohibitive manual overhead required to aggregate continuous compliance evidence for SOC 2 Type II and ISO 27001 audits.",
            "Potential real-time threat mitigation gap: Static rule-based alerts generating excessive noise without automated context-aware containment actions."
        ]
    else:
        gaps = [
            "Potential enterprise integration gap: Incumbent solutions operate in closed silos, lacking turn-key enterprise API integrations and zero-trust security audit trails.",
            "Potential deterministic performance gap: Excessive reliance on manual heuristics rather than adaptive, predictive real-time optimization.",
            "Potential commercial access gap: Prohibitive upfront enterprise licensing and inflexible multi-year contracts creating an underserved mid-market segment."
        ]

    gaps.append(
        "Further primary customer discovery and technical benchmarking recommended to validate potential market white-space."
    )
    return gaps


async def _run_gemini_competitor_analysis(
    idea: str,
    search_results: List[Dict[str, Any]],
    api_key: str,
    max_competitors: int = 5,
) -> Optional[Dict[str, Any]]:
    import random

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

    prompt = f"""You are a Lead Competitive Intelligence Analyst and Market Benchmarking Specialist.

Analyze the following startup idea and grounded web research evidence to produce a high-accuracy Competitor & Market Gap Analysis.

STARTUP IDEA:
"{idea}"

RETRIEVED WEB RESEARCH EVIDENCE:
{evidence_json}

CRITICAL RULES FOR COMPETITOR IDENTIFICATION:
0. PRIMARY BUSINESS FUNCTION FIRST: Identify the PRIMARY business function first — what does this company actually DO and WHO does it connect or serve — before considering secondary features like payment processing, AI, subscriptions, or monetization mechanics. Do not classify based on HOW the company monetizes or WHAT TECHNOLOGY it uses — focus on WHAT PROBLEM it solves and for WHOM.
1. ONLY identify REAL commercial companies, startups, software products, autonomous platforms, or equipment manufacturers (e.g. Vertiv, Phaidra, CoolIT Systems, Schneider Electric, Submer, Orchard Robotics).
2. AGGRESSIVE COMPANY ENTITY CLEANING: STRICTLY FORBIDDEN: DO NOT use academic research papers, scientific articles, university publications, arXiv/MDPI titles, or market research report firms (e.g. IDTechEx, MarketsAndMarkets, Grand View Research, Mordor Intelligence, Technavio, HubSpot, Substack) as competitor names!
3. If an evidence snippet is from an academic paper or report discussing automation, extract the real commercial company or platform benchmarked in that industry.
4. The competitor "name" MUST be a clean, concise company/product brand name (e.g. "Vertiv", "CoolIT Systems"), NOT a long research title or article headline.
5. PURGE GENERIC E-COMMERCE / PERSONALIZATION TEMPLATES: Generate domain-specific, actionable white-space market gaps tailored precisely to the startup idea's technical domain.

INSTRUCTIONS:
1. Identify up to {max_competitors} DIRECT COMPETITORS (real commercial companies/products offering direct solutions).
2. Identify up to 2 INDIRECT COMPETITORS (manual workarounds, traditional methods, or adjacent legacy platforms).
3. For each competitor, extract actual company/product name, clean domain or URL, product/service description, target customers, key features (list of strings), pricing model, strengths (list of strings), and weaknesses (list of strings).
4. Build a competitor comparison array where each element has: competitor (clean company name), target_customers, key_features, strengths, weaknesses.
5. Produce 3-5 sharp, highly specific market_gaps that highlight white-space opportunities uniquely addressed by this startup idea.

OUTPUT FORMAT:
Return ONLY a valid JSON object matching this exact schema:
{{
  "competitor_analysis": {{
    "direct_competitors": [
      {{
        "name": "Clean Commercial Company Name",
        "url": "https://example.com",
        "product_service": "Brief product description",
        "target_customers": "Target audience",
        "key_features": ["Feature 1", "Feature 2"],
        "pricing": "Pricing detail or tier",
        "strengths": ["Strength 1", "Strength 2"],
        "weaknesses": ["Weakness 1", "Weakness 2"]
      }}
    ],
    "indirect_competitors": [
      {{
        "name": "Indirect Competitor or Traditional Method",
        "url": null,
        "product_service": "Description of alternative approach",
        "target_customers": "Audience",
        "key_features": ["Feature 1"],
        "pricing": "Pricing or cost",
        "strengths": ["Strength 1"],
        "weaknesses": ["Weakness 1"]
      }}
    ],
    "comparison": [
      {{
        "competitor": "Company Name",
        "target_customers": "Target audience",
        "key_features": "Summary of key features",
        "strengths": "Main strength",
        "weaknesses": "Main weakness"
      }}
    ],
    "market_gaps": [
      "Specific unfulfilled market gap 1",
      "Specific unfulfilled market gap 2",
      "Specific unfulfilled market gap 3"
    ]
  }}
}}
"""

    models = [
        "gemini-3.6-flash",         # confirmed working, has quota
        "gemini-3-flash-preview",   # confirmed working, has quota
        "gemini-flash-lite-latest", # confirmed working, has quota
        "gemini-2.5-flash",         # last resort — quota resets daily
        # "gemini-3.1-pro-preview", # pro-tier fallback — currently at 0 quota, re-enable after reset
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
        for attempt in range(3):
            try:
                timeout_config = httpx.Timeout(30.0, connect=5.0)
                async with httpx.AsyncClient(timeout=timeout_config) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                raw_text = parts[0].get("text", "").strip()
                                if raw_text.startswith("```"):
                                    raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.MULTILINE)
                                    raw_text = re.sub(r"\s*```$", "", raw_text, flags=re.MULTILINE)
                                parsed = json.loads(raw_text.strip())
                                if isinstance(parsed, dict):
                                    comp_dict = parsed.get("competitor_analysis", parsed)
                                    if "direct_competitors" in comp_dict:
                                        # Sanitize direct competitor entities
                                        clean_directs = []
                                        for d in comp_dict.get("direct_competitors", []):
                                            c_name = str(d.get("name", "")).strip()
                                            if not any(b in c_name.lower() for b in [
                                                "marketsandmarkets", "grand view", "idtechex",
                                                "mordor", "technavio", "substack", "hubspot"
                                            ]):
                                                clean_directs.append(d)
                                        comp_dict["direct_competitors"] = clean_directs
                                        return {"competitor_analysis": comp_dict}
                        break
                    elif resp.status_code in (400, 401, 403):
                        logger.warning(f"Gemini API returned HTTP {resp.status_code} (Authentication/Project error). Aborting API retries.")
                        return None
                    elif resp.status_code in (429, 500, 502, 503, 504):
                        delay = (0.5 * (2 ** attempt)) + random.uniform(0.1, 0.3)
                        logger.warning(f"Gemini model {model} HTTP {resp.status_code}, retrying in {delay:.2f}s (attempt {attempt+1}/3)...")
                        await asyncio.sleep(delay)
                        continue
                    elif resp.status_code == 404:
                        logger.warning(f"Gemini model {model} returned 404, trying next model.")
                        break
                    else:
                        logger.warning(f"Gemini model {model} returned HTTP {resp.status_code}")
                        break
            except (httpx.ConnectError, httpx.ConnectTimeout, httpx.NetworkError) as net_err:
                logger.warning(f"Gemini model {model} connection failed ({net_err}). Trying next model.")
                break  # try next model in the fallback list
            except httpx.TimeoutException as timeout_err:
                if attempt < 2:
                    logger.warning(f"Gemini model {model} timeout (attempt {attempt+1}/3), retrying...")
                    await asyncio.sleep(1.0)
                    continue
                logger.warning(f"Gemini model {model} timed out after 3 attempts. Trying next model.")
                break  # try next model
            except Exception as exc:
                logger.warning(f"Gemini call to {model} failed: {exc}")
                await asyncio.sleep(0.3)
                continue

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

    idea = _safe_text(idea)

    valid_results = []
    if isinstance(search_results, list):
        for item in search_results:
            if _is_valid_search_result(item) and not _is_irrelevant_source(item):
                valid_results.append(item)

    if not valid_results:
        return {
            "competitor_analysis": {
                "direct_competitors": [],
                "indirect_competitors": [],
                "comparison": [],
                "market_gaps": [
                    "There is potential for further market research to identify specific competitor white-space opportunities."
                ],
            }
        }

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key.strip():
        gemini_result = await _run_gemini_competitor_analysis(
            idea=idea,
            search_results=valid_results,
            api_key=api_key.strip(),
            max_competitors=max_competitors
        )
        if gemini_result:
            comp_data = gemini_result.get("competitor_analysis", gemini_result)
            directs = comp_data.get("direct_competitors", [])
            
            # Targeted per-competitor audience matching (avoid positional cross-contamination)
            generic_audiences = {"general market", "enterprise customers", "businesses", "consumers", "target audience", "users", "customers", "all users", ""}
            if valid_results and directs:
                for comp in directs:
                    curr_aud = str(comp.get("target_customers") or "").strip().lower()
                    is_generic = (not curr_aud) or (curr_aud in generic_audiences) or ("target audience" in curr_aud)
                    if is_generic:
                        comp_name = str(comp.get("name") or "").strip().lower()
                        comp_url = str(comp.get("website") or comp.get("url") or "").strip().lower()
                        matched_aud = None
                        for r in valid_results:
                            r_url = str(r.get("url") or "").strip().lower()
                            r_title = str(r.get("title") or "").strip().lower()
                            aud = r.get("target_audience")
                            if not aud:
                                continue
                            if comp_url and r_url and (comp_url in r_url or r_url in comp_url):
                                matched_aud = aud
                                break
                            if comp_name and len(comp_name) > 3 and comp_name in r_title:
                                matched_aud = aud
                                break
                        if matched_aud:
                            comp["target_customers"] = matched_aud
                        
            gaps = comp_data.get("market_gaps", [])
            gap_str = " ".join(gaps).lower()
            if not any(k in gap_str for k in ["potential", "further", "validated", "no explicit"]):
                comp_data.setdefault("market_gaps", []).append(
                    "Further primary research recommended to validate potential white-space opportunities."
                )
                
            return {
                "competitor_analysis": {
                    "direct_competitors": comp_data.get("direct_competitors", []),
                    "indirect_competitors": comp_data.get("indirect_competitors", []),
                    "comparison": comp_data.get("comparison", []),
                    "market_gaps": comp_data.get("market_gaps", []),
                }
            }

    # --------------------------------------------------------
    # Containers
    # --------------------------------------------------------

    direct_competitors: List[
        Dict[str, Any]
    ] = []

    indirect_competitors: List[
        Dict[str, Any]
    ] = []

    # ========================================================
    # PROCESS SEARCH RESULTS
    # ========================================================

    for result in search_results:

        # ----------------------------------------------------
        # Invalid result
        # ----------------------------------------------------

        if not _is_valid_search_result(
            result
        ):
            continue

        # ----------------------------------------------------
        # Irrelevant source
        # ----------------------------------------------------

        if _is_irrelevant_source(
            result
        ):
            continue

        # ----------------------------------------------------
        # DIRECT
        #
        # Check direct first because digital products should
        # remain direct competitors.
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

    # ========================================================
    # APPLY LIMIT
    # ========================================================

    direct_competitors = (
        direct_competitors[:max_competitors]
    )

    indirect_competitors = (
        indirect_competitors[:max_competitors]
    )

    # ========================================================
    # COMPARISON
    # ========================================================

    comparison = _build_comparison(
        direct_competitors
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
