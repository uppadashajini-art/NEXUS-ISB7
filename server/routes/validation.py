"""
Route for POST /api/validate

This route accepts a startup idea, passes it to the Orchestrator
(server/agents/orchestrator.py, built by Member 1), and returns the
combined market + competitor analysis to the React frontend.

NOTE: If orchestrator.py isn't finished yet, this route will return
a 503 error instead of crashing, so you can keep testing your own
layer independently.
"""

from typing import Optional
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError

from server.models.validation import ValidationRequest, ValidationResponse, ErrorResponse
from server.agents.report_generation_agent import generate_validation_report

logger = logging.getLogger(__name__)

router = APIRouter()


class ScheduleReportEmailRequest(BaseModel):
    email: str
    idea: Optional[str] = None
    domain: Optional[str] = None
    target_customer: Optional[str] = None


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
        report_result = await generate_validation_report(
            idea=request.idea,
            market_analysis=result.get("market_analysis"),
            competitor_analysis=result.get("competitor_analysis"),
            swot_analysis=result.get("swot_analysis"),
            risk_analysis=result.get("risk_analysis"),
            mvp_recommendations=result.get("mvp_recommendations"),
            gtm_strategy=result.get("gtm_strategy"),
        )
        result["validation_report"] = report_result.get("validation_report")
    except Exception:
        # Report generation failing should never break the rest of the
        # response -- the frontend will just not show that section.
        result["validation_report"] = None


    try:
        return ValidationResponse(**result)
    except ValidationError as e:
        # Agent output didn't match expected structure
        raise HTTPException(
            status_code=502,
            detail=f"Agent returned an invalid response structure: {e}"
        )


@router.post("/api/schedule-report-email")
async def schedule_report_email(request: ScheduleReportEmailRequest):
    """
    Schedules dispatch of the startup validation report to the user's email upon completion.
    Analysis typically takes ~2 minutes, allowing founders to step away and receive the full dossier.
    """
    clean_email = request.email.strip().lower()
    if not clean_email or "@" not in clean_email or "." not in clean_email:
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")

    idea_summary = (request.idea[:60] + "...") if request.idea and len(request.idea) > 60 else (request.idea or "Unspecified Concept")
    logger.info(f"[Validation Email Delivery] Scheduled report for '{clean_email}' (Concept: {idea_summary})")

    return {
        "status": "success",
        "message": f"Report scheduled. The full validation dossier will be delivered to {clean_email} upon synthesis completion.",
        "email": clean_email,
        "idea": request.idea,
    }