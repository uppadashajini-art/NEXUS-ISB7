"""
NEXUS-ISB7 - Competitor Analysis Agent

Role: Member 3

Analyzes web-search evidence to identify:
- Direct competitors
- Indirect competitors
- Competitor features
- Target customers
- Pricing information
- Strengths
- Weaknesses
- Competitor comparison
- Potential market gaps

Important:
- Never invent competitor information.
- Prefer actual products/services over articles and market reports.
- Use only evidence available in web-search results.
"""

import asyncio
import logging
import re
from typing import Any, Dict, List
from urllib.parse import urlparse

from server.models.validation import (
    ComparisonRow,
    Competitor,
    CompetitorAnalysis,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# KEYWORDS
# ---------------------------------------------------------------------------

COMPETITOR_KEYWORDS = [
    "competitor",
    "competitors",
    "alternative",
    "alternatives",
    "similar to",
    "vs",
    "versus",
    "comparison",
    "market leader",
    "leading platform",
    "software",
    "app",
    "platform",
    "solution",
    "product",
    "service",
]

INDIRECT_KEYWORDS = [
    "alternative",
    "traditional",
    "manual",
    "spreadsheet",
    "consultant",
    "consultancy",
    "agency",
    "offline",
    "do it yourself",
    "diy",
    "personal trainer",
    "coach",
    "coaching",
]

PRICING_KEYWORDS = [
    "pricing",
    "price",
    "cost",
    "subscription",
    "free",
    "premium",
    "pro plan",
    "basic plan",
    "per month",
    "per year",
    "monthly",
    "annual",
    "$",
    "₹",
    "usd",
    "inr",
]

FEATURE_KEYWORDS = [
    "feature",
    "features",
    "provides",
    "offers",
    "includes",
    "supports",
    "allows",
    "analytics",
    "dashboard",
    "automation",
    "personalization",
    "personalized",
    "recommendation",
    "recommendations",
    "integration",
    "tracking",
    "workout",
    "training",
    "coaching",
    "progress",
    "monitoring",
]

STRENGTH_KEYWORDS = [
    "leading",
    "popular",
    "large",
    "advanced",
    "powerful",
    "easy",
    "simple",
    "robust",
    "integrated",
    "personalized",
    "automated",
    "comprehensive",
    "effective",
    "widely used",
    "trusted",
]

WEAKNESS_KEYWORDS = [
    "limited",
    "lack",
    "lacks",
    "expensive",
    "complex",
    "difficult",
    "poor",
    "disadvantage",
    "drawback",
    "complaint",
    "problem",
    "issue",
    "weakness",
    "missing",
    "high cost",
    "costly",
]

# These are generally research/editorial domains rather than actual products.
RESEARCH_DOMAIN_KEYWORDS = [
    "marketresearch",
    "marketintel",
    "insightaceanalytic",
    "fortunebusinessinsights",
    "grandviewresearch",
    "mordorintelligence",
    "researchandmarkets",
    "ibisworld",
    "gminsights",
    "datainsightsmarket",
    "wiseguyreports",
    "futuredatastats",
    "market.us",
    "marketresearchfuture",
]

IRRELEVANT_TITLE_KEYWORDS = [
    "market size",
    "market research",
    "market report",
    "industry report",
    "industry analysis",
    "market analysis",
    "case study",
    "pricing strategy",
    "how should",
    "future of",
    "trends and forecast",
    "forecast 20",
    "top competitors analysis",
    "research report",
]

IRRELEVANT_CONTENT_KEYWORDS = [
    "market research report",
    "market size",
    "forecast period",
    "industry analysis",
    "revenue forecast",
    "market share forecast",
    "research report",
]

GIFT_KEYWORDS = [
    "gift",
    "gifts",
    "gift card",
    "christmas gift",
    "birthday gift",
    "best gifts",
]

WIKIPEDIA_DOMAINS = {
    "wikipedia.org",
    "wikimedia.org",
}


# ---------------------------------------------------------------------------
# BASIC HELPERS
# ---------------------------------------------------------------------------

def _clean_text(value: Any) -> str:
    """Safely convert a value to clean normalized text."""
    if value is None:
        return ""

    text = str(value)

    # Remove excessive whitespace.
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _get_domain_name(url: str) -> str:
    """
    Extract a readable domain/company name from a URL.

    Examples:
        https://www.fitbod.me/ -> Fitbod
        https://producthunt.com/... -> Producthunt
    """
    if not url:
        return ""

    try:
        normalized_url = url.strip()

        if "://" not in normalized_url:
            normalized_url = f"https://{normalized_url}"

        parsed = urlparse(normalized_url)
        host = parsed.netloc.lower().split(":")[0]

        if host.startswith("www."):
            host = host[4:]

        if not host:
            return ""

        parts = host.split(".")

        if len(parts) >= 2:
            name = parts[-2]
        else:
            name = parts[0]

        name = name.replace("-", " ")
        name = re.sub(r"[_]+", " ", name)

        return name.title()

    except Exception:
        return ""


def _get_full_domain(url: str) -> str:
    """Return normalized full domain."""
    if not url:
        return ""

    try:
        normalized_url = url.strip()

        if "://" not in normalized_url:
            normalized_url = f"https://{normalized_url}"

        parsed = urlparse(normalized_url)
        host = parsed.netloc.lower().split(":")[0]

        if host.startswith("www."):
            host = host[4:]

        return host

    except Exception:
        return ""


def _extract_sentences(text: str) -> List[str]:
    """Split source content into reasonably sized sentences."""
    if not text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text)

    cleaned_sentences = []

    for sentence in sentences:
        sentence = sentence.strip()

        if len(sentence) < 15:
            continue

        cleaned_sentences.append(sentence)

    return cleaned_sentences


def _find_matching_sentences(
    content: str,
    keywords: List[str],
    limit: int = 3,
) -> List[str]:
    """Find evidence sentences containing relevant keywords."""
    sentences = _extract_sentences(content)

    matches: List[str] = []

    for sentence in sentences:
        lower_sentence = sentence.lower()

        if any(
            keyword.lower() in lower_sentence
            for keyword in keywords
        ):
            if sentence not in matches:
                matches.append(sentence)

        if len(matches) >= limit:
            break

    return matches


# ---------------------------------------------------------------------------
# RESULT CLASSIFICATION
# ---------------------------------------------------------------------------

def _is_wikipedia(url: str) -> bool:
    """Return True when URL belongs to Wikipedia."""
    domain = _get_full_domain(url)

    return any(
        domain == blocked or domain.endswith(f".{blocked}")
        for blocked in WIKIPEDIA_DOMAINS
    )


def _looks_like_gift_page(
    title: str,
    content: str,
) -> bool:
    """Reject gift-related pages that are unrelated to startup validation."""
    text = f"{title} {content}".lower()

    return any(
        keyword in text
        for keyword in GIFT_KEYWORDS
    )


def _looks_like_research_source(
    title: str,
    content: str,
    url: str,
) -> bool:
    """
    Detect market reports, research pages, and editorial articles.

    These can be useful for market analysis but should not automatically
    become competitors.
    """
    title_lower = title.lower()
    content_lower = content.lower()
    domain_lower = _get_full_domain(url)

    # Domain-level detection.
    for keyword in RESEARCH_DOMAIN_KEYWORDS:
        if keyword in domain_lower:
            return True

    # Strong title signals.
    strong_title_signals = [
        "market size",
        "market research",
        "market report",
        "industry report",
        "industry analysis",
        "market forecast",
        "market trends",
        "research report",
        "top competitors analysis",
        "pricing strategy",
        "case study",
    ]

    if any(
        signal in title_lower
        for signal in strong_title_signals
    ):
        return True

    # Content signals.
    research_signal_count = sum(
        1
        for keyword in IRRELEVANT_CONTENT_KEYWORDS
        if keyword in content_lower
    )

    if research_signal_count >= 2:
        return True

    return False


def _looks_like_actual_product(
    title: str,
    content: str,
    url: str,
) -> bool:
    """
    Determine whether a result appears to represent a real product/service.

    We prefer pages that mention an identifiable product or service rather
    than generic market research.
    """
    if not title and not content:
        return False

    if _is_wikipedia(url):
        return False

    if _looks_like_gift_page(title, content):
        return False

    if _looks_like_research_source(title, content, url):
        return False

    text = f"{title} {content}".lower()

    product_signals = [
        "app",
        "platform",
        "software",
        "service",
        "product",
        "tool",
        "website",
        "download",
        "subscription",
        "users can",
        "helps users",
        "allows users",
        "provides users",
        "personalized",
        "training plans",
        "workout plans",
        "fitness coaching",
        "personal trainer",
    ]

    signal_count = sum(
        1
        for signal in product_signals
        if signal in text
    )

    return signal_count >= 1


def _looks_like_competitor(
    title: str,
    content: str,
    url: str = "",
) -> bool:
    """Determine whether a search result contains competitor evidence."""
    if not _looks_like_actual_product(title, content, url):
        return False

    text = f"{title} {content}".lower()

    return any(
        keyword.lower() in text
        for keyword in COMPETITOR_KEYWORDS
    )


def _looks_like_indirect_competitor(
    title: str,
    content: str,
    url: str = "",
) -> bool:
    """Detect possible indirect alternatives."""
    if not _looks_like_actual_product(title, content, url):
        return False

    text = f"{title} {content}".lower()

    return any(
        keyword.lower() in text
        for keyword in INDIRECT_KEYWORDS
    )


# ---------------------------------------------------------------------------
# INFORMATION EXTRACTION
# ---------------------------------------------------------------------------

def _extract_features(content: str) -> List[str]:
    """Extract feature-related evidence from source content."""
    matches = _find_matching_sentences(
        content,
        FEATURE_KEYWORDS,
        limit=5,
    )

    features: List[str] = []

    for sentence in matches:
        cleaned = sentence[:220].strip()

        if cleaned and cleaned not in features:
            features.append(cleaned)

    return features[:5]


def _extract_pricing(content: str) -> str | None:
    """Extract pricing-related evidence when explicitly present."""
    matches = _find_matching_sentences(
        content,
        PRICING_KEYWORDS,
        limit=3,
    )

    if not matches:
        return None

    pricing_text = " ".join(matches)

    return pricing_text[:350]


def _extract_target_customers(
    result: Dict[str, Any],
) -> str | None:
    """
    Extract target customers from search evidence.

    Explicit target_audience from the search agent is preferred.
    """
    audience = _clean_text(
        result.get("target_audience")
    )

    if audience:
        return audience

    content = _clean_text(
        result.get("content")
    ).lower()

    customer_patterns = [
        "for businesses",
        "for enterprises",
        "for students",
        "for professionals",
        "for developers",
        "for consumers",
        "for small businesses",
        "for teams",
        "for organizations",
        "for athletes",
        "for fitness enthusiasts",
        "for gym owners",
        "for personal trainers",
    ]

    for pattern in customer_patterns:
        if pattern in content:
            return pattern.replace(
                "for ",
                "",
            ).title()

    return None


def _extract_strengths(
    content: str,
    features: List[str],
) -> List[str]:
    """Identify evidence-backed strengths."""
    matches = _find_matching_sentences(
        content,
        STRENGTH_KEYWORDS,
        limit=3,
    )

    strengths: List[str] = []

    for sentence in matches:
        cleaned = sentence[:220].strip()

        if cleaned and cleaned not in strengths:
            strengths.append(cleaned)

    # Only use this fallback when there is actual feature evidence.
    if not strengths and features:
        strengths.append(
            "Offers documented product functionality "
            "in the available search evidence."
        )

    return strengths[:3]


def _extract_weaknesses(
    content: str,
) -> List[str]:
    """Identify explicitly documented weaknesses."""
    matches = _find_matching_sentences(
        content,
        WEAKNESS_KEYWORDS,
        limit=3,
    )

    weaknesses: List[str] = []

    for sentence in matches:
        cleaned = sentence[:220].strip()

        if cleaned and cleaned not in weaknesses:
            weaknesses.append(cleaned)

    return weaknesses[:3]


# ---------------------------------------------------------------------------
# COMPETITOR NAME EXTRACTION
# ---------------------------------------------------------------------------

def _clean_product_name(name: str) -> str:
    """Clean a potential competitor/product name."""
    name = _clean_text(name)

    if not name:
        return ""

    # Remove common editorial prefixes.
    prefixes = [
        "review:",
        "review -",
        "review –",
        "best ",
        "top ",
        "alternatives to ",
        "alternative to ",
    ]

    lowered = name.lower()

    for prefix in prefixes:
        if lowered.startswith(prefix):
            name = name[len(prefix):].strip()
            break

    # Avoid extremely long article titles.
    if len(name) > 80:
        return ""

    return name


def _extract_product_name_from_title(
    title: str,
    url: str,
) -> str:
    """
    Try to identify a product/service name from a search result title.

    Domain name is used only when the title does not provide a better
    identifiable product name.
    """
    title = _clean_text(title)

    if not title:
        return _get_domain_name(url)

    # Common title patterns.
    patterns = [
        r"^(.+?)\s+review\b",
        r"^(.+?)\s+alternatives?\b",
        r"^(.+?)\s+competitors?\b",
        r"^(.+?)\s+vs\.?\s+",
        r"^(.+?)\s+pricing\b",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            title,
            flags=re.IGNORECASE,
        )

        if match:
            candidate = _clean_product_name(
                match.group(1)
            )

            if candidate:
                return candidate

    # If title is clearly a product-like title, use it.
    if len(title) <= 70:
        candidate = _clean_product_name(title)

        if candidate:
            return candidate

    return _get_domain_name(url)


# ---------------------------------------------------------------------------
# BUILD COMPETITOR
# ---------------------------------------------------------------------------

def _build_competitor(
    result: Dict[str, Any],
) -> Competitor | None:
    """
    Convert one web-search result into a structured competitor.

    Only information present in the search result is used.
    """
    if not isinstance(result, dict):
        return None

    title = _clean_text(
        result.get("title")
    )

    url = _clean_text(
        result.get("url")
    )

    content = _clean_text(
        result.get("content")
    )

    if not title and not url:
        return None

    # Do not turn obvious research pages into competitors.
    if _is_wikipedia(url):
        return None

    if _looks_like_gift_page(title, content):
        return None

    if _looks_like_research_source(
        title,
        content,
        url,
    ):
        return None

    name = _extract_product_name_from_title(
        title,
        url,
    )

    if not name:
        name = _get_domain_name(url)

    if not name:
        return None

    features = _extract_features(content)

    pricing = _extract_pricing(content)

    target_customers = _extract_target_customers(
        result
    )

    strengths = _extract_strengths(
        content,
        features,
    )

    weaknesses = _extract_weaknesses(
        content
    )

    return Competitor(
        name=name,
        url=url or None,
        product_service=(
            content[:300]
            if content
            else title or None
        ),
        target_customers=target_customers,
        key_features=features,
        pricing=pricing,
        strengths=strengths,
        weaknesses=weaknesses,
    )


# ---------------------------------------------------------------------------
# DEDUPLICATION
# ---------------------------------------------------------------------------

def _deduplicate_competitors(
    competitors: List[Competitor],
) -> List[Competitor]:
    """Remove duplicate competitors by name and URL."""
    unique: List[Competitor] = []

    seen_names = set()
    seen_urls = set()

    for competitor in competitors:
        name = _clean_text(
            competitor.name
        ).lower()

        url = _clean_text(
            competitor.url
        ).lower()

        if name and name in seen_names:
            continue

        if url and url in seen_urls:
            continue

        if name:
            seen_names.add(name)

        if url:
            seen_urls.add(url)

        unique.append(competitor)

    return unique


# ---------------------------------------------------------------------------
# COMPARISON
# ---------------------------------------------------------------------------

def _build_comparison(
    competitors: List[Competitor],
) -> List[ComparisonRow]:
    """Build comparison rows from structured competitors."""
    rows: List[ComparisonRow] = []

    for competitor in competitors:
        rows.append(
            ComparisonRow(
                competitor=competitor.name,
                target_customers=(
                    competitor.target_customers
                ),
                key_features=(
                    ", ".join(
                        competitor.key_features[:3]
                    )
                    if competitor.key_features
                    else None
                ),
                strengths=(
                    ", ".join(
                        competitor.strengths[:2]
                    )
                    if competitor.strengths
                    else None
                ),
                weaknesses=(
                    ", ".join(
                        competitor.weaknesses[:2]
                    )
                    if competitor.weaknesses
                    else None
                ),
            )
        )

    return rows


# ---------------------------------------------------------------------------
# MARKET GAPS
# ---------------------------------------------------------------------------

def _identify_market_gaps(
    direct_competitors: List[Competitor],
) -> List[str]:
    """
    Identify potential market gaps from documented competitor weaknesses.

    These are opportunities, not guaranteed market facts.
    """
    gaps: List[str] = []

    weakness_text: List[str] = []

    for competitor in direct_competitors:
        weakness_text.extend(
            competitor.weaknesses
        )

    combined = " ".join(
        weakness_text
    ).lower()

    if "limited" in combined:
        gaps.append(
            "Potential opportunity to provide capabilities "
            "that existing solutions describe as limited."
        )

    if (
        "expensive" in combined
        or "costly" in combined
        or "high cost" in combined
    ):
        gaps.append(
            "Potential opportunity for a more affordable "
            "pricing model."
        )

    if (
        "complex" in combined
        or "difficult" in combined
    ):
        gaps.append(
            "Potential opportunity for a simpler and "
            "easier user experience."
        )

    if (
        "lack" in combined
        or "missing" in combined
    ):
        gaps.append(
            "Potential opportunity to address functionality "
            "identified as missing or insufficient."
        )

    if "poor" in combined:
        gaps.append(
            "Potential opportunity to improve user experience "
            "or service quality."
        )

    if not gaps:
        gaps.append(
            "Potential differentiation opportunities should "
            "be validated through deeper competitor and "
            "customer research."
        )

    return gaps[:5]


# ---------------------------------------------------------------------------
# FALLBACK COMPETITOR EXTRACTION
# ---------------------------------------------------------------------------

def _fallback_extract_competitors(
    search_results: List[Dict[str, Any]],
    existing: List[Competitor],
    limit: int = 5,
) -> List[Competitor]:
    """
    Use relevant product/service search results when explicit competitor
    keywords are not present.

    Research reports and articles are still excluded.
    """
    competitors: List[Competitor] = []

    existing_names = {
        _clean_text(
            competitor.name
        ).lower()
        for competitor in existing
    }

    for result in search_results:
        if not isinstance(result, dict):
            continue

        title = _clean_text(
            result.get("title")
        )

        content = _clean_text(
            result.get("content")
        )

        url = _clean_text(
            result.get("url")
        )

        if not _looks_like_actual_product(
            title,
            content,
            url,
        ):
            continue

        competitor = _build_competitor(result)

        if competitor is None:
            continue

        name = _clean_text(
            competitor.name
        ).lower()

        if not name or name in existing_names:
            continue

        competitors.append(competitor)
        existing_names.add(name)

        if len(competitors) >= limit:
            break

    return competitors


# ---------------------------------------------------------------------------
# MAIN AGENT
# ---------------------------------------------------------------------------

async def run_competitor_analysis_agent(
    idea: str,
    search_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Analyze web-search evidence for competitors.

    Important:
    - No fabricated competitors.
    - Research articles are not treated as competitors.
    - Actual products/services are preferred.
    """
    if not isinstance(search_results, list):
        search_results = []

    logger.info(
        "Competitor Analysis Agent started for idea: %s",
        idea[:120] if idea else "",
    )

    direct_competitors: List[Competitor] = []
    indirect_competitors: List[Competitor] = []

    seen_urls = set()

    # ---------------------------------------------------------------
    # STEP 1: CLASSIFY SEARCH RESULTS
    # ---------------------------------------------------------------

    for result in search_results:
        if not isinstance(result, dict):
            continue

        url = _clean_text(
            result.get("url")
        )

        normalized_url = url.lower().strip()

        if normalized_url and normalized_url in seen_urls:
            continue

        if normalized_url:
            seen_urls.add(normalized_url)

        title = _clean_text(
            result.get("title")
        )

        content = _clean_text(
            result.get("content")
        )

        if not title and not content:
            continue

        # Skip clearly irrelevant sources.
        if _is_wikipedia(url):
            logger.debug(
                "Skipping Wikipedia result: %s",
                title,
            )
            continue

        if _looks_like_gift_page(
            title,
            content,
        ):
            logger.debug(
                "Skipping gift-related result: %s",
                title,
            )
            continue

        if _looks_like_research_source(
            title,
            content,
            url,
        ):
            logger.debug(
                "Skipping research/article result: %s",
                title,
            )
            continue

        competitor = _build_competitor(
            result
        )

        if competitor is None:
            continue

        # Indirect alternatives first.
        if _looks_like_indirect_competitor(
            title,
            content,
            url,
        ):
            indirect_competitors.append(
                competitor
            )

        elif _looks_like_competitor(
            title,
            content,
            url,
        ):
            direct_competitors.append(
                competitor
            )

    # ---------------------------------------------------------------
    # STEP 2: FALLBACK
    # ---------------------------------------------------------------

    direct_competitors = _deduplicate_competitors(
        direct_competitors
    )

    indirect_competitors = _deduplicate_competitors(
        indirect_competitors
    )

    # If explicit competitor evidence was weak, extract actual products
    # from relevant search results.
    if len(direct_competitors) < 3:
        fallback_competitors = (
            _fallback_extract_competitors(
                search_results,
                existing=(
                    direct_competitors
                    + indirect_competitors
                ),
                limit=5 - len(direct_competitors),
            )
        )

        direct_competitors.extend(
            fallback_competitors
        )

    # ---------------------------------------------------------------
    # STEP 3: FINAL DEDUPLICATION
    # ---------------------------------------------------------------

    direct_competitors = _deduplicate_competitors(
        direct_competitors
    )[:5]

    indirect_competitors = _deduplicate_competitors(
        indirect_competitors
    )[:5]

    # ---------------------------------------------------------------
    # STEP 4: BUILD COMPARISON
    # ---------------------------------------------------------------

    comparison = _build_comparison(
        direct_competitors
    )

    # ---------------------------------------------------------------
    # STEP 5: MARKET GAPS
    # ---------------------------------------------------------------

    market_gaps = _identify_market_gaps(
        direct_competitors
    )

    # ---------------------------------------------------------------
    # STEP 6: CREATE RESPONSE
    # ---------------------------------------------------------------

    analysis = CompetitorAnalysis(
        direct_competitors=direct_competitors,
        indirect_competitors=indirect_competitors,
        comparison=comparison,
        market_gaps=market_gaps,
    )

    logger.info(
        "Competitor Analysis completed: "
        "%d direct, %d indirect competitors",
        len(direct_competitors),
        len(indirect_competitors),
    )

    return {
        "competitor_analysis": analysis.model_dump()
    }


# ---------------------------------------------------------------------------
# LOCAL TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    sample_results = [
        {
            "title": "FitnessAI Review – Cost, Use Cases & Alternatives",
            "url": "https://example.com/fitnessai",
            "target_audience": "fitness enthusiasts",
            "content": (
                "FitnessAI is an AI-powered fitness app designed "
                "to optimize strength training by providing "
                "personalized workout plans that adapt to user "
                "performance. The platform offers personalized "
                "recommendations and progress tracking."
            ),
        },
        {
            "title": "Fitbod - Personalized Workout Plans",
            "url": "https://fitbod.me",
            "target_audience": "fitness enthusiasts",
            "content": (
                "Fitbod provides personalized workout plans "
                "based on user goals and training history. "
                "The app supports workout tracking and "
                "personalized recommendations."
            ),
        },
        {
            "title": "AI in Fitness Market Size and Trends 2035",
            "url": "https://example.com/market-report",
            "target_audience": "fitness enthusiasts",
            "content": (
                "The AI in Fitness market research report "
                "provides market size, revenue forecasts, "
                "industry analysis and market trends."
            ),
        },
        {
            "title": "AI Fitness App Pricing",
            "url": "https://example.com/pricing",
            "target_audience": "college students",
            "content": (
                "The app offers personalized workout plans, "
                "analytics and progress tracking. Pricing "
                "starts at $9.99 per month."
            ),
        },
    ]

    result = asyncio.run(
        run_competitor_analysis_agent(
            idea=(
                "AI platform that provides personalized "
                "fitness plans for users"
            ),
            search_results=sample_results,
        )
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )