"""

These models define:
- The incoming request shape (the startup idea).
- The structured output shape expected from the Market Analysis Agent (Member 2)
  and the Competitor Analysis Agent (Member 3).
- The final combined response returned by FastAPI to the React frontend.

"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Request Model
# ---------------------------------------------------------------------------

class ValidationRequest(BaseModel):
    """Incoming request body for POST /api/validate"""

    idea: str = Field(..., description="The startup idea submitted by the user")
    domain: Optional[str] = Field(None, description="Optional user-specified domain category")
    target_customer: Optional[str] = Field(None, description="Optional target customer segment")

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
# Deep Validation Models (Technical, Scientific, Regulatory)
# ---------------------------------------------------------------------------

class TechnicalFeasibility(BaseModel):
    score: float = Field(default=7.0, description="Feasibility score from 1.0 to 10.0")
    feasibility_rating: str = Field(default="Medium", description="High, Medium, Low, or Moonshot")
    key_barriers: List[str] = Field(default_factory=list)
    signal_constraints: List[str] = Field(default_factory=list)
    recommended_tech_stack: List[str] = Field(default_factory=list)


class ScientificValidation(BaseModel):
    score: float = Field(default=6.5, description="Scientific confidence score from 1.0 to 10.0")
    evidence_level: str = Field(default="Emerging Hypothesis", description="Clinical Fact, Emerging Hypothesis, or Unsubstantiated")
    key_findings: List[str] = Field(default_factory=list)
    clinical_findings: List[str] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)
    required_trials: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def sync_findings(self) -> "ScientificValidation":
        if not self.key_findings and self.clinical_findings:
            self.key_findings = list(self.clinical_findings)
        elif not self.clinical_findings and self.key_findings:
            self.clinical_findings = list(self.key_findings)
        return self


class RegulatoryRisk(BaseModel):
    risk_level: str = Field(default="Medium", description="Low, Medium, High, or Critical")
    fda_classification: str = Field(default="Standard Industry Governance", description="General Wellness, SaMD Class I/II/III, or Industry Governance")
    regulatory_classification: Optional[str] = Field(default=None)
    compliance_requirements: List[str] = Field(default_factory=list)
    recommended_pathway: str = Field(default="", description="Go-to-market regulatory disclaimers & approval strategy")


# ---------------------------------------------------------------------------
# Combined Response Model (what FastAPI returns to React)
# ---------------------------------------------------------------------------

class ValidationResponse(BaseModel):
    idea: str
    market_analysis: MarketAnalysis
    competitor_analysis: CompetitorAnalysis
    technical_feasibility: Optional[TechnicalFeasibility] = None
    scientific_validation: Optional[ScientificValidation] = None
    regulatory_risk: Optional[RegulatoryRisk] = None
    # The exact search results the analysis agents used — returned to the
    # frontend so it can display Research Sources without a second API call.
    search_results: List[Dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Error Response Model (used when an agent or orchestrator step fails)
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None