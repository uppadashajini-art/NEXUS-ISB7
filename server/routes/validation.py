"""
Route for POST /api/validate

This route accepts a startup idea, passes it to the Orchestrator
(server/agents/orchestrator.py, built by Member 1), and returns the
combined market + competitor analysis to the React frontend.

NOTE: If orchestrator.py isn't finished yet, this route will return
a 503 error instead of crashing, so you can keep testing your own
layer independently.
"""

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from server.models.validation import ValidationRequest, ValidationResponse, ErrorResponse

router = APIRouter()

# Try to import the orchestrator. If it's not ready yet, we handle that gracefully.
try:
    from server.agents.orchestrator import run_orchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False


@router.post("/api/validate", response_model=ValidationResponse, responses={
    400: {"model": ErrorResponse},
    502: {"model": ErrorResponse},
    503: {"model": ErrorResponse},
})
async def validate_idea(request: ValidationRequest):
    """
    Accepts a startup idea, runs it through the orchestrator
    (web search -> market analysis + competitor analysis -> combined result),
    and returns a structured response for the frontend.
    """

    if not ORCHESTRATOR_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Orchestrator is not available yet. Check back once Member 1's "
                   "orchestrator.py is implemented."
        )

    try:
        result = await run_orchestrator(
            idea=request.idea,
            domain=request.domain,
            audience=request.target_customer,
        )
    except ValueError as e:
        # Raised for bad/invalid input that got past initial validation
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        # Raised if web search / external API calls fail
        raise HTTPException(status_code=502, detail=f"Upstream service failed: {e}")
    except Exception as e:
        # Catch-all for agent or orchestrator failures
        raise HTTPException(status_code=500, detail=f"Orchestrator failed: {e}")

    try:
        return ValidationResponse(**result)
    except ValidationError as e:
        # Agent output didn't match expected structure
        raise HTTPException(
            status_code=502,
            detail=f"Agent returned an invalid response structure: {e}"
        )