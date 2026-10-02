"""
FastAPI Route for Conversational Startup Advisor
Member 3 — NEXUS AI Startup Idea Validator

Endpoint:
POST /api/advisor
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from server.agents.startup_advisor_agent import run_startup_advisor

router = APIRouter(tags=["Startup Advisor"])


# ============================================================================
# PYDANTIC DATA MODELS (Self-Contained in Member 3 Domain)
# ============================================================================

class AdvisorRequest(BaseModel):
    """Incoming request model for POST /api/advisor."""
    question: str = Field(..., description="The founder's question")
    validation_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="The full or partial startup validation results from previous steps"
    )

    @field_validator("question")
    @classmethod
    def question_must_be_valid(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Question cannot be empty.")
        if len(cleaned) < 3:
            raise ValueError("Question is too short to provide actionable advice.")
        return cleaned


class AdvisorResponse(BaseModel):
    """Outgoing response model for POST /api/advisor."""
    answer: str
    suggested_followups: List[str] = Field(default_factory=list)


# ============================================================================
# API ROUTE HANDLERS
# ============================================================================

@router.post(
    "/api/advisor",
    response_model=AdvisorResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask the AI Startup Advisor a grounded question"
)
async def ask_advisor(request: AdvisorRequest) -> AdvisorResponse:
    """
    Receives a founder question and validation context,
    invokes the Startup Advisor Agent, and returns a grounded answer.
    """
    try:
        result = await run_startup_advisor(
            question=request.question,
            validation_context=request.validation_context
        )
        return AdvisorResponse(
            answer=result.get("answer", "No answer generated."),
            suggested_followups=result.get("suggested_followups", [])
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Advisor Agent encountered an error: {str(exc)}"
        )
