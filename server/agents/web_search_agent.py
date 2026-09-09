import asyncio
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "can",
    "could", "should", "would", "will", "shall", "platform", "app", "application",
    "website", "tool", "service", "system", "solution", "based", "powered",
    "startup", "business", "product", "idea", "aimed", "helping", "people",
    "users", "clients", "companies", "designed", "that", "this", "which",
    "turns", "into", "their", "your", "our", "provide", "provides", "making",
    "make", "use", "using", "uses", "solves", "solve", "solving", "deploy",
    "deploys", "deploying", "repurpose", "repurposes", "repurposing",
    "enable", "enables", "enabling", "guarantee", "guarantees", "operate",
    "operates", "operating", "serves", "serve", "serving", "persistent"
}

# ============================================================
# Configuration
# ============================================================

MAX_TOTAL_RESULTS = 10
SEARCH_RESULTS_PER_QUERY = 5
SEARCH_TIMEOUT_SECONDS = 30

DOMAIN_KEYWORD_TAXONOMY = [
    ("construction contractor labor marketplace", ["construction", "contractor", "contractors", "subcontractor", "subcontractors", "builder", "builders", "tradesperson", "electrician", "plumber", "jobsite", "field work"]),
    ("pet care services marketplace", ["pet", "pets", "dog", "cat", "sitter", "sitters", "walker", "walkers", "groomer", "groomers", "veterinary", "animal", "canine", "feline"]),
    ("3d graphics spatial web studio", ["3d", "webgl", "three.js", "threejs", "spatial", "motion design", "shaders", "portfolio", "creative dev", "canvas", "rendering", "3d web"]),
    ("devtools developer experience", ["devtools", "developer", "api", "sdk", "code", "ide", "cli", "github", "framework", "open-source"]),
    ("design tools creative tech", ["design", "figma", "motion", "animation", "ui/ux", "creative", "studio", "prototype", "asset"]),
    ("creator economy content tech", ["creator", "content", "media", "influencer", "streamer", "video", "monetization"]),
    ("last-mile logistics micro-fulfillment", ["last-mile", "supply chain", "fulfillment", "delivery", "warehouse", "logistics", "courier", "freight", "transit"]),
    ("cleantech carbon sustainability", ["sustainability", "carbon", "emissions", "cleantech", "renewable", "solar", "esg", "recycle"]),
    ("fintech banking payments", ["fintech", "banking", "payment", "payments", "lending", "credit", "wealth", "invest"]),
    ("digital health fitness", ["health", "fitness", "workout", "wellness", "medical", "clinic", "telehealth"]),
    ("edtech learning education", ["education", "edtech", "student", "lecture", "quiz", "course", "tutor"]),
    ("ecommerce retail commerce", ["ecommerce", "e-commerce", "retail", "merchant", "marketplace", "shop", "store"]),
    ("enterprise saas productivity", ["saas", "enterprise", "workflow", "productivity", "collaboration", "crm"]),
    ("cybersecurity data privacy", ["cybersecurity", "security", "privacy", "gdpr", "compliance", "fraud"]),
    ("ai automation robotics", ["ai", "automation", "robotics", "drones", "ground bots", "autonomous", "machine learning"])
]

GENERIC_BUSINESS_MODEL_TERMS = {
    "subscription", "subscriptions", "payment", "payments", "billing",
    "monetization", "fintech", "saas", "platform", "platforms", "ai",
    "automation", "b2b", "b2c", "app", "application", "service", "tool",
    "marketplace", "software"
}


def _detect_domain_from_keywords(text: str) -> str:
    text_lower = text.lower()
    best_domain = ""
    best_matches = 0
    for domain_name, keywords in DOMAIN_KEYWORD_TAXONOMY:
        matches = 0
        for kw in keywords:
            if kw.lower() in GENERIC_BUSINESS_MODEL_TERMS:
                continue
            count = len(re.findall(rf"\b{re.escape(kw)}\b", text_lower))
            matches += count * 10
        if matches > best_matches:
            best_matches = matches
            best_domain = domain_name
    return best_domain


# ============================================================
# Environment
# ============================================================

def _load_env_if_needed() -> None:
    """
    Explicitly load C:/Nexus/server/.env.
    """

    try:
        from dotenv import load_dotenv

        # web_search_agent.py
        # C:/Nexus/server/agents/web_search_agent.py
        #
        # parents[0] = agents
        # parents[1] = server
        server_dir = Path(__file__).resolve().parents[1]

        env_path = server_dir / ".env"

        if env_path.exists():
            load_dotenv(
                dotenv_path=env_path,
                override=False,
            )

            logger.info(
                "Environment loaded from: %s",
                env_path,
            )

            logger.info(
                "Tavily configured: %s",
                bool(os.getenv("TAVILY_API_KEY")),
            )

        else:
            logger.warning(
                "server/.env was not found at: %s",
                env_path,
            )

    except ImportError:
        logger.warning(
            "python-dotenv is not installed; "
            "using existing environment variables."
        )


_load_env_if_needed()


# ============================================================
# Text Utilities
# ============================================================

def clean_text(text: str) -> str:
    """
    Clean text while preserving useful words.
    """

    if not text:
        return ""

    text = str(text)

    # Remove markdown formatting characters.
    text = re.sub(
        r"[*()\[\]{}]",
        " ",
        text,
    )

    # Keep letters, numbers, spaces and hyphens.
    text = re.sub(
        r"[^a-zA-Z0-9\s\-]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def extract_key_phrases(
    text: str,
    max_terms: int = 5,
) -> str:
    """
    Extract meaningful keywords from text.
    """

    cleaned = clean_text(text)

    words = cleaned.lower().split()

    meaningful_words = []

    for word in words:

        word = word.strip("-")

        if not word:
            continue

        if word in STOP_WORDS:
            continue

        if len(word) <= 2:
            continue

        if word not in meaningful_words:
            meaningful_words.append(word)

    return " ".join(
        meaningful_words[:max_terms]
    )


# ============================================================
# Startup Idea Decomposition
# ============================================================

def decompose_startup_idea(
    idea: str,
    domain: str = "",
    audience: str = "",
) -> Dict[str, str]:
    """
    Decompose startup idea into:

    domain
    audience
    problem
    solution
    """

    cleaned_idea = clean_text(idea)
    words = cleaned_idea.split()
    first_word = words[0].lower() if words else ""
    
    # 1. Domain Vector
    domain_vec = extract_key_phrases(domain, max_terms=3) if domain else ""
    if not domain_vec:
        detected = _detect_domain_from_keywords(cleaned_idea)
        if detected:
            domain_vec = detected
        else:
            domain_vec = extract_key_phrases(cleaned_idea, max_terms=4)
    
    # 2. Audience Vector
    audience_vec = extract_key_phrases(audience, max_terms=3) if audience else ""
    if not audience_vec:
        aud_match = re.search(r"(?:for|designed for|targeting|aimed at|sold to|enabling|empowers?|built for|helps?|allows?)\s+([A-Za-z0-9\s-]+?)(?:\.|\,|$)", idea, re.IGNORECASE)
        if aud_match:
            audience_vec = extract_key_phrases(aud_match.group(1), max_terms=3)
            
    # 3. Problem & Value Vector
    problem_words = []
    for m in re.finditer(r"(?:eliminat\w*|reduc\w*|cost\w*|expens\w*|problem\w*|friction|wast\w*|loss\w*|challeng\w*|bottleneck\w*|overcoming?)\s+([A-Za-z0-9\s-]+?)(?:\.|\,|$)", idea, re.IGNORECASE):
        problem_words.extend(extract_key_phrases(m.group(1), max_terms=3).split())
    problem_vec = " ".join(list(dict.fromkeys([w for w in problem_words if w.lower() != first_word]))[:4])
    if not problem_vec:
        problem_vec = extract_key_phrases(cleaned_idea, max_terms=3)
        
    # 4. Mechanism / Innovation Vector
    solution_words = []
    for m in re.finditer(r"(?:combining|utilizing|using|with|via|through|platform|network|deploying|repurposing|studio|engine|tool)\s+([A-Za-z0-9\s-]+?)(?:\.|\,|$)", idea, re.IGNORECASE):
        solution_words.extend(extract_key_phrases(m.group(1), max_terms=3).split())
    solution_vec = " ".join(list(dict.fromkeys([w for w in solution_words if w.lower() != first_word]))[:4])
    if not solution_vec:
        solution_vec = extract_key_phrases(" ".join(words[1:]) if len(words) > 1 else cleaned_idea, max_terms=4)
        
    fallback_domain = extract_key_phrases(cleaned_idea, max_terms=4) or "software platform service"

    return {
        "domain": domain_vec if domain_vec else fallback_domain,
        "audience": audience_vec,
        "problem": problem_vec,
        "solution": solution_vec,
    }


# ============================================================
# Search Query Generation
# ============================================================

def generate_search_queries(
    decomposed: Dict[str, str],
    validation_type: str = "all",
) -> List[str]:
    """
    Generate domain-aware search queries.
    """

    domain = decomposed.get(
        "domain",
        "",
    ).strip()

    audience = decomposed.get(
        "audience",
        "",
    ).strip()

    problem = decomposed.get(
        "problem",
        "",
    ).strip()

    solution = decomposed.get(
        "solution",
        "",
    ).strip()

    # --------------------------------------------------------
    # Build core
    # --------------------------------------------------------

    core_parts = []

    if domain:
        core_parts.append(domain)

    if solution:
        core_parts.append(solution)

    core = " ".join(core_parts).strip()

    # --------------------------------------------------------
    # Remove duplicate words
    # --------------------------------------------------------

    words = core.split()

    seen = set()

    core_words = []

    for word in words:

        key = word.lower()

        if key not in seen:

            seen.add(key)

            core_words.append(word)

    core = " ".join(core_words)

    # --------------------------------------------------------
    # Queries
    # --------------------------------------------------------

    queries = []

    # Market
    if validation_type in (
        "all",
        "market",
    ):

        queries.append(
            f"{core} market size growth trends "
            f"industry forecast"
        )

    # Competition
    if validation_type in (
        "all",
        "competition",
    ):

        queries.append(
            f"{core} competitors alternatives "
            f"market leaders products"
        )

    # Customers
    if validation_type in (
        "all",
        "customers",
    ):

        audience_part = (
            f" {audience}"
            if audience
            else ""
        )

        queries.append(
            f"{core}{audience_part} "
            f"customer needs pain points "
            f"user problems"
        )

    # Business
    if validation_type in (
        "all",
        "business",
    ):

        queries.append(
            f"{core} business model pricing "
            f"subscription revenue"
        )

    # Risks
    if validation_type in (
        "all",
        "risks",
    ):

        queries.append(
            f"{core} startup challenges risks "
            f"failure reasons"
        )

    # Problem-specific
    if problem and validation_type in (
        "all",
        "customers",
        "risks",
    ):

        queries.append(
            f"{core} {problem} "
            f"customer research"
        )

    # Scientific Validation
    if validation_type in (
        "all",
        "scientific",
        "risks",
    ):
        queries.append(
            f"{core} scientific validation peer reviewed clinical literature biomarker studies pubmed research"
        )

    # Technical Feasibility
    if validation_type in (
        "all",
        "technical",
    ):
        queries.append(
            f"{core} technical feasibility acoustic signal processing algorithms sensor constraints audio frequency limits"
        )

    # Regulatory Risk & Compliance
    if validation_type in (
        "all",
        "regulatory",
        "risks",
    ):
        queries.append(
            f"{core} FDA SaMD software as a medical device classification clinical trial requirements wellness disclaimer"
        )

    # --------------------------------------------------------
    # Remove duplicate queries
    # --------------------------------------------------------

    unique_queries = []

    seen_queries = set()

    for query in queries:

        normalized = " ".join(
            query.lower().split()
        )

        if normalized in seen_queries:
            continue

        seen_queries.add(normalized)

        unique_queries.append(
            query.strip()
        )

    return unique_queries


# ============================================================
# Tavily Search
# ============================================================

async def _search_tavily(
    query: str,
    max_results: int = 5,
) -> List[Dict[str, Any]]:
    """
    Search using Tavily.
    Tavily is the primary provider.
    """

    _load_env_if_needed()

    api_key = os.getenv(
        "TAVILY_API_KEY"
    )

    if not api_key:

        logger.warning(
            "TAVILY_API_KEY is not configured."
        )

        return []

    if api_key == "your_key_here":

        logger.warning(
            "TAVILY_API_KEY contains placeholder value."
        )

        return []

    try:

        from tavily import TavilyClient

        client = TavilyClient(
            api_key=api_key
        )

        response = await asyncio.wait_for(
            asyncio.to_thread(
                client.search,
                query=query,
                search_depth="advanced",
                max_results=max_results,
            ),
            timeout=SEARCH_TIMEOUT_SECONDS,
        )

        if not isinstance(
            response,
            dict,
        ):
            return []

        results = []

        for item in response.get(
            "results",
            [],
        ):

            if not isinstance(
                item,
                dict,
            ):
                continue

            title = str(
                item.get(
                    "title",
                    "",
                )
            ).strip()

            url = str(
                item.get(
                    "url",
                    "",
                )
            ).strip()

            content = str(
                item.get(
                    "content",
                    "",
                )
            ).strip()

            if not title or not url:
                continue

            results.append(
                {
                    "title": title,
                    "url": url,
                    "content": content,
                }
            )

        logger.info(
            "Tavily returned %d results for query: %s",
            len(results),
            query,
        )

        return results

    except asyncio.TimeoutError:

        logger.warning(
            "Tavily search timed out for query: %s",
            query,
        )

        return []

    except Exception as exc:

        logger.warning(
            "Tavily search failed: %s",
            exc,
        )

        return []


# ============================================================
# DuckDuckGo / DDGS Search
# ============================================================

async def _search_ddg_async(
    query: str,
    max_results: int = 5,
) -> List[Dict[str, Any]]:
    """
    Search using DDGS as fallback.
    """

    try:

        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS

        def search_sync():

            with DDGS() as ddgs:

                return list(
                    ddgs.text(
                        query,
                        max_results=max_results,
                    )
                )

        raw_results = await asyncio.wait_for(
            asyncio.to_thread(
                search_sync
            ),
            timeout=SEARCH_TIMEOUT_SECONDS,
        )

        results = []

        for item in raw_results:

            if not isinstance(
                item,
                dict,
            ):
                continue

            title = str(
                item.get(
                    "title",
                    "",
                )
            ).strip()

            url = str(
                item.get(
                    "href",
                    "",
                )
            ).strip()

            content = str(
                item.get(
                    "body",
                    "",
                )
            ).strip()

            if not title or not url:
                continue

            results.append(
                {
                    "title": title,
                    "url": url,
                    "content": content,
                }
            )

        logger.info(
            "DDGS returned %d results for query: %s",
            len(results),
            query,
        )

        return results

    except asyncio.TimeoutError:

        logger.warning(
            "DDGS search timed out for query: %s",
            query,
        )

        return []

    except Exception as exc:

        logger.warning(
            "DDGS search failed: %s",
            exc,
        )

        return []


# ============================================================
# Execute Search
# ============================================================

async def _execute_single_query(
    query: str,
    max_results: int = 5,
) -> List[Dict[str, Any]]:
    """
    Execute one search query.

    Tavily first.
    DDGS fallback.
    """

    tavily_results = await _search_tavily(
        query,
        max_results=max_results,
    )

    if tavily_results:

        return tavily_results

    logger.info(
        "Tavily returned no results; "
        "trying DDGS fallback."
    )

    return await _search_ddg_async(
        query,
        max_results=max_results,
    )


# ============================================================
# URL Utilities
# ============================================================

def _get_domain_name(url: str) -> str:
    """
    Extract the main domain name from a URL.
    """

    if not url:
        return ""

    try:

        parsed = urlparse(url)

        hostname = (
            parsed.netloc
            or parsed.path
        )

        hostname = hostname.lower()

        hostname = re.sub(
            r"^www\.",
            "",
            hostname,
        )

        if not hostname:
            return ""

        parts = hostname.split(".")

        if len(parts) >= 2:

            return parts[-2]

        return parts[0]

    except Exception:

        return ""


# ============================================================
# Sentence Utilities
# ============================================================

def _extract_sentences(
    text: str,
) -> List[str]:
    """
    Split text into sentences.
    """

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def _find_matching_sentences(
    text: str,
    keywords: List[str],
    max_sentences: int = 3,
) -> List[str]:
    """
    Find sentences containing relevant keywords.
    """

    sentences = _extract_sentences(text)

    matches = []

    for sentence in sentences:

        lower_sentence = sentence.lower()

        if any(
            keyword.lower() in lower_sentence
            for keyword in keywords
        ):

            matches.append(sentence)

        if len(matches) >= max_sentences:
            break

    return matches


# ============================================================
# Relevance Scoring
# ============================================================

def _score_source_quality_and_relevance(
    result: Dict[str, Any],
    decomposed: Dict[str, str],
) -> float:
    """
    Score search result based on:

    - domain relevance
    - solution relevance
    - audience relevance
    - market signals
    - source authority
    - competitor signals
    - spam signals
    """

    title = str(
        result.get(
            "title",
            "",
        )
    )

    content = str(
        result.get(
            "content",
            "",
        )
    )

    url = str(
        result.get(
            "url",
            "",
        )
    )

    full_text = (
        f"{title} {content} {url}"
    ).lower()

    score = 0.0

    # --------------------------------------------------------
    # Authority domains
    # --------------------------------------------------------

    authority_domains = {
        "statista",
        "grandviewresearch",
        "mordorintelligence",
        "fortunebusinessinsights",
        "researchandmarkets",
        "ibisworld",
        "gminsights",
        "nih",
        "ncbi",
        "forbes",
        "techcrunch",
        "businessinsider",
        "mckinsey",
        "deloitte",
        "pwc",
        "gartner",
        "hbr",
        "harvard",
    }

    domain_name = _get_domain_name(url)

    if domain_name in authority_domains:

        score += 15

    # --------------------------------------------------------
    # Domain
    # --------------------------------------------------------

    domain = decomposed.get(
        "domain",
        "",
    ).lower()

    domain_terms = [
        term
        for term in domain.split()
        if len(term) > 2
    ]

    for term in domain_terms:

        if term in full_text:

            score += 5

    # --------------------------------------------------------
    # Solution
    # --------------------------------------------------------

    solution = decomposed.get(
        "solution",
        "",
    ).lower()

    solution_terms = [
        term
        for term in solution.split()
        if len(term) > 2
    ]

    for term in solution_terms:

        if term in full_text:

            score += 4

    # --------------------------------------------------------
    # Audience
    # --------------------------------------------------------

    audience = decomposed.get(
        "audience",
        "",
    ).lower()

    audience_terms = [
        term
        for term in audience.split()
        if len(term) > 2
    ]

    audience_matches = 0

    for term in audience_terms:

        if term in full_text:

            audience_matches += 1

    if audience_matches:

        score += min(
            audience_matches * 4,
            12,
        )

    # --------------------------------------------------------
    # Industry relevance
    # --------------------------------------------------------

    industry_keywords = [

        "fitness",
        "workout",
        "exercise",
        "gym",
        "training",

        "health",
        "healthcare",
        "wellness",

        "education",
        "student",
        "learning",

        "finance",
        "fintech",
        "banking",
        "investment",

        "retail",
        "ecommerce",

        "agriculture",
        "agritech",

        "travel",
        "tourism",

        "logistics",

        "insurance",

        "software",
        "saas",

        "artificial intelligence",
        "machine learning",
        "ai",
    ]

    industry_matches = sum(
        1
        for keyword in industry_keywords
        if keyword in full_text
    )

    if industry_matches == 0:

        score -= 15

    elif industry_matches == 1:

        score += 4

    elif industry_matches == 2:

        score += 7

    else:

        score += 10

    # --------------------------------------------------------
    # Market quality signals
    # --------------------------------------------------------

    metric_patterns = [

        r"\b\d+(?:\.\d+)?\s*%\b",

        r"\bcagr\b",

        r"\bmarket size\b",

        r"\brevenue\b",

        r"\bbillion\b",

        r"\bmillion\b",

        r"\bpricing\b",

        r"\bsubscription\b",

        r"\bforecast\b",

        r"\bgrowth rate\b",

        r"\bmarket share\b",

        r"\bvaluation\b",
    ]

    for pattern in metric_patterns:

        if re.search(
            pattern,
            full_text,
            flags=re.IGNORECASE,
        ):

            score += 3

    # --------------------------------------------------------
    # Competitor signals
    # --------------------------------------------------------

    competitor_keywords = [

        "competitor",
        "competitors",

        "alternative",
        "alternatives",

        "market leader",

        "similar",

        "comparison",

        "compare",

        "competitor analysis",

        "top companies",

        "leading companies",

        "leading platforms",

        "market players",
    ]

    for keyword in competitor_keywords:

        if keyword in full_text:

            score += 2

    # --------------------------------------------------------
    # Customer signals
    # --------------------------------------------------------

    customer_keywords = [

        "customer needs",
        "user needs",
        "pain points",
        "user problems",
        "consumer behavior",
        "customer behavior",
        "target users",
        "target audience",
        "user preferences",
        "consumer preferences",
    ]

    for keyword in customer_keywords:

        if keyword in full_text:

            score += 3

    # --------------------------------------------------------
    # Business signals
    # --------------------------------------------------------

    business_keywords = [

        "business model",
        "revenue model",
        "subscription model",
        "pricing model",
        "subscription",
        "freemium",
        "monthly plan",
        "annual plan",
        "monetization",
    ]

    for keyword in business_keywords:

        if keyword in full_text:

            score += 3

    # --------------------------------------------------------
    # Risk signals
    # --------------------------------------------------------

    risk_keywords = [

        "risk",
        "risks",
        "challenge",
        "challenges",
        "barrier",
        "barriers",
        "privacy concern",
        "security concern",
        "regulatory",
        "failure",
        "limitations",
    ]

    for keyword in risk_keywords:

        if keyword in full_text:

            score += 2

    # --------------------------------------------------------
    # Gift filtering
    # --------------------------------------------------------

    gift_keywords = [

        "gift",
        "gifts",
        "personalized gifts",
        "personalised gifts",
        "custom gifts",
        "customized gifts",
        "customised gifts",
        "birthday gifts",
        "wedding gifts",
        "corporate gifts",
        "gift ideas",
        "gift shop",
        "gift store",
    ]

    gift_matches = sum(
        1
        for keyword in gift_keywords
        if keyword in full_text
    )

    if gift_matches:

        score -= 25

    # --------------------------------------------------------
    # Weak page signals
    # --------------------------------------------------------

    weak_keywords = [

        "coupon",
        "discount code",
        "free download",
        "template",
        "pinterest",
        "shopping",
        "shop now",
        "giveaway",
        "affiliate",
    ]

    for keyword in weak_keywords:

        if keyword in full_text:

            score -= 8

    # --------------------------------------------------------
    # Wikipedia
    # --------------------------------------------------------

    if "wikipedia.org" in url.lower():

        score -= 30

    return score


# ============================================================
# Heuristic Reranking
# ============================================================

def _heuristic_rerank(
    results: List[Dict[str, Any]],
    decomposed: Dict[str, str],
) -> List[Dict[str, Any]]:
    """
    Rank results using deterministic local scoring.
    """

    scored_results = []

    for result in results:

        score = _score_source_quality_and_relevance(
            result,
            decomposed,
        )

        result_copy = dict(result)

        result_copy[
            "_relevance_score"
        ] = score

        scored_results.append(
            result_copy
        )

    scored_results.sort(
        key=lambda item: item.get(
            "_relevance_score",
            0,
        ),
        reverse=True,
    )

    return scored_results


# ============================================================
# Gemini Prompt
# ============================================================

def _build_gemini_prompt(
    idea: str,
    results: List[Dict[str, Any]],
) -> str:
    """
    Keep this helper for compatibility.

    Gemini is intentionally not used in the main search flow.
    """

    formatted_results = []

    for index, result in enumerate(results):

        formatted_results.append(
            f"""
RESULT {index + 1}

Title: {result.get("title", "")}

URL: {result.get("url", "")}

Content: {result.get("content", "")[:1500]}
"""
        )

    return f"""
You are a startup research search-quality evaluator.

Startup idea:

{idea}

Evaluate the following search results.

Prefer genuinely relevant:

- Direct competitors
- Similar products
- Alternative solutions
- Industry market reports
- Customer research
- Pricing information
- Business model information
- Technology trends
- Startup risks

Do NOT select:

- Gift websites
- Gift shops
- Birthday gifts
- Wedding gifts
- Corporate gifts
- Wikipedia
- Irrelevant shopping pages
- Completely unrelated pages

Return only the indexes of relevant results.

{"".join(formatted_results)}
"""


# ============================================================
# Gemini Reranking
# ============================================================

async def _rerank_with_gemini(
    idea: str,
    results: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Gemini reranking is intentionally disabled.

    Reason:
    The search agent should not depend on Gemini authentication.
    Tavily + local relevance ranking are sufficient.

    The helper remains available so existing tests/imports
    do not break.
    """
    logger.info(
        "Gemini reranking skipped; using deterministic relevance ranking."
    )
    return results


# ============================================================
# Audience Inference
# ============================================================

async def _decompose_with_gemini_async(idea: str) -> Optional[Dict[str, str]]:
    """
    Decompose startup idea using Gemini with explicit primary business function instructions.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        return None

    import httpx, json
    prompt = f"""Identify the PRIMARY business function first — what does this company actually DO and WHO does it connect or serve — before considering secondary features like payment processing, AI, subscriptions, or monetization mechanics. A company that connects contractors with subcontractors is a CONSTRUCTION/LABOR MARKETPLACE, even if it charges via subscriptions or processes payments. A company that matches pet owners with sitters is a PET SERVICES MARKETPLACE, even if it uses AI matching. Do not classify based on HOW the company monetizes or WHAT TECHNOLOGY it uses — classify based on WHAT PROBLEM it solves and for WHOM. List the 2-3 core nouns describing what is being connected/served (e.g. 'contractors', 'subcontractors', 'construction projects') and derive industry from those, not from adjacent business-model language.

Analyze this startup idea:
"{idea}"

Return ONLY a valid JSON object with these exact keys:
{{
  "domain": "2-4 core nouns describing the primary business domain (e.g. 'construction contractor labor marketplace', 'pet care services marketplace')",
  "audience": "Target audience (e.g. 'General Contractors & Subcontractors', 'Pet Owners & Sitters')",
  "problem": "Core problem solved (e.g. 'managing bidding worker scheduling labor shortages')",
  "solution": "Core mechanism or solution (e.g. 'bidding and scheduling platform')"
}}
"""
    models = ["gemini-3.6-flash", "gemini-3-flash-preview", "gemini-flash-lite-latest", "gemini-2.5-flash"]
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key.strip()}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
        }
        try:
            timeout_config = httpx.Timeout(15.0, connect=3.0)
            async with httpx.AsyncClient(timeout=timeout_config) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    cand = resp.json().get("candidates", [])
                    if cand:
                        parts = cand[0].get("content", {}).get("parts", [])
                        if parts:
                            raw_text = parts[0].get("text", "").strip()
                            if raw_text.startswith("```"):
                                raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.MULTILINE)
                                raw_text = re.sub(r"\s*```$", "", raw_text, flags=re.MULTILINE)
                            res = json.loads(raw_text.strip())
                            if isinstance(res, dict) and res.get("domain"):
                                return {
                                    "domain": str(res.get("domain", "")).strip(),
                                    "audience": str(res.get("audience", "")).strip(),
                                    "problem": str(res.get("problem", "")).strip(),
                                    "solution": str(res.get("solution", "")).strip(),
                                }
        except Exception as exc:
            logger.warning(f"Gemini decomposition call to {model} failed: {exc}")
            continue
    return None


# ============================================================
# Audience Inference
# ============================================================

def _infer_fallback_audience(
    result: Dict[str, Any],
    domain: str,
    idea: str = "",
    decomposed: Optional[Dict[str, str]] = None,
) -> str:
    """
    Infer specific, idea-relevant target audience for search results.
    Reuses seed audience extraction from idea + snippet matching to prevent 'General Users'.
    """
    title = str(result.get("title", "")).strip()
    content = str(result.get("content", "")).strip()
    full_text = f"{title} {content}".lower()

    # 1. Extract seed audiences from idea
    seed_audiences = []
    if idea:
        persona_patterns = [
            r"(?:for|enabling|helping|targeting|sold to|connecting|matches?)\s+([A-Za-z0-9\s-]+?)(?:,|\.|\band\b|through|with|by|$)",
            r"\b(general contractors|subcontractors|contractors|builders|pet owners|pet sitters|dog walkers|mobile groomers|fleet managers|plant operators|facility managers|homeowners|small businesses|merchants|retailers|students|teachers|patients|doctors|clinics)\b"
        ]
        action_verbs = {"leaving", "boarding", "overpaying", "finding", "searching", "buying", "using", "paying", "managing"}
        for pat in persona_patterns:
            for m in re.finditer(pat, idea, re.IGNORECASE):
                val = m.group(0 if m.lastindex is None else 1).strip()
                clean_val = re.sub(r"^(?:for|enabling|helping|targeting|sold to|connecting|matches?)\s+", "", val, flags=re.IGNORECASE).strip()
                first_word = clean_val.split()[0].lower() if clean_val.split() else ""
                if first_word in action_verbs:
                    continue
                if len(clean_val) > 3 and len(clean_val.split()) <= 5 and clean_val.lower() not in [s.lower() for s in seed_audiences]:
                    seed_audiences.append(clean_val.title())

    if decomposed and decomposed.get("audience"):
        aud_dec = decomposed.get("audience").title()
        if aud_dec and aud_dec.lower() not in [s.lower() for s in seed_audiences]:
            seed_audiences.append(aud_dec)

    # 2. Match seed audience terms against snippet
    for seed in seed_audiences:
        seed_words = [w for w in seed.lower().split() if len(w) > 3 and w not in STOP_WORDS and w not in GENERIC_BUSINESS_MODEL_TERMS]
        if any(w in full_text for w in seed_words):
            return seed

    # 3. Industry-specific domain mappings
    domain_audience_rules = [
        (["contractor", "subcontractor", "construction", "builder", "jobsite"], "General Contractors & Subcontractors"),
        (["pet", "dog", "cat", "sitter", "walker", "groomer"], "Pet Owners & Pet Care Providers"),
        (["fleet", "driver", "courier", "logistics", "freight"], "Logistics Operators & Fleet Managers"),
        (["patient", "doctor", "clinic", "hospital", "health"], "Healthcare Consumers & Medical Providers"),
        (["student", "teacher", "school", "course", "tutor"], "Students & Educational Professionals"),
        (["farmer", "crop", "agri", "vineyard"], "Agricultural Producers & Farm Managers"),
        (["data center", "cooling", "server", "thermal"], "Data Center Operations & Infrastructure Managers"),
    ]

    for keywords, target in domain_audience_rules:
        if any(kw in full_text for kw in keywords):
            return target

    if seed_audiences:
        return seed_audiences[0]

    if domain:
        clean_dom = domain.replace("marketplace", "").replace("services", "").replace("platform", "").strip().title()
        if clean_dom:
            return f"{clean_dom} Professionals & Users"

    return "Target Industry Buyers & Service Providers"


# ============================================================
# Gemini Result Validation
# ============================================================

def _validate_gemini_results(
    original_results: List[Dict[str, Any]],
    reranked_results: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Ensure reranked results are from the original search.
    """

    original_urls = {
        result.get("url")
        for result in original_results
        if result.get("url")
    }

    validated = []

    for result in reranked_results:

        url = result.get("url")

        if url in original_urls:

            validated.append(result)

    return validated


# ============================================================
# Result Filtering
# ============================================================

def _is_obviously_irrelevant(
    result: Dict[str, Any],
) -> bool:
    """
    Reject obviously irrelevant pages.
    """

    title = str(
        result.get(
            "title",
            "",
        )
    ).lower()

    content = str(
        result.get(
            "content",
            "",
        )
    ).lower()

    url = str(
        result.get(
            "url",
            "",
        )
    ).lower()

    full_text = (
        f"{title} {content} {url}"
    )

    # Wikipedia
    if "wikipedia.org" in url:
        return True

    # Gift-related pages
    gift_keywords = [
        "gift shop",
        "gift store",
        "gift ideas",
        "birthday gifts",
        "wedding gifts",
        "corporate gifts",
        "custom gifts",
        "personalized gifts",
        "personalised gifts",
    ]

    if any(
        keyword in full_text
        for keyword in gift_keywords
    ):

        return True

    # Shopping pages
    shopping_keywords = [
        "coupon",
        "discount code",
        "shop now",
        "free download",
        "giveaway",
    ]

    if any(
        keyword in full_text
        for keyword in shopping_keywords
    ):

        return True

    return False


# ============================================================
# Main Web Search Agent
# ============================================================

async def run_web_search_agent(
    idea: str,
    domain: str = "",
    audience: str = "",
    validation_type: str = "all",
) -> Dict[str, Any]:
    """
    Main Web Search Agent.

    Flow:

        Startup Idea
              ↓
        Decomposition
              ↓
        Query Generation
              ↓
        Tavily
              ↓
        DDGS fallback
              ↓
        Deduplication
              ↓
        Relevance Ranking
              ↓
        Filtering
              ↓
        Target Audience
              ↓
        Final Results

    Gemini is intentionally not part of the active flow.
    """

    try:

        _load_env_if_needed()
        cleaned_idea = clean_text(idea)

        if not cleaned_idea:
            raise ValueError(
                "Startup idea cannot be empty"
            )

        if len(cleaned_idea) < 10:

            raise ValueError(
                "Startup idea is too short to analyze meaningfully"
            )

        # ----------------------------------------------------
        # Validate search type
        # ----------------------------------------------------

        allowed_types = {
            "all",
            "market",
            "competition",
            "customers",
            "business",
            "risks",
            "scientific",
            "technical",
            "regulatory",
        }

        validation_type = (
            validation_type or "all"
        ).lower().strip()

        if validation_type not in allowed_types:

            validation_type = "all"

        # ----------------------------------------------------
        # Decompose idea
        # ----------------------------------------------------

        gemini_dec = await _decompose_with_gemini_async(cleaned_idea)
        if gemini_dec:
            decomposed = gemini_dec
            logger.info("Startup idea decomposition via Gemini: %s", decomposed)
        else:
            decomposed = decompose_startup_idea(
                cleaned_idea,
                domain=domain,
                audience=audience,
            )
            logger.info("Startup idea decomposition via Heuristic: %s", decomposed)

        # ----------------------------------------------------
        # Generate queries
        # ----------------------------------------------------

        queries = generate_search_queries(
            decomposed,
            validation_type,
        )

        logger.info(
            "Generated search queries: %s",
            queries,
        )

        if not queries:

            return {
                "results": []
            }

        # ----------------------------------------------------
        # Execute searches concurrently
        # ----------------------------------------------------

        tasks = [

            _execute_single_query(
                query,
                max_results=SEARCH_RESULTS_PER_QUERY,
            )

            for query in queries
        ]

        search_batches = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        # ----------------------------------------------------
        # Collect results
        # ----------------------------------------------------

        all_results = []

        for batch in search_batches:

            if isinstance(
                batch,
                Exception,
            ):

                logger.warning(
                    "Search batch failed: %s",
                    batch,
                )

                continue

            if not isinstance(
                batch,
                list,
            ):

                continue

            all_results.extend(batch)

        logger.info(
            "Collected %d raw search results",
            len(all_results),
        )

        if not all_results:

            logger.warning(
                "No search results returned "
                "from Tavily or DDGS."
            )

            return {
                "results": []
            }

        # ----------------------------------------------------
        # Deduplicate URLs
        # ----------------------------------------------------

        unique_results = []

        seen_urls = set()

        for result in all_results:

            url = str(
                result.get(
                    "url",
                    "",
                )
            ).strip()

            if not url:
                continue

            normalized_url = (
                url.lower().rstrip("/")
            )

            if normalized_url in seen_urls:
                continue

            seen_urls.add(
                normalized_url
            )

            unique_results.append(
                result
            )

        logger.info(
            "Unique search results: %d",
            len(unique_results),
        )

        # ----------------------------------------------------
        # Remove obvious irrelevant pages BEFORE ranking
        # ----------------------------------------------------

        prefiltered_results = []

        for result in unique_results:

            if _is_obviously_irrelevant(
                result
            ):

                continue

            prefiltered_results.append(
                result
            )

        logger.info(
            "Results after obvious filtering: %d",
            len(prefiltered_results),
        )

        # ----------------------------------------------------
        # Rank results
        # ----------------------------------------------------

        ranked_results = _heuristic_rerank(
            prefiltered_results,
            decomposed,
        )

        # ----------------------------------------------------
        # Final relevance filtering
        # ----------------------------------------------------

        filtered_results = []

        for result in ranked_results:

            score = result.get(
                "_relevance_score",
                0,
            )

            if score < -10:
                continue

            filtered_results.append(
                result
            )

        # ----------------------------------------------------
        # Keep top 10
        # ----------------------------------------------------

        filtered_results = filtered_results[
            :MAX_TOTAL_RESULTS
        ]

        logger.info(
            "Results after relevance filtering: %d",
            len(filtered_results),
        )

        # ----------------------------------------------------
        # Add target audience
        # ----------------------------------------------------

        final_results = []

        explicit_audience = clean_text(
            audience
        )

        for result in filtered_results:

            result_copy = dict(result)

            result_copy.pop(
                "_relevance_score",
                None,
            )

            # IMPORTANT:
            # If user supplied target customer,
            # always preserve it.
            if explicit_audience:

                result_copy[
                    "target_audience"
                ] = explicit_audience

            else:

                existing_audience = (
                    result_copy.get(
                        "target_audience"
                    )
                )

                if existing_audience and existing_audience not in ("General Users", "Potential Customers"):
                    result_copy["target_audience"] = existing_audience
                else:
                    result_copy["target_audience"] = _infer_fallback_audience(
                        result_copy,
                        domain=decomposed.get("domain", ""),
                        idea=cleaned_idea,
                        decomposed=decomposed,
                    )

            final_results.append(
                result_copy
            )

        # ----------------------------------------------------
        # Return
        # ----------------------------------------------------

        logger.info(
            "Returning %d final search results",
            len(final_results),
        )

        return {
            "results": final_results
        }

    except ValueError as exc:

        logger.warning(
            "Invalid search request: %s",
            exc,
        )

        return {
            "results": []
        }

    except Exception as exc:

        logger.exception(
            "Web Search Agent failed: %s",
            exc,
        )

        return {
            "results": []
        }


# ============================================================
# Local Test
# ============================================================

if __name__ == "__main__":

    async def main():

        idea = (
            "AI platform that provides personalized "
            "fitness plans for users"
        )

        result = await run_web_search_agent(
            idea=idea,
            domain="fitness",
            audience=(
                "college students and working professionals"
            ),
            validation_type="all",
        )

        from pprint import pprint

        pprint(result)

    asyncio.run(main())