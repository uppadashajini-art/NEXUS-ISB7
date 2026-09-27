from typing import Any, Dict, List, Optional


def _join_or_default(items: Optional[List[str]], default: str, limit: int = 3) -> str:
    """Join up to `limit` list items into a readable sentence fragment."""
    if not items:
        return default
    cleaned = [str(i).strip() for i in items if str(i).strip()]
    if not cleaned:
        return default
    return ", ".join(cleaned[:limit])


def _summarize_market(market_analysis: Optional[Dict[str, Any]]) -> str:
    if not market_analysis:
        return "Market analysis was not available for this validation run."
    industry = market_analysis.get("industry", "the target industry")
    opportunity = market_analysis.get("market_opportunity", "")
    trends = _join_or_default(market_analysis.get("market_trends"), "no major trends identified")
    summary = f"The startup operates in {industry}."
    if opportunity:
        summary += f" {opportunity}"
    summary += f" Key trends include: {trends}."
    return summary


def _summarize_competitors(competitor_analysis: Optional[Dict[str, Any]]) -> str:
    if not competitor_analysis:
        return "Competitor analysis was not available for this validation run."
    direct = competitor_analysis.get("direct_competitors") or []
    gaps = _join_or_default(competitor_analysis.get("market_gaps"), "no significant gaps identified")
    count = len(direct)
    return (
        f"{count} direct competitor(s) were identified in this space. "
        f"Potential market gaps include: {gaps}."
    )


def _summarize_swot(swot_analysis: Optional[Dict[str, Any]]) -> str:
    if not swot_analysis:
        return "SWOT analysis was not available for this validation run."
    strengths = _join_or_default(swot_analysis.get("strengths"), "no notable strengths identified")
    threats = _join_or_default(swot_analysis.get("threats"), "no major threats identified")
    return f"Key strengths: {strengths}. Key threats to monitor: {threats}."


def _summarize_risk(risk_analysis: Optional[List[Dict[str, Any]]]) -> str:
    if not risk_analysis:
        return "Risk analysis was not available for this validation run."
    high = [r for r in risk_analysis if str(r.get("severity", "")).lower() in ("high", "critical")]
    if high:
        top = high[0].get("risk", "an unspecified risk")
        return f"{len(risk_analysis)} risk(s) identified, including a high-severity risk: {top}."
    return f"{len(risk_analysis)} risk(s) identified, none rated as high severity."


def _summarize_mvp(mvp_recommendations: Optional[Dict[str, Any]]) -> str:
    if not mvp_recommendations:
        return "MVP recommendations were not available for this validation run."
    must_have = mvp_recommendations.get("must_have") or []
    names = _join_or_default(
        [f.get("feature", "") for f in must_have if isinstance(f, dict)],
        "no must-have features specified",
    )
    return f"Recommended MVP must-have features: {names}."


def _summarize_gtm(gtm_strategy: Optional[Dict[str, Any]]) -> str:
    if not gtm_strategy:
        return "Go-to-market strategy was not available for this validation run."
    positioning = gtm_strategy.get("positioning", "")
    channels = _join_or_default(gtm_strategy.get("marketing_channels"), "no channels specified")
    summary = f"Suggested marketing channels: {channels}."
    if positioning:
        summary = f"{positioning} {summary}"
    return summary


def _build_recommendations(
    swot_analysis: Optional[Dict[str, Any]],
    risk_analysis: Optional[List[Dict[str, Any]]],
    mvp_recommendations: Optional[Dict[str, Any]],
) -> str:
    parts = []
    if mvp_recommendations and mvp_recommendations.get("must_have"):
        parts.append("Prioritize building the identified must-have MVP features first.")
    if risk_analysis:
        high = [r for r in risk_analysis if str(r.get("severity", "")).lower() in ("high", "critical")]
        if high:
            parts.append("Address high-severity risks before scaling further.")
    if swot_analysis and swot_analysis.get("opportunities"):
        parts.append("Capitalize on the identified market opportunities early.")
    if not parts:
        parts.append("Proceed with further validation before committing significant resources.")
    return " ".join(parts)


async def generate_validation_report(
    idea: str,
    market_analysis: Optional[Dict[str, Any]] = None,
    competitor_analysis: Optional[Dict[str, Any]] = None,
    swot_analysis: Optional[Dict[str, Any]] = None,
    risk_analysis: Optional[List[Dict[str, Any]]] = None,
    mvp_recommendations: Optional[Dict[str, Any]] = None,
    gtm_strategy: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Combine every agent's output into a final structured validation report.
    Safe to call even if some inputs are None -- degrades gracefully.
    """
    market_summary = _summarize_market(market_analysis)
    competitor_summary = _summarize_competitors(competitor_analysis)
    swot_summary = _summarize_swot(swot_analysis)
    risk_summary = _summarize_risk(risk_analysis)
    mvp_summary = _summarize_mvp(mvp_recommendations)
    gtm_summary = _summarize_gtm(gtm_strategy)
    recommendations = _build_recommendations(swot_analysis, risk_analysis, mvp_recommendations)

    executive_summary = (
        f"This report validates the startup idea: \"{idea}\". "
        f"{market_summary} {competitor_summary}"
    )

    conclusion = (
        "Based on the combined market, competitive, SWOT, risk, and MVP analysis, "
        "this idea shows potential but should be validated further with real customers "
        "before major investment."
    )

    return {
        "validation_report": {
            "executive_summary": executive_summary,
            "market_summary": market_summary,
            "competitor_summary": competitor_summary,
            "swot_summary": swot_summary,
            "risk_summary": risk_summary,
            "mvp_summary": mvp_summary,
            "gtm_summary": gtm_summary,
            "recommendations": recommendations,
            "conclusion": conclusion,
        }
    }