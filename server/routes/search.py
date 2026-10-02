from inspect import signature
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from server.models.search import SearchRequest, SearchResponse


# ---------------------------------------------------------
# Import Web Search Agent
# ---------------------------------------------------------
try:
    from server.agents.web_search_agent import run_web_search_agent
except ImportError:
    try:
        from server.agents import run_web_search_agent
    except ImportError:

        async def run_web_search_agent(
            idea: str,
            domain: str | None = None,
            audience: str | None = None,
            target_customer: str | None = None,
            validation_type: str = "all",
        ) -> dict:
            """
            Fallback mock agent used only when the real
            web search agent cannot be imported.
            """
            return {
                "results": [
                    {
                        "title": "Mock Search Result",
                        "url": "https://example.com",
                        "content": (
                            f"Mock search result for startup idea: {idea}"
                        ),
                        "target_audience": (
                            target_customer or audience
                        ),
                    }
                ]
            }


router = APIRouter()


# ---------------------------------------------------------
# Helper: safely call Web Search Agent
# ---------------------------------------------------------
async def _call_web_search_agent(
    idea: str,
    domain: str | None = None,
    target_customer: str | None = None,
    validation_type: str = "all",
) -> Dict[str, Any]:
    """
    Calls run_web_search_agent using only the parameters
    supported by the currently installed agent.

    This keeps the API route compatible with different
    versions of web_search_agent.py.
    """

    possible_arguments = {
        "idea": idea,
        "domain": domain,
        "audience": target_customer,
        "target_customer": target_customer,
        "validation_type": validation_type,
    }

    try:
        supported_parameters = signature(
            run_web_search_agent
        ).parameters

        agent_arguments = {
            name: value
            for name, value in possible_arguments.items()
            if name in supported_parameters
        }

        # idea is required by the search agent.
        if "idea" not in agent_arguments:
            raise RuntimeError(
                "run_web_search_agent must accept an 'idea' parameter."
            )

        result = await run_web_search_agent(**agent_arguments)

        if result is None:
            return {"results": []}

        if not isinstance(result, dict):
            return {"results": []}

        return result

    except TypeError:
        # Compatibility fallback for agents that use
        # a simple (idea, domain) signature.
        try:
            result = await run_web_search_agent(
                idea=idea,
                domain=domain,
            )

            if isinstance(result, dict):
                return result

            return {"results": []}

        except Exception as exc:
            raise RuntimeError(
                f"Web search agent failed: {exc}"
            ) from exc


# ---------------------------------------------------------
# POST /api/search
# ---------------------------------------------------------
@router.post(
    "/api/search",
    response_model=SearchResponse,
)
async def search_idea(request: SearchRequest):
    """
    Search the web for information relevant to a startup idea.
    """

    # -----------------------------------------------------
    # Clean input
    # -----------------------------------------------------
    idea = request.idea.strip()

    domain = (
        request.domain.strip()
        if request.domain
        else None
    )

    target_customer = (
        request.target_customer.strip()
        if request.target_customer
        else None
    )

    validation_type = (
        request.validation_type.strip().lower()
        if request.validation_type
        else "all"
    )

    # -----------------------------------------------------
    # Validate startup idea
    # -----------------------------------------------------
    if not idea:
        raise HTTPException(
            status_code=400,
            detail="Idea cannot be empty or just whitespace.",
        )

    if len(idea) < 3:
        raise HTTPException(
            status_code=400,
            detail="Idea is too short to validate.",
        )

    # -----------------------------------------------------
    # Validate validation_type
    # -----------------------------------------------------
    allowed_validation_types = {
        "all",
        "market",
        "competition",
        "customers",
        "business",
        "risks",
    }

    if validation_type not in allowed_validation_types:
        validation_type = "all"

    # -----------------------------------------------------
    # Call Web Search Agent
    # -----------------------------------------------------
    try:
        agent_response = await _call_web_search_agent(
            idea=idea,
            domain=domain,
            target_customer=target_customer,
            validation_type=validation_type,
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Search agent failed to process the request."
            ),
        ) from exc

    # -----------------------------------------------------
    # Normalize response
    # -----------------------------------------------------
    if not agent_response:
        return SearchResponse(results=[])

    results = agent_response.get("results", [])

    if not isinstance(results, list):
        results = []

    # -----------------------------------------------------
    # Clean individual search results
    # -----------------------------------------------------
    cleaned_results = []

    for result in results:
        if not isinstance(result, dict):
            continue

        title = str(
            result.get("title") or "Untitled Result"
        ).strip()

        url = str(
            result.get("url") or ""
        ).strip()

        content = str(
            result.get("content") or ""
        ).strip()

        target_audience = result.get(
            "target_audience"
        )

        if target_audience is not None:
            target_audience = str(
                target_audience
            ).strip() or None

        # SearchResultItem requires title, url and content.
        # Skip completely invalid results.
        if not title or not url or not content:
            continue

        cleaned_results.append(
            {
                "title": title,
                "url": url,
                "content": content,
                "target_audience": target_audience,
            }
        )

    # -----------------------------------------------------
    # Return validated Pydantic response
    # -----------------------------------------------------
    return SearchResponse(
        results=cleaned_results
    )