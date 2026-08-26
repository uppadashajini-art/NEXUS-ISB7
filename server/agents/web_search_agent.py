import asyncio
import json
import logging
import os
import re
import warnings
from typing import Any, Dict, List, Set

# Suppress deprecation/rename runtime warnings from duckduckgo_search if present
warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")

logger = logging.getLogger(__name__)

# Common filler words to filter when extracting keyword bases
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "can",
    "could", "should", "would", "will", "shall", "platform", "app", "application",
    "website", "tool", "service", "system", "solution", "based", "powered",
    "startup", "business", "product", "idea", "aimed", "helping", "people",
    "users", "clients", "companies", "designed"
}

MAX_TOTAL_RESULTS = 10


def _load_env_if_needed() -> None:
    """
    Attempt to load .env from the server root if environment variables are missing.
    Self-contained using standard library only.
    """
    if not os.getenv("TAVILY_API_KEY"):
        env_paths = [
            os.path.join(os.path.dirname(__file__), "..", ".env"),
            os.path.join(os.getcwd(), ".env"),
            os.path.join(os.getcwd(), "server", ".env")
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


def extract_query_base(idea: str) -> str:
    """
    Extract key terms from a startup idea string.
    Falls back to the raw idea if extraction yields fewer than 3 characters.
    """
    if not idea or not isinstance(idea, str):
        return ""
    
    cleaned = re.sub(r"[^\w\s-]", " ", idea)
    words = cleaned.strip().split()
    meaningful_words = [w for w in words if w.lower() not in STOP_WORDS and len(w) > 1]
    query_base = " ".join(meaningful_words).strip()
    
    # Fallback to raw idea string if extraction yields < 3 chars
    if len(query_base) < 3:
        query_base = idea.strip()
        
    return query_base


def generate_search_queries(idea: str) -> List[str]:
    """
    Generate 4-5 relevant market research queries from the idea.
    """
    base = extract_query_base(idea)
    if not base:
        return []
    
    return [
        f"{base} competitors",
        f"{base} market trends",
        f"{base} apps platforms",
        f"{base} pricing business model",
        f"{base} customer problems"
    ]


def _normalize_url(url: str) -> str:
    """
    Normalize URLs for reliable deduplication.
    """
    if not url:
        return ""
    return url.strip().rstrip("/")


def _search_tavily(query: str, api_key: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Execute search via tavily-python SDK.
    """
    from tavily import TavilyClient
    client = TavilyClient(api_key=api_key)
    response = client.search(query=query, max_results=max_results)
    
    raw_results = response.get("results", []) if isinstance(response, dict) else []
    cleaned_results: List[Dict[str, str]] = []
    
    for item in raw_results:
        title = item.get("title", "") or ""
        url = item.get("url", "") or ""
        content = item.get("content", "") or item.get("raw_content", "") or ""
        if url:
            cleaned_results.append({
                "title": title.strip(),
                "url": url.strip(),
                "content": content.strip()
            })
            
    return cleaned_results


def _search_duckduckgo(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Execute fallback search via duckduckgo-search / ddgs package.
    Tries multiple backends ('lite', 'auto', 'html') to maximize reliability.
    """
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS

    raw_results = []
    for backend in ("lite", "auto", "html"):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, backend=backend, max_results=max_results))
                if results:
                    raw_results = results
                    break
        except Exception:
            continue

    cleaned_results: List[Dict[str, str]] = []
    for item in raw_results:
        title = item.get("title", "") or ""
        url = item.get("href", "") or item.get("url", "") or ""
        content = item.get("body", "") or item.get("content", "") or ""
        if url:
            cleaned_results.append({
                "title": title.strip(),
                "url": url.strip(),
                "content": content.strip()
            })
            
    return cleaned_results


async def _execute_single_query(query: str, tavily_api_key: str | None) -> List[Dict[str, str]]:
    """
    Execute search for a single query using Tavily (if key present),
    falling back to DuckDuckGo if Tavily fails or key is missing.
    """
    if tavily_api_key:
        try:
            results = await asyncio.to_thread(_search_tavily, query, tavily_api_key)
            if results:
                return results
        except Exception as e:
            logger.warning(f"Tavily search failed for query '{query}': {e}. Falling back to DuckDuckGo.")
    
    # Fallback to DuckDuckGo
    try:
        return await asyncio.to_thread(_search_duckduckgo, query)
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed for query '{query}': {e}")
        return []


async def run_web_search_agent(idea: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Asynchronous web search agent for startup validation.
    
    Args:
        idea: Startup idea description string.
        
    Returns:
        Dict with shape {"results": [{"title": "", "url": "", "content": ""}]}
        Guaranteed to return {"results": []} on total failure (never raises).
    """
    try:
        _load_env_if_needed()
        
        if not idea or not isinstance(idea, str) or not idea.strip():
            return {"results": []}
        
        queries = generate_search_queries(idea)
        if not queries:
            return {"results": []}
        
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if tavily_api_key:
            tavily_api_key = tavily_api_key.strip()
            if not tavily_api_key:
                tavily_api_key = None
        
        # Concurrently execute queries via Tavily (or DuckDuckGo fallback)
        search_tasks = [_execute_single_query(q, tavily_api_key) for q in queries]
        query_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        seen_urls: Set[str] = set()
        aggregated_results: List[Dict[str, str]] = []
        
        for batch in query_results:
            if isinstance(batch, Exception) or not batch:
                continue
            for item in batch:
                raw_url = item.get("url", "")
                norm_url = _normalize_url(raw_url)
                if norm_url and norm_url not in seen_urls:
                    seen_urls.add(norm_url)
                    aggregated_results.append({
                        "title": item.get("title", ""),
                        "url": raw_url,
                        "content": item.get("content", "")
                    })
                    if len(aggregated_results) >= MAX_TOTAL_RESULTS:
                        break
            if len(aggregated_results) >= MAX_TOTAL_RESULTS:
                break
                
        return {"results": aggregated_results}

    except Exception as e:
        logger.error(f"Unexpected error in run_web_search_agent: {e}")
        return {"results": []}


if __name__ == "__main__":
    sample_idea = "AI based platform for personalized fitness plans"
    print(f"Testing Web Search Agent with idea: '{sample_idea}'\n")
    output = asyncio.run(run_web_search_agent(sample_idea))
    print("Result output:")
    print(json.dumps(output, indent=2))
    print(f"\nTotal results returned: {len(output.get('results', []))}")
