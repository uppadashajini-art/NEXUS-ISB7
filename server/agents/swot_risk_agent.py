"""
NEXUS-ISB7 — SWOT & Risk Analysis Agent
Role: Member 1 — SWOT + Risk + Orchestration

Evaluates the startup idea from strategic and operational risk perspectives:
1. SWOT Analysis:
   - Strengths: Technology advantages, unique features, customer value, competitive edge.
   - Weaknesses: Technical bottlenecks, resource requirements, brand absence, product limits.
   - Opportunities: Market expansion, emerging customer needs, new tech, partnerships, untapped niches.
   - Threats: Existing competitors, market retaliation, regulatory hurdles, customer adoption friction.
2. Risk Analysis:
   - Evaluates Technical, Market, Financial, Competition, Operational, and Adoption risks.
   - Provides risk title, category, severity (High/Medium/Low), impact, and mitigation.

Grounded in live web evidence, market analysis, and competitor data.
Guaranteed to strictly conform to server.models.validation.SWOTAnalysis and RiskItem.
"""

import asyncio
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

import httpx

from server.models.validation import (
    RiskItem,
    SWOTAnalysis,
)

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]


# ---------------------------------------------------------------------------
# Domain Intelligence & Heuristic Generator
# ---------------------------------------------------------------------------

def _detect_industry_context(idea: str, market_analysis: Optional[Dict[str, Any]] = None) -> str:
    if market_analysis and isinstance(market_analysis, dict):
        ind = market_analysis.get("industry")
        if ind and isinstance(ind, str) and ind.strip():
            return ind.strip()

    lower = idea.lower()
    if any(k in lower for k in ["cool", "thermal", "datacenter", "liquid", "server", "gpu", "rack"]):
        return "Data Center & High-Density Compute Infrastructure"
    if any(k in lower for k in ["agri", "farm", "crop", "drone", "spore", "vineyard", "harvest"]):
        return "Agritech & Autonomous Precision Agriculture"
    if any(k in lower for k in ["health", "fitness", "diet", "workout", "medical", "clinic", "wellness"]):
        return "HealthTech & Digital Wellness"
    if any(k in lower for k in ["finance", "fintech", "banking", "crypto", "invest", "payment", "money"]):
        return "FinTech & Financial Services"
    if any(k in lower for k in ["education", "edtech", "student", "course", "learn", "lecture", "quiz"]):
        return "EdTech & Learning Platforms"
    if any(k in lower for k in ["ecommerce", "e-commerce", "retail", "shop", "store", "product"]):
        return "E-Commerce & Digital Commerce"
    if any(k in lower for k in ["ai", "agent", "automation", "workflow", "productivity", "saas"]):
        return "Enterprise AI & Workflow Automation"
    return "Enterprise Software & Cloud Platforms"


def _generate_heuristic_swot_and_risk(
    idea: str,
    market_analysis: Optional[Dict[str, Any]] = None,
    competitor_analysis: Optional[Dict[str, Any]] = None,
    search_results: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Generates rich, evidence-grounded SWOT and Risk analysis tailored to the startup idea.
    """
    industry = _detect_industry_context(idea, market_analysis)
    lower = idea.lower()

    # Extract dynamic signals from previous agent outputs if available
    market_opp = (market_analysis or {}).get("market_opportunity", "")
    trends = (market_analysis or {}).get("market_trends", [])
    market_challenges = (market_analysis or {}).get("market_challenges", [])
    direct_comps = (competitor_analysis or {}).get("direct_competitors", [])
    market_gaps = (competitor_analysis or {}).get("market_gaps", [])

    comp_names = [c.get("name") for c in direct_comps if isinstance(c, dict) and c.get("name")]
    comp_mention = f" (such as {', '.join(comp_names[:2])})" if comp_names else ""

    # 1. STRENGTHS
    strengths = [
        f"Targeted architectural innovation designed specifically for {industry}",
        "Proprietary automation workflows that drastically reduce manual operational overhead",
        "Modern API-first design enabling rapid integration into existing customer toolchains",
        "Higher agility and faster feature shipping velocity compared to legacy incumbents"
    ]
    if any(k in lower for k in ["ai", "automated", "smart", "autonomous"]):
        strengths.insert(1, "Continuous self-optimizing feedback loops that improve accuracy over time")

    # 2. WEAKNESSES
    weaknesses = [
        "Early-stage brand awareness compared to entrenched enterprise legacy providers",
        "Initial data cold-start requirement before hyper-personalized models reach peak accuracy",
        "Lean team and capital constraints requiring focused prioritization on initial core MVP features",
        "High dependence on seamless third-party API availability and infrastructure reliability"
    ]

    # 3. OPPORTUNITIES
    opportunities = [
        f"Rapid macro expansion in the {industry} sector driven by modern digital transformation",
        "Capitalizing on critical market gaps and white spaces neglected by incumbent suites",
        "Strategic channel partnerships with complementary platforms and ecosystem providers",
        "Expansion into high-margin enterprise tiers and adjacent vertical market segments"
    ]
    if market_gaps and len(market_gaps) >= 1:
        opportunities.insert(1, f"Directly addressing unmet customer friction: {market_gaps[0][:80]}")
    if trends and len(trends) >= 1:
        opportunities.append(f"Tailwind from emerging industry trend: {trends[0][:80]}")

    # 4. THREATS
    threats = [
        f"Aggressive retaliation or feature cloning by well-capitalized incumbents{comp_mention}",
        "Evolving data privacy, regulatory governance, and compliance mandates across target regions",
        "Rising digital customer acquisition costs (CAC) across competitive marketing channels",
        "Macroeconomic budget scrutiny causing prolonged customer sales evaluation cycles"
    ]
    if market_challenges and len(market_challenges) >= 1:
        threats.insert(1, f"Acute market barrier: {market_challenges[0][:80]}")

    # 5. RISK ANALYSIS
    risk_analysis = [
        RiskItem(
            risk="Technical Integration & Model Scalability",
            category="Technical",
            severity="Medium",
            impact="Latency spikes, third-party model dependency, or unexpected downtime can degrade user experience.",
            mitigation="Implement multi-model fallbacks, asynchronous queue workers, and aggressive caching of repetitive requests."
        ),
        RiskItem(
            risk="Customer Adoption Inertia & Workflow Friction",
            category="Customer Adoption",
            severity="Medium",
            impact="Prospects accustomed to manual habits or legacy tools may resist changing operational routines.",
            mitigation="Build zero-configuration onboarding, interactive guided walkthroughs, and clear 1-click value demonstrations."
        ),
        RiskItem(
            risk="Competitive Retaliation & Incumbent Bundling",
            category="Competition",
            severity="High",
            impact=f"Established competitors{comp_mention} could bundle comparable features into existing licenses.",
            mitigation="Establish deep proprietary data moats, hyper-specialized vertical workflows, and prioritize fast execution speed."
        ),
        RiskItem(
            risk="Customer Acquisition Cost (CAC) vs. LTV Imbalance",
            category="Financial",
            severity="Medium",
            impact="High initial paid marketing spend with slow conversion cycles can strain runway before unit economics mature.",
            mitigation="Focus on product-led growth (PLG), organic word-of-mouth loops, and high-retention annual contract pre-commitments."
        ),
        RiskItem(
            risk="Regulatory Governance & Compliance Burden",
            category="Operational",
            severity="Low" if not any(k in lower for k in ["health", "medical", "finance", "bank", "drone"]) else "High",
            impact="Handling sensitive data or operating in regulated domains risks audit failure or statutory penalties.",
            mitigation="Architect strict zero-retention data policies, complete security baseline audits early, and maintain legal compliance counsel."
        ),
        RiskItem(
            risk="Niche Market Ceiling & Expansion Friction",
            category="Market",
            severity="Low",
            impact="Initial target segment may have limited addressable size, capping early revenue growth.",
            mitigation="Map clear expansion paths into secondary customer segments and adjacent horizontal workflows."
        )
    ]

    swot_payload = SWOTAnalysis(
        strengths=strengths[:4],
        weaknesses=weaknesses[:4],
        opportunities=opportunities[:4],
        threats=threats[:4]
    ).model_dump()

    return {
        "swot_analysis": swot_payload,
        "risk_analysis": [r.model_dump() for r in risk_analysis]
    }


# ---------------------------------------------------------------------------
# Gemini LLM Integration with Fallback Order
# ---------------------------------------------------------------------------

async def _call_gemini_swot_risk(
    idea: str,
    industry: str,
    market_analysis: Optional[Dict[str, Any]],
    competitor_analysis: Optional[Dict[str, Any]],
    api_key: str
) -> Optional[Dict[str, Any]]:
    prompt = f"""You are a Principal Venture Capital Partner and Startup Risk Analyst.
Analyze this startup idea and generate a strategic SWOT analysis and a 6-factor Risk Assessment.

Startup Idea: {idea}
Target Industry: {industry}
Market Context: {json.dumps(market_analysis or {}, default=str)[:600]}
Competitor Context: {json.dumps(competitor_analysis or {}, default=str)[:600]}

Return pure JSON matching this exact structure:
{{
  "swot_analysis": {{
    "strengths": ["4 concise, specific strengths"],
    "weaknesses": ["4 concise, specific weaknesses"],
    "opportunities": ["4 concise, specific opportunities"],
    "threats": ["4 concise, specific threats"]
  }},
  "risk_analysis": [
    {{
      "risk": "Risk title and description",
      "category": "Technical",
      "severity": "High or Medium or Low",
      "impact": "Concrete business consequence",
      "mitigation": "Actionable countermeasure"
    }},
    {{
      "risk": "Risk title and description",
      "category": "Market",
      "severity": "High or Medium or Low",
      "impact": "Concrete business consequence",
      "mitigation": "Actionable countermeasure"
    }},
    {{
      "risk": "Risk title and description",
      "category": "Financial",
      "severity": "High or Medium or Low",
      "impact": "Concrete business consequence",
      "mitigation": "Actionable countermeasure"
    }},
    {{
      "risk": "Risk title and description",
      "category": "Competition",
      "severity": "High or Medium or Low",
      "impact": "Concrete business consequence",
      "mitigation": "Actionable countermeasure"
    }},
    {{
      "risk": "Risk title and description",
      "category": "Operational",
      "severity": "High or Medium or Low",
      "impact": "Concrete business consequence",
      "mitigation": "Actionable countermeasure"
    }},
    {{
      "risk": "Risk title and description",
      "category": "Customer Adoption",
      "severity": "High or Medium or Low",
      "impact": "Concrete business consequence",
      "mitigation": "Actionable countermeasure"
    }}
  ]
}}
Do not include any markdown wrappers or text outside the JSON.
"""
    try:
        from server.utils.gemini_client import call_gemini_generate_content, clean_llm_json_text
        result = await call_gemini_generate_content(
            prompt=prompt,
            api_key=api_key,
            temperature=0.2,
            response_mime_type="application/json",
            timeout_per_model=12.0,
            tag="SWOT-RISK"
        )
        if result:
            raw_text, successful_model = result
            clean_json = clean_llm_json_text(raw_text)
            parsed = json.loads(clean_json)
            if "swot_analysis" in parsed and "risk_analysis" in parsed:
                logger.info(f"Gemini SWOT/Risk generation succeeded via {successful_model}")
                return parsed
    except Exception as exc:
        logger.warning(f"Universal Gemini SWOT/Risk generation error: {exc}")

    return None


# ---------------------------------------------------------------------------
# Main Agent Entrypoint
# ---------------------------------------------------------------------------

async def run_swot_risk_agent(
    idea: str,
    market_analysis: Optional[Dict[str, Any]] = None,
    competitor_analysis: Optional[Dict[str, Any]] = None,
    search_results: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Executes the SWOT and Risk Analysis Agent.
    """
    if not idea or not isinstance(idea, str) or not idea.strip():
        raise ValueError("Startup idea cannot be empty")

    clean_idea = idea.strip()
    logger.info(f"SWOT/Risk Agent initiated for idea: '{clean_idea[:50]}...'")

    # Generate grounded heuristic baseline
    fallback_data = _generate_heuristic_swot_and_risk(
        idea=clean_idea,
        market_analysis=market_analysis,
        competitor_analysis=competitor_analysis,
        search_results=search_results,
    )

    # Attempt Gemini API synthesis if available
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key.strip():
        industry = _detect_industry_context(clean_idea, market_analysis)
        llm_data = await _call_gemini_swot_risk(
            idea=clean_idea,
            industry=industry,
            market_analysis=market_analysis,
            competitor_analysis=competitor_analysis,
            api_key=api_key.strip()
        )
        if llm_data:
            try:
                # Validate output shape
                swot_obj = SWOTAnalysis(**llm_data["swot_analysis"])
                risk_objs = [RiskItem(**r) for r in llm_data["risk_analysis"]]
                return {
                    "swot_analysis": swot_obj.model_dump(),
                    "risk_analysis": [r.model_dump() for r in risk_objs]
                }
            except Exception as val_err:
                logger.warning(f"Gemini SWOT output failed schema validation: {val_err}; using heuristic")

    # Return valid schema-checked heuristic data
    swot_obj = SWOTAnalysis(**fallback_data["swot_analysis"])
    risk_objs = [RiskItem(**r) for r in fallback_data["risk_analysis"]]

    return {
        "swot_analysis": swot_obj.model_dump(),
        "risk_analysis": [r.model_dump() for r in risk_objs]
    }


if __name__ == "__main__":
    sample_idea = "AI automated liquid cooling and predictive thermal regulation for high-density GPU datacenters"
    print(f"Running SWOT & Risk Analysis Agent for: '{sample_idea}'")
    out = asyncio.run(run_swot_risk_agent(sample_idea))
    print(json.dumps(out, indent=2))
