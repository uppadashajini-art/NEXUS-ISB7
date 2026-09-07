"""
Pydantic models for the /api/validate endpoint.

These models define:
- The incoming request shape (the startup idea).
- The structured output shape expected from the Market Analysis Agent (Member 2)
  and the Competitor Analysis Agent (Member 3).
- The final combined response returned by FastAPI to the React frontend.

Place this file at: server/models/validation.py
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Request Model
# ---------------------------------------------------------------------------

class ValidationRequest(BaseModel):
    """Incoming request body for POST /api/validate"""

    idea: str = Field(..., description="The startup idea submitted by the user")

    @field_validator("idea")
    @classmethod
    def idea_must_not_be_empty_or_too_short(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Startup idea cannot be empty")
        if len(cleaned) < 10:
            raise ValueError("Startup idea is too short to analyze meaningfully")
        return cleaned


# ---------------------------------------------------------------------------
# Market Analysis Models (Member 2's agent output)
# ---------------------------------------------------------------------------

class CustomerSegment(BaseModel):
    segment: str
    needs: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)


class MarketAnalysis(BaseModel):
    industry: str
    market_opportunity: str
    market_trends: List[str] = Field(default_factory=list)
    customer_segments: List[CustomerSegment] = Field(default_factory=list)
    growth_drivers: List[str] = Field(default_factory=list)
    market_challenges: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Competitor Analysis Models (Member 3's agent output)
# ---------------------------------------------------------------------------

class Competitor(BaseModel):
    name: str
    url: Optional[str] = None
    product_service: Optional[str] = None
    target_customers: Optional[str] = None
    key_features: List[str] = Field(default_factory=list)
    pricing: Optional[str] = None
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)


class ComparisonRow(BaseModel):
    """A single row in the competitor comparison table."""
    competitor: str
    target_customers: Optional[str] = None
    key_features: Optional[str] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None


class CompetitorAnalysis(BaseModel):
    direct_competitors: List[Competitor] = Field(default_factory=list)
    indirect_competitors: List[Competitor] = Field(default_factory=list)
    comparison: List[ComparisonRow] = Field(default_factory=list)
    market_gaps: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Combined Response Model (what FastAPI returns to React)
# ---------------------------------------------------------------------------

class ValidationResponse(BaseModel):
    idea: str
    market_analysis: MarketAnalysis
    competitor_analysis: CompetitorAnalysis


# ---------------------------------------------------------------------------
# Error Response Model (used when an agent or orchestrator step fails)
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None