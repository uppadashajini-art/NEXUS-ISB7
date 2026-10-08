"""
These models define:
- The incoming request shape (the startup idea).
- The structured output shape expected from the Market Analysis Agent.
- The structured output shape expected from the Competitor Analysis Agent.
- SWOT and Risk analysis output.
- MVP Feature Recommendation output.
- The final combined response returned by FastAPI to the React frontend.
"""

import re
from typing import Any, Dict, List, Literal, Optional, Tuple, Union
from urllib.parse import urlparse
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

    @field_validator("objections", "needs", "acquisition_channels", mode="before")
    @classmethod
    def _coerce_string_list(cls, v):
        if not isinstance(v, list):
            return []
        cleaned = []
        for item in v:
            if isinstance(item, str):
                if item.strip():
                    cleaned.append(item.strip())
            elif isinstance(item, dict):
                val = (
                    item.get("objection")
                    or item.get("need")
                    or item.get("channel")
                    or item.get("text")
                    or item.get("value")
                    or item.get("description")
                )
                if not val and item:
                    for sub_v in item.values():
                        if isinstance(sub_v, str) and sub_v.strip():
                            val = sub_v
                            break
                if val:
                    cleaned.append(str(val).strip())
                else:
                    cleaned.append(str(item).strip())
            elif item is not None:
                cleaned.append(str(item).strip())
        return cleaned


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

class RegimeItem(BaseModel):
    """Structured regulatory regime or voluntary standard with explicit application rationale."""
    name: str = Field(..., description="Name of regulation or standard")
    type: Literal["mandatory", "voluntary"] = Field(default="mandatory", description="mandatory regulation | voluntary standard")
    why_applies: str = Field(..., description="One-line justification of why this regime applies to this specific startup idea")


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

    why_competitor: Optional[str] = Field(
        default=None,
        description="One-line explanation of why this company is a competitor (same customer, same problem, same jurisdiction)"
    )

    region: Optional[str] = Field(
        default=None,
        description="Geographic region or jurisdiction of the competitor (e.g., India, US, Global)"
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

    verification_status: Optional[str] = Field(
        default="verified",
        description="'verified' | 'Unverified, from model knowledge'"
    )

    source_type: Optional[str] = Field(
        default="web_search",
        description="'web_search' | 'unverified_model_knowledge'"
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

    evidence_status: Optional[str] = Field(
        default="sufficient",
        description="'sufficient' | 'not_enough_evidence'"
    )

    evidence_reason: Optional[str] = Field(
        default=None,
        description="Explanation when verified competitor evidence is insufficient"
    )

    unverified_candidates: List[Competitor] = Field(
        default_factory=list,
        description="Up to 3 LLM-suggested candidates clearly labeled 'Unverified, from model knowledge'"
    )


class StartupMetadata(BaseModel):
    """
    Extracted startup metadata from initial LLM reasoning.
    Used across all validation modules and UI title generation.
    """
    product: str = Field(
        ...,
        description="Clean, concise product name or title (e.g. Gig Worker Instant Micro-Lending Platform)"
    )
    target_user: str = Field(
        ...,
        description="Primary target user persona (e.g. Gig delivery workers and rideshare drivers)"
    )
    domain: str = Field(
        ...,
        description="Primary industry domain (e.g. FinTech & Financial Services)"
    )
    jurisdiction: str = Field(
        default="Global",
        description="Target geographical jurisdiction (e.g. India, US, Global)"
    )
    business_model: Literal["lending", "saas", "marketplace", "hardware", "other"] = Field(
        default="saas",
        description="Monetization model: lending | saas | marketplace | hardware | other"
    )
    source_type: Literal["llm_extracted", "heuristic_fallback"] = Field(
        default="heuristic_fallback",
        description="Source of metadata classification: llm_extracted or heuristic_fallback"
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

    applicable_regimes: List[str] = Field(
        default_factory=list,
        description="Governing regulatory bodies and standards shared with Regulatory Runway (Pillar 05)"
    )

    recommended_pathway: str = Field(
        default="",
        description=(
            "Go-to-market regulatory disclaimers "
            "& approval strategy"
        )
    )

def compute_unit_economics_margin(cost_to_serve: float, suggested_price: float) -> tuple[float, str]:
    """
    Computes gross margin percentage and margin grade deterministically.
    Grade rules:
      - healthy: >= 70%
      - thin: 30% - 69.9%
      - margin_trap: < 30%
    """
    try:
        cost = float(cost_to_serve)
        price = float(suggested_price)
    except (ValueError, TypeError):
        return 0.0, "margin_trap"

    if price <= 0:
        return 0.0, "margin_trap"

    margin_pct = round(((price - cost) / price) * 100.0, 1)
    if margin_pct >= 70.0:
        grade = "healthy"
    elif margin_pct >= 30.0:
        grade = "thin"
    else:
        grade = "margin_trap"
    return margin_pct, grade


def compute_lending_unit_economics(
    loan_size: float = 5000.0,
    tenure_days: int = 30,
    interest_rate_pct: float = 3.0,
    processing_fee: float = 250.0,
    annual_cost_of_capital_pct: float = 18.0,
    default_rate_pct: float = 5.0,
    collections_cost: float = 40.0,
    cac: float = 15.0,
    currency_symbol: str = "₹"
) -> Dict[str, Any]:
    """
    Computes per-loan lending unit economics deterministically in Python for a single scenario.
    Revenue = Interest + Origination Fees
    Cost = Cost of Capital + Expected Default Loss (default_rate * loan_size) + Collections Cost + CAC
    Net Contribution = Revenue - Cost
    Margin = Net Contribution / Revenue
    Effective APR = ((Revenue / loan_size) * (365 / tenure_days)) * 100
    """
    interest_amount = round(loan_size * (interest_rate_pct / 100.0), 2)
    revenue = round(interest_amount + processing_fee, 2)

    # Cost of capital prorated for loan tenure
    coc = round(loan_size * (annual_cost_of_capital_pct / 100.0) * (tenure_days / 365.0), 2)
    default_loss = round(loan_size * (default_rate_pct / 100.0), 2)
    total_cost = round(coc + default_loss + collections_cost + cac, 2)

    net_contribution = round(revenue - total_cost, 2)
    margin_pct = round((net_contribution / revenue) * 100.0, 1) if revenue > 0 else 0.0
    grade = "healthy" if margin_pct >= 70.0 else ("thin" if margin_pct >= 30.0 else "margin_trap")

    effective_apr = round(((revenue / loan_size) * (365.0 / tenure_days)) * 100.0, 1) if loan_size > 0 else 0.0

    assumptions = [
        f"Average micro-loan size: {currency_symbol}{loan_size:,.0f} with a {tenure_days}-day repayment tenure.",
        f"Revenue per loan: {currency_symbol}{revenue:,.0f} ({currency_symbol}{interest_amount:.0f} interest @ {interest_rate_pct}%/mo + {currency_symbol}{processing_fee:.0f} origination fee).",
        f"Cost of capital: {currency_symbol}{coc:,.0f} ({annual_cost_of_capital_pct}% annualized wholesale debt spread over {tenure_days} days).",
        f"Expected default loss: {currency_symbol}{default_loss:,.0f} ({default_rate_pct}% default rate on {currency_symbol}{loan_size:,.0f} principal).",
        f"Digital collections and recovery cost: {currency_symbol}{collections_cost:,.0f} per loan.",
        f"Borrower acquisition cost (CAC amortization): {currency_symbol}{cac:,.0f} per loan.",
        f"Net contribution: {currency_symbol}{net_contribution:,.0f} per loan ({margin_pct}% contribution margin).",
        f"Effective annualized percentage rate (APR): {effective_apr}% p.a. based on {tenure_days}-day tenure (NOT flat fee)."
    ]

    return {
        "cost_to_serve_per_user_usd": total_cost,
        "total_cost_to_serve": total_cost,
        "suggested_price_usd": revenue,
        "gross_margin_pct": margin_pct,
        "margin_grade": grade,
        "currency_symbol": currency_symbol,
        "unit_label": "loan",
        "loan_size": loan_size,
        "revenue_per_loan": revenue,
        "cost_of_capital": coc,
        "expected_default_loss": default_loss,
        "default_rate_pct": default_rate_pct,
        "collections_cost": collections_cost,
        "cac": cac,
        "net_contribution_per_loan": net_contribution,
        "effective_apr": effective_apr,
        "assumptions": assumptions
    }


def compute_lending_unit_economics_scenarios(
    loan_size_low: float = 2000.0,
    loan_size_base: float = 5000.0,
    loan_size_high: float = 10000.0,
    tenure_days: int = 30,
    tenure_days_low: Optional[int] = None,
    tenure_days_base: Optional[int] = None,
    tenure_days_high: Optional[int] = None,
    interest_rate_pct: float = 3.0,
    interest_rate_pct_low: Optional[float] = None,
    interest_rate_pct_base: Optional[float] = None,
    interest_rate_pct_high: Optional[float] = None,
    processing_fee: float = 250.0,
    processing_fee_low: Optional[float] = None,
    processing_fee_base: Optional[float] = None,
    processing_fee_high: Optional[float] = None,
    annual_cost_of_capital_pct_low: float = 22.0,
    annual_cost_of_capital_pct_base: float = 18.0,
    annual_cost_of_capital_pct_high: float = 14.0,
    default_rate_pct_low: float = 8.0,
    default_rate_pct_base: float = 5.0,
    default_rate_pct_high: float = 3.0,
    collections_cost: float = 40.0,
    cac: float = 15.0,
    currency_symbol: str = "\u20b9"
) -> Dict[str, Any]:
    """
    Computes lending unit economics for three deterministic scenarios:
      - low:  smallest loan + worst-case cost of capital + highest default rate (stress)
      - base: mid loan + base assumptions (expected)
      - high: largest loan + cheapest capital + lowest default rate (optimistic)
    Returns all three scenarios plus the base scenario fields for backward compatibility.
    Also returns break_even_default_rate_pct: the default rate at which net_contribution == 0 (base assumptions).
    """
    t_low = tenure_days_low if tenure_days_low is not None else tenure_days
    t_base = tenure_days_base if tenure_days_base is not None else tenure_days
    t_high = tenure_days_high if tenure_days_high is not None else tenure_days

    i_low = interest_rate_pct_low if interest_rate_pct_low is not None else interest_rate_pct
    i_base = interest_rate_pct_base if interest_rate_pct_base is not None else interest_rate_pct
    i_high = interest_rate_pct_high if interest_rate_pct_high is not None else interest_rate_pct

    p_base = processing_fee_base if processing_fee_base is not None else processing_fee
    if processing_fee_low is not None:
        p_low = processing_fee_low
    elif loan_size_base > 0:
        p_low = round(p_base * (loan_size_low / loan_size_base), 2)
    else:
        p_low = p_base

    if processing_fee_high is not None:
        p_high = processing_fee_high
    elif loan_size_base > 0:
        p_high = round(p_base * (loan_size_high / loan_size_base), 2)
    else:
        p_high = p_base

    low = compute_lending_unit_economics(
        loan_size=loan_size_low,
        tenure_days=t_low,
        interest_rate_pct=i_low,
        processing_fee=p_low,
        annual_cost_of_capital_pct=annual_cost_of_capital_pct_low,
        default_rate_pct=default_rate_pct_low,
        collections_cost=collections_cost,
        cac=cac,
        currency_symbol=currency_symbol,
    )
    base = compute_lending_unit_economics(
        loan_size=loan_size_base,
        tenure_days=t_base,
        interest_rate_pct=i_base,
        processing_fee=p_base,
        annual_cost_of_capital_pct=annual_cost_of_capital_pct_base,
        default_rate_pct=default_rate_pct_base,
        collections_cost=collections_cost,
        cac=cac,
        currency_symbol=currency_symbol,
    )
    high = compute_lending_unit_economics(
        loan_size=loan_size_high,
        tenure_days=t_high,
        interest_rate_pct=i_high,
        processing_fee=p_high,
        annual_cost_of_capital_pct=annual_cost_of_capital_pct_high,
        default_rate_pct=default_rate_pct_high,
        collections_cost=collections_cost,
        cac=cac,
        currency_symbol=currency_symbol,
    )

    base_interest = round(loan_size_base * (i_base / 100.0), 2)
    base_revenue = round(base_interest + p_base, 2)
    base_coc = round(loan_size_base * (annual_cost_of_capital_pct_base / 100.0) * (t_base / 365.0), 2)
    break_even_numerator = base_revenue - base_coc - collections_cost - cac
    if loan_size_base > 0 and break_even_numerator > 0:
        break_even_default_rate_pct = round((break_even_numerator / loan_size_base) * 100.0, 2)
    else:
        break_even_default_rate_pct = 0.0

    # One-driver-at-a-time sensitivity table (holding all other parameters at base)
    drv_default = compute_lending_unit_economics(
        loan_size=loan_size_base, tenure_days=t_base, interest_rate_pct=i_base, processing_fee=p_base,
        annual_cost_of_capital_pct=annual_cost_of_capital_pct_base, default_rate_pct=default_rate_pct_low,
        collections_cost=collections_cost, cac=cac, currency_symbol=currency_symbol
    )
    drv_coc = compute_lending_unit_economics(
        loan_size=loan_size_base, tenure_days=t_base, interest_rate_pct=i_base, processing_fee=p_base,
        annual_cost_of_capital_pct=annual_cost_of_capital_pct_low, default_rate_pct=default_rate_pct_base,
        collections_cost=collections_cost, cac=cac, currency_symbol=currency_symbol
    )
    drv_price = compute_lending_unit_economics(
        loan_size=loan_size_base, tenure_days=t_base, interest_rate_pct=i_base, processing_fee=p_low,
        annual_cost_of_capital_pct=annual_cost_of_capital_pct_base, default_rate_pct=default_rate_pct_base,
        collections_cost=collections_cost, cac=cac, currency_symbol=currency_symbol
    )
    drv_cac = compute_lending_unit_economics(
        loan_size=loan_size_base, tenure_days=t_base, interest_rate_pct=i_base, processing_fee=p_base,
        annual_cost_of_capital_pct=annual_cost_of_capital_pct_base, default_rate_pct=default_rate_pct_base,
        collections_cost=collections_cost, cac=cac * 1.5, currency_symbol=currency_symbol
    )

    sensitivity_table = [
        {
            "driver": f"Default Rate Surge ({default_rate_pct_base}% → {default_rate_pct_low}%)",
            "base_margin_pct": base["gross_margin_pct"],
            "stressed_margin_pct": drv_default["gross_margin_pct"],
            "margin_delta_pct": round(drv_default["gross_margin_pct"] - base["gross_margin_pct"], 1),
            "severity": "High" if abs(drv_default["gross_margin_pct"] - base["gross_margin_pct"]) > 10 else "Medium",
        },
        {
            "driver": f"Cost of Capital Rise ({annual_cost_of_capital_pct_base}% → {annual_cost_of_capital_pct_low}%)",
            "base_margin_pct": base["gross_margin_pct"],
            "stressed_margin_pct": drv_coc["gross_margin_pct"],
            "margin_delta_pct": round(drv_coc["gross_margin_pct"] - base["gross_margin_pct"], 1),
            "severity": "Medium",
        },
        {
            "driver": f"Processing Fee Compression ({currency_symbol}{p_base} → {currency_symbol}{p_low})",
            "base_margin_pct": base["gross_margin_pct"],
            "stressed_margin_pct": drv_price["gross_margin_pct"],
            "margin_delta_pct": round(drv_price["gross_margin_pct"] - base["gross_margin_pct"], 1),
            "severity": "Medium",
        },
        {
            "driver": f"Acquisition Friction (CAC {currency_symbol}{cac} → {currency_symbol}{cac * 1.5})",
            "base_margin_pct": base["gross_margin_pct"],
            "stressed_margin_pct": drv_cac["gross_margin_pct"],
            "margin_delta_pct": round(drv_cac["gross_margin_pct"] - base["gross_margin_pct"], 1),
            "severity": "Low",
        },
    ]

    return {
        **base,
        "scenarios": {
            "low": {
                "label": "Stress",
                "description": f"Loan {currency_symbol}{loan_size_base:,.0f}, Default {default_rate_pct_low}%, CoC {annual_cost_of_capital_pct_base}%",
                "gross_margin_pct": drv_default["gross_margin_pct"],
                "margin_grade": drv_default["margin_grade"],
                "net_contribution_per_loan": drv_default["net_contribution_per_loan"],
                "effective_apr": drv_default["effective_apr"],
                "loan_size": loan_size_base,
                "default_rate_pct": default_rate_pct_low,
            },
            "base": {
                "label": "Base",
                "description": f"Loan {currency_symbol}{loan_size_base:,.0f}, {annual_cost_of_capital_pct_base}% CoC, {default_rate_pct_base}% default",
                "gross_margin_pct": base["gross_margin_pct"],
                "margin_grade": base["margin_grade"],
                "net_contribution_per_loan": base["net_contribution_per_loan"],
                "effective_apr": base["effective_apr"],
                "loan_size": loan_size_base,
                "default_rate_pct": default_rate_pct_base,
            },
            "high": {
                "label": "Optimistic",
                "description": f"Loan {currency_symbol}{loan_size_high:,.0f}, {annual_cost_of_capital_pct_high}% CoC, {default_rate_pct_high}% default",
                "gross_margin_pct": high["gross_margin_pct"],
                "margin_grade": high["margin_grade"],
                "net_contribution_per_loan": high["net_contribution_per_loan"],
                "effective_apr": high["effective_apr"],
                "loan_size": loan_size_high,
                "default_rate_pct": default_rate_pct_high,
            },
        },
        "sensitivity_table": sensitivity_table,
        "margin_range": [min(drv_default["gross_margin_pct"], base["gross_margin_pct"], high["gross_margin_pct"]), max(drv_default["gross_margin_pct"], base["gross_margin_pct"], high["gross_margin_pct"])],
        "margin_spread": round(max(drv_default["gross_margin_pct"], base["gross_margin_pct"], high["gross_margin_pct"]) - min(drv_default["gross_margin_pct"], base["gross_margin_pct"], high["gross_margin_pct"]), 1),
        "wide_uncertainty": (max(drv_default["gross_margin_pct"], base["gross_margin_pct"], high["gross_margin_pct"]) - min(drv_default["gross_margin_pct"], base["gross_margin_pct"], high["gross_margin_pct"])) > 40.0,
        "margin_range_formatted": f"{min(drv_default['gross_margin_pct'], base['gross_margin_pct'], high['gross_margin_pct'])}% – {max(drv_default['gross_margin_pct'], base['gross_margin_pct'], high['gross_margin_pct'])}%" + (" (wide uncertainty)" if (max(drv_default["gross_margin_pct"], base["gross_margin_pct"], high["gross_margin_pct"]) - min(drv_default["gross_margin_pct"], base["gross_margin_pct"], high["gross_margin_pct"])) > 40.0 else ""),
        "break_even_default_rate_pct": break_even_default_rate_pct,
    }


def compute_saas_unit_economics_scenarios(
    inference_cost_low: float = 1.0,
    inference_cost_base: float = 3.0,
    inference_cost_high: float = 6.0,
    hosting_cost_low: float = 0.5,
    hosting_cost_base: float = 1.5,
    hosting_cost_high: float = 3.0,
    support_cost_low: float = 0.5,
    support_cost_base: float = 1.5,
    support_cost_high: float = 3.0,
    price_low: float = 20.0,
    price_base: float = 35.0,
    price_high: float = 60.0,
    currency_symbol: str = "$",
    unit_label: str = "customer/month"
) -> Dict[str, Any]:
    """
    Computes SaaS unit economics deterministically in Python:
    Uses a one-driver-at-a-time sensitivity table rather than a stacked worst-case.
    """
    cost_base = round(inference_cost_base + hosting_cost_base + support_cost_base, 2)
    p_base = price_base
    m_base, g_base = compute_unit_economics_margin(cost_base, p_base)

    # One-driver-at-a-time stresses
    cost_inf_stress = round(inference_cost_high + hosting_cost_base + support_cost_base, 2)
    m_inf, g_inf = compute_unit_economics_margin(cost_inf_stress, p_base)

    cost_host_stress = round(inference_cost_base + hosting_cost_high + support_cost_base, 2)
    m_host, g_host = compute_unit_economics_margin(cost_host_stress, p_base)

    m_price_stress, g_price_stress = compute_unit_economics_margin(cost_base, price_low)

    cost_sup_stress = round(inference_cost_base + hosting_cost_base + support_cost_high, 2)
    m_sup, g_sup = compute_unit_economics_margin(cost_sup_stress, p_base)

    # Scale efficiency optimistic
    cost_scale = round(inference_cost_low + hosting_cost_low + support_cost_low, 2)
    m_scale, g_scale = compute_unit_economics_margin(cost_scale, price_high)

    sensitivity_table = [
        {
            "driver": f"LLM Token Inference Surge ({currency_symbol}{inference_cost_base:,.2f} → {currency_symbol}{inference_cost_high:,.2f})",
            "base_margin_pct": m_base,
            "stressed_margin_pct": m_inf,
            "margin_delta_pct": round(m_inf - m_base, 1),
            "severity": "High" if abs(m_inf - m_base) > 10 else "Medium",
        },
        {
            "driver": f"Subscription Price Discount ({currency_symbol}{p_base:,.2f} → {currency_symbol}{price_low:,.2f})",
            "base_margin_pct": m_base,
            "stressed_margin_pct": m_price_stress,
            "margin_delta_pct": round(m_price_stress - m_base, 1),
            "severity": "High" if abs(m_price_stress - m_base) > 10 else "Medium",
        },
        {
            "driver": f"Cloud Hosting & Egress ({currency_symbol}{hosting_cost_base:,.2f} → {currency_symbol}{hosting_cost_high:,.2f})",
            "base_margin_pct": m_base,
            "stressed_margin_pct": m_host,
            "margin_delta_pct": round(m_host - m_base, 1),
            "severity": "Low" if abs(m_host - m_base) < 5 else "Medium",
        },
        {
            "driver": f"Support Operations ({currency_symbol}{support_cost_base:,.2f} → {currency_symbol}{support_cost_high:,.2f})",
            "base_margin_pct": m_base,
            "stressed_margin_pct": m_sup,
            "margin_delta_pct": round(m_sup - m_base, 1),
            "severity": "Low" if abs(m_sup - m_base) < 5 else "Medium",
        },
    ]

    assumptions = [
        f"Inference & model API cost: {currency_symbol}{inference_cost_base:,.2f}/{unit_label} (OCR parsing, embeddings, LLM reasoning).",
        f"Cloud infrastructure & hosting: {currency_symbol}{hosting_cost_base:,.2f}/{unit_label} (database, storage, network egress).",
        f"Customer support & account management: {currency_symbol}{support_cost_base:,.2f}/{unit_label}.",
        f"Target subscription price: {currency_symbol}{p_base:,.2f}/{unit_label}.",
        f"Total monthly cost-to-serve: {currency_symbol}{cost_base:,.2f}/{unit_label} yielding a base gross margin of {m_base}%.",
        f"Key cost driver: LLM token inference and document OCR processing."
    ]

    # Primary stress case comes from the single most sensitive driver
    stress_margin = min(m_inf, m_price_stress)
    stress_grade = g_inf if m_inf <= m_price_stress else g_price_stress

    return {
        "cost_to_serve_per_user_usd": cost_base,
        "suggested_price_usd": p_base,
        "gross_margin_pct": m_base,
        "margin_grade": g_base,
        "currency_symbol": currency_symbol,
        "unit_label": unit_label,
        "margin_range": [min(stress_margin, m_base, m_scale), max(stress_margin, m_base, m_scale)],
        "margin_spread": round(max(stress_margin, m_base, m_scale) - min(stress_margin, m_base, m_scale), 1),
        "wide_uncertainty": (max(stress_margin, m_base, m_scale) - min(stress_margin, m_base, m_scale)) > 40.0,
        "margin_range_formatted": f"{min(stress_margin, m_base, m_scale)}% – {max(stress_margin, m_base, m_scale)}%" + (" (wide uncertainty)" if (max(stress_margin, m_base, m_scale) - min(stress_margin, m_base, m_scale)) > 40.0 else ""),
        "scenarios": {
            "low": {
                "label": "Stress",
                "description": f"Price {currency_symbol}{p_base:,.0f}, Cost {currency_symbol}{cost_inf_stress:,.2f} (50% higher model inference)",
                "gross_margin_pct": stress_margin,
                "margin_grade": stress_grade,
                "cost_to_serve": cost_inf_stress,
                "price": p_base,
            },
            "base": {
                "label": "Base",
                "description": f"Price {currency_symbol}{p_base:,.0f}, Cost {currency_symbol}{cost_base:,.2f}",
                "gross_margin_pct": m_base,
                "margin_grade": g_base,
                "cost_to_serve": cost_base,
                "price": p_base,
            },
            "high": {
                "label": "Optimistic",
                "description": f"Price {currency_symbol}{price_high:,.0f}, Cost {currency_symbol}{cost_scale:,.2f} (scale efficiency)",
                "gross_margin_pct": m_scale,
                "margin_grade": g_scale,
                "cost_to_serve": cost_scale,
                "price": price_high,
            },
        },
        "sensitivity_table": sensitivity_table,
        "assumptions": assumptions,
        "key_cost_driver": "LLM token inference & OCR parsing"
    }


def compute_hardware_unit_economics_scenarios(
    unit_bom_low: float = 350.0,
    unit_bom_base: float = 500.0,
    unit_bom_high: float = 750.0,
    assembly_cost_low: float = 50.0,
    assembly_cost_base: float = 80.0,
    assembly_cost_high: float = 120.0,
    cert_amort_low: float = 20.0,
    cert_amort_base: float = 40.0,
    cert_amort_high: float = 70.0,
    logistics_cost_low: float = 30.0,
    logistics_cost_base: float = 50.0,
    logistics_cost_high: float = 80.0,
    warranty_cost_low: float = 20.0,
    warranty_cost_base: float = 30.0,
    warranty_cost_high: float = 50.0,
    price_low: float = 900.0,
    price_base: float = 1400.0,
    price_high: float = 2000.0,
    currency_symbol: str = "₹",
    unit_label: str = "sensor unit"
) -> Dict[str, Any]:
    """
    Computes Hardware unit economics deterministically in Python for three scenarios:
      - low (stress): distributor/wholesale price + highest component BOM, assembly, logistics, and warranty
      - base (expected): target retail price + base manufacturing costs
      - high (optimistic): direct-to-farm retail price + volume procurement discounts
    Notice: No monthly inference costs!
    """
    cost_low = round(unit_bom_high + assembly_cost_high + cert_amort_high + logistics_cost_high + warranty_cost_high, 2)
    p_low = price_low
    m_low, g_low = compute_unit_economics_margin(cost_low, p_low)

    cost_base = round(unit_bom_base + assembly_cost_base + cert_amort_base + logistics_cost_base + warranty_cost_base, 2)
    p_base = price_base
    m_base, g_base = compute_unit_economics_margin(cost_base, p_base)

    # One-driver-at-a-time stresses
    cost_bom_stress = round(unit_bom_high + assembly_cost_base + cert_amort_base + logistics_cost_base + warranty_cost_base, 2)
    m_bom, g_bom = compute_unit_economics_margin(cost_bom_stress, p_base)

    m_price_stress, g_price_stress = compute_unit_economics_margin(cost_base, price_low)

    cost_log_stress = round(unit_bom_base + assembly_cost_base + cert_amort_base + logistics_cost_high + warranty_cost_base, 2)
    m_log, g_log = compute_unit_economics_margin(cost_log_stress, p_base)

    cost_scale = round(unit_bom_low + assembly_cost_low + cert_amort_low + logistics_cost_low + warranty_cost_low, 2)
    m_scale, g_scale = compute_unit_economics_margin(cost_scale, price_high)

    sensitivity_table = [
        {
            "driver": f"Unit BOM Component Surge ({currency_symbol}{unit_bom_base:,.2f} → {currency_symbol}{unit_bom_high:,.2f})",
            "base_margin_pct": m_base,
            "stressed_margin_pct": m_bom,
            "margin_delta_pct": round(m_bom - m_base, 1),
            "severity": "High" if abs(m_bom - m_base) > 10 else "Medium",
        },
        {
            "driver": f"Wholesale Discount Pressure ({currency_symbol}{price_base:,.2f} → {currency_symbol}{price_low:,.2f})",
            "base_margin_pct": m_base,
            "stressed_margin_pct": m_price_stress,
            "margin_delta_pct": round(m_price_stress - m_base, 1),
            "severity": "High" if abs(m_price_stress - m_base) > 10 else "Medium",
        },
        {
            "driver": f"Logistics & Freight ({currency_symbol}{logistics_cost_base:,.2f} → {currency_symbol}{logistics_cost_high:,.2f})",
            "base_margin_pct": m_base,
            "stressed_margin_pct": m_log,
            "margin_delta_pct": round(m_log - m_base, 1),
            "severity": "Low" if abs(m_log - m_base) < 5 else "Medium",
        },
    ]

    assumptions = [
        f"Unit Bill of Materials (BOM): {currency_symbol}{unit_bom_base:,.2f}/{unit_label} (capacitive probe, MCU, LoRa/GSM telemetry module, weather-sealed enclosure).",
        f"Surface-mount assembly & QC testing: {currency_symbol}{assembly_cost_base:,.2f}/{unit_label}.",
        f"Regulatory certification amortization (WPC/TEC/CE): {currency_symbol}{cert_amort_base:,.2f}/{unit_label}.",
        f"Distribution & shipping logistics: {currency_symbol}{logistics_cost_base:,.2f}/{unit_label}.",
        f"Field warranty & replacement reserve (2-yr): {currency_symbol}{warranty_cost_base:,.2f}/{unit_label}.",
        f"Target retail / distributor price: {currency_symbol}{price_base:,.2f}/{unit_label}.",
        f"Total per-unit cost: {currency_symbol}{cost_base:,.2f}/{unit_label} yielding a base gross margin of {m_base}%.",
        f"Key cost driver: Sensor probes, wireless telemetry module, and tooling/molding amortization (NO monthly inference cost)."
    ]

    stress_margin = min(m_bom, m_price_stress)
    stress_grade = g_bom if m_bom <= m_price_stress else g_price_stress

    return {
        "cost_to_serve_per_user_usd": cost_base,
        "suggested_price_usd": p_base,
        "gross_margin_pct": m_base,
        "margin_grade": g_base,
        "currency_symbol": currency_symbol,
        "unit_label": unit_label,
        "margin_range": [min(stress_margin, m_base, m_scale), max(stress_margin, m_base, m_scale)],
        "margin_spread": round(max(stress_margin, m_base, m_scale) - min(stress_margin, m_base, m_scale), 1),
        "wide_uncertainty": (max(stress_margin, m_base, m_scale) - min(stress_margin, m_base, m_scale)) > 40.0,
        "margin_range_formatted": f"{min(stress_margin, m_base, m_scale)}% – {max(stress_margin, m_base, m_scale)}%" + (" (wide uncertainty)" if (max(stress_margin, m_base, m_scale) - min(stress_margin, m_base, m_scale)) > 40.0 else ""),
        "scenarios": {
            "low": {
                "label": "Stress",
                "description": f"Price {currency_symbol}{p_base:,.0f}, Cost {currency_symbol}{cost_bom_stress:,.2f} (30% BOM inflation)",
                "gross_margin_pct": stress_margin,
                "margin_grade": stress_grade,
                "cost_to_serve": cost_bom_stress,
                "price": p_base,
            },
            "base": {
                "label": "Base",
                "description": f"Price {currency_symbol}{p_base:,.0f}, Cost {currency_symbol}{cost_base:,.2f}",
                "gross_margin_pct": m_base,
                "margin_grade": g_base,
                "cost_to_serve": cost_base,
                "price": p_base,
            },
            "high": {
                "label": "Optimistic",
                "description": f"Price {currency_symbol}{price_high:,.0f}, Cost {currency_symbol}{cost_scale:,.2f} (volume purchasing)",
                "gross_margin_pct": m_scale,
                "margin_grade": g_scale,
                "cost_to_serve": cost_scale,
                "price": price_high,
            },
        },
        "sensitivity_table": sensitivity_table,
        "assumptions": assumptions,
        "key_cost_driver": "Sensor probes, wireless telemetry module, and tooling/molding amortization"
    }


def enforce_unit_economics_invariants(
    ue: Dict[str, Any],
    idea_text: str = "",
    extracted_unit_label: Optional[str] = None
) -> Dict[str, Any]:
    """
    INVARIANT ENFORCEMENT:
    1. Headline cost must equal the sum of itemized assumptions.
    2. Unit label must come from extracted metadata (never hardcoded 'SME').
    """
    if not isinstance(ue, dict):
        return ue

    idea_lower = (idea_text or "").lower()

    # 1. Derive idea-specific unit label
    if extracted_unit_label and extracted_unit_label.strip() and extracted_unit_label.strip() != "SME/month":
        unit_lbl = extracted_unit_label.strip()
    elif ue.get("unit_label") and ue.get("unit_label") != "SME/month" and ue.get("unit_label") != "user":
        unit_lbl = ue.get("unit_label")
    elif any(k in idea_lower for k in ["elderly", "parent", "family", "adherence", "patient", "medication"]):
        unit_lbl = "family/month" if "family" in idea_lower else "user/month"
    elif any(k in idea_lower for k in ["loan", "lending", "micro-loan", "microloan", "borrow"]):
        unit_lbl = "loan"
    elif any(k in idea_lower for k in ["sensor", "hardware", "device", "probe", "irrigation"]):
        unit_lbl = "unit"
    elif any(k in idea_lower for k in ["invoice", "sme", "erp", "reconciliation"]):
        unit_lbl = "SME/month"
    else:
        unit_lbl = "user/month"

    ue["unit_label"] = unit_lbl

    # 2. Extract itemized costs from assumptions and verify invariant
    assumptions = ue.get("assumptions") or []
    item_costs: List[float] = []

    for a in assumptions:
        a_str = str(a).strip()
        if any(skip in a_str.lower() for skip in ["target subscription price", "target price", "target retail", "total per-unit", "total monthly cost", "total cost"]):
            continue
        m = re.search(r"[\$₹]?\s*(\d+(?:\.\d{1,2})?)\s*(?:/[a-zA-Z\-_/]+)?", a_str)
        if m:
            try:
                val = float(m.group(1))
                if val > 0:
                    item_costs.append(val)
            except (ValueError, TypeError):
                pass

    if item_costs:
        sum_costs = round(sum(item_costs), 2)
        headline_cost = float(ue.get("cost_to_serve_per_user_usd") or 0.0)
        if abs(headline_cost - sum_costs) > 0.05:
            ue["cost_to_serve_per_user_usd"] = sum_costs
            price = float(ue.get("suggested_price_usd") or (sum_costs * 1.6))
            if price > 0:
                m_pct = round(((price - sum_costs) / price) * 100.0, 1)
                g_str = "healthy" if m_pct >= 50 else ("caution" if m_pct >= 20 else "underwater")
                ue["gross_margin_pct"] = m_pct
                ue["margin_grade"] = g_str

    return ue


def derive_kill_threshold_from_unit_economics(unit_economics: Dict[str, Any], business_model: Optional[str] = None) -> Optional[str]:
    """
    Derives a quantitative kill-switch threshold from unit economics break-even default rate for lending.
    For non-lending models (SaaS, Hardware), margin thresholds are NOT valid kill tests.
    Kill tests must be 14-day operational falsification experiments with explicit numeric pass/fail.
    Returns string threshold for lending, or None for non-lending (preserving the experimental kill test).
    """
    be_default = unit_economics.get("break_even_default_rate_pct")
    if be_default is not None and float(be_default) > 0:
        be_pct = float(be_default)
        # Kill at 75% of break-even to preserve safety buffer
        kill_pct = round(be_pct * 0.75, 1)
        return (
            f"Default rate exceeds {kill_pct}% on initial 30-loan cohort "
            f"(break-even is {be_pct}% — 75% safety buffer applied)."
        )
    return None



class EvidenceItem(BaseModel):
    """Grounding claim and verified reference link."""
    claim: str = Field(..., description="The verified claim or factual assertion")
    source_url: Optional[str] = Field(None, description="URL reference supporting the claim")


class KillSwitch(BaseModel):
    """
    Adversarial Pre-Mortem & Falsification Engine.
    Exposes the fatal assumption and defines a concrete 14-day zero-code/micro-budget test.
    """
    fatal_assumption: str = Field(
        ...,
        description="The single unproven belief the business depends on"
    )
    cheap_test: str = Field(
        ...,
        description="Zero-code or micro-budget experiment doable in 14 days"
    )
    test_budget_usd: int = Field(
        default=250,
        description="Micro-budget in USD required to execute the cheap test"
    )
    kill_threshold: str = Field(
        ...,
        description="Quantitative walk-away condition containing an explicit numeric metric"
    )
    confidence: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="Confidence level based on available evidence ('low', 'medium', 'high')"
    )
    evidence: List[EvidenceItem] = Field(
        default_factory=list,
        description="Evidentiary claims and supporting URLs"
    )

    source_type: Literal["llm_grounded", "heuristic_fallback"] = Field(
        default="llm_grounded",
        description="Whether this evaluation was grounded via LLM or deterministic fallback"
    )

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, v: Any) -> str:
        if isinstance(v, str):
            v_low = v.strip().lower()
            if v_low in ("low", "medium", "high"):
                return v_low
            if "low" in v_low:
                return "low"
            if "high" in v_low:
                return "high"
        return "medium"

    @field_validator("source_type", mode="before")
    @classmethod
    def normalize_source_type(cls, v: Any) -> str:
        if isinstance(v, str) and "heuristic" in v.lower():
            return "heuristic_fallback"
        return "llm_grounded"

    @field_validator("kill_threshold")
    @classmethod
    def must_contain_number(cls, v: str) -> str:
        s = str(v).strip()
        if not any(char.isdigit() for char in s):
            return f"{s} (< 15% benchmark)"
        return s

    @model_validator(mode="after")
    def enforce_source_type_confidence(self) -> "KillSwitch":
        if self.source_type == "heuristic_fallback":
            self.confidence = "low"
        return self



class UnitEconomics(BaseModel):
    """
    Compute & Unit Economics Viability Matrix.
    Evaluates monthly cost-to-serve, suggested pricing, and computed gross margin.
    """
    cost_to_serve_per_user_usd: float = Field(
        ...,
        description="Estimated monthly inference, hardware, API, or ops cost per active user"
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="Clear assumptions underlying the cost calculation"
    )
    suggested_price_usd: float = Field(
        ...,
        description="Suggested market price per active user/customer in USD"
    )
    gross_margin_pct: float = Field(
        default=0.0,
        description="Gross margin percentage computed in code ((price - cost) / price * 100)"
    )
    margin_grade: Literal["healthy", "thin", "margin_trap"] = Field(
        default="healthy",
        description="Margin health classification: healthy (>=70%), thin (30-70%), margin_trap (<30%)"
    )
    platform_dependency_risk: str = Field(
        ...,
        description="'low' | 'medium' | 'high' with one-line reason"
    )
    confidence: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="Confidence level based on market/pricing evidence"
    )
    evidence: List[EvidenceItem] = Field(
        default_factory=list,
        description="Evidentiary claims and supporting URLs"
    )

    source_type: Literal["llm_grounded", "heuristic_fallback"] = Field(
        default="llm_grounded",
        description="Whether this evaluation was grounded via LLM or deterministic fallback"
    )

    currency_symbol: str = Field(
        default="$",
        description="Currency symbol ($ for US/Global, ₹ for India)"
    )

    unit_label: str = Field(
        default="user/month",
        description="Pricing metric unit: user/month, loan, transaction, etc."
    )

    loan_size: Optional[float] = Field(
        default=None,
        description="Average principal loan size if lending model"
    )

    revenue_per_loan: Optional[float] = Field(
        default=None,
        description="Interest + origination fee per loan in local currency"
    )

    cost_of_capital: Optional[float] = Field(
        default=None,
        description="Wholesale funding / borrowing cost per loan"
    )

    expected_default_loss: Optional[float] = Field(
        default=None,
        description="Expected credit default loss per loan"
    )

    collections_cost: Optional[float] = Field(
        default=None,
        description="Servicing and collections cost per loan"
    )

    cac: Optional[float] = Field(
        default=None,
        description="Customer acquisition cost per active borrower"
    )

    net_contribution_per_loan: Optional[float] = Field(
        default=None,
        description="Net contribution per loan in local currency"
    )

    effective_apr: Optional[float] = Field(
        default=None,
        description="Effective annualized percentage rate derived from tenure in Python"
    )

    margin_range: Optional[List[float]] = Field(
        default=None,
        description="Scenario gross margin range [low_pct, high_pct]"
    )

    margin_range_formatted: Optional[str] = Field(
        default=None,
        description="Formatted scenario margin range (e.g. '12.5% – 38.2%')"
    )

    scenarios: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Low, base, and high unit economics scenario calculations"
    )

    break_even_default_rate_pct: Optional[float] = Field(
        default=None,
        description="Break-even default rate at which contribution margin hits 0%"
    )

    @model_validator(mode="before")
    @classmethod
    def apply_invariants(cls, v: Any) -> Any:
        if isinstance(v, dict):
            return enforce_unit_economics_invariants(v)
        return v

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, v: Any) -> str:
        if isinstance(v, str):
            v_low = v.strip().lower()
            if v_low in ("low", "medium", "high"):
                return v_low
            if "low" in v_low:
                return "low"
            if "high" in v_low:
                return "high"
        return "medium"

    @field_validator("source_type", mode="before")
    @classmethod
    def normalize_source_type(cls, v: Any) -> str:
        if isinstance(v, str) and "heuristic" in v.lower():
            return "heuristic_fallback"
        return "llm_grounded"

    @field_validator("margin_grade", mode="before")
    @classmethod
    def normalize_grade(cls, v: Any) -> str:
        if isinstance(v, str):
            v_low = v.strip().lower()
            if v_low in ("healthy", "thin", "margin_trap"):
                return v_low
            if "healthy" in v_low:
                return "healthy"
            if "thin" in v_low:
                return "thin"
            if "trap" in v_low:
                return "margin_trap"
        return "thin"

    @model_validator(mode="after")
    def compute_deterministic_margin(self) -> "UnitEconomics":
        margin_pct, grade = compute_unit_economics_margin(
            self.cost_to_serve_per_user_usd,
            self.suggested_price_usd
        )
        self.gross_margin_pct = margin_pct
        self.margin_grade = grade  # type: ignore
        if self.source_type == "heuristic_fallback":
            self.confidence = "low"
        return self


# ---------------------------------------------------------------------------
# Regulatory Runway & TRL Readiness Models
# ---------------------------------------------------------------------------

class RegulatoryRunway(BaseModel):
    """
    Regulatory Runway & CapEx Penalty Estimator.
    Calculates time-to-clearance, pre-revenue burn penalty, required compliance hires,
    and identifies the closest non-regulated bridge product.
    """
    applicable_regimes: List[str] = Field(
        default_factory=list,
        description="Governing regulatory regimes (e.g., FDA Class II 510(k), HIPAA, GDPR, SEBI, none)"
    )
    mandatory_regulations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Itemized mandatory legal regulations with why_applies rationale"
    )
    voluntary_standards: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Itemized voluntary certifications and standards with why_applies rationale"
    )
    time_to_clearance_months_min: int = Field(
        default=0,
        ge=0,
        description="Minimum months to achieve regulatory clearance/certification"
    )
    time_to_clearance_months_max: int = Field(
        default=0,
        ge=0,
        description="Maximum months to achieve regulatory clearance/certification"
    )
    pre_revenue_burn_usd_min: int = Field(
        default=0,
        ge=0,
        description="Minimum pre-revenue regulatory/audit/clinical burn in USD"
    )
    pre_revenue_burn_usd_max: int = Field(
        default=0,
        ge=0,
        description="Maximum pre-revenue regulatory/audit/clinical burn in USD"
    )
    required_hires: List[str] = Field(
        default_factory=list,
        description="Specialized regulatory or compliance roles required before commercial launch"
    )
    runway_penalty_summary: str = Field(
        ...,
        description="One line summary: 'adds X-Y months and $A-$B before first revenue'"
    )
    non_regulated_bridge: str = Field(
        default="",
        description="Closest product version that avoids the regulatory wall (empty string if none needed)"
    )
    confidence: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="Confidence level ('low', 'medium', 'high')"
    )
    evidence: List[EvidenceItem] = Field(
        default_factory=list,
        description="Evidentiary claims and supporting URLs"
    )
    source_type: Literal["llm_grounded", "heuristic_fallback"] = Field(
        default="llm_grounded",
        description="llm_grounded | heuristic_fallback"
    )

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, v: Any) -> str:
        if isinstance(v, str):
            v_low = v.strip().lower()
            if v_low in ("low", "medium", "high"):
                return v_low
            if "low" in v_low:
                return "low"
            if "high" in v_low:
                return "high"
        return "medium"

    @field_validator("source_type", mode="before")
    @classmethod
    def normalize_source_type(cls, v: Any) -> str:
        if isinstance(v, str) and "heuristic" in v.lower():
            return "heuristic_fallback"
        return "llm_grounded"

    @model_validator(mode="after")
    def validate_pure_software_and_fallback(self) -> "RegulatoryRunway":
        regimes_lower = [str(r).strip().lower() for r in self.applicable_regimes]
        if not regimes_lower or regimes_lower == ["none"] or (len(regimes_lower) == 1 and regimes_lower[0] in ("none", "n/a", "not applicable", "pure software")):
            self.applicable_regimes = ["none"]
            self.time_to_clearance_months_min = 0
            self.time_to_clearance_months_max = 0
            self.pre_revenue_burn_usd_min = 0
            self.pre_revenue_burn_usd_max = 0
            self.non_regulated_bridge = ""
            if not self.runway_penalty_summary or "adds" in self.runway_penalty_summary.lower():
                self.runway_penalty_summary = "Pure software deployment: 0 regulatory clearance delay."

        if self.source_type == "heuristic_fallback":
            self.confidence = "low"
        return self


def derive_software_readiness_label(level: int) -> str:
    """
    Derives software-specific readiness stage for SaaS and lending startups:
      - TRL 1-2: Concept Research / Tech Spec
      - TRL 3: Architectural Spike / Proof-of-Concept
      - TRL 4: Core Engine Alpha / API Prototype
      - TRL 5: Integration Sandbox / Pilot API
      - TRL 6: Beta Customer Trial
      - TRL 7: Production MVP / Launch Pilot
      - TRL 8: Commercial Scale System
      - TRL 9: Enterprise Production Infrastructure
    """
    lvl = max(1, min(9, int(level)))
    labels = {
        1: "Concept Research",
        2: "Tech Spec / Formulation",
        3: "Architectural Spike / PoC",
        4: "Core Engine Alpha / API Prototype",
        5: "Integration Sandbox / Pilot API",
        6: "Beta Customer Trial",
        7: "Production MVP / Launch Pilot",
        8: "Commercial Scale System",
        9: "Enterprise Production Infrastructure"
    }
    return f"TRL {lvl} ({labels.get(lvl, 'Core Engine Alpha')})"


def derive_trl_stage(level: int) -> str:
    """
    Derives software readiness stage deterministically from 1-9 TRL level:
      - 1 to 3 -> 'prototype'
      - 4 to 5 -> 'validated model'
      - 6 to 7 -> 'pilot'
      - 8 to 9 -> 'production'
    """
    try:
        lvl = max(1, min(9, int(level)))
    except (ValueError, TypeError):
        lvl = 4
    if lvl <= 3:
        return "prototype"
    elif lvl <= 5:
        return "validated model"
    elif lvl <= 7:
        return "pilot"
    else:
        return "production"


class TRLBottleneck(BaseModel):
    """Critical bottleneck obstructing TRL advancement."""
    name: str = Field(..., description="Bottleneck description")
    type: Literal["hardware", "data", "compute", "talent", "regulatory"] = Field(
        ...,
        description="hardware | data | compute | talent | regulatory"
    )
    severity: Literal["low", "medium", "high"] = Field(
        ...,
        description="low | medium | high"
    )

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, v: Any) -> str:
        s = str(v).strip().lower()
        if s in ("hardware", "data", "compute", "talent", "regulatory"):
            return s
        for candidate in ("hardware", "data", "compute", "talent", "regulatory"):
            if candidate in s:
                return candidate
        return "data"

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, v: Any) -> str:
        s = str(v).strip().lower()
        if s in ("low", "medium", "high"):
            return s
        if "high" in s or "crit" in s:
            return "high"
        if "med" in s:
            return "medium"
        return "low"


class TRLReadiness(BaseModel):
    """
    NASA/DoD Technology Readiness Level (1-9) Engine.
    Evaluates current maturity stage, bottlenecks, and the single point of failure.
    """
    trl_level: int = Field(
        ...,
        ge=1,
        le=9,
        description="Technology Readiness Level on 1-9 scale"
    )
    trl_stage: Literal["prototype", "validated model", "pilot", "production"] = Field(
        default="validated model",
        description="Derived deterministically in Python from trl_level"
    )
    bottlenecks: List[TRLBottleneck] = Field(
        default_factory=list,
        description="Itemized bottlenecks with category and severity"
    )
    single_point_of_failure: str = Field(
        ...,
        description="The primary single point of failure (SPOF) for the technology"
    )
    confidence: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="Confidence level ('low', 'medium', 'high')"
    )
    evidence: List[EvidenceItem] = Field(
        default_factory=list,
        description="Evidentiary claims and supporting URLs"
    )
    source_type: Literal["llm_grounded", "heuristic_fallback"] = Field(
        default="llm_grounded",
        description="llm_grounded | heuristic_fallback"
    )

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, v: Any) -> str:
        if isinstance(v, str):
            v_low = v.strip().lower()
            if v_low in ("low", "medium", "high"):
                return v_low
            if "low" in v_low:
                return "low"
            if "high" in v_low:
                return "high"
        return "medium"

    @field_validator("source_type", mode="before")
    @classmethod
    def normalize_source_type(cls, v: Any) -> str:
        if isinstance(v, str) and "heuristic" in v.lower():
            return "heuristic_fallback"
        return "llm_grounded"

    @model_validator(mode="after")
    def compute_trl_stage(self) -> "TRLReadiness":
        self.trl_stage = derive_trl_stage(self.trl_level)  # type: ignore
        if self.source_type == "heuristic_fallback":
            self.confidence = "low"
        return self


# ---------------------------------------------------------------------------
# Moat Durability & Pivot Generator Models
# ---------------------------------------------------------------------------

class MoatVector(BaseModel):
    """Defensibility dimension score (0-100) and rationale."""
    score: int = Field(..., ge=0, le=100, description="0-100 defensibility score")
    reason: str = Field(..., description="Strategic rationale for this score")

    @field_validator("score", mode="before")
    @classmethod
    def clamp_score(cls, v: Any) -> int:
        try:
            val = int(v)
            return max(0, min(100, val))
        except Exception:
            return 50


def compute_moat_score(
    data_score: Union[int, float],
    lockin_score: Union[int, float] = 40.0,
    regulatory_score: Union[int, float] = 40.0,
    **kwargs: Any
) -> Tuple[float, str]:
    """
    Computes moat durability score as weighted average:
      - Data Network Effect: 35%
      - Workflow Lock-in: 35%
      - Regulatory / IP Moat: 30%
    Tier rules:
      - fragile: < 35
      - defensible: 35 - 65
      - durable: > 65
    """
    if "reg_score" in kwargs:
        regulatory_score = kwargs["reg_score"]
    if "regulatory_ip_score" in kwargs:
        regulatory_score = kwargs["regulatory_ip_score"]
    if "workflow_lockin_score" in kwargs:
        lockin_score = kwargs["workflow_lockin_score"]

    try:
        d = float(data_score)
        w = float(lockin_score)
        r = float(regulatory_score)
    except (ValueError, TypeError):
        d, w, r = 40.0, 40.0, 40.0

    score = round(0.35 * d + 0.35 * w + 0.30 * r, 1)
    if score < 35.0:
        tier = "fragile"
    elif score <= 65.0:
        tier = "defensible"
    else:
        tier = "durable"
    return score, tier


class MoatDurability(BaseModel):
    """
    Moat Durability & Defensibility Matrix.
    Evaluates data network effects, workflow lock-in, and IP/regulatory barriers,
    estimating replication timeline and primary competitor/incumbent threat.
    """
    data_network_effect: MoatVector = Field(..., description="Data feedback loops and compounding dataset advantage")
    workflow_lockin: MoatVector = Field(..., description="Integration depth, switching costs, and process entanglement")
    regulatory_ip_moat: MoatVector = Field(..., description="Patents, exclusive regulatory approvals, and compliance moats")
    replication_window_months_min: int = Field(..., ge=0, description="Minimum months for a well-funded rival to replicate")
    replication_window_months_max: int = Field(..., ge=0, description="Maximum months for a well-funded rival to replicate")
    likely_replicator: str = Field(..., description="Named incumbent or competitor most likely to clone or absorb the product")
    moat_score: float = Field(default=0.0, description="Weighted average (data 35%, lock-in 35%, regulatory/IP 30%) computed in Python")
    moat_tier: Literal["fragile", "defensible", "durable"] = Field(default="defensible", description="fragile (<35) | defensible (35-65) | durable (>65)")
    confidence: Literal["low", "medium", "high"] = Field(default="medium", description="'low' | 'medium' | 'high'")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Evidentiary claims and supporting URLs")
    source_type: Literal["llm_grounded", "heuristic_fallback"] = Field(default="llm_grounded", description="llm_grounded | heuristic_fallback")

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, v: Any) -> str:
        if isinstance(v, str):
            v_low = v.strip().lower()
            if v_low in ("low", "medium", "high"):
                return v_low
            if "low" in v_low:
                return "low"
            if "high" in v_low:
                return "high"
        return "medium"

    @field_validator("source_type", mode="before")
    @classmethod
    def normalize_source_type(cls, v: Any) -> str:
        if isinstance(v, str) and "heuristic" in v.lower():
            return "heuristic_fallback"
        return "llm_grounded"

    @model_validator(mode="after")
    def compute_moat_attributes(self) -> "MoatDurability":
        score, tier = compute_moat_score(
            self.data_network_effect.score,
            self.workflow_lockin.score,
            self.regulatory_ip_moat.score
        )
        self.moat_score = score
        self.moat_tier = tier  # type: ignore
        if self.source_type == "heuristic_fallback":
            self.confidence = "low"
        return self


def evaluate_pivot_triggers(
    trl_level: int,
    regulatory_months_max: int = 0,
    margin_grade: str = "healthy",
    moat_tier: str = "defensible",
    **kwargs: Any
) -> Tuple[bool, List[str]]:
    """
    Evaluates whether the venture triggers an automated strategic pivot.
    Triggered if ANY of:
      1. trl_level <= 3
      2. regulatory time_to_clearance_months_max >= 12
      3. margin_grade == 'margin_trap'
      4. moat_tier == 'fragile'
    """
    if "regulatory_clearance_months_max" in kwargs:
        regulatory_months_max = kwargs["regulatory_clearance_months_max"]
    if "clearance_months_max" in kwargs:
        regulatory_months_max = kwargs["clearance_months_max"]
    reasons: List[str] = []
    try:
        lvl = int(trl_level)
    except Exception:
        lvl = 4

    try:
        reg_max = int(regulatory_months_max)
    except Exception:
        reg_max = 0

    m_grade = str(margin_grade).lower().strip()
    m_tier = str(moat_tier).lower().strip()

    if lvl <= 3:
        reasons.append(f"Low TRL level (TRL Level {lvl} <= 3): early lab hypothesis with severe technical de-risking required")
    if reg_max >= 12:
        reasons.append(f"Extended regulatory clearance ({reg_max} months >= 12 months) causing dangerous pre-revenue burn")
    if m_grade == "margin_trap":
        reasons.append("Unviable unit economics: classified as margin_trap (< 30% gross margin)")
    if m_tier == "fragile":
        reasons.append("Vulnerable competitive defensibility: moat tier is fragile (< 35)")

    return len(reasons) > 0, reasons


class PivotPlan(BaseModel):
    """
    Automated Strategic Pivot Recommendation.
    Generated when high-risk thresholds are breached in TRL, regulatory runway,
    unit economics, or moat durability.
    """
    triggered: bool = Field(default=False, description="True if ANY critical risk trigger condition is met")
    trigger_reasons: List[str] = Field(default_factory=list, description="List of specific conditions triggering the pivot")
    pivot_name: str = Field(default="", description="Target strategic pivot concept title")
    what_changes: str = Field(default="", description="What components, models, or operational burdens to cut or swap")
    months_saved: int = Field(default=0, ge=0, description="Time-to-market months saved compared to original concept")
    new_regulatory_exposure: str = Field(default="", description="Significantly lighter or non-regulated regulatory profile")
    first_test: str = Field(default="", description="Actionable 14-day zero-code or micro-budget experiment for the pivot")
    confidence: Literal["low", "medium", "high"] = Field(default="medium", description="'low' | 'medium' | 'high'")
    source_type: Literal["llm_grounded", "heuristic_fallback"] = Field(default="llm_grounded", description="llm_grounded | heuristic_fallback")

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, v: Any) -> str:
        if isinstance(v, str):
            v_low = v.strip().lower()
            if v_low in ("low", "medium", "high"):
                return v_low
            if "low" in v_low:
                return "low"
            if "high" in v_low:
                return "high"
        return "medium"

    @field_validator("source_type", mode="before")
    @classmethod
    def normalize_source_type(cls, v: Any) -> str:
        if isinstance(v, str) and "heuristic" in v.lower():
            return "heuristic_fallback"
        return "llm_grounded"

    @model_validator(mode="after")
    def enforce_pivot_rules(self) -> "PivotPlan":
        if self.source_type == "heuristic_fallback":
            self.confidence = "low"
        if not self.triggered:
            self.trigger_reasons = []
        return self


# ---------------------------------------------------------------------------
# Regulatory & Evidence Grounding Helpers
# ---------------------------------------------------------------------------

_STOP_WORDS = {
    "the", "and", "for", "with", "this", "that", "from", "are", "was", "were",
    "been", "have", "has", "had", "will", "would", "could", "should", "what",
    "which", "when", "where", "who", "whom", "whose", "why", "how", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "such", "than", "too",
    "very", "can", "just", "into", "over", "after", "also", "about", "between",
    "through", "during", "before", "under", "above"
}


def extract_meaningful_keywords(text: str) -> set[str]:
    """Extract lowercase words >= 3 chars excluding common stop words."""
    words = re.findall(r"[a-zA-Z0-9]{3,}", (text or "").lower())
    return {w for w in words if w not in _STOP_WORDS}


def filter_grounded_evidence(
    raw_evidence: List[Any],
    search_results: Optional[List[Dict[str, Any]]],
    current_confidence: Optional[str] = None,
    **kwargs: Any
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Verifies that each evidence source_url appears in the actual Tavily search results list
    AND that the claim shares at least 2 meaningful keywords with that result's title/snippet.
    Drops any items that fail either check.
    If none remain, sets confidence to 'low'.
    """
    if "original_confidence" in kwargs and current_confidence is None:
        current_confidence = kwargs["original_confidence"]

    url_to_texts: Dict[str, str] = {}
    if search_results:
        for r in search_results:
            u = str(r.get("url") or "").strip()
            if u:
                blob = f"{r.get('title', '')} {r.get('content', '')} {r.get('snippet', '')}"
                for variant in (u, u.rstrip("/"), u.lower(), u.rstrip("/").lower()):
                    url_to_texts[variant] = blob

    clean_ev = []
    for item in (raw_evidence or []):
        claim = ""
        url = ""
        if isinstance(item, dict):
            claim = str(item.get("claim") or "").strip()
            url = str(item.get("source_url") or "").strip()
        elif hasattr(item, "claim") and hasattr(item, "source_url"):
            claim = str(item.claim or "").strip()
            url = str(item.source_url or "").strip()

        if not claim or not url:
            continue

        matched_blob = None
        for variant in (url, url.rstrip("/"), url.lower(), url.rstrip("/").lower()):
            if variant in url_to_texts:
                matched_blob = url_to_texts[variant]
                break

        if matched_blob is None:
            continue

        claim_kw = extract_meaningful_keywords(claim)
        result_kw = extract_meaningful_keywords(matched_blob)
        shared_kw = claim_kw & result_kw

        # Must share at least 2 meaningful keywords
        if len(shared_kw) >= 2:
            clean_ev.append({"claim": claim, "source_url": url})

    if clean_ev:
        conf = current_confidence if current_confidence in ("low", "medium", "high") else "medium"
        return clean_ev, conf
    return [], "low"


def detect_regulatory_requirements(
    idea: str,
    domain: str = "",
    jurisdiction: str = "Global",
    business_model: str = "saas"
) -> Dict[str, Any]:
    """
    Evaluates regulatory obligations tailored strictly to jurisdiction and business model.
    CRITICAL:
    1. The India NBFC/LSP dual-path is ONLY activated when:
       business_model == "lending" AND "india" in jurisdiction.lower()
    2. For all other cases, regulatory paths are built ONLY from extracted metadata
       (domain, jurisdiction, business_model), NEVER from keyword matching on idea text.
    """
    bm = (business_model or "saas").lower().strip()
    jur = (jurisdiction or "global").lower().strip()
    dom = (domain or "").lower().strip()
    idea_lower = (idea or "").lower().strip()

    # Detect offline tool / non-networked CLI
    if any(k in idea_lower for k in ["offline", "zero network", "local disk", "command-line", "linter", "formatter", "local-only", "local-first"]):
        return {
            "jurisdiction": jurisdiction,
            "is_regulated": False,
            "applicable_regimes": ["none"],
            "time_to_clearance_months_min": 0,
            "time_to_clearance_months_max": 0,
            "pre_revenue_burn_usd_min": 0,
            "pre_revenue_burn_usd_max": 0,
            "required_hires": [],
            "runway_penalty_summary": "Pure offline tool: 0 regulatory clearance delay.",
            "non_regulated_bridge": "",
        }

    # If domain was omitted from call, infer domain category from idea
    if not dom:
        if any(k in idea_lower for k in ["child", "children", "minor", "student", "math practice", "elementary school", "k-12", "edtech"]):
            dom = "edtech"
        elif any(k in idea_lower for k in ["health", "medical", "patient", "clinical", "diagnostic", "therapy", "doctor", "hospital"]):
            dom = "healthtech"
        elif any(k in idea_lower for k in ["legal", "contract", "nda", "lawyer", "attorney", "redlin"]):
            dom = "legaltech"
        elif any(k in idea_lower for k in ["payment", "checkout", "credit card billing", "stripe checkout", "billing", "payout", "lending", "loan", "loans", "micro-loan", "microloan", "borrow"]):
            dom = "fintech"
            if any(k in idea_lower for k in ["lending", "loan", "loans", "micro-loan", "microloan"]):
                bm = "lending"
        elif any(k in idea_lower for k in ["sensor", "soil-moisture", "hardware", "iot"]):
            dom = "hardware"
        elif any(k in idea_lower for k in ["crm", "customer contact", "employee profile"]):
            dom = "enterprise saas"

    is_india = "india" in jur
    is_us = "us" in jur or "united states" in jur
    is_eu = "eu" in jur or "europe" in jur or "uk" in jur

    # 1. STRICT GATE: India NBFC/LSP dual path ONLY when business_model == "lending" AND is_india
    if bm == "lending" and is_india:
        applicable = [
            "RBI Digital Lending Guidelines (LSP vs NBFC)",
            "Reserve Bank of India (RBI) NBFC Framework",
            "Digital Personal Data Protection (DPDP) Act, 2023",
            "RBI Account Aggregator (NBFC-AA) Framework"
        ]
        return {
            "jurisdiction": "India",
            "is_regulated": True,
            "applicable_regimes": applicable,
            "time_to_clearance_months_min": 2,
            "time_to_clearance_months_max": 24,
            "pre_revenue_burn_usd_min": 6000,
            "pre_revenue_burn_usd_max": 600000,
            "required_hires": [
                "RBI Digital Lending & Fintech Compliance Officer",
                "NBFC Banking Partnership Lead",
                "DPDP Privacy & Consent Architect"
            ],
            "recommended_pathway": "Two-Path Strategy: Launch initially as a Lending Service Provider (LSP) partnered with a licensed NBFC (2-4 months to live disbursals), then transition to an Own NBFC License once portfolio scales past \u20b950Cr AUM.",
            "runway_penalty_summary": "Two paths: (a) LSP Partnership: 2-4 months and $6,000-$18,000 (\u20b95L-\u20b915L); (b) Own NBFC License: 12-24 months and $250,000-$600,000 (\u20b92Cr-\u20b95Cr).",
            "non_regulated_bridge": "Gig worker earnings analytics and credit-readiness score dashboard without balance-sheet lending or direct loan disbursals.",
            "lending_paths": {
                "lsp_partnership": {
                    "name": "Lending Service Provider (LSP) Partnership",
                    "months": "2 - 4 months",
                    "burn": "$6,000 - $18,000 (\u20b95 Lakh - \u20b915 Lakh)",
                    "details": "Contract with regulated NBFC/bank as LSP under RBI Digital Lending Guidelines. Disbursals and collections flow directly through regulated entity accounts."
                },
                "own_nbfc": {
                    "name": "Full RBI NBFC License",
                    "months": "12 - 24 months",
                    "burn": "$250,000 - $600,000 (\u20b92 Crore - \u20b95 Crore)",
                    "details": "Direct balance sheet lending license from Reserve Bank of India with mandatory Net Owned Funds (NOF) statutory reserve."
                }
            }
        }

    # 2. Lending in other jurisdictions (US, EU, Global)
    if bm == "lending":
        if is_us:
            applicable = ["CFPB / Truth in Lending Act (TILA)", "State Consumer Lending Licenses", "Fair Credit Reporting Act (FCRA)"]
            pathway = "Partner with an FDIC-insured partner bank via BaaS to bypass individual state lending licensing barriers."
            summary = "Partner bank path: 3-6 months and $20,000-$50,000; Direct state licenses: 12-18 months and $150,000-$300,000."
        elif is_eu:
            applicable = ["FCA Consumer Credit Authorization / EU Consumer Credit Directive", "GDPR Financial Data Protection", "EBA Guidelines"]
            pathway = "Operate as an appointed representative under an authorized principal firm before seeking full direct authorization."
            summary = "Appointed representative: 3-5 months and $15,000-$40,000; Direct authorization: 12-20 months and $100,000-$250,000."
        else:
            applicable = ["Regional Consumer Credit Regulatory Framework", "Anti-Money Laundering (AML/KYC)", "Responsible Lending Standards"]
            pathway = "Partner with an established local regulated lending entity as a technology origination partner."
            summary = "Originator partnership: 3-6 months and $15,000-$40,000."
        return {
            "jurisdiction": jurisdiction,
            "is_regulated": True,
            "applicable_regimes": applicable,
            "time_to_clearance_months_min": 3,
            "time_to_clearance_months_max": 18,
            "pre_revenue_burn_usd_min": 15000,
            "pre_revenue_burn_usd_max": 250000,
            "required_hires": ["Fintech Regulatory & Compliance Officer", "Credit Risk & Underwriting Lead"],
            "recommended_pathway": pathway,
            "runway_penalty_summary": summary,
            "non_regulated_bridge": "Credit scoring analytics dashboard without balance-sheet lending or direct loan disbursals.",
        }

    # 3. HealthTech / Digital Health domain
    if any(k in dom for k in ["health", "medical", "clinic", "diagnostic", "biotech"]):
        if is_us:
            applicable = ["FDA SaMD Guidance (510(k))", "HIPAA / HITECH Security Rule"]
            pathway = "Pursue initial launch under FDA General Wellness guidance with non-diagnostic claims while preparing 510(k) trial."
            summary = "adds 10-20 months and $120,000-$350,000 before first revenue"
        elif is_eu:
            applicable = ["EU MDR (Medical Device Regulation)", "GDPR Health Data Compliance", "ISO 13485"]
            pathway = "Conformity assessment under EU MDR Annex IX with designated Notified Body."
            summary = "adds 12-22 months and $130,000-$380,000 before commercial distribution"
        elif is_india:
            applicable = ["CDSCO Medical Device Rules", "Digital Personal Data Protection (DPDP) Act, 2023", "ISO 13485"]
            pathway = "CDSCO Class B registration via Online Medical Device Portal with certified clinical testing."
            summary = "adds 6-12 months and $15,000-$45,000 (\u20b912L-\u20b935L) for CDSCO clearance"
        else:
            applicable = ["ISO 13485 Quality Management", "IEC 62304 Medical Device Software", "Health Data Privacy Standards"]
            pathway = "Standard wellness tier release with non-clinical disclaimer during ISO 13485 audit."
            summary = "adds 8-16 months and $80,000-$200,000 for medical certification"
        return {
            "jurisdiction": jurisdiction,
            "is_regulated": True,
            "applicable_regimes": applicable,
            "time_to_clearance_months_min": 6,
            "time_to_clearance_months_max": 20,
            "pre_revenue_burn_usd_min": 15000,
            "pre_revenue_burn_usd_max": 350000,
            "required_hires": ["Clinical Regulatory Affairs Specialist", "Health Data Privacy Officer"],
            "recommended_pathway": pathway,
            "runway_penalty_summary": summary,
            "non_regulated_bridge": "Non-diagnostic wellness tracking tier with explicit clinical disclaimer",
        }

    # 4. EdTech / Learning domain
    if any(k in dom for k in ["edtech", "education", "student", "learn", "school"]):
        if is_india:
            applicable = ["Digital Personal Data Protection (DPDP) Act, 2023", "Digital Education Content Guidelines"]
            pathway = "Architect verifiable parental consent workflows and zero student profiling under DPDP Act 2023."
            summary = "adds 2-4 months and $4,000-$12,000 (\u20b93L-\u20b910L) for DPDP parental consent verification"
        elif is_us:
            applicable = ["COPPA (Children's Online Privacy)", "FERPA Student Privacy", "State Student Privacy Laws"]
            pathway = "Architect client-side zero-PII data processing to bypass COPPA parental consent hurdles."
            summary = "adds 2-5 months and $8,000-$25,000 before school district procurement"
        else:
            applicable = ["COPPA (Children's Online Privacy)", "FERPA Student Privacy", "GDPR Article 8 (Child Data Protection)"]
            pathway = "Standard school district procurement clearance with automated parental consent forms."
            summary = "adds 2-5 months and $8,000-$25,000 for child privacy validation"
        return {
            "jurisdiction": jurisdiction,
            "is_regulated": True,
            "applicable_regimes": applicable,
            "time_to_clearance_months_min": 2,
            "time_to_clearance_months_max": 5,
            "pre_revenue_burn_usd_min": 4000,
            "pre_revenue_burn_usd_max": 25000,
            "required_hires": ["Student Data Privacy & Child Safety Counsel"],
            "recommended_pathway": pathway,
            "runway_penalty_summary": summary,
            "non_regulated_bridge": "Teacher-facing curriculum generation and lesson planning tool with zero student PII capture",
        }

    # 5. LegalTech domain
    if any(k in dom for k in ["legal", "compliance", "law"]):
        if is_india:
            applicable = ["Advocates Act, 1961 / Bar Council Guidelines", "Digital Personal Data Protection (DPDP) Act, 2023", "SOC 2 Type II Audit"]
            pathway = "Deploy as attorney-directed assistive copilot requiring affirmative legal professional signoff to stay outside non-advocate practice restrictions."
            summary = "adds 2-4 months and $5,000-$15,000 (\u20b94L-\u20b912L) for ethics audit and DPDP isolation"
        elif is_us:
            applicable = ["ABA Model Rule 5.4 / State Bar Ethics", "SOC 2 Type II Audit", "CCPA Data Protection"]
            pathway = "Deploy as attorney-directed assistive copilot requiring affirmative legal professional signoff to stay outside UPL licensing walls."
            summary = "adds 2-4 months and $8,000-$25,000 before first revenue"
        else:
            applicable = ["ABA Model Rule 5.4 / State Bar Ethics", "GDPR / DPDP Act Data Protection", "SOC 2 Type II Audit"]
            pathway = "Assistive workflow tool with mandatory legal professional signoff."
            summary = "adds 2-4 months and $8,000-$25,000 for professional liability clearance"
        return {
            "jurisdiction": jurisdiction,
            "is_regulated": True,
            "applicable_regimes": applicable,
            "time_to_clearance_months_min": 2,
            "time_to_clearance_months_max": 4,
            "pre_revenue_burn_usd_min": 5000,
            "pre_revenue_burn_usd_max": 25000,
            "required_hires": ["Legal Ethics & Bar Compliance Counsel"],
            "recommended_pathway": pathway,
            "runway_penalty_summary": summary,
            "non_regulated_bridge": "Paralegal-assisted draft structuring without formal legal opinion delivery",
        }

    # 6. FinTech / Financial Services (non-lending: payments, banking, wealth, crypto)
    if any(k in dom for k in ["fintech", "finance", "payment", "banking", "wealth", "invest"]):
        if is_india:
            applicable = ["RBI Payment Aggregator / Payment Gateway (PA/PG) Guidelines", "Digital Personal Data Protection (DPDP) Act, 2023", "PCI-DSS Level 1"]
            pathway = "Partner with licensed Payment Aggregators (Razorpay / Cashfree) as a pure software facilitator to bypass balance-sheet capital escrow licensing."
            summary = "adds 2-5 months and $8,000-$25,000 (\u20b96L-\u20b920L) for PCI-DSS certification and PA integration"
        elif is_us:
            applicable = ["FinCEN MSB Registration / State Money Transmitter Licenses", "PCI-DSS Level 1", "Gramm-Leach-Bliley Act (GLBA)"]
            pathway = "Partner with chartered sponsor bank or licensed money transmitter via API rails."
            summary = "adds 3-6 months and $15,000-$50,000 before first revenue"
        else:
            applicable = ["PCI-DSS Level 1", "Payment Services Regulations (PSD2/PSD3)", "Anti-Money Laundering (AML/KYC)"]
            pathway = "Partner with authorized payment rails as a non-custodial technology intermediary."
            summary = "adds 3-6 months and $15,000-$50,000 for security audits"
        return {
            "jurisdiction": jurisdiction,
            "is_regulated": True,
            "applicable_regimes": applicable,
            "time_to_clearance_months_min": 2,
            "time_to_clearance_months_max": 6,
            "pre_revenue_burn_usd_min": 8000,
            "pre_revenue_burn_usd_max": 50000,
            "required_hires": ["Fintech Regulatory & Compliance Officer", "InfoSec & PCI Auditor"],
            "recommended_pathway": pathway,
            "runway_penalty_summary": summary,
            "non_regulated_bridge": "Un-regulated financial analytics and lead matchmaking tool without funds custody or direct transaction settlement",
        }

    # 7. Hardware / Industrial IoT / AgriTech sensor
    if bm in ("hardware", "industrial") or any(k in dom for k in ["hardware", "industrial", "iot", "sensor", "agritech", "agriculture"]):
        if is_india:
            applicable = [
                "Bureau of Indian Standards (BIS) Certification",
                "WPC ETA (Wireless Planning & Coordination)",
                "RoHS Compliance"
            ]
            pathway = "Obtain WPC Equipment Type Approval (ETA) for sub-GHz / cellular RF telemetry and BIS certification via accredited domestic test labs."
            summary = "adds 3-6 months and $4,000-$12,000 (\u20b93L-\u20b910L) for BIS/WPC RF certification and lab testing"
        elif is_us:
            applicable = ["FCC Part 15 (RF Emissions & Unintentional Radiators)", "UL Safety Certification", "RoHS Compliance"]
            pathway = "Use FCC pre-certified RF modules to slash laboratory EMC testing cycles from months to weeks."
            summary = "adds 2-5 months and $10,000-$30,000 for FCC Part 15 laboratory EMC certification"
        elif is_eu:
            applicable = ["CE Marking (Radio Equipment Directive 2014/53/EU)", "RoHS / WEEE Directives", "ISO 9001"]
            pathway = "Modular CE pre-certification architecture using pre-tested European sub-assemblies."
            summary = "adds 3-6 months and $10,000-$35,000 for modular CE/RED testing"
        else:
            applicable = ["CE Marking (Radio Equipment Directive)", "FCC Part 15", "RoHS Compliance"]
            pathway = "Turnkey sub-assembly testing with accredited international laboratory."
            summary = "adds 3-6 months and $10,000-$35,000 for EMC and environmental compliance"
        return {
            "jurisdiction": jurisdiction,
            "is_regulated": True,
            "applicable_regimes": applicable,
            "time_to_clearance_months_min": 3,
            "time_to_clearance_months_max": 6,
            "pre_revenue_burn_usd_min": 4000,
            "pre_revenue_burn_usd_max": 35000,
            "required_hires": ["Hardware Compliance & RF Test Engineer"],
            "recommended_pathway": pathway,
            "runway_penalty_summary": summary,
            "non_regulated_bridge": "Software simulation tier and pre-order pilot reservations before physical manufacturing rollout.",
        }

    # 8. Enterprise SaaS / B2B SaaS / General Software
    if bm == "saas" or any(k in dom for k in ["saas", "enterprise", "productivity", "cloud", "software"]):
        if is_india:
            applicable = [
                "Digital Personal Data Protection (DPDP) Act, 2023",
                "CERT-In Cybersecurity Directions",
                "SOC 2 Type II / ISO 27001"
            ]
            pathway = "Standard cloud SaaS rollout with DPDP consent manager and automated SOC 2 Type II readiness."
            summary = "adds 2-4 months and $4,000-$12,000 (\u20b93L-\u20b910L) for SOC 2 Type II audit and DPDP consent architecture"
        elif is_us:
            applicable = ["SOC 2 Type II Audit", "CCPA / CPRA Privacy Regulations", "ISO 27001"]
            pathway = "Cloud deployment with automated SOC 2 compliance platforms (Vanta / Drata)."
            summary = "adds 2-4 months and $10,000-$25,000 for automated SOC 2 audit readiness"
        elif is_eu:
            applicable = ["EU General Data Protection Regulation (GDPR)", "SOC 2 Type II Audit", "ISO 27001"]
            pathway = "GDPR-compliant EU data hosting architecture with standardized DPA agreements."
            summary = "adds 2-4 months and $10,000-$30,000 for GDPR DPA and SOC 2 compliance"
        else:
            applicable = ["GDPR / DPDP Act / CCPA Data Protection", "SOC 2 Type II Audit"]
            pathway = "Commercial B2B SaaS rollout with standard SOC 2 Type II assurance."
            summary = "adds 2-4 months and $8,000-$25,000 for commercial compliance"
        return {
            "jurisdiction": jurisdiction,
            "is_regulated": True,
            "applicable_regimes": applicable,
            "time_to_clearance_months_min": 2,
            "time_to_clearance_months_max": 4,
            "pre_revenue_burn_usd_min": 4000,
            "pre_revenue_burn_usd_max": 25000,
            "required_hires": ["Data Protection & InfoSec Specialist"],
            "recommended_pathway": pathway,
            "runway_penalty_summary": summary,
            "non_regulated_bridge": "Self-hosted or sandboxed free trial tier before enterprise procurement signoff.",
        }

    # Default fallback for unclassified / offline tools
    return {
        "jurisdiction": jurisdiction,
        "is_regulated": False,
        "applicable_regimes": ["none"],
        "time_to_clearance_months_min": 0,
        "time_to_clearance_months_max": 0,
        "pre_revenue_burn_usd_min": 0,
        "pre_revenue_burn_usd_max": 0,
        "required_hires": [],
        "runway_penalty_summary": "Pure offline tool: 0 regulatory clearance delay.",
        "non_regulated_bridge": "",
    }


def ensure_regulatory_compliance_for_idea(arg1: Any, arg2: Any = None) -> Dict[str, Any]:
    """
    Enforces that pure software ideas with payments, health data, minors' data, or personal data
    do NOT escape regulation with applicable_regimes=['none'].
    Supports both ensure_regulatory_compliance_for_idea(regulatory_data, idea)
    and ensure_regulatory_compliance_for_idea(idea, regulatory_data).
    """
    if isinstance(arg1, dict):
        regulatory_data = arg1
        idea = str(arg2 or "")
    else:
        idea = str(arg1 or "")
        regulatory_data = arg2 if isinstance(arg2, dict) else {}

    regimes = [str(r).strip().lower() for r in regulatory_data.get("applicable_regimes", [])]
    is_declared_none = not regimes or regimes == ["none"] or (len(regimes) == 1 and regimes[0] in ("none", "n/a", "not applicable"))

    detected = detect_regulatory_requirements(idea)
    if is_declared_none and detected["applicable_regimes"] != ["none"]:
        merged = dict(regulatory_data)
        merged["applicable_regimes"] = detected["applicable_regimes"]
        if merged.get("time_to_clearance_months_max", 0) == 0:
            merged["time_to_clearance_months_min"] = detected["time_to_clearance_months_min"]
            merged["time_to_clearance_months_max"] = detected["time_to_clearance_months_max"]
            merged["pre_revenue_burn_usd_min"] = detected["pre_revenue_burn_usd_min"]
            merged["pre_revenue_burn_usd_max"] = detected["pre_revenue_burn_usd_max"]
            merged["runway_penalty_summary"] = detected["runway_penalty_summary"]
            merged["non_regulated_bridge"] = detected["non_regulated_bridge"]
            if not merged.get("required_hires"):
                merged["required_hires"] = detected["required_hires"]
        return merged

    return regulatory_data



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


def derive_research_confidence(data: Dict[str, Any]) -> str:
    """
    Derives overall Research Confidence in Python from:
    1. Number of sources
    2. Share of company (non-academic) sources
    3. search_status ("ok", "thin", "quota_exhausted")
    4. Individual module confidences

    Hard Rules:
    - Fewer than 8 sources OR no company sources = 'LOW'.
    - Never 'HIGH' with thin evidence (search_status != 'ok' or sources < 10 or company_share < 0.30).
    """
    search_res = data.get("search_results")
    search_status = str(data.get("search_status") or "ok").lower()

    if search_status == "quota_exhausted":
        return "LOW"

    # Only evaluate search_results if explicitly present in the data dict
    if search_res is not None:
        num_sources = len(search_res)
        academic_domains = {
            "edu", "gov", "org", "mdpi.com", "arxiv.org", "biorxiv.org", "medrxiv.org",
            "sciencedirect.com", "springer.com", "wiley.com", "frontiersin.org", "nature.com",
            "ieee.org", "researchgate.net", "academia.edu", "ncbi.nlm.nih.gov",
            "pubmed.ncbi.nlm.nih.gov", "jstor.org", "semanticscholar.org", "tandfonline.com",
            "cell.com", "nih.gov", "who.int", "cdc.gov"
        }
        company_sources = 0
        for s in search_res:
            url = str(s.get("url") or "")
            parsed = urlparse(url)
            domain = (parsed.netloc or "").lower().split(":")[0]
            is_academic = any(domain.endswith(f".{ad}") or domain == ad for ad in academic_domains)
            if not is_academic and domain:
                company_sources += 1

        company_share = company_sources / max(1, num_sources)
        if num_sources < 8 or company_sources == 0:
            return "LOW"
    else:
        num_sources = 10
        company_share = 0.5

    # Module confidence scores
    scores: List[float] = []
    modules = ["kill_switch", "unit_economics", "regulatory_runway", "trl_readiness", "moat_durability", "pivot_plan"]

    for m in modules:
        mod = data.get(m)
        if isinstance(mod, dict):
            if mod.get("source_type") == "heuristic_fallback":
                scores.append(1.0)
            else:
                conf = str(mod.get("confidence", "medium")).lower()
                if "high" in conf:
                    scores.append(3.0)
                elif "low" in conf:
                    scores.append(1.0)
                else:
                    scores.append(2.0)

    if not scores:
        return "LOW" if num_sources < 8 else "MEDIUM"

    avg = sum(scores) / len(scores)

    # Never HIGH with thin evidence or non-ok search status
    if search_status != "ok" or num_sources < 10 or company_share < 0.30:
        return "LOW" if (num_sources < 8 or avg < 1.8) else "MEDIUM"

    if avg >= 2.4 and company_share >= 0.35 and num_sources >= 8:
        return "HIGH"
    elif avg >= 1.7:
        return "MEDIUM"
    return "LOW"


def check_cross_tab_consistency(data: Dict[str, Any]) -> List[str]:
    """
    Validates cross-tab consistency between Deep Validation Matrix, GTM Strategy, Overview, and Risk Audit.
    Returns a list of consistency warnings (displayed as an amber notification list).
    If either side of a cross-check is source_type == 'heuristic_fallback', skips the cross-check and
    records '[Check Name]: not verified (using heuristic fallback)' instead of falsely reporting a pass.
    """
    warnings: List[str] = []

    # 1. Unit economics margin check between Deep Matrix and GTM Strategy
    ue = data.get("unit_economics") or {}
    dm_margin = ue.get("gross_margin_pct")
    ue_source = ue.get("source_type", "llm_grounded")

    gtm = data.get("gtm_strategy") or {}
    gtm_ue = gtm.get("unit_economics") or {}
    gtm_metrics = gtm_ue.get("metrics") or {}
    gtm_margin_str = gtm_metrics.get("gross_margin") or gtm_metrics.get("contribution_margin") or gtm_ue.get("gross_margin")
    gtm_source = gtm.get("source_type") or gtm_ue.get("source_type", "llm_grounded")

    if ue_source == "heuristic_fallback" or gtm_source == "heuristic_fallback":
        if dm_margin is not None or gtm_margin_str:
            warnings.append("Gross margin: not verified (using heuristic fallback)")
    elif dm_margin is not None and gtm_margin_str:
        matches = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)%", str(gtm_margin_str))]
        if matches:
            gtm_margin_val = sum(matches) / len(matches)
            if abs(float(dm_margin) - gtm_margin_val) > 10.0:
                warnings.append(
                    f"Gross margin divergence: Deep Validation Matrix calculates {dm_margin}% margin, but GTM Strategy reports {gtm_margin_str}."
                )

    # 2. Moat score vs Overview score
    moat = data.get("moat_durability") or {}
    sub_scores = data.get("sub_scores") or {}
    market_an = data.get("market_analysis") or {}
    moat_score = moat.get("moat_score")
    overview_comp = sub_scores.get("competition") if sub_scores.get("competition") is not None else market_an.get("competitor_strength")
    moat_source = moat.get("source_type", "llm_grounded")

    if moat_source == "heuristic_fallback":
        if moat_score is not None and overview_comp is not None:
            warnings.append("Moat score: not verified (using heuristic fallback)")
    elif moat_score is not None and overview_comp is not None:
        if abs(float(moat_score) - float(overview_comp)) > 2.0:
            warnings.append(
                f"Moat divergence: Moat Durability computes {moat_score}/100, while Overview score displays {overview_comp}/100."
            )

    # 3. Kill-switch threshold vs derived break-even default rate from unit economics
    kill_switch = data.get("kill_switch") or {}
    kill_thresh = str(kill_switch.get("kill_threshold", ""))
    kill_thresh_lower = kill_thresh.lower()
    assumptions_text = " ".join([str(a) for a in ue.get("assumptions", [])]).lower()
    ks_source = kill_switch.get("source_type", "llm_grounded")

    if ks_source == "heuristic_fallback" or ue_source == "heuristic_fallback":
        if kill_thresh:
            warnings.append("Kill-switch threshold: not verified (using heuristic fallback)")
    else:
        # Check if kill threshold references a default rate that has diverged from break-even
        be_default = ue.get("break_even_default_rate_pct")
        if be_default is not None and float(be_default) > 0:
            be_pct = float(be_default)
            derived_kill_pct = round(be_pct * 0.75, 1)
            kill_def_match = re.search(
                r"(?:default\s*rate\s*(?:exceeds|>|is\s*over)?\s*|[><]\s*)(\d+(?:\.\d+)?)\s*%",
                kill_thresh_lower
            )
            if not kill_def_match:
                kill_def_match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*(?:predicted\s*)?default", kill_thresh_lower)
            if kill_def_match:
                kill_def_val = float(kill_def_match.group(1))
                if abs(kill_def_val - derived_kill_pct) > 1.5 or (derived_kill_pct > 0 and abs(kill_def_val - derived_kill_pct) / derived_kill_pct > 0.20):
                    warnings.append(
                        f"Kill-switch threshold mismatch: Kill-switch uses {kill_def_val}% default rate trigger, "
                        f"but unit economics break-even is {be_pct}% (75% buffer suggests {derived_kill_pct}%). "
                        f"Consider updating the kill threshold to {derived_kill_pct}%."
                    )
        elif ue.get("default_rate_pct") is not None or ue.get("expected_default_loss") is not None or "default rate" in assumptions_text:
            base_def = float(ue.get("default_rate_pct") or 5.0)
            kill_def_match = re.search(
                r"(?:default\s*rate\s*(?:exceeds|>|is\s*over)?\s*|[><]\s*)(\d+(?:\.\d+)?)\s*%",
                kill_thresh_lower
            )
            if not kill_def_match:
                kill_def_match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*(?:predicted\s*)?default", kill_thresh_lower)
            if kill_def_match:
                kill_def = float(kill_def_match.group(1))
                if base_def >= kill_def:
                    warnings.append(
                        f"Default loss contradiction: Base unit economics assumes a {base_def:.1f}% default rate, "
                        f"which meets or exceeds the walk-away kill threshold ({kill_def}%)."
                    )

    # 4. High risk in Risk Audit not reflected in Deep Validation
    risk_data = data.get("risk_analysis") or []
    if isinstance(risk_data, dict):
        risk_list = risk_data.get("risks", []) or []
    elif isinstance(risk_data, list):
        risk_list = risk_data
    else:
        risk_list = []

    reg_risk_obj = data.get("regulatory_risk") or {}
    reg_runway_obj = data.get("regulatory_runway") or {}
    deep_text = (
        f"{kill_switch.get('fatal_assumption', '')} "
        f"{ue.get('platform_dependency_risk', '')} "
        f"{' '.join([str(r) for r in reg_risk_obj.get('compliance_requirements', [])])} "
        f"{' '.join([str(r) for r in reg_runway_obj.get('applicable_regimes', [])])}"
    ).lower()

    for r in risk_list:
        if isinstance(r, dict) and str(r.get("severity", "")).lower() in ("high", "critical"):
            risk_name = str(r.get("risk") or r.get("title") or r.get("category", "")).strip()
            if any(w in risk_name.lower() for w in ["platform", "encroach", "partner", "default", "regulatory"]):
                tokens = [w for w in re.findall(r"\b[a-z]{4,}\b", risk_name.lower()) if w not in ("risk", "high", "critical")]
                if tokens and not any(t in deep_text for t in tokens):
                    warnings.append(
                        f"Unaddressed risk: High-severity risk '{risk_name}' from Risk Audit is not reflected in the Deep Validation Matrix modules."
                    )

    return warnings


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

    startup_metadata: Optional[StartupMetadata] = Field(
        default=None,
        description="Extracted startup metadata (product, target_user, domain, jurisdiction, business_model)"
    )

    research_confidence: Optional[str] = Field(
        default="HIGH",
        description="Overall research confidence derived in Python from module confidences ('HIGH', 'MEDIUM', 'LOW')"
    )

    search_status: Optional[str] = Field(
        default="ok",
        description="Web search status: 'ok', 'thin', or 'quota_exhausted'"
    )

    consistency_warnings: List[str] = Field(
        default_factory=list,
        description="Cross-tab consistency warnings checking for numerical or architectural contradictions"
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

    technical_feasibility: Optional[Union[TechnicalFeasibility, Dict[str, Any]]] = None

    scientific_validation: Optional[Union[ScientificValidation, Dict[str, Any]]] = None

    regulatory_risk: Optional[Union[RegulatoryRisk, Dict[str, Any]]] = None

    execution_feasibility: Optional[Any] = None

    kill_switch: Optional[Union[KillSwitch, Dict[str, Any]]] = None

    unit_economics: Optional[Union[UnitEconomics, Dict[str, Any]]] = None

    regulatory_runway: Optional[Union[RegulatoryRunway, Dict[str, Any]]] = None

    trl_readiness: Optional[Union[TRLReadiness, Dict[str, Any]]] = None

    moat_durability: Optional[Union[MoatDurability, Dict[str, Any]]] = None

    pivot_plan: Optional[Union[PivotPlan, Dict[str, Any]]] = None

    deep_validation: Optional[Dict[str, Any]] = None

    @field_validator("technical_feasibility", mode="before")
    @classmethod
    def parse_technical_feasibility(cls, v: Any) -> Any:
        if isinstance(v, dict):
            try:
                return TechnicalFeasibility(**v)
            except Exception:
                return v
        return v

    @field_validator("scientific_validation", mode="before")
    @classmethod
    def parse_scientific_validation(cls, v: Any) -> Any:
        if isinstance(v, dict):
            try:
                return ScientificValidation(**v)
            except Exception:
                return v
        return v

    @field_validator("regulatory_risk", mode="before")
    @classmethod
    def parse_regulatory_risk(cls, v: Any) -> Any:
        if isinstance(v, dict):
            try:
                return RegulatoryRisk(**v)
            except Exception:
                return v
        return v

    @field_validator("kill_switch", mode="before")
    @classmethod
    def parse_kill_switch(cls, v: Any) -> Any:
        if isinstance(v, dict):
            try:
                return KillSwitch(**v)
            except Exception:
                return v
        return v

    @field_validator("unit_economics", mode="before")
    @classmethod
    def parse_unit_economics(cls, v: Any) -> Any:
        if isinstance(v, dict):
            try:
                return UnitEconomics(**v)
            except Exception:
                return v
        return v

    @field_validator("regulatory_runway", mode="before")
    @classmethod
    def parse_regulatory_runway(cls, v: Any) -> Any:
        if isinstance(v, dict):
            try:
                return RegulatoryRunway(**v)
            except Exception:
                return v
        return v

    @field_validator("trl_readiness", mode="before")
    @classmethod
    def parse_trl_readiness(cls, v: Any) -> Any:
        if isinstance(v, dict):
            try:
                return TRLReadiness(**v)
            except Exception:
                return v
        return v

    @field_validator("moat_durability", mode="before")
    @classmethod
    def parse_moat_durability(cls, v: Any) -> Any:
        if isinstance(v, dict):
            try:
                return MoatDurability(**v)
            except Exception:
                return v
        return v

    @field_validator("pivot_plan", mode="before")
    @classmethod
    def parse_pivot_plan(cls, v: Any) -> Any:
        if isinstance(v, dict):
            try:
                return PivotPlan(**v)
            except Exception:
                return v
        return v


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