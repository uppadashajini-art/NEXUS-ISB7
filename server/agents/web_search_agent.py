import asyncio
import json
import logging
import os
import re
import urllib.parse
import warnings
from typing import Any, Dict, List, Set

import httpx

# Suppress deprecation/rename runtime warnings from duckduckgo_search if present
warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")

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
    "make", "use", "using", "uses"
}

VALID_VALIDATION_TYPES = {
    "all", "market", "competition", "customers", "business", "risks"
}

MAX_TOTAL_RESULTS = 10


def _load_env_if_needed() -> None:
    """
    Attempt to load .env from the server root if environment variables are missing.
    """
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


def clean_text(text: str) -> str:
    """Strip parentheses, brackets, special characters, and excess whitespace."""
    if not text:
        return ""
    # remove parenthetical phrases like (or E-retailers)
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"\[[^\]]*\]", "", text)
    text = re.sub(r"[^\w\s-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_key_phrases(text: str, max_terms: int = 4) -> str:
    """Extract the most meaningful non-stop keywords from text."""
    cleaned = clean_text(text)
    words = cleaned.split()
    meaningful = [w for w in words if w.lower() not in STOP_WORDS and len(w) > 2]
    seen = set()
    result = []
    for w in meaningful:
        wl = w.lower()
        if wl not in seen:
            seen.add(wl)
            result.append(w)
            if len(result) >= max_terms:
                break
    return " ".join(result)


def decompose_startup_idea(idea: str, domain: str = "", audience: str = "") -> Dict[str, str]:
    """
    Decompose complex or casual startup descriptions into 4 distinct, clean search vectors:
    domain, audience, core problem, and proposed innovation mechanism.
    """
    cleaned_idea = clean_text(idea)
    
    # 1. Domain Vector
    domain_vec = extract_key_phrases(domain, max_terms=3) if domain else ""
    if not domain_vec:
        domain_vec = extract_key_phrases(cleaned_idea[:120], max_terms=3)
    
    # 2. Audience Vector
    audience_vec = extract_key_phrases(audience, max_terms=3) if audience else ""
    if not audience_vec:
        aud_match = re.search(r"(?:for|designed for|targeting|aimed at)\s+([A-Za-z0-9\s-]+?)(?:\.|\,|$)", idea, re.IGNORECASE)
        if aud_match:
            audience_vec = extract_key_phrases(aud_match.group(1), max_terms=3)
            
    # 3. Problem & Value Vector (look for eliminate, reduce, cost, friction, problem, loss)
    problem_words = []
    for m in re.finditer(r"(?:eliminat\w*|reduc\w*|cost\w*|expens\w*|problem\w*|friction|wast\w*|loss\w*|challeng\w*)\s+([A-Za-z0-9\s-]+?)(?:\.|\,|$)", idea, re.IGNORECASE):
        problem_words.extend(extract_key_phrases(m.group(1), max_terms=3).split())
    problem_vec = " ".join(list(dict.fromkeys(problem_words))[:4])
    if not problem_vec:
        problem_vec = "cost margin loss friction"
        
    # 4. Mechanism / Innovation Vector (look for algorithms, hubs, micro, auctions, automated)
    solution_words = []
    for m in re.finditer(r"(?:combining|utilizing|using|with|via|through|platform|network)\s+([A-Za-z0-9\s-]+?)(?:\.|\,|$)", idea, re.IGNORECASE):
        solution_words.extend(extract_key_phrases(m.group(1), max_terms=3).split())
    solution_vec = " ".join(list(dict.fromkeys(solution_words))[:4])
    if not solution_vec:
        solution_vec = extract_key_phrases(cleaned_idea, max_terms=4)
        
    return {
        "domain": domain_vec if domain_vec else "e-commerce logistics",
        "audience": audience_vec,
        "problem": problem_vec,
        "solution": solution_vec
    }


def generate_search_queries(decomposed: Dict[str, str], validation_type: str = "all") -> List[str]:
    """
    Generate clean, surgical search queries without long-string noise or boolean artifacts.
    """
    d = decomposed.get("domain", "")
    a = decomposed.get("audience", "")
    p = decomposed.get("problem", "")
    s = decomposed.get("solution", "")
    
    core = f"{d} {a}".strip() if a else d
    
    query_map = {
        "market": [
            f"{d} market size USD billion CAGR forecast",
            f"{d} total addressable market TAM spending growth",
            f"{s} industry valuation trends forecast",
            f"{d} market research report statistics"
        ],
        "competition": [
            f"{d} top competitors market landscape comparison",
            f"{s} competing startups platforms alternatives",
            f"{d} competitor pricing feature comparison",
            f"{s} alternative solutions market leaders review"
        ],
        "customers": [
            f"{core} {p} customer pain points benchmark",
            f"{a} {d} daily workflow friction complaints",
            f"{d} {p} financial impact wasted hours statistics",
            f"{core} willingness to pay ROI direct solution"
        ],
        "business": [
            f"{d} B2B SaaS pricing models subscription unit economics",
            f"{s} monetization strategy revenue model customer willingness to pay",
            f"{d} customer acquisition cost CAC LTV benchmarks",
            f"{s} enterprise licensing contract value ARR"
        ],
        "risks": [
            f"{d} startup failure reasons common pitfalls risks",
            f"{s} regulatory compliance legal liabilities risks",
            f"{core} customer adoption resistance churn operational challenges",
            f"{s} security vulnerability architecture failure risks"
        ]
    }
    
    if validation_type == "all" or validation_type not in query_map:
        return [
            query_map["market"][0],
            query_map["competition"][0],
            query_map["customers"][0],
            query_map["business"][0],
            query_map["risks"][0]
        ]
    return query_map[validation_type]


def _normalize_url(url: str) -> str:
    """
    Normalize URLs by stripping tracking parameters, query artifacts, and trailing slashes.
    """
    if not url:
        return ""
    try:
        parsed = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qsl(parsed.query)
        filtered_params = [
            (k, v) for k, v in query_params 
            if not k.startswith("utm_") and k not in ("ref", "fbclid", "gclid", "source")
        ]
        new_query = urllib.parse.urlencode(filtered_params)
        normalized = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path.rstrip("/"),
            "",
            new_query,
            ""
        ))
        return normalized.rstrip("/")
    except Exception:
        return url.strip().rstrip("/")


def _search_tavily(query: str, api_key: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Execute search via tavily-python SDK.
    """
    from tavily import TavilyClient
    client = TavilyClient(api_key=api_key)
    response = client.search(query=query, max_results=max_results, search_depth="advanced")
    
    raw_results = response.get("results", []) if isinstance(response, dict) else []
    cleaned_results: List[Dict[str, str]] = []
    
    for item in raw_results:
        title = item.get("title", "") or ""
        url = item.get("url", "") or ""
        content = item.get("content", "") or item.get("raw_content", "") or ""
        if url and (title or content):
            cleaned_results.append({
                "title": title.strip(),
                "url": url.strip(),
                "content": re.sub(r"\s+", " ", content).strip()
            })
            
    return cleaned_results


async def _search_ddg_async(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Asynchronously execute search via DuckDuckGo without blocking the event loop.
    """
    def _sync_ddg():
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                return list(ddgs.text(query, max_results=max_results))
        except Exception as e:
            logger.warning(f"DuckDuckGo search error for query '{query}': {e}")
            return []
            
    loop = asyncio.get_running_loop()
    raw = await loop.run_in_executor(None, _sync_ddg)
    cleaned = []
    for item in raw:
        title = item.get("title", "") or ""
        url = item.get("href", "") or item.get("url", "") or ""
        body = item.get("body", "") or item.get("snippet", "") or ""
        if url and (title or body):
            cleaned.append({
                "title": title.strip(),
                "url": url.strip(),
                "content": re.sub(r"\s+", " ", body).strip()
            })
    return cleaned


async def _execute_single_query(query: str, tavily_api_key: str | None) -> List[Dict[str, str]]:
    """
    Execute a single search query preferring Tavily, falling back to DuckDuckGo.
    """
    if tavily_api_key:
        try:
            loop = asyncio.get_running_loop()
            results = await loop.run_in_executor(None, _search_tavily, query, tavily_api_key, 5)
            if results:
                return results
        except Exception as e:
            logger.warning(f"Tavily search failed for '{query}': {e}. Falling back to DuckDuckGo.")
            
    try:
        return await _search_ddg_async(query, max_results=5)
    except Exception as e:
        logger.error(f"DuckDuckGo fallback also failed for '{query}': {e}")
        return []


def _build_gemini_prompt(
    idea: str,
    domain: str | None,
    target_customer: str | None,
    validation_type: str,
    results: List[Dict[str, str]]
) -> str:
    """
    Build structured prompt for Gemini synthesis, relevance verification, and re-ranking
    enforcing rigorous 20-point evidence quality, anti-bias, and validation rules.
    """
    domain_text = domain.strip() if domain and domain.strip() else "Not specified"
    audience_text = target_customer.strip() if target_customer and target_customer.strip() else "Not specified"
    compact_results = []
    for r in results:
        compact_results.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": (r.get("content", "") or "")[:350]
        })
    
    focus_guidelines = {
        "market": "STRICT MARKET DEMAND VALIDATION:\n"
                  "- Do NOT validate generic tech optimism, broad industry hype, or vague claims of growth.\n"
                  "- ONLY validate and prioritize evidence demonstrating exact market valuation ($ USD), CAGR growth projections, TAM, and verified budget allocations.",

        "competition": "STRICT COMPETITIVE LANDSCAPE VALIDATION:\n"
                       "- Do NOT validate generic tech directory listings or unrelated tech giants.\n"
                       "- ONLY validate and prioritize evidence demonstrating direct competitors, product feature gaps, pricing comparisons, limitations, and defensible moats.",

        "customers": "STRICT TARGET CUSTOMER PROBLEM VALIDATION:\n"
                     "- Do NOT validate general preferences (e.g. generic desire for automation or efficiency) unless explicitly connected to the core problem.\n"
                     "- ONLY validate evidence showing the customer experiences the EXACT problem frequently with MEASURABLE COST / IMPACT.",

        "business": "STRICT BUSINESS & MONETIZATION VALIDATION:\n"
                    "- Do NOT validate speculative revenue claims or unproven free-tier models.\n"
                    "- ONLY validate proven pricing models (usage, seat, value-share), customer Willingness to Pay (WTP), and unit economics (LTV/CAC).",

        "risks": "STRICT RISK & PITFALL VALIDATION:\n"
                 "- Do NOT validate generic philosophical risks.\n"
                 "- ONLY validate specific regulatory/legal liabilities (GDPR, HIPAA, SOC 2), technical feasibility/security bottlenecks, and proven failure pitfalls.",

        "all": "STRICT 360-DEGREE STARTUP VALIDATION:\n"
               "- Select and rank the highest-precision evidence across Market Size ($ and CAGR), Direct Competitors, Exact Customer Pain, Pricing Models, and Critical Regulatory/Failure Risks."
    }
    
    specific_instruction = focus_guidelines.get(validation_type, focus_guidelines["all"])
    
    return f"""You are an elite AI Startup Research & Evidence Quality Analyst.
Your objective is to strictly evaluate EVIDENCE QUALITY, eliminate false positives, avoid market-size bias, and provide the most accurate, evidence-backed assessment possible.

PROPOSITION DETAILS:
- Startup Idea: {idea}
- Domain / Industry: {domain_text}
- Target Audience / Customer: {audience_text}
- Validation Focus Area: {validation_type.upper()}

FOCUS GUIDELINE:
{specific_instruction}

CORE EVIDENCE EVALUATION RULES:
1. Extract the primary claim from each candidate source.
2. Classify evidence type: Market Size | Problem Validation | Customer Pain | Willingness To Pay | Competition | Business Potential | Risk | Industry Context.
3. Determine evidence relevance & strength:
   - Direct Evidence (1.0) = explicitly validates the startup idea / exact problem
   - Strong Indirect Evidence (0.75) = validates a closely related problem
   - Weak Indirect Evidence (0.50) = supports surrounding context only
   - Contextual Evidence (0.25) = general industry background
   - Noise (0.0) = not useful / promotional spam
4. Determine source quality: Academic/Gov/Industry Research Firm > Public Company Report > Industry Publication > Company Website > Blog/Social.
5. ANTI-BIAS GUARDRAILS:
   - NEVER treat industry growth as proof of customer demand.
   - NEVER treat market size as proof of problem existence.
   - NEVER treat customer interest as proof of willingness to pay.
   - NEVER treat a related industry problem as validation of the startup's exact problem.
6. A source must be scored based on how DIRECTLY it validates the startup's core problem, not just matching the industry.
7. If evidence only validates the industry and not the startup idea itself, explicitly state:
   "This source validates the market context but does not directly validate the startup's core problem."
8. Include contradictory or risk-challenging evidence when found—do not hide real obstacles.
9. Weighting priorities: Problem Validation (35%) > Customer Pain (25%) > Willingness To Pay (15%) > Market Size (10%) > Competition (10%) > Risks (5%).
10. Final selection priority: Direct Evidence > Strong Indirect Evidence > Contextual Evidence.

CANDIDATE WEB RESEARCH RESULTS:
{json.dumps(compact_results, indent=2)}

YOUR OBJECTIVES:
1. Filter out pure promotional spam or off-topic noise.
2. Re-order the results so that highest-strength Direct Evidence matching '{validation_type}' appears first.
3. For each source, synthesize a crisp 1-2 sentence evidence-backed finding following: [Evidence Classification] Specific Claim → Core Problem Takeaway.
4. Strictly PRESERVE the exact 'title' and 'url' from the candidate list. DO NOT invent or alter URLs.
5. Return ONLY a valid JSON array of objects with keys: "title", "url", "content".

Output JSON format:
[
  {{
    "title": "Exact Title",
    "url": "Exact URL",
    "content": "Actionable, evidence-backed takeaway directly tying the finding to the startup's core problem and validation focus."
  }}
]"""


def _score_source_quality_and_relevance(
    item: Dict[str, str],
    decomposed: Dict[str, str],
    validation_type: str
) -> float:
    """
    Score source candidates deterministically based on domain authority,
    metric density, and vector relevance.
    """
    score = 0.0
    url = (item.get("url") or "").lower()
    title = (item.get("title") or "").lower()
    content = (item.get("content") or "").lower()
    full_text = f"{title} {content}"

    # 1. Authoritative Domain Tier (+30 pts)
    high_authority_domains = [
        "mckinsey", "gartner", "statista", "forbes", "hbr.org", "techcrunch",
        "bloomberg", "reuters", "coresight", "retaildive", "supplychaindive",
        "wsj", "imarcgroup", "polarismarketresearch", "dataintelo", "grandviewresearch",
        "marketsandmarkets", "pwc", "deloitte", "bain", "accenture", "globenewswire",
        "prnewswire", "businesswire", "sciencedirect", "springer", "nature.com"
    ]
    for d in high_authority_domains:
        if d in url:
            score += 30.0
            break

    # 2. Key Vector Relevance (+20 pts)
    for k in ["domain", "problem", "solution", "audience"]:
        vec_words = decomposed.get(k, "").lower().split()
        matches = sum(1 for w in vec_words if w and w in full_text)
        score += matches * 4.0

    # 3. Quantitative / Hard Metric Density (+15 pts)
    metric_patterns = [r"\d+%", r"\$\s*\d+", r"\bCAGR\b", r"\bbillion\b", r"\bmillion\b", r"\b202[4-9]\b"]
    for pat in metric_patterns:
        if re.search(pat, full_text, re.IGNORECASE):
            score += 3.5

    # 4. Validation Focus Alignment (+15 pts)
    focus_keywords = {
        "market": ["market size", "cagr", "valuation", "forecast", "tam", "growth"],
        "competition": ["competitor", "alternative", "vs", "comparison", "feature", "pricing"],
        "customers": ["pain", "friction", "cost", "complaint", "hours", "bottleneck", "loss", "return"],
        "business": ["pricing", "subscription", "monetization", "margin", "revenue", "cac", "ltv"],
        "risks": ["risk", "compliance", "penalty", "failure", "liability", "pitfall", "gdpr", "hipaa", "fraud"],
        "all": ["market", "competitor", "cost", "pricing", "risk"]
    }
    for kw in focus_keywords.get(validation_type, focus_keywords["all"]):
        if kw in full_text:
            score += 3.0

    # 5. Low-Quality Spam Penalty (-30 pts)
    spam_indicators = ["login", "sign in", "privacy policy", "cookie policy", "terms of service", "404 not found"]
    for sp in spam_indicators:
        if sp in title:
            score -= 30.0

    return score


def _heuristic_rerank(
    results: List[Dict[str, str]],
    decomposed: Dict[str, str],
    validation_type: str
) -> List[Dict[str, str]]:
    """Rerank candidates deterministically based on evidence strength and domain authority."""
    scored = []
    for r in results:
        s = _score_source_quality_and_relevance(r, decomposed, validation_type)
        scored.append((s, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored]


def _validate_gemini_results(
    gemini_output_text: str,
    original_results: List[Dict[str, str]]
) -> List[Dict[str, str]] | None:
    """
    Defensively validate Gemini's JSON output ensuring only genuine input URLs are used.
    """
    try:
        text = gemini_output_text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
            text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
        
        parsed = json.loads(text.strip())
        if not isinstance(parsed, list):
            return None
        
        original_urls = {_normalize_url(r.get("url", "")) for r in original_results if r.get("url")}
        valid_items: List[Dict[str, str]] = []
        
        for item in parsed:
            if not isinstance(item, dict):
                continue
            url = str(item.get("url", "")).strip()
            norm_url = _normalize_url(url)
            if norm_url in original_urls and url:
                valid_items.append({
                    "title": str(item.get("title", "")).strip(),
                    "url": url,
                    "content": str(item.get("content", "")).strip()
                })
        
        if valid_items:
            return valid_items
        return None
    except Exception as e:
        logger.warning(f"Failed to parse or validate Gemini output: {e}")
        return None


async def _rerank_with_gemini(
    idea: str,
    domain: str | None,
    target_customer: str | None,
    validation_type: str,
    results: List[Dict[str, str]],
    api_key: str
) -> List[Dict[str, str]]:
    """
    Asynchronously invoke Gemini API to verify accuracy, synthesize takeaways, and re-rank results
    with multi-model fallbacks.
    """
    if not results or not api_key:
        return results
        
    prompt = _build_gemini_prompt(idea, domain, target_customer, validation_type, results)
    
    models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.5-flash-lite"]
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
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        content_parts = candidates[0].get("content", {}).get("parts", [])
                        if content_parts:
                            raw_text = content_parts[0].get("text", "")
                            validated = _validate_gemini_results(raw_text, results)
                            if validated:
                                return validated
        except Exception as e:
            logger.warning(f"Gemini model '{model}' call error: {e}")
            continue
            
    return results


async def run_web_search_agent(
    idea: str,
    domain: str | None = None,
    target_customer: str | None = None,
    validation_type: str = "all"
) -> Dict[str, List[Dict[str, str]]]:
    """
    Asynchronous web search & intelligence validation agent.
    
    Args:
        idea: Startup idea description string.
        domain: Optional startup domain/industry.
        target_customer: Optional customer segment.
        validation_type: Focus area ('all', 'market', 'competition', 'customers', 'business', 'risks').
        
    Returns:
        Dict with shape {"results": [{"title": "", "url": "", "content": ""}]}
    """
    try:
        _load_env_if_needed()
        
        if not idea or not isinstance(idea, str) or not idea.strip():
            return {"results": []}
        
        if validation_type not in VALID_VALIDATION_TYPES:
            validation_type = "all"
        
        # 1. Intelligent Decomposition
        decomposed = decompose_startup_idea(
            idea=idea,
            domain=domain or "",
            audience=target_customer or ""
        )
        
        # 2. Smart Query Generation
        queries = generate_search_queries(decomposed, validation_type)
        if not queries:
            return {"results": []}
        
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if tavily_api_key:
            tavily_api_key = tavily_api_key.strip()
            if not tavily_api_key:
                tavily_api_key = None
        
        # 3. Concurrent Search Execution
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
                    if len(aggregated_results) >= MAX_TOTAL_RESULTS * 2:
                        break
            if len(aggregated_results) >= MAX_TOTAL_RESULTS * 2:
                break
        
        # 4. Deterministic Pre-Ranking
        aggregated_results = _heuristic_rerank(aggregated_results, decomposed, validation_type)
        
        # 5. Gemini 20-Point Synthesis & Verification (with fallbacks)
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key and gemini_api_key.strip() and aggregated_results:
            aggregated_results = await _rerank_with_gemini(
                idea=idea,
                domain=domain,
                target_customer=target_customer,
                validation_type=validation_type,
                results=aggregated_results,
                api_key=gemini_api_key.strip()
            )
                
        return {"results": aggregated_results[:MAX_TOTAL_RESULTS]}

    except Exception as e:
        logger.error(f"Unexpected error in run_web_search_agent: {e}")
        return {"results": []}


if __name__ == "__main__":
    sample_idea = "AI platform that turns recorded college lectures into interactive quizzes and summary flashcards"
    sample_customer = "college students and university professors"
    sample_validation_type = "risks"
    
    print(f"Testing Web Search Agent with:")
    print(f"- Idea: '{sample_idea}'")
    print(f"- Target Customer: '{sample_customer}'")
    print(f"- Validation Type: '{sample_validation_type}'\n")
    
    output = asyncio.run(run_web_search_agent(
        idea=sample_idea,
        target_customer=sample_customer,
        validation_type=sample_validation_type
    ))
    
    print("Result output:")
    print(json.dumps(output, indent=2))
    print(f"\nTotal results returned: {len(output.get('results', []))}")
