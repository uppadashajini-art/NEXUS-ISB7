"""
These models define:
- The incoming request shape (the startup idea).
- The structured output shape expected from the Market Analysis Agent.
- The structured output shape expected from the Competitor Analysis Agent.
- SWOT and Risk analysis output.
- MVP Feature Recommendation output.
- The final combined response returned by FastAPI to the React frontend.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Request Model
# ---------------------------------------------------------------------------

class ValidationRequest(BaseModel):
    """Incoming request body for POST /api/validate"""

    idea: str = Field(
        ...,
        description="The startup idea submitted by the user"
    )

    domain: Optional[str] = Field(
        None,
        description="Optional user-specified domain category"
    )

    target_customer: Optional[str] = Field(
        None,
        description="Optional target customer segment"
    )

    @field_validator("idea")
    @classmethod
    def idea_must_not_be_empty_or_too_short(cls, value: str) -> str:
        cleaned = value.strip()

        if not cleaned:
            raise ValueError("Startup idea cannot be empty")

        if len(cleaned) < 10:
            raise ValueError(
                "Startup idea is too short to analyze meaningfully"
            )

        return cleaned


# ---------------------------------------------------------------------------
# Market Analysis Models
# ---------------------------------------------------------------------------

class CustomerSegment(BaseModel):
    segment: str
    role: Optional[str] = None
    company_size: Optional[str] = None
    pain_points: List[Any] = Field(
        default_factory=list,
        description="Acute pain points, optionally with severity ('Critical', 'High', 'Medium')"
    )
    willingness_to_pay: Optional[str] = None
    acquisition_channels: List[str] = Field(
        default_factory=list
    )
    objections: List[str] = Field(
        default_factory=list
    )
    needs: List[str] = Field(
        default_factory=list
    )
    profile: Optional[str] = None
    urgency: Optional[str] = None


class MarketSizing(BaseModel):
    tam: str = Field(default="$14.8B", description="Total Addressable Market")
    sam: str = Field(default="$2.4B", description="Serviceable Addressable Market")
    som: str = Field(default="$180M", description="Serviceable Obtainable Market")
    cagr: str = Field(default="+18.4%", description="Compound Annual Growth Rate")
    methodology: str = Field(
        default="Top-down industry sizing combined with bottom-up practitioner unit economics.",
        description="Calculation methodology and analytical logic"
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="Core modeling assumptions underpinning market sizing"
    )
    growth_drivers: List[str] = Field(
        default_factory=list,
        description="Macro and micro factors accelerating adoption"
    )
    headwinds: List[str] = Field(
        default_factory=list,
        description="Industry or macroeconomic friction points"
    )
    projection_5yr: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="5-year projected market trajectory ({ year, size, label })"
    )
    sources: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Verifiable source citations for TAM, SAM, SOM, CAGR ({ metric, figure, source_name, url })"
    )


class MarketAnalysis(BaseModel):
    industry: str

    market_opportunity: str

    market_trends: List[str] = Field(
        default_factory=list
    )

    customer_segments: List[CustomerSegment] = Field(
        default_factory=list
    )

    growth_drivers: List[str] = Field(
        default_factory=list
    )

    market_challenges: List[str] = Field(
        default_factory=list
    )

    market_sizing: Optional[MarketSizing] = None


# ---------------------------------------------------------------------------
# Competitor Analysis Models
# ---------------------------------------------------------------------------

class Competitor(BaseModel):
    name: str

    url: Optional[str] = None

    product_service: Optional[str] = None

    target_customers: Optional[str] = None

    funding_size: Optional[str] = Field(
        default=None,
        description="Funding stage or estimated revenue/size (e.g. Series B / $42M, Bootstrapped, Public)"
    )

    market_position: Optional[str] = Field(
        default=None,
        description="Market tier: Enterprise incumbent, fast-growing challenger, niche specialist"
    )

    key_features: List[str] = Field(
        default_factory=list
    )

    pricing: Optional[str] = None

    strengths: List[str] = Field(
        default_factory=list
    )

    weaknesses: List[str] = Field(
        default_factory=list
    )


class ComparisonRow(BaseModel):
    """A single row in the competitor comparison table."""

    competitor: str

    target_customers: Optional[str] = None

    key_features: Optional[str] = None

    strengths: Optional[str] = None

    weaknesses: Optional[str] = None


class CompetitorAnalysis(BaseModel):
    direct_competitors: List[Competitor] = Field(
        default_factory=list
    )

    indirect_competitors: List[Competitor] = Field(
        default_factory=list
    )

    comparison: List[ComparisonRow] = Field(
        default_factory=list
    )

    market_gaps: List[str] = Field(
        default_factory=list
    )

    feature_matrix: Optional[Any] = Field(
        default=None,
        description="Structured comparison across key capabilities (e.g. telemetry, webhooks, self-serve)"
    )


# ---------------------------------------------------------------------------
# Deep Validation Models
# Technical, Scientific, Regulatory, Execution
# ---------------------------------------------------------------------------

class TechnicalFeasibility(BaseModel):
    score: float = Field(
        default=7.0,
        description="Feasibility score from 1.0 to 10.0"
    )

    feasibility_rating: str = Field(
        default="Medium",
        description="High, Medium, Low, or Moonshot"
    )

    rationale: Optional[str] = Field(
        default=None,
        description="Detailed technical feasibility rationale"
    )

    risks: List[str] = Field(
        default_factory=list,
        description="Concrete architectural and engineering risks"
    )

    mitigations: List[str] = Field(
        default_factory=list,
        description="Actionable engineering mitigations"
    )

    key_barriers: List[str] = Field(
        default_factory=list
    )

    signal_constraints: List[str] = Field(
        default_factory=list
    )

    recommended_tech_stack: List[str] = Field(
        default_factory=list
    )


class ScientificValidation(BaseModel):
    score: float = Field(
        default=6.5,
        description="Scientific confidence score from 1.0 to 10.0"
    )

    evidence_level: str = Field(
        default="Emerging Hypothesis",
        description=(
            "Clinical Fact, Emerging Hypothesis, "
            "or Unsubstantiated"
        )
    )

    key_findings: List[str] = Field(
        default_factory=list
    )

    clinical_findings: List[str] = Field(
        default_factory=list
    )

    risk_flags: List[str] = Field(
        default_factory=list
    )

    required_trials: List[str] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def sync_findings(self) -> "ScientificValidation":

        if not self.key_findings and self.clinical_findings:
            self.key_findings = list(self.clinical_findings)

        elif not self.clinical_findings and self.key_findings:
            self.clinical_findings = list(self.key_findings)

        return self


class RegulatoryRisk(BaseModel):
    score: Optional[float] = Field(
        default=7.5,
        description="Regulatory clearance confidence score (1.0 to 10.0)"
    )

    risk_level: str = Field(
        default="Medium",
        description="Low, Medium, High, or Critical"
    )

    fda_classification: str = Field(
        default="Standard Industry Governance",
        description=(
            "General Wellness, SaMD Class I/II/III, "
            "or Industry Governance"
        )
    )

    regulatory_classification: Optional[str] = Field(
        default=None
    )

    rationale: Optional[str] = Field(
        default=None,
        description="Regulatory pathway rationale"
    )

    risks: List[str] = Field(
        default_factory=list,
        description="Primary compliance hazards"
    )

    mitigations: List[str] = Field(
        default_factory=list,
        description="Compliance clearance strategies"
    )

    compliance_requirements: List[str] = Field(
        default_factory=list
    )

    recommended_pathway: str = Field(
        default="",
        description=(
            "Go-to-market regulatory disclaimers "
            "& approval strategy"
        )
    )


class ExecutionFeasibility(BaseModel):
    score: float = Field(
        default=8.5,
        description="Execution and deployment feasibility score (1.0 to 10.0 or 0-100)"
    )

    rating: str = Field(
        default="High",
        description="High, Medium, or Low"
    )

    rationale: Optional[str] = Field(
        default=None,
        description="Assessment of team execution and go-to-market friction"
    )

    risks: List[str] = Field(
        default_factory=list,
        description="Key execution bottlenecks"
    )

    mitigations: List[str] = Field(
        default_factory=list,
        description="Execution risk mitigations"
    )

    key_milestones: List[str] = Field(
        default_factory=list,
        description="Critical launch milestones"
    )


class ComplianceChecklistItem(BaseModel):
    text: str
    done: bool = False
    mandatory: bool = True

    @model_validator(mode="before")
    @classmethod
    def parse_item(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"text": data, "done": False, "mandatory": True}
        return data


class ComplianceFramework(BaseModel):
    id: Optional[str] = None
    name: str
    severity: str = Field(default="Medium", description="critical, high, medium, low")
    status: str = Field(default="In Review", description="Clear, In Review, or Blocker")
    desc: Optional[str] = Field(default="", description="Description")
    description: Optional[str] = Field(default=None, description="Detailed framework description")
    checklist: List[ComplianceChecklistItem] = Field(default_factory=list)
    remediation: Optional[str] = Field(default="", description="Recommended action / remediation pathway")
    jurisdiction: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def sync_desc_and_id(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("id"):
                data["id"] = str(data.get("name", "framework")).lower().replace(" ", "_").replace("/", "_")
            if not data.get("desc") and data.get("description"):
                data["desc"] = str(data.get("description"))
            if not data.get("description") and data.get("desc"):
                data["description"] = str(data.get("desc"))
        return data


# ---------------------------------------------------------------------------
# SWOT & Risk Analysis Models
# Member 1 — Milestone 3/4
# ---------------------------------------------------------------------------

class SWOTAnalysis(BaseModel):

    strengths: List[str] = Field(
        default_factory=list,
        description=(
            "Unique features, technological edge, "
            "customer value, and competitive advantages"
        )
    )

    weaknesses: List[str] = Field(
        default_factory=list,
        description=(
            "Technical bottlenecks, resource constraints, "
            "brand absence, and product limits"
        )
    )

    opportunities: List[str] = Field(
        default_factory=list,
        description=(
            "Market expansion, emerging customer demands, "
            "new tech, and untapped niches"
        )
    )

    threats: List[str] = Field(
        default_factory=list,
        description=(
            "Incumbent reactions, price wars, regulatory hurdles, "
            "and adoption barriers"
        )
    )


class RiskItem(BaseModel):

    risk: str = Field(
        ...,
        description="Description of the identified risk"
    )

    category: str = Field(
        ...,
        description=(
            "Technical, Market, Financial, Competition, "
            "Operational, or Adoption"
        )
    )

    severity: str = Field(
        default="Medium",
        description="High, Medium, or Low"
    )

    impact: str = Field(
        ...,
        description=(
            "Concrete business consequence "
            "if this risk materializes"
        )
    )

    mitigation: str = Field(
        ...,
        description=(
            "Actionable strategic countermeasure "
            "to minimize or eliminate this risk"
        )
    )


# ---------------------------------------------------------------------------
# MVP Feature Recommendation Models
# Member 2 — Milestone 3/4
# ---------------------------------------------------------------------------

class MVPFeature(BaseModel):
    """
    Represents one feature recommended for the startup MVP.
    """

    feature: str = Field(
        ...,
        description="Name of the recommended feature"
    )

    priority: str = Field(
        ...,
        description=(
            "Must Have, Should Have, "
            "Could Have, or Future Features"
        )
    )

    reason: Optional[str] = Field(
        default="",
        description="Why this feature is recommended"
    )

    customer_value: Optional[str] = Field(
        default="High",
        description=(
            "Expected customer value: "
            "High, Medium, or Low"
        )
    )

    complexity: Optional[str] = Field(
        default="Medium",
        description=(
            "Implementation complexity: "
            "High, Medium, or Low"
        )
    )

    effort: Optional[str] = Field(
        default=None,
        description="Engineering effort: Low, Medium, High"
    )

    impact: Optional[str] = Field(
        default=None,
        description="Customer or business impact: Critical, High, Medium"
    )

    @model_validator(mode="after")
    def sync_effort_impact(self) -> "MVPFeature":
        if not self.effort:
            self.effort = self.complexity or "Medium"
        if not self.impact:
            self.impact = self.customer_value or "High"
        return self


class MVPRecommendations(BaseModel):
    """
    Groups recommended MVP features according to priority.
    """

    must_have: List[MVPFeature] = Field(
        default_factory=list,
        description="Features required for the initial MVP (Core)"
    )

    should_have: List[MVPFeature] = Field(
        default_factory=list,
        description="Important features after core MVP functionality (Secondary)"
    )

    could_have: List[MVPFeature] = Field(
        default_factory=list,
        description="Useful but non-essential MVP features (Out of Scope / Later)"
    )

    future_features: List[MVPFeature] = Field(
        default_factory=list,
        description="Features planned for future versions"
    )


# ---------------------------------------------------------------------------
# Go-To-Market Strategy Models (Member 3 — Milestone 3/4)
# ---------------------------------------------------------------------------

class GtmStrategy(BaseModel):
    target_market: List[str] = Field(default_factory=list)
    positioning: Optional[Any] = None
    marketing_channels: List[Any] = Field(default_factory=list)
    customer_acquisition: List[str] = Field(default_factory=list)
    pricing_strategy: Optional[Any] = None
    launch_strategy: List[Any] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Validation Report Model (Member 4 — Milestone 4)
# ---------------------------------------------------------------------------

class ValidationReport(BaseModel):
    executive_summary: str
    market_summary: str
    competitor_summary: str
    swot_summary: str
    risk_summary: str
    mvp_summary: str
    gtm_summary: str
    recommendations: str
    conclusion: str


# ---------------------------------------------------------------------------
# Combined Response Model
# What FastAPI returns to React
# ---------------------------------------------------------------------------

class ValidationResponse(BaseModel):

    idea: str

    product_name: Optional[str] = Field(
        default=None,
        description="Clean, concise brand or product name for the concept (e.g. OncoScribe AI, KubeSRE)"
    )

    overall_score: Optional[float] = Field(
        default=84.0,
        description="Overall validation score (0-100)"
    )

    sub_scores: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Sub-scores: market, technical, regulatory, execution, competition"
    )

    key_signals: Optional[List[Any]] = Field(
        default_factory=list,
        description="Key market and validation signals"
    )

    verdict: Optional[str] = Field(
        default="High Market Feasibility",
        description="High-level validation verdict (e.g. High Market Feasibility)"
    )

    market_analysis: MarketAnalysis

    competitor_analysis: CompetitorAnalysis

    technical_feasibility: Optional[Any] = None

    scientific_validation: Optional[Any] = None

    regulatory_risk: Optional[Any] = None

    execution_feasibility: Optional[Any] = None

    compliance_frameworks: List[ComplianceFramework] = Field(
        default_factory=list,
        description="Applicable compliance frameworks (GDPR, HIPAA, SOC 2, AI Governance, etc.)"
    )

    swot_analysis: Optional[Any] = None

    risk_analysis: Optional[List[Any]] = Field(
        default_factory=list
    )

    mvp_recommendations: Optional[Any] = None

    gtm_strategy: Optional[Dict[str, Any]] = None

    validation_report: Optional[Any] = None

    citations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Evidence sources linked to claims"
    )

    search_results: List[Dict[str, Any]] = Field(
        default_factory=list
    )


# ---------------------------------------------------------------------------
# Error Response Model
# Used when an agent or orchestrator step fails
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):

    error: str

    detail: Optional[str] = None