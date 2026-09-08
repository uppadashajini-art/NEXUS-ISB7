
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

import re
from typing import Any, Dict, List


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
    "is an app",
    "is a app",
    "is a mobile app",
    "is a web app",
    "is an application",
    "is a platform",
    "is software",
    "is a saas",
    "is a tool",

    "mobile app",
    "web app",

    "fitness app",
    "workout app",
    "training app",

    "fitness platform",
    "workout platform",
    "training platform",

    "ai fitness",
    "ai fitness app",
    "ai fitness platform",
    "ai fitness coach",

    "ai coach",
    "ai-powered coach",
    "ai powered coach",

    "digital platform",
    "online platform",
    "software platform",
    "digital coaching",

    "personalized fitness platform",
    "personalized workout platform",

    "personalized workout plans",
    "personalized training plans",

    "provides an app",
    "provides a platform",
    "provides software",

    "offers an app",
    "offers a platform",
    "offers software",

    "provides personalized workout plans",
    "provides personalized training plans",

    "online fitness platform",
    "online fitness app",
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
]


# ============================================================
# DIRECT COMPETITOR SIGNALS
# ============================================================

DIRECT_SERVICE_PHRASES = [
    "personalized workout",
    "personalized training",
    "personalized workout plans",
    "personalized training plans",

    "workout plans",
    "training plans",

    "fitness tracking",
    "workout tracking",

    "fitness recommendations",
    "training recommendations",

    "ai recommendations",
    "personalized recommendations",

    "online fitness",
    "digital fitness",
    "digital training",

    "fitness tracking app",
    "workout tracking app",

    "personalized fitness",
]


# ============================================================
# INDIRECT COMPETITOR SIGNALS
# ============================================================

INDIRECT_SERVICE_PHRASES = [
    # --------------------------------------------------------
    # Personal trainers
    # --------------------------------------------------------
    "personal trainer",
    "personal trainers",

    "personal training",
    "personal training service",
    "personal training services",

    "trainer service",
    "trainer services",

    "training service",
    "training services",

    # --------------------------------------------------------
    # Traditional coaching
    # --------------------------------------------------------
    "traditional coaching",
    "traditional coach",
    "traditional coaches",

    "traditional personal training",

    "fitness coach",
    "fitness coaches",

    "fitness coaching",
    "personal coaching",

    "coaching service",
    "coaching services",

    # --------------------------------------------------------
    # Offline / physical
    # --------------------------------------------------------
    "in-person coaching",
    "in person coaching",

    "in-person training",
    "in person training",

    "offline coaching",
    "offline training",
    "offline fitness",

    "face-to-face training",
    "face to face training",

    "face-to-face coaching",
    "face to face coaching",

    # --------------------------------------------------------
    # Gyms
    # --------------------------------------------------------
    "gym membership",
    "gym memberships",

    "fitness center",
    "fitness centre",

    "fitness club",
    "fitness clubs",

    "local gym",
    "local gyms",

    "gym service",
    "gym services",

    "gym",

    # --------------------------------------------------------
    # One-to-one
    # --------------------------------------------------------
    "one-on-one training",
    "one on one training",

    "one-on-one coaching",
    "one on one coaching",

    "one-to-one training",
    "one to one training",

    "one-to-one coaching",
    "one to one coaching",

    # --------------------------------------------------------
    # Classes
    # --------------------------------------------------------
    "fitness classes",
    "fitness class",

    "group fitness",
    "group training",

    "yoga classes",
    "workout classes",
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
# IRRELEVANT SOURCE SIGNALS
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

    "gift ideas",
    "gift guide",
    "best gifts",
    "birthday gifts",
    "christmas gifts",
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

    # --------------------------------------------------------
    # Wikipedia
    # --------------------------------------------------------

    if "wikipedia.org" in url:
        return True

    if "wikipedia" in title:
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

def _build_competitor(
    result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convert search result into competitor object.
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

    name = (
        title
        or _safe_text(
            result.get("name")
        )
        or "Unknown Competitor"
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
    # Remove duplicate gaps
    # --------------------------------------------------------

    unique_gaps: List[str] = []

    for gap in gaps:

        if gap not in unique_gaps:
            unique_gaps.append(
                gap
            )

    # --------------------------------------------------------
    # Conservative fallback
    # --------------------------------------------------------

    if not unique_gaps:

        if indirect_competitors:

            unique_gaps.append(
                "There is potential to differentiate by "
                "combining digital personalization with "
                "needs currently served by traditional "
                "alternatives."
            )

        elif direct_competitors:

            unique_gaps.append(
                "Further competitor research is needed "
                "to confirm a specific market gap."
            )

        else:

            unique_gaps.append(
                "There is potential for further market "
                "research to identify a specific competitor "
                "gap."
            )

    return unique_gaps


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

    Expected result:

    {
        "competitor_analysis": {
            "direct_competitors": [],
            "indirect_competitors": [],
            "comparison": [],
            "market_gaps": []
        }
    }
    """

    idea = _safe_text(
        idea
    )

    # --------------------------------------------------------
    # Handle invalid search results
    # --------------------------------------------------------

    if not isinstance(
        search_results,
        list,
    ):
        search_results = []

    # --------------------------------------------------------
    # Competitor limit
    # --------------------------------------------------------

    try:

        limit = int(
            max_competitors
        )

    except (
        TypeError,
        ValueError,
    ):

        limit = DEFAULT_COMPETITOR_LIMIT

    # Never allow more than 5
    limit = max(
        1,
        min(
            limit,
            MAX_COMPETITOR_LIMIT,
        ),
    )

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
        direct_competitors[:limit]
    )

    indirect_competitors = (
        indirect_competitors[:limit]
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
