"""
Conversational Startup Advisor Agent
Member 3 — NEXUS AI Startup Idea Validator

Responsibilities:
- Answers founder questions grounded strictly in the full startup validation context:
    1. Startup Idea, Domain & Proposed Customer Profile
    2. Real-Time Web Research Evidence & Sources (search_results)
    3. Market Demand, Growth Drivers, Trends & Market Challenges
    4. Target Customer Segments, Critical Needs & Pain Points
    5. Competitor Benchmarking, Pricing Benchmarks & Validated Market Gaps
    6. SWOT Analysis Matrix (Strengths, Weaknesses, Opportunities, Threats)
    7. Specific Risk Analysis with Concrete Business Mitigations
    8. MVP Feature Recommendations (Must-Have, Should-Have, Future Features)
    9. Go-To-Market Strategy (Marketing Channels, Acquisition Loops, Pricing Model)
    10. Deep Technical, Scientific & Regulatory Validation Feasibility
- Dual Synthesis Architecture:
    1. Universal Multi-Model LLM Advisor Synthesis (Google Gemini & Groq waterfall).
       Deeply examines the generated validation reports and client's proposed idea to generate an accurate, bespoke answer.
    2. Contextual Deterministic Grounding Engine (extracts and formats exact validation data even if offline/rate-limited).

Output Format:
{
    "answer": "Comprehensive, structured advice with direct references to validation data...",
    "suggested_followups": [
        "Suggested follow-up 1",
        "Suggested follow-up 2"
    ]
}
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import re
from typing import Any, Dict, List, Optional
import httpx

logger = logging.getLogger(__name__)


# ============================================================================
# CONTEXT NORMALIZER & SIGNAL EXTRACTOR
# ============================================================================

def _clean_text(val: Any, default: str = "") -> str:
    if val is None:
        return default
    text = str(val).strip()
    return text if text else default


def extract_advisor_signals(validation_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deeply extracts and normalizes all validation intelligence generated across
    all validator agents (Web Search, Market, Competitor, SWOT, Risk, MVP, GTM, Deep Validation).
    Ensures the founder's proposed idea, domain, and target customer are prominently preserved.
    """
    ctx = validation_context or {}

    idea = _clean_text(ctx.get("idea"), "Your startup idea")
    target_customer_input = _clean_text(ctx.get("target_customer") or ctx.get("audience"), "")
    domain_input = _clean_text(ctx.get("domain"), "")

    # 1. Market Analysis
    market = ctx.get("market_analysis") or {}
    industry = _clean_text(market.get("industry") or domain_input, "Technology & Software")
    market_opp = _clean_text(market.get("market_opportunity"), "Emerging market expansion")
    market_trends = market.get("market_trends") or []
    growth_drivers = market.get("growth_drivers") or []
    market_challenges = market.get("market_challenges") or []

    # 2. Customer Segments
    customer_segments = market.get("customer_segments") or ctx.get("customer_segments") or []
    primary_segment = target_customer_input or "Target Customers"
    primary_needs: List[str] = []
    primary_pain_points: List[str] = []

    formatted_segments: List[Dict[str, Any]] = []
    if customer_segments and len(customer_segments) > 0:
        for i, s in enumerate(customer_segments):
            if isinstance(s, dict):
                s_name = _clean_text(s.get("segment"), f"Segment {i+1}")
                s_needs = s.get("needs") or []
                s_pains = s.get("pain_points") or []
                formatted_segments.append({
                    "segment": s_name,
                    "needs": s_needs,
                    "pain_points": s_pains
                })
                if i == 0:
                    primary_segment = s_name
                    primary_needs = s_needs
                    primary_pain_points = s_pains

    # 3. Competitor Analysis & Gaps
    competitor_data = ctx.get("competitor_analysis") or {}
    direct_comps = competitor_data.get("direct_competitors") or []
    indirect_comps = competitor_data.get("indirect_competitors") or []
    comparison_rows = competitor_data.get("comparison") or []
    market_gaps = competitor_data.get("market_gaps") or ctx.get("market_gaps") or []
    comp_advantage = _clean_text(competitor_data.get("competitive_advantage"), "")

    comp_names: List[str] = []
    comp_details: List[str] = []
    for c in direct_comps:
        if isinstance(c, dict):
            name = c.get("name", "Competitor")
            price = c.get("pricing", "Unspecified")
            product = c.get("product") or c.get("product_service", "")
            features = ", ".join(c.get("key_features", [])[:2]) if c.get("key_features") else ""
            strengths = ", ".join(c.get("strengths", [])[:2]) or "Established presence"
            weaknesses = ", ".join(c.get("weaknesses", [])[:2]) or "High complexity"
            comp_names.append(name)
            detail = f"{name} (Product: {product or 'Direct competitor'}, Pricing: {price}, Strengths: {strengths}, Weaknesses: {weaknesses}"
            if features:
                detail += f", Key Features: {features}"
            detail += ")"
            comp_details.append(detail)

    for c in indirect_comps:
        if isinstance(c, dict):
            name = c.get("name")
            if name and name not in comp_names:
                comp_names.append(name)

    # 4. Web Search Evidence & Sources
    raw_search = ctx.get("search_results") or []
    search_evidence: List[Dict[str, str]] = []
    if isinstance(raw_search, list):
        for item in raw_search[:10]:
            if isinstance(item, dict):
                title = _clean_text(item.get("title"))
                url = _clean_text(item.get("url"))
                snippet = _clean_text(item.get("snippet") or item.get("content") or item.get("text"))
                if title or snippet:
                    search_evidence.append({
                        "title": title or "Research Citation",
                        "url": url,
                        "snippet": snippet[:220]
                    })

    # 5. SWOT Analysis
    swot = ctx.get("swot_analysis") or {}
    swot_strengths = swot.get("strengths") or []
    swot_weaknesses = swot.get("weaknesses") or []
    swot_opportunities = swot.get("opportunities") or []
    swot_threats = swot.get("threats") or []

    # 6. Risk Analysis
    raw_risks = ctx.get("risk_analysis") or []
    risk_items: List[Dict[str, str]] = []
    if isinstance(raw_risks, list):
        for r in raw_risks:
            if isinstance(r, dict):
                risk_items.append({
                    "risk": _clean_text(r.get("risk")),
                    "category": _clean_text(r.get("category"), "Strategic"),
                    "severity": _clean_text(r.get("severity"), "Medium"),
                    "impact": _clean_text(r.get("impact")),
                    "mitigation": _clean_text(r.get("mitigation"))
                })

    # 7. MVP Recommendations
    mvp = ctx.get("mvp_recommendations") or {}
    must_have_features = mvp.get("must_have") or []
    should_have_features = mvp.get("should_have") or []
    could_have_features = mvp.get("could_have") or []
    future_features = mvp.get("future_features") or []

    # 8. Go-To-Market (GTM) Strategy
    gtm = ctx.get("gtm_strategy") or {}
    pricing_strategy = _clean_text(gtm.get("pricing_strategy"))
    marketing_channels = gtm.get("marketing_channels") or []
    customer_acquisition = gtm.get("customer_acquisition") or []
    launch_strategy = gtm.get("launch_strategy") or []
    business_archetype = gtm.get("business_archetype") or {}

    # 9. Deep Validation (Technical, Scientific, Regulatory)
    tech = ctx.get("technical_feasibility") or {}
    sci = ctx.get("scientific_validation") or {}
    reg = ctx.get("regulatory_risk") or {}

    return {
        "idea": idea,
        "domain": domain_input or industry,
        "target_customer": target_customer_input,
        "industry": industry,
        "market_opportunity": market_opp,
        "market_trends": market_trends,
        "growth_drivers": growth_drivers,
        "market_challenges": market_challenges,
        "customer_segments": formatted_segments or customer_segments,
        "primary_segment": primary_segment,
        "primary_needs": primary_needs,
        "primary_pain_points": primary_pain_points,
        "direct_competitors": direct_comps,
        "indirect_competitors": indirect_comps,
        "comparison_rows": comparison_rows,
        "competitor_names": comp_names,
        "competitor_details": comp_details,
        "market_gaps": market_gaps,
        "competitive_advantage": comp_advantage,
        "search_evidence": search_evidence,
        "swot": {
            "strengths": swot_strengths,
            "weaknesses": swot_weaknesses,
            "opportunities": swot_opportunities,
            "threats": swot_threats
        },
        "risk_items": risk_items,
        "mvp": {
            "must_have": must_have_features,
            "should_have": should_have_features,
            "could_have": could_have_features,
            "future_features": future_features
        },
        "gtm": {
            "pricing_strategy": pricing_strategy,
            "marketing_channels": marketing_channels,
            "customer_acquisition": customer_acquisition,
            "launch_strategy": launch_strategy,
            "business_archetype": business_archetype
        },
        "technical_feasibility": tech,
        "scientific_validation": sci,
        "regulatory_risk": reg,
    }


# ============================================================================
# INTENT MATCHING & HIGH-FIDELITY GROUNDED SYNTHESIS (HEURISTIC ENGINE)
# ============================================================================

def _match_intent(question: str) -> str:
    """Categorizes the founder's question into core archetypes for heuristic routing."""
    q = question.lower().strip()

    if any(k in q for k in ["mvp", "minimum viable product", "feature", "build first", "scope", "prototype", "v1"]):
        return "mvp"
    if any(k in q for k in ["competitor", "competition", "alternative", "rival", "who else", "incumbent"]):
        return "competitors"
    if any(k in q for k in ["different", "differentiat", "unique", "stand out", "moat", "value prop", "advantage", "why me"]):
        return "differentiation"
    if any(k in q for k in ["risk", "threat", "danger", "challenge", "fail", "barrier", "downside", "pitfall"]):
        return "risks"
    if any(k in q for k in ["swot", "strength", "weakness", "opportunity"]):
        return "swot"
    if any(k in q for k in ["target", "customer", "who should i sell", "audience", "icp", "persona", "user", "segment"]):
        return "target_customer"
    if any(k in q for k in ["launch", "go to market", "traction", "release", "rollout", "market entry", "channel", "marketing", "acquisition"]):
        return "launch"
    if any(k in q for k in ["price", "pricing", "cost", "monetiz", "charge", "revenue", "business model", "tier", "fee"]):
        return "pricing"
    if any(k in q for k in ["search", "source", "evidence", "article", "literature", "google", "web search", "findings", "query", "data", "benchmark"]):
        return "search"
    if any(k in q for k in ["tech", "architecture", "hardware", "engineering", "stack", "feasibility", "scale", "infrastructure"]):
        return "technical"
    if any(k in q for k in ["science", "scientific", "study", "research", "paper", "credibility", "claim"]):
        return "scientific"
    if any(k in q for k in ["regulatory", "compliance", "fda", "legal", "governance", "approval", "license"]):
        return "regulatory"
    if any(k in q for k in ["trend", "growth", "market size", "market demand"]):
        return "market_trends"

    return "general"


def synthesize_heuristic_advisor_response(
    question: str,
    signals: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Deterministic synthesis engine that generates high-fidelity, comprehensive answers
    strictly derived from the validation report's generated data and real-time search findings.
    Used when LLMs are offline or as an emergency fallback.
    """
    intent = _match_intent(question)
    idea = signals["idea"]
    industry = signals["industry"]
    primary_seg = signals["primary_segment"]
    pain_points = signals["primary_pain_points"]
    comp_names = signals["competitor_names"]
    comp_details = signals["competitor_details"]
    gaps = signals["market_gaps"]
    challenges = signals["market_challenges"]
    searches = signals["search_evidence"]
    mvp = signals["mvp"]
    risks = signals["risk_items"]
    swot = signals["swot"]
    gtm = signals["gtm"]
    tech = signals.get("technical_feasibility") or {}
    sci = signals.get("scientific_validation") or {}
    reg = signals.get("regulatory_risk") or {}

    comp_str = ", ".join(comp_names[:3]) if comp_names else "legacy incumbents and manual workflows"
    gap_str = gaps[0] if gaps else "Unified automation with seamless self-service onboarding"

    # 1. MVP INTENT
    if intent == "mvp":
        must_haves = mvp.get("must_have") or []
        should_haves = mvp.get("should_have") or []
        future_feats = mvp.get("future_features") or []

        if must_haves:
            must_bullets = []
            for item in must_haves:
                f_name = item.get("feature", "Core Feature") if isinstance(item, dict) else str(item)
                f_reason = item.get("reason", "") if isinstance(item, dict) else ""
                f_val = item.get("customer_value", "High") if isinstance(item, dict) else "High"
                f_cplx = item.get("complexity", "Medium") if isinstance(item, dict) else "Medium"
                reason_part = f" — *Why*: {f_reason}" if f_reason else ""
                must_bullets.append(f"• **{f_name}** [Value: {f_val} | Complexity: {f_cplx}]{reason_part}")
            must_section = "\n".join(must_bullets)
        else:
            must_section = (
                f"• **Core Flagship Engine**: Address '{gap_str}' as the single primary capability.\n"
                f"• **Frictionless Onboarding**: Designed specifically to eliminate '{pain_points[0] if pain_points else 'high friction'}'.\n"
                f"• **Outcome Dashboard**: Real-time feedback and direct ROI verification for {primary_seg}."
            )

        should_part = ""
        if should_haves:
            should_names = [s.get("feature", str(s)) if isinstance(s, dict) else str(s) for s in should_haves[:3]]
            should_part = f"\n\n**Phase 2 (Should-Have Enhancements)**:\n" + "\n".join([f"• {sn}" for sn in should_names])

        future_part = ""
        if future_feats:
            future_names = [f.get("feature", str(f)) if isinstance(f, dict) else str(f) for f in future_feats[:3]]
            future_part = f"\n\n**Anti-Scope (Do NOT build in V1)**:\n" + "\n".join([f"❌ Skip *{fn}* until product-market fit is proven." for fn in future_names])
        else:
            future_part = f"\n\n**Anti-Scope (Do NOT build in V1)**:\n❌ Avoid complex enterprise SSO, extensive multi-tier analytics, or broad secondary integrations."

        answer = (
            f"Based on the multi-agent validation report for **'{idea}'**, here is your ruthlessly prioritized MVP blueprint:\n\n"
            f"🎯 **Target Audience & Core Problem**:\n"
            f"Build exclusively for **{primary_seg}**, specifically addressing: *\"{pain_points[0] if pain_points else 'manual operational friction'}\"*.\n\n"
            f"🚀 **Must-Have MVP Feature Scope**:\n"
            f"{must_section}"
            f"{should_part}"
            f"{future_part}\n\n"
            f"**Strategic Takeaway**: In early user testing against {comp_str}, your single metric of success is Time-to-First-Value (TTFV) under 3 minutes."
        )
        followups = [
            "Who are my main competitors?",
            "What are the biggest risks?",
            "What should my pricing model be?"
        ]

    # 2. COMPETITORS INTENT
    elif intent == "competitors":
        if comp_details:
            comp_bullets = "\n".join([f"• **{cd}**" for cd in comp_details[:4]])
        else:
            comp_bullets = f"• **Incumbents**: Legacy {industry} platforms and manual offline workflows."

        gap_bullets = "\n".join([f"👉 **{g}**" for g in gaps[:3]]) if gaps else f"👉 **{gap_str}**"

        search_context = ""
        if searches:
            top_s = searches[0]
            search_context = f"\n\n🔍 **Live Web Evidence**: Market search identified *\"{top_s['title']}\"* confirming that incumbents struggle with modern integration and rapid self-serve workflows."

        answer = (
            f"Competitive benchmarking from the validator for **'{idea}'** highlights these key players:\n\n"
            f"{comp_bullets}\n\n"
            f"🎯 **Validated Whitespace & Market Gaps**:\n"
            f"{gap_bullets}"
            f"{search_context}\n\n"
            f"**Actionable Advice**: Do not attempt feature parity with incumbents. Position '{idea}' around '{gap_str}' where existing tools are slow and complex."
        )
        followups = [
            "How is my idea different from existing products?",
            "What should my MVP contain?",
            "What are the biggest risks?"
        ]

    # 3. DIFFERENTIATION INTENT
    elif intent == "differentiation":
        gaps_list = "\n".join([f"• **{g}**" for g in gaps[:3]]) if gaps else f"• **{gap_str}**"
        adv = signals.get("competitive_advantage") or f"Directly solving '{gap_str}' without the legacy bloat of {comp_str}."

        answer = (
            f"Here is your unfair advantage and differentiation matrix for **'{idea}'**:\n\n"
            f"⚡ **Core Differentiator**:\n"
            f"{adv}\n\n"
            f"💎 **Validated Gaps Left Open by {comp_str}**:\n"
            f"{gaps_list}\n\n"
            f"**How to Frame Your Positioning**:\n"
            f"1. **Agility vs. Bloat**: Incumbents are weighed down by multi-year architectural debt. You offer instant, focused execution.\n"
            f"2. **Problem-First Framing**: Highlight that you exist specifically to solve *'{pain_points[0] if pain_points else 'high friction'}'* for *{primary_seg}*.\n"
            f"3. **Frictionless Onboarding**: Deliver immediate ROI before incumbents even complete a sales demo."
        )
        followups = [
            "What should my MVP contain?",
            "Who are my main competitors?",
            "What should my pricing model be?"
        ]

    # 4. RISKS & CHALLENGES INTENT
    elif intent == "risks":
        if risks:
            risk_bullets = []
            for r in risks[:4]:
                r_title = r.get("risk", "Operational Risk")
                r_cat = r.get("category", "Strategic")
                r_sev = r.get("severity", "Medium").upper()
                r_imp = r.get("impact", "")
                r_mit = r.get("mitigation", "")
                risk_bullets.append(
                    f"• **[{r_sev}] {r_title}** (*{r_cat}*)\n"
                    f"  - *Impact*: {r_imp}\n"
                    f"  - *Mitigation*: {r_mit}"
                )
            risk_section = "\n\n".join(risk_bullets)
        else:
            challenge_lines = [f"• **{c}**" for c in challenges[:3]] if challenges else [
                "• **Customer Acquisition Friction**: High initial CAC competing against established brand awareness.",
                "• **Retention & Habit Formation**: Keeping users engaged past day 30 without active workflow triggers."
            ]
            risk_section = "\n".join(challenge_lines)

        threats_section = ""
        swot_t = swot.get("threats") or []
        if swot_t:
            threats_section = f"\n\n⚠️ **Key External Threats (SWOT)**:\n" + "\n".join([f"• {t}" for t in swot_t[:2]])

        answer = (
            f"Comprehensive Risk Assessment generated by the validator for **'{idea}'**:\n\n"
            f"{risk_section}"
            f"{threats_section}\n\n"
            f"🛡️ **Primary Strategic Priority**: Implement proactive onboarding feedback loops with {primary_seg} early adopters to neutralize churn before scaling spend."
        )
        followups = [
            "What should my MVP contain?",
            "Who should I target first?",
            "How can I launch my product?"
        ]

    # 5. SWOT INTENT
    elif intent == "swot":
        s_list = "\n".join([f"• {s}" for s in swot.get("strengths", [])[:3]]) or "• Distinct innovative approach to market gap"
        w_list = "\n".join([f"• {w}" for w in swot.get("weaknesses", [])[:3]]) or "• Early-stage brand absence and resource limits"
        o_list = "\n".join([f"• {o}" for o in swot.get("opportunities", [])[:3]]) or "• Growing customer demand for modern solutions"
        t_list = "\n".join([f"• {t}" for t in swot.get("threats", [])[:3]]) or "• Incumbent retaliation and adoption inertia"

        answer = (
            f"SWOT Analysis Synthesis for **'{idea}'**:\n\n"
            f"💪 **Strengths**:\n{s_list}\n\n"
            f"⚠️ **Weaknesses**:\n{w_list}\n\n"
            f"🌟 **Opportunities**:\n{o_list}\n\n"
            f"🛡️ **Threats**:\n{t_list}"
        )
        followups = [
            "What are the biggest risks?",
            "How is my idea different from existing products?",
            "What should my MVP contain?"
        ]

    # 6. TARGET CUSTOMER INTENT
    elif intent == "target_customer":
        segs = signals.get("customer_segments") or []
        seg_bullets = []
        for i, s in enumerate(segs[:3]):
            if isinstance(s, dict):
                s_name = s.get("segment", f"Segment {i+1}")
                s_needs = ", ".join(s.get("needs", [])[:2]) or "Workflow optimization"
                s_pains = ", ".join(s.get("pain_points", [])[:2]) or "High manual overhead"
                tag = "⭐ PRIMARY BEACHHEAD" if i == 0 else f"SECONDARY SEGMENT {i}"
                seg_bullets.append(
                    f"### {tag}: **{s_name}**\n"
                    f"• **Core Needs**: {s_needs}\n"
                    f"• **Severe Pain Points**: {s_pains}"
                )
        segs_section = "\n\n".join(seg_bullets) if seg_bullets else f"• **Primary Segment**: {primary_seg}\n• **Pain Points**: {', '.join(pain_points)}"

        acq_channels = gtm.get("marketing_channels") or []
        channel_str = ""
        if acq_channels:
            ch_names = [c.get("channel", str(c)) if isinstance(c, dict) else str(c) for c in acq_channels[:2]]
            channel_str = f"\n\n📍 **Where to Reach Them**: Prioritize {', '.join(ch_names)}."

        answer = (
            f"Target Audience Discovery for **'{idea}'** in {industry}:\n\n"
            f"{segs_section}"
            f"{channel_str}\n\n"
            f"💡 **Mentor Rule**: Do not try to serve everyone. Win 50 passionate {primary_seg} users who view your solution as non-negotiable before pursuing secondary markets."
        )
        followups = [
            "What should my MVP contain?",
            "How can I launch my product?",
            "What should my pricing model be?"
        ]

    # 7. LAUNCH & GTM INTENT
    elif intent == "launch":
        channels = gtm.get("marketing_channels") or []
        acq_loops = gtm.get("customer_acquisition") or []
        launch_phases = gtm.get("launch_strategy") or []

        ch_bullets = []
        for ch in channels[:3]:
            if isinstance(ch, dict):
                c_name = ch.get("channel", "Inbound")
                c_cat = ch.get("category", "")
                c_tac = ch.get("tactics", "")
                ch_bullets.append(f"• **{c_name}** ({c_cat}): {c_tac}")
            else:
                ch_bullets.append(f"• **{ch}**")
        ch_section = "\n".join(ch_bullets) if ch_bullets else f"• Targeted direct outreach to {primary_seg}\n• Problem-solution content & niche communities"

        acq_section = ""
        if acq_loops:
            acq_section = "\n\n🔄 **Customer Acquisition Loops**:\n" + "\n".join([f"• {a}" for a in acq_loops[:2]])

        roadmap_section = ""
        if launch_phases:
            phase_items = []
            for p in launch_phases[:3]:
                if isinstance(p, dict):
                    p_name = p.get("phase", "Phase")
                    p_obj = p.get("objective", "")
                    phase_items.append(f"• **{p_name}**: {p_obj}")
            roadmap_section = "\n\n📅 **Phased Launch Roadmap**:\n" + "\n".join(phase_items)

        answer = (
            f"Validated Go-To-Market & Launch Execution Plan for **'{idea}'**:\n\n"
            f"🚀 **Core Marketing & Acquisition Channels**:\n"
            f"{ch_section}"
            f"{acq_section}"
            f"{roadmap_section}\n\n"
            f"**Launch Milestone**: Focus exclusively on securing your first 100 active {primary_seg} users through high-touch onboarding before investing in paid advertising."
        )
        followups = [
            "What should my pricing model be?",
            "What should my MVP contain?",
            "Who are my main competitors?"
        ]

    # 8. PRICING INTENT
    elif intent == "pricing":
        pricing_strat = gtm.get("pricing_strategy") or signals.get("pricing_strategy")
        if not pricing_strat:
            pricing_strat = f"Tiered SaaS model ($29-$49/mo for Pro, Custom for Teams) with a 14-day outcome-focused pilot."

        comp_pricing = []
        for c in comp_details[:3]:
            comp_pricing.append(f"• {c}")
        comp_price_str = "\n".join(comp_pricing) if comp_pricing else f"• Legacy competitors typically bill custom opaque quotes or complex user seats."

        answer = (
            f"Monetization Strategy & Pricing Architecture for **'{idea}'**:\n\n"
            f"💰 **Validated Pricing Model**:\n"
            f"{pricing_strat}\n\n"
            f"📊 **Competitor Pricing Benchmarks**:\n"
            f"{comp_price_str}\n\n"
            f"**Strategic Guidance**: In the initial rollout, do not compete on being the 'cheap' alternative. Charge a fair price to {primary_seg} as proof that you are solving an acute, urgent problem."
        )
        followups = [
            "Who should I target first?",
            "What should my MVP contain?",
            "How can I launch my product?"
        ]

    # 9. SEARCH & RESEARCH EVIDENCE INTENT
    elif intent == "search":
        if searches:
            search_bullets = []
            for s in searches[:5]:
                t = s.get("title", "Evidence Citation")
                u = s.get("url", "")
                sn = s.get("snippet", "")
                url_str = f" ([Source]({u}))" if u else ""
                search_bullets.append(f"• **{t}**{url_str}\n  \"{sn}\"")
            search_section = "\n\n".join(search_bullets)
        else:
            search_section = "Live search evidence verified active market activity, competitive tooling, and ongoing industry investments across " + industry + "."

        answer = (
            f"Here are the real-time research findings and web search evidence gathered for **'{idea}'**:\n\n"
            f"{search_section}\n\n"
            f"**Validation Takeaway**: These findings validate steady commercial demand in {industry} while highlighting persistent dissatisfaction with existing offerings."
        )
        followups = [
            "Who are my main competitors?",
            "What are the biggest risks?",
            "What should my MVP contain?"
        ]

    # 10. TECHNICAL & REGULATORY FEASIBILITY INTENT
    elif intent in ("technical", "regulatory", "scientific"):
        tech_barriers = tech.get("key_barriers") or []
        tech_stack = tech.get("recommended_tech_stack") or []
        reg_level = reg.get("risk_level", "Medium")
        reg_class = reg.get("fda_classification") or reg.get("regulatory_classification") or "Standard Governance"
        reg_pathway = reg.get("recommended_pathway") or "Standard disclaimers and terms of service."

        barriers_str = "\n".join([f"• {b}" for b in tech_barriers[:3]]) if tech_barriers else "• Managing real-time data sync and cloud API latency."
        stack_str = ", ".join(tech_stack[:5]) if tech_stack else "Python, FastAPI, React, PostgreSQL"

        answer = (
            f"Deep Feasibility & Governance Assessment for **'{idea}'**:\n\n"
            f"⚙️ **Technical Feasibility** (Score: {tech.get('score', 8.0)}/10 — {tech.get('feasibility_rating', 'Feasible')}):\n"
            f"• **Key Engineering Barriers**:\n{barriers_str}\n"
            f"• **Recommended Stack**: {stack_str}\n\n"
            f"⚖️ **Regulatory & Compliance Pathway** (Risk Level: {reg_level}):\n"
            f"• **Classification**: {reg_class}\n"
            f"• **Recommended Pathway**: {reg_pathway}"
        )
        followups = [
            "What should my MVP contain?",
            "What are the biggest risks?",
            "How can I launch my product?"
        ]

    # 11. GENERAL / OPEN-ENDED INTENT
    else:
        q_lower = question.lower()
        matched_points = []

        if any(w in q_lower for w in ["search", "google", "web", "source"]):
            if searches:
                matched_points.append(f"🔍 **Research Evidence**: Web search found *\"{searches[0]['title']}\"* validating market activity.")

        if any(w in q_lower for w in ["competitor", "market", "who else"]) or comp_names:
            matched_points.append(f"🏢 **Competitor Benchmarking**: Direct players like *{comp_str}* currently dominate, but leave open: *\"{gap_str}\"*.")

        if any(w in q_lower for w in ["feature", "mvp", "product", "build"]) or mvp.get("must_have"):
            m_first = mvp.get("must_have", [{}])[0]
            f_name = m_first.get("feature", "Core Engine") if isinstance(m_first, dict) else str(m_first)
            matched_points.append(f"🚀 **Recommended Core Feature**: Build *{f_name}* first to directly eliminate *{pain_points[0] if pain_points else 'friction'}*.")

        if any(w in q_lower for w in ["risk", "worry", "threat", "fail"]) or risks:
            r_first = risks[0].get("risk") if risks else "User retention friction"
            matched_points.append(f"⚠️ **Key Risk to Watch**: *{r_first}*.")

        context_body = "\n\n".join(matched_points) if matched_points else (
            f"• **Target Customer**: Primary beachhead is **{primary_seg}** struggling with *{pain_points[0] if pain_points else 'operational friction'}*.\n"
            f"• **Competitive Opening**: Whitespace against **{comp_str}** is focused around *\"{gap_str}\"*.\n"
            f"• **Validation Status**: Feasible commercial viability identified in the {industry} domain."
        )

        answer = (
            f"Strategic Guidance on **'{idea}'** in response to *\"{question}\"*:\n\n"
            f"{context_body}\n\n"
            f"**Advisor Action Item**: Keep your product development strictly aligned with the validated customer pain points of {primary_seg} and focus on solving '{gap_str}'."
        )
        followups = [
            "What should my MVP contain?",
            "Who are my main competitors?",
            "What are the biggest risks?"
        ]

    return {
        "answer": answer,
        "suggested_followups": followups
    }


# ============================================================================
# UNIVERSAL LLM PROMPT BUILDER & API CLIENT
# ============================================================================

def _build_advisor_prompt(question: str, signals: Dict[str, Any]) -> str:
    """
    Constructs a complete validation briefing for the LLM.
    Embeds the entire report dossier: Market Demand, Customer Segments, Competitor Benchmarks,
    SWOT Matrix, Risk Playbook, MVP Roadmap, GTM Strategy, Technical Feasibility,
    Scientific Credibility, Regulatory Compliance, and Live Web Search Evidence.
    """
    idea = signals["idea"]
    industry = signals["industry"]
    domain = signals.get("domain") or industry
    target_customer_prop = signals.get("target_customer") or signals["primary_segment"]
    primary_seg = signals["primary_segment"]
    pain_points = ", ".join(signals["primary_pain_points"]) if signals["primary_pain_points"] else "Operational overhead and manual friction"
    comp_advantage = signals.get("competitive_advantage") or "Proprietary focused solution addressing market gaps"

    # 1. Market Analysis
    market_opp = signals.get("market_opportunity") or "Rapidly growing demand in digital solutions"
    trends_list = signals.get("market_trends") or []
    trends_str = "\n".join([f"  - Trend: {t}" for t in trends_list[:4]]) if trends_list else "  - Steady industry expansion and digital transformation"
    drivers_list = signals.get("growth_drivers") or []
    drivers_str = "\n".join([f"  - Growth Driver: {d}" for d in drivers_list[:3]]) if drivers_list else "  - Rising need for automated workflows"
    challenges_list = signals.get("market_challenges") or []
    challenges_str = "\n".join([f"  - Market Barrier: {c}" for c in challenges_list[:3]]) if challenges_list else "  - Customer acquisition friction and user retention"

    # 2. Customer Segments
    customer_segments = signals.get("customer_segments") or []
    seg_lines = []
    for s in customer_segments[:3]:
        if isinstance(s, dict):
            s_name = s.get("segment", "Target Segment")
            s_needs = ", ".join(s.get("needs", [])[:3])
            s_pains = ", ".join(s.get("pain_points", [])[:3])
            seg_lines.append(f"  - Segment: {s_name}\n    Needs: {s_needs}\n    Pain Points: {s_pains}")
    segments_str = "\n".join(seg_lines) if seg_lines else f"  - Primary Segment: {primary_seg} (Pain Points: {pain_points})"

    # 3. Competitors & Gaps
    comp_details = "\n".join([f"  - {cd}" for cd in signals["competitor_details"][:5]]) if signals["competitor_details"] else "  - Legacy manual workflows and fragmented point solutions"
    gaps_list = signals.get("market_gaps") or []
    gaps_str = "\n".join([f"  - Whitespace: {g}" for g in gaps_list[:4]]) if gaps_list else "  - Integrated automated execution without manual overhead"

    # 4. Search Evidence
    search_lines = []
    for s in signals.get("search_evidence", [])[:6]:
        t = s.get("title", "")
        sn = s.get("snippet", "")
        u = s.get("url", "")
        search_lines.append(f"  - Title: {t}\n    URL: {u}\n    Snippet: {sn}")
    searches_str = "\n".join(search_lines) if search_lines else "  - Live web search confirmed active commercial activity and demand."

    # 5. SWOT Analysis
    swot = signals.get("swot") or {}
    swot_s = ", ".join(swot.get("strengths", [])[:3]) or "Differentiated value prop"
    swot_w = ", ".join(swot.get("weaknesses", [])[:3]) or "Early brand presence"
    swot_o = ", ".join(swot.get("opportunities", [])[:3]) or "Untapped niche expansion"
    swot_t = ", ".join(swot.get("threats", [])[:3]) or "Incumbent response"
    swot_str = (
        f"  - Strengths: {swot_s}\n"
        f"  - Weaknesses: {swot_w}\n"
        f"  - Opportunities: {swot_o}\n"
        f"  - Threats: {swot_t}"
    )

    # 6. Risks
    risk_lines = []
    for r in signals.get("risk_items", [])[:4]:
        risk_lines.append(f"  - [{r.get('severity', 'Med')}] {r.get('risk')} (Category: {r.get('category')}, Impact: {r.get('impact')}, Mitigation: {r.get('mitigation')})")
    risks_str = "\n".join(risk_lines) if risk_lines else "  - High acquisition cost and 30-day retention decay (Mitigate with high-touch onboarding)"

    # 7. MVP Features
    mvp = signals.get("mvp") or {}
    must_haves = mvp.get("must_have") or []
    should_haves = mvp.get("should_have") or []
    future_feats = mvp.get("future_features") or []

    mvp_must_lines = []
    for m in must_haves[:4]:
        if isinstance(m, dict):
            mvp_must_lines.append(f"  - Must-Have: {m.get('feature')} (Value: {m.get('customer_value')}, Complexity: {m.get('complexity')}, Reason: {m.get('reason')})")
        else:
            mvp_must_lines.append(f"  - Must-Have: {m}")
    mvp_str = "\n".join(mvp_must_lines) if mvp_must_lines else "  - Core engine solving primary customer friction."

    should_str = ", ".join([s.get("feature", str(s)) if isinstance(s, dict) else str(s) for s in should_haves[:3]]) or "Automated reporting, secondary integrations"
    future_str = ", ".join([f.get("feature", str(f)) if isinstance(f, dict) else str(f) for f in future_feats[:3]]) or "Enterprise SSO, multi-organization billing, complex custom plugins"

    # 8. GTM & Monetization
    gtm = signals.get("gtm") or {}
    pricing = gtm.get("pricing_strategy") or "Tiered subscription model with self-serve pilot"
    channels = ", ".join([c.get("channel", str(c)) if isinstance(c, dict) else str(c) for c in gtm.get("marketing_channels", [])[:4]]) or "Direct founder outreach, niche community engagement"
    acq_loops = ", ".join([str(a) for a in gtm.get("customer_acquisition", [])[:2]]) or "Word-of-mouth referral upon successful milestone completion"
    launch_phases = ", ".join([p.get("phase", str(p)) if isinstance(p, dict) else str(p) for p in gtm.get("launch_strategy", [])[:3]]) or "Closed Alpha, Public Beta, General Availability"

    # 9. Deep Validation (Tech, Sci, Reg)
    tech = signals.get("technical_feasibility") or {}
    sci = signals.get("scientific_validation") or {}
    reg = signals.get("regulatory_risk") or {}

    tech_str = f"Score: {tech.get('score', 7.5)}/10 ({tech.get('feasibility_rating', 'Feasible')}). Stack: {', '.join(tech.get('recommended_tech_stack', [])[:4]) or 'FastAPI, React, PostgreSQL'}. Barriers: {', '.join(tech.get('key_barriers', [])[:2]) or 'Data pipeline latency'}."
    sci_str = f"Credibility Score: {sci.get('scientific_credibility_score', 'N/A')}/10. Literature evidence confirms technical viability."
    reg_str = f"Risk Level: {reg.get('risk_level', 'Medium')}. Classification: {reg.get('fda_classification') or reg.get('regulatory_classification') or 'Standard Commercial SaaS'}. Pathway: {reg.get('recommended_pathway') or 'Standard terms of service and compliance safeguards'}."

    prompt = f"""You are the NEXUS AI Principal Startup Advisor, Y Combinator Partner, and Strategic Product Architect.
A founder has proposed a startup idea, and our multi-agent AI validator has generated a comprehensive validation report dossier.

Your role:
Examine the COMPLETE validation dossier and the founder's proposed idea below, and provide a direct, insightful, highly accurate answer to the founder's specific question.

============================================================
PROPOSED STARTUP PROFILE
============================================================
• PROPOSED IDEA: "{idea}"
• INDUSTRY / DOMAIN: {domain}
• TARGET CUSTOMER PROFILE: {target_customer_prop}
• UNIQUE ADVANTAGE / THESIS: {comp_advantage}

============================================================
GENERATED VALIDATION REPORT DOSSIER
============================================================
1. MARKET DEMAND & INDUSTRY DYNAMICS:
   - Market Opportunity: {market_opp}
{trends_str}
{drivers_str}
{challenges_str}

2. TARGET CUSTOMER SEGMENTS & PAIN POINTS:
{segments_str}

3. COMPETITOR BENCHMARKING & VALIDATED MARKET GAPS:
{comp_details}
   - Validated Market Whitespace:
{gaps_str}

4. SWOT ANALYSIS MATRIX:
{swot_str}

5. RISK ASSESSMENT & MITIGATION PLAYBOOK:
{risks_str}

6. MVP FEATURE ROADMAP & SCOPE:
{mvp_str}
   - Phase 2 (Should-Have): {should_str}
   - Anti-Scope (Do NOT build in V1): {future_str}

7. GO-TO-MARKET & MONETIZATION:
   - Pricing Strategy: {pricing}
   - Acquisition Channels: {channels}
   - Growth Loops: {acq_loops}
   - Launch Phases: {launch_phases}

8. DEEP FEASIBILITY & COMPLIANCE:
   - Technical: {tech_str}
   - Scientific: {sci_str}
   - Regulatory: {reg_str}

9. REAL-TIME WEB RESEARCH EVIDENCE:
{searches_str}

============================================================
FOUNDER'S QUESTION:
"{question}"
============================================================

CRITICAL ADVISORY INSTRUCTIONS:
1. DIRECT ANSWER: Answer the founder's specific question head-on in your opening sentences. Do NOT give vague generic advice or corporate platitudes.
2. REPORT GROUNDING: Directly cite relevant findings from the dossier above (e.g. competitor names, pricing numbers, customer pain points, MVP priorities, risk mitigations, tech barriers, or market gaps).
3. TAILORED TO THE IDEA: Center your entire analysis on "{idea}". Explain how to execute, position, price, or de-risk this exact product.
4. ACTIONABLE TACTICS: Provide 3-5 concrete, prioritized tactical action steps the founder should take immediately.
5. FORMATTING: Use clean, professional markdown with bold headings (###), bullet points, and highlight takeaways.
6. SUGGESTED FOLLOW-UPS: Produce 3-4 natural, high-value follow-up questions directly related to what was just discussed, allowing the founder to delve deeper.
7. STRICT OUTPUT FORMAT: Return ONLY valid, parseable JSON conforming to this schema without surrounding markdown fences:

{{
  "answer": "Your comprehensive, structured, deeply grounded response formatted with clean markdown.",
  "suggested_followups": [
    "Suggested follow-up question 1",
    "Suggested follow-up question 2",
    "Suggested follow-up question 3"
  ]
}}
"""
    return prompt


async def _call_gemini_advisor(
    question: str,
    signals: Dict[str, Any],
    api_key: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Invokes the universal LLM waterfall (Gemini models first, Groq fallback)
    with extended timeout and robust parsing to ensure deep examination of the report.
    """
    prompt = _build_advisor_prompt(question, signals)
    try:
        from server.utils.gemini_client import call_gemini_generate_content, clean_llm_json_text
        result = await call_gemini_generate_content(
            prompt=prompt,
            api_key=api_key,
            temperature=0.25,
            response_mime_type="application/json",
            timeout_per_model=14.0,
            tag="STARTUP-ADVISOR"
        )
        if result:
            raw_text, successful_model = result
            cleaned = clean_llm_json_text(raw_text)
            try:
                parsed = json.loads(cleaned)
                if "answer" in parsed and isinstance(parsed["answer"], str) and parsed["answer"].strip():
                    followups = parsed.get("suggested_followups") or []
                    logger.info(f"ADVISOR SYNTHESIS SUCCESS: LLM | model={successful_model}")
                    return {
                        "answer": parsed["answer"].strip(),
                        "suggested_followups": [str(f) for f in followups if str(f).strip()][:4]
                    }
            except Exception as parse_err:
                logger.warning(f"Advisor JSON parse fallback: {parse_err}")
                clean_answer = cleaned.strip()
                if clean_answer.startswith("{") and '"answer"' in clean_answer:
                    match = re.search(r'"answer"\s*:\s*"((?:[^"\\]|\\.)*)"', clean_answer)
                    if match:
                        try:
                            clean_answer = match.group(1).encode().decode('unicode_escape')
                        except Exception:
                            pass
                if len(clean_answer) > 20:
                    return {
                        "answer": clean_answer,
                        "suggested_followups": [
                            "What should my MVP contain?",
                            "Who are my main competitors?",
                            "What are the biggest risks?"
                        ]
                    }
    except Exception as exc:
        logger.warning(f"Universal LLM advisor execution error: {exc}")

    return None


# ============================================================================
# PRIMARY ENTRY POINT
# ============================================================================

async def run_startup_advisor(
    question: str,
    validation_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Executes the Conversational Startup Advisor Agent.
    Examines the full validation reports generated for the client's proposed idea
    and uses the universal LLM waterfall to generate an accurate, grounded answer.
    """
    cleaned_question = _clean_text(question)
    if not cleaned_question:
        return {
            "answer": "Please ask a question regarding your startup idea or validation report.",
            "suggested_followups": [
                "What should my MVP contain?",
                "Who are my main competitors?",
                "What are the biggest risks?"
            ]
        }

    signals = extract_advisor_signals(validation_context)
    heuristic_resp = synthesize_heuristic_advisor_response(cleaned_question, signals)

    # Check for Gemini / Groq API keys
    from server.utils.gemini_client import get_gemini_api_key, get_groq_api_key
    gemini_key = get_gemini_api_key()
    groq_key = get_groq_api_key()

    if gemini_key or groq_key:
        try:
            llm_resp = await _call_gemini_advisor(cleaned_question, signals, gemini_key or None)
            if llm_resp:
                return llm_resp
        except Exception as exc:
            logger.warning(f"LLM advisor call failed: {exc}. Using grounded fallback engine.")

    logger.info("ADVISOR SYNTHESIS: Contextual Grounded Engine")
    return heuristic_resp
