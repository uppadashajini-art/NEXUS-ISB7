"""
NEXUS-ISB7 — MVP Feature Recommendation Agent

Role: Member 2

Responsibilities:
- Analyze startup idea
- Use market analysis
- Use competitor analysis
- Use SWOT and risk context when available
- Recommend MVP features
- Categorize features into:
    Must Have
    Should Have
    Could Have
    Future Features
- Provide reason, customer value and implementation complexity
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Feature creation helper
# ---------------------------------------------------------

def _create_feature(
    feature: str,
    priority: str,
    reason: str,
    customer_value: str,
    complexity: str,
) -> Dict[str, str]:
    """
    Create one standardized MVP feature object.
    """

    return {
        "feature": feature,
        "priority": priority,
        "reason": reason,
        "customer_value": customer_value,
        "complexity": complexity,
    }


# ---------------------------------------------------------
# Context extraction helpers
# ---------------------------------------------------------

def _get_customer_needs(
    market_analysis: Optional[Dict[str, Any]]
) -> List[str]:
    """
    Extract customer needs/pain points from market analysis.
    """

    if not market_analysis:
        return []

    needs = []

    for key in [
        "customer_needs",
        "pain_points",
        "customer_pain_points",
        "customer_problems",
    ]:
        value = market_analysis.get(key)

        if isinstance(value, list):
            needs.extend(str(item) for item in value)

        elif isinstance(value, str) and value.strip():
            needs.append(value)

    return needs


def _get_customer_segments(
    market_analysis: Optional[Dict[str, Any]]
) -> List[str]:
    """
    Extract customer segments from market analysis.
    """

    if not market_analysis:
        return []

    segments = market_analysis.get("customer_segments", [])

    if isinstance(segments, list):
        return [str(item) for item in segments]

    if isinstance(segments, str) and segments.strip():
        return [segments]

    return []


def _get_market_gaps(
    competitor_analysis: Optional[Dict[str, Any]]
) -> List[str]:
    """
    Extract market gaps from competitor analysis.
    """

    if not competitor_analysis:
        return []

    gaps = competitor_analysis.get("market_gaps", [])

    if isinstance(gaps, list):
        return [str(item) for item in gaps]

    if isinstance(gaps, str) and gaps.strip():
        return [gaps]

    return []


def _get_competitors(
    competitor_analysis: Optional[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Extract direct competitors.
    """

    if not competitor_analysis:
        return []

    competitors = competitor_analysis.get(
        "direct_competitors",
        []
    )

    if isinstance(competitors, list):
        return [
            item for item in competitors
            if isinstance(item, dict)
        ]

    return []


# ---------------------------------------------------------
# Feature recommendation logic
# ---------------------------------------------------------

def _generate_features(
    idea: str,
    market_analysis: Optional[Dict[str, Any]],
    competitor_analysis: Optional[Dict[str, Any]],
    swot_analysis: Optional[Dict[str, Any]],
    risk_analysis: Optional[List[Dict[str, Any]]],
) -> Dict[str, List[Dict[str, str]]]:
    """
    Generate MVP feature recommendations using available context.
    """

    customer_needs = _get_customer_needs(market_analysis)
    customer_segments = _get_customer_segments(market_analysis)
    market_gaps = _get_market_gaps(competitor_analysis)
    competitors = _get_competitors(competitor_analysis)

    must_have = []
    should_have = []
    could_have = []
    future_features = []

    # -----------------------------------------------------
    # Core product feature
    # -----------------------------------------------------

    must_have.append(
        _create_feature(
            feature="Core Product Functionality",
            priority="Must Have",
            reason=(
                "The MVP must provide the primary functionality "
                "described in the startup idea."
            ),
            customer_value="High",
            complexity="Medium",
        )
    )

    # -----------------------------------------------------
    # Customer needs
    # -----------------------------------------------------

    if customer_needs:

        must_have.append(
            _create_feature(
                feature="Customer Pain Point Solution",
                priority="Must Have",
                reason=(
                    "This feature directly addresses the customer "
                    "needs and pain points identified in the market analysis."
                ),
                customer_value="High",
                complexity="Medium",
            )
        )

    # -----------------------------------------------------
    # Customer segments
    # -----------------------------------------------------

    if customer_segments:

        must_have.append(
            _create_feature(
                feature="Customer Profile and Preferences",
                priority="Must Have",
                reason=(
                    "The product should capture the target customer's "
                    "basic profile and preferences so the core experience "
                    "can be tailored to the intended users."
                ),
                customer_value="High",
                complexity="Medium",
            )
        )

    # -----------------------------------------------------
    # Market gaps
    # -----------------------------------------------------

    if market_gaps:

        should_have.append(
            _create_feature(
                feature="Market Gap Differentiation",
                priority="Should Have",
                reason=(
                    "This capability can help address gaps identified "
                    "in the competitor analysis and differentiate the product."
                ),
                customer_value="High",
                complexity="Medium",
            )
        )

    # -----------------------------------------------------
    # Competitor analysis
    # -----------------------------------------------------

    if competitors:

        should_have.append(
            _create_feature(
                feature="Competitor-Informed Feature Comparison",
                priority="Should Have",
                reason=(
                    "Competitor analysis can be used to understand "
                    "existing capabilities and provide useful differentiation."
                ),
                customer_value="Medium",
                complexity="Medium",
            )
        )

    # -----------------------------------------------------
    # Feedback
    # -----------------------------------------------------

    should_have.append(
        _create_feature(
            feature="User Feedback Collection",
            priority="Should Have",
            reason=(
                "Early user feedback can help validate the MVP "
                "and identify improvements before wider launch."
            ),
            customer_value="High",
            complexity="Low",
        )
    )

    # -----------------------------------------------------
    # Analytics
    # -----------------------------------------------------

    could_have.append(
        _create_feature(
            feature="Basic Usage Analytics",
            priority="Could Have",
            reason=(
                "Analytics can help understand user behavior, "
                "but detailed analytics are not required for the first release."
            ),
            customer_value="Medium",
            complexity="Medium",
        )
    )

    # -----------------------------------------------------
    # Notifications
    # -----------------------------------------------------

    could_have.append(
        _create_feature(
            feature="Notifications and Reminders",
            priority="Could Have",
            reason=(
                "Notifications may improve engagement after the core "
                "product experience has been validated."
            ),
            customer_value="Medium",
            complexity="Low",
        )
    )

    # -----------------------------------------------------
    # Advanced AI
    # -----------------------------------------------------

    future_features.append(
        _create_feature(
            feature="Advanced AI Personalization",
            priority="Future Features",
            reason=(
                "Advanced personalization can be added after sufficient "
                "user data and MVP validation have been collected."
            ),
            customer_value="High",
            complexity="High",
        )
    )

    # -----------------------------------------------------
    # Integrations
    # -----------------------------------------------------

    future_features.append(
        _create_feature(
            feature="Third-Party Integrations",
            priority="Future Features",
            reason=(
                "External integrations can expand the product ecosystem "
                "after the core MVP has been validated."
            ),
            customer_value="Medium",
            complexity="High",
        )
    )

    return {
        "must_have": must_have,
        "should_have": should_have,
        "could_have": could_have,
        "future_features": future_features,
    }


# ---------------------------------------------------------
# Main Agent
# ---------------------------------------------------------

async def run_mvp_recommendation_agent(
    idea: str,
    market_analysis: Optional[Dict[str, Any]] = None,
    competitor_analysis: Optional[Dict[str, Any]] = None,
    swot_analysis: Optional[Dict[str, Any]] = None,
    risk_analysis: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Main entry point for the MVP Recommendation Agent.

    Parameters:
        idea:
            Startup idea.

        market_analysis:
            Output from Market Analysis Agent.

        competitor_analysis:
            Output from Competitor Analysis Agent.

        swot_analysis:
            Output from SWOT/Risk Agent.

        risk_analysis:
            Risk information generated by SWOT/Risk Agent.

    Returns:
        Structured MVP recommendation dictionary.
    """

    # -----------------------------------------------------
    # Input validation
    # -----------------------------------------------------

    if idea is None or not idea.strip():
        raise ValueError("Startup idea cannot be empty")

    if len(idea.strip()) < 10:
        raise ValueError("Startup idea is too short")

    try:

        recommendations = _generate_features(
            idea=idea.strip(),
            market_analysis=market_analysis,
            competitor_analysis=competitor_analysis,
            swot_analysis=swot_analysis,
            risk_analysis=risk_analysis,
        )

        return {
            "mvp_recommendations": recommendations
        }

    except Exception as exc:

        logger.exception(
            "MVP Recommendation Agent failed: %s",
            exc
        )

        # Graceful fallback
        return {
            "mvp_recommendations": {
                "must_have": [
                    _create_feature(
                        feature="Core Product Functionality",
                        priority="Must Have",
                        reason=(
                            "The first release must provide the "
                            "core functionality described by the startup idea."
                        ),
                        customer_value="High",
                        complexity="Medium",
                    )
                ],
                "should_have": [],
                "could_have": [],
                "future_features": [],
            }
        }