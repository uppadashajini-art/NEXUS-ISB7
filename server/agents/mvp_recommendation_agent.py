"""
NEXUS-ISB7 — MVP Feature Recommendation Agent

Role:
    Member 2 — MVP Feature Recommendation

Purpose:
    Analyze startup idea + previous agent outputs and recommend
    prioritized MVP features.

Inputs:
    - Startup idea
    - Market analysis
    - Competitor analysis
    - SWOT analysis
    - Risk analysis

Outputs:
    {
        "mvp_recommendations": {
            "must_have": [...],
            "should_have": [...],
            "could_have": [...],
            "future_features": [...]
        }
    }

Design principles:
    - Deterministic
    - Explainable
    - Context-aware
    - No hallucinated market facts
    - Graceful handling of missing context
    - Compatible with the NEXUS orchestrator
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from server.models.validation import MVPFeature, MVPRecommendations


logger = logging.getLogger(__name__)


# =====================================================================
# Constants
# =====================================================================

VALID_PRIORITIES = {
    "Must Have",
    "Should Have",
    "Could Have",
    "Future Features",
}

VALID_CUSTOMER_VALUES = {
    "High",
    "Medium",
    "Low",
}

VALID_COMPLEXITIES = {
    "High",
    "Medium",
    "Low",
}


# =====================================================================
# Generic helper functions
# =====================================================================

def _is_empty(value: Any) -> bool:
    """
    Return True when a value is None, empty string, empty list,
    or empty dictionary.
    """

    if value is None:
        return True

    if isinstance(value, str):
        return not value.strip()

    if isinstance(value, (list, tuple, set, dict)):
        return len(value) == 0

    return False


def _to_dict(value: Any) -> Dict[str, Any]:
    """
    Convert dictionaries, Pydantic models, and objects into dictionaries.
    """

    if value is None:
        return {}

    if isinstance(value, dict):
        return value

    # Pydantic v2
    if hasattr(value, "model_dump"):
        try:
            result = value.model_dump()
            if isinstance(result, dict):
                return result
        except Exception:
            pass

    # Pydantic v1
    if hasattr(value, "dict"):
        try:
            result = value.dict()
            if isinstance(result, dict):
                return result
        except Exception:
            pass

    # Generic object
    if hasattr(value, "__dict__"):
        try:
            return {
                key: val
                for key, val in vars(value).items()
                if not key.startswith("_")
            }
        except Exception:
            pass

    return {}


def _clean_text(value: Any) -> str:
    """
    Safely convert a value into clean text.
    """

    if value is None:
        return ""

    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()

    if isinstance(value, (int, float, bool)):
        return str(value)

    return str(value).strip()


def _normalize_text(value: Any) -> str:
    """
    Normalize text for comparison and duplicate detection.
    """

    text = _clean_text(value).lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    return text


def _unique_strings(values: List[Any]) -> List[str]:
    """
    Clean and deduplicate a list of values.
    """

    result: List[str] = []
    seen = set()

    for value in values:

        text = _clean_text(value)

        if not text:
            continue

        normalized = _normalize_text(text)

        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(normalized)
        result.append(text)

    return result


def _shorten(text: str, max_length: int = 90) -> str:
    """
    Keep generated feature names/reasons concise.
    """

    text = _clean_text(text)

    if len(text) <= max_length:
        return text

    shortened = text[:max_length].rsplit(" ", 1)[0]

    return shortened.rstrip(".,;:-")


# =====================================================================
# Context extraction
# =====================================================================

def _get_customer_segments(
    market_analysis: Optional[Any],
) -> List[str]:
    """
    Extract customer segment names from market analysis.

    Supports:
        ["Students", "Professionals"]

    and:

        [
            {
                "segment": "Students",
                "needs": [...],
                "pain_points": [...]
            }
        ]
    """

    data = _to_dict(market_analysis)

    raw_segments = data.get(
        "customer_segments",
        data.get("segments", []),
    )

    if not isinstance(raw_segments, list):
        return []

    segments: List[str] = []

    for item in raw_segments:

        if isinstance(item, str):
            segments.append(item)
            continue

        item_dict = _to_dict(item)

        segment = (
            item_dict.get("segment")
            or item_dict.get("name")
            or item_dict.get("customer_segment")
            or item_dict.get("title")
        )

        if segment:
            segments.append(_clean_text(segment))

    return _unique_strings(segments)


def _get_customer_needs(
    market_analysis: Optional[Any],
) -> List[str]:
    """
    Extract customer needs from market analysis.
    """

    data = _to_dict(market_analysis)

    needs: List[Any] = []

    for key in [
        "customer_needs",
        "customer_need",
        "needs",
        "user_needs",
        "customer_requirements",
    ]:
        value = data.get(key)

        if isinstance(value, list):
            needs.extend(value)

        elif isinstance(value, str):
            needs.append(value)

    # Also inspect nested customer segments.
    segments = data.get("customer_segments", [])

    if isinstance(segments, list):

        for segment in segments:

            segment_dict = _to_dict(segment)

            for key in [
                "needs",
                "customer_needs",
                "requirements",
            ]:
                value = segment_dict.get(key)

                if isinstance(value, list):
                    needs.extend(value)

                elif isinstance(value, str):
                    needs.append(value)

    return _unique_strings(needs)


def _get_pain_points(
    market_analysis: Optional[Any],
) -> List[str]:
    """
    Extract customer pain points from market analysis.
    """

    data = _to_dict(market_analysis)

    pain_points: List[Any] = []

    for key in [
        "pain_points",
        "customer_pain_points",
        "customer_problems",
        "problems",
        "user_pain_points",
        "challenges",
    ]:
        value = data.get(key)

        if isinstance(value, list):
            pain_points.extend(value)

        elif isinstance(value, str):
            pain_points.append(value)

    # Also inspect nested customer segments.
    segments = data.get("customer_segments", [])

    if isinstance(segments, list):

        for segment in segments:

            segment_dict = _to_dict(segment)

            for key in [
                "pain_points",
                "customer_pain_points",
                "problems",
                "challenges",
            ]:
                value = segment_dict.get(key)

                if isinstance(value, list):
                    pain_points.extend(value)

                elif isinstance(value, str):
                    pain_points.append(value)

    return _unique_strings(pain_points)


def _get_competitors(
    competitor_analysis: Optional[Any],
) -> List[Dict[str, Any]]:
    """
    Extract competitor objects.
    """

    data = _to_dict(competitor_analysis)

    competitors: List[Dict[str, Any]] = []

    for key in [
        "direct_competitors",
        "indirect_competitors",
        "competitors",
    ]:

        value = data.get(key)

        if not isinstance(value, list):
            continue

        for item in value:

            if isinstance(item, dict):
                competitors.append(item)

            else:
                item_dict = _to_dict(item)

                if item_dict:
                    competitors.append(item_dict)

    return competitors


def _get_competitor_features(
    competitor_analysis: Optional[Any],
) -> List[str]:
    """
    Extract features offered by competitors.
    """

    competitors = _get_competitors(competitor_analysis)

    features: List[Any] = []

    for competitor in competitors:

        for key in [
            "key_features",
            "features",
            "core_features",
            "product_features",
        ]:

            value = competitor.get(key)

            if isinstance(value, list):
                features.extend(value)

            elif isinstance(value, str):
                features.append(value)

    # Some competitor-analysis implementations may return
    # comparison rows separately.
    data = _to_dict(competitor_analysis)

    comparisons = data.get("comparison", [])

    if isinstance(comparisons, list):

        for comparison in comparisons:

            comparison_dict = _to_dict(comparison)

            for key in [
                "features",
                "key_features",
                "competitor_features",
            ]:

                value = comparison_dict.get(key)

                if isinstance(value, list):
                    features.extend(value)

                elif isinstance(value, str):
                    features.append(value)

    return _unique_strings(features)


def _get_competitor_weaknesses(
    competitor_analysis: Optional[Any],
) -> List[str]:
    """
    Extract competitor weaknesses.
    """

    competitors = _get_competitors(competitor_analysis)

    weaknesses: List[Any] = []

    for competitor in competitors:

        for key in [
            "weaknesses",
            "weakness",
            "limitations",
            "gaps",
        ]:

            value = competitor.get(key)

            if isinstance(value, list):
                weaknesses.extend(value)

            elif isinstance(value, str):
                weaknesses.append(value)

    return _unique_strings(weaknesses)


def _get_market_gaps(
    competitor_analysis: Optional[Any],
) -> List[str]:
    """
    Extract identified market gaps.
    """

    data = _to_dict(competitor_analysis)

    gaps: List[Any] = []

    for key in [
        "market_gaps",
        "gaps",
        "market_gap",
        "opportunities",
    ]:

        value = data.get(key)

        if isinstance(value, list):
            gaps.extend(value)

        elif isinstance(value, str):
            gaps.append(value)

    return _unique_strings(gaps)


def _get_swot_items(
    swot_analysis: Optional[Any],
) -> Tuple[List[str], List[str], List[str], List[str]]:
    """
    Extract:
        strengths
        weaknesses
        opportunities
        threats
    """

    data = _to_dict(swot_analysis)

    strengths = _unique_strings(
        data.get("strengths", [])
        if isinstance(data.get("strengths", []), list)
        else [data.get("strengths")]
    )

    weaknesses = _unique_strings(
        data.get("weaknesses", [])
        if isinstance(data.get("weaknesses", []), list)
        else [data.get("weaknesses")]
    )

    opportunities = _unique_strings(
        data.get("opportunities", [])
        if isinstance(data.get("opportunities", []), list)
        else [data.get("opportunities")]
    )

    threats = _unique_strings(
        data.get("threats", [])
        if isinstance(data.get("threats", []), list)
        else [data.get("threats")]
    )

    return (
        strengths,
        weaknesses,
        opportunities,
        threats,
    )


def _get_risks(
    risk_analysis: Optional[Any],
) -> List[Dict[str, Any]]:
    """
    Extract structured risk objects.

    Supports:
        {
            "risks": [
                {
                    "risk": "...",
                    "severity": "High",
                    "impact": "...",
                    "mitigation": "..."
                }
            ]
        }

    Also handles simpler string risks.
    """

    data = _to_dict(risk_analysis)

    raw_risks = (
        data.get("risks")
        or data.get("risk_analysis")
        or data.get("identified_risks")
        or []
    )

    if not isinstance(raw_risks, list):
        raw_risks = [raw_risks]

    risks: List[Dict[str, Any]] = []

    for item in raw_risks:

        if isinstance(item, str):

            text = _clean_text(item)

            if text:
                risks.append(
                    {
                        "risk": text,
                        "severity": "",
                        "impact": "",
                        "mitigation": "",
                    }
                )

            continue

        item_dict = _to_dict(item)

        if not item_dict:
            continue

        risk_text = (
            item_dict.get("risk")
            or item_dict.get("name")
            or item_dict.get("description")
            or item_dict.get("title")
        )

        if not risk_text:
            continue

        risks.append(
            {
                "risk": _clean_text(risk_text),
                "severity": _clean_text(
                    item_dict.get("severity")
                    or item_dict.get("risk_level")
                    or item_dict.get("priority")
                ),
                "impact": _clean_text(
                    item_dict.get("impact")
                    or item_dict.get("potential_impact")
                ),
                "mitigation": _clean_text(
                    item_dict.get("mitigation")
                    or item_dict.get("mitigation_strategy")
                    or item_dict.get("recommendation")
                ),
            }
        )

    return risks


# =====================================================================
# Feature analysis helpers
# =====================================================================

def _estimate_complexity(
    feature_name: str,
    reason: str,
) -> str:
    """
    Estimate implementation complexity.

    This is an MVP planning heuristic, not an engineering estimate.
    """

    text = (
        f"{feature_name} {reason}"
    ).lower()

    high_complexity_keywords = [
        "advanced ai",
        "machine learning",
        "deep learning",
        "real-time",
        "realtime",
        "multi-platform",
        "complex automation",
        "advanced personalization",
        "third-party integration",
        "third party integration",
        "large-scale",
        "large scale",
        "prediction",
        "recommendation engine",
    ]

    medium_complexity_keywords = [
        "personalization",
        "authentication",
        "authorization",
        "payment",
        "integration",
        "dashboard",
        "tracking",
        "comparison",
        "notification",
        "reminder",
        "analytics",
    ]

    for keyword in high_complexity_keywords:
        if keyword in text:
            return "High"

    for keyword in medium_complexity_keywords:
        if keyword in text:
            return "Medium"

    return "Low"


def _estimate_customer_value(
    category: str,
    evidence_type: str,
) -> str:
    """
    Estimate customer value from the reason/evidence source.
    """

    evidence = evidence_type.lower()

    if (
        category == "Must Have"
        or evidence in {
            "pain_point",
            "high_risk",
            "market_gap",
            "customer_need",
        }
    ):
        return "High"

    if category == "Should Have":
        return "High" if evidence in {
            "competitor_weakness",
            "swot_opportunity",
        } else "Medium"

    if category == "Could Have":
        return "Medium"

    return "Low"


def _priority_rank(priority: str) -> int:
    """
    Lower number = higher priority.
    """

    ranks = {
        "Must Have": 1,
        "Should Have": 2,
        "Could Have": 3,
        "Future Features": 4,
    }

    return ranks.get(priority, 99)


def _make_short_phrase(text: str, max_words: int = 7) -> str:
    """
    Convert context into a short readable feature phrase.
    """

    text = _clean_text(text)

    if not text:
        return "identified requirement"

    # Remove common sentence prefixes.
    text = re.sub(
        r"^(lack of|difficulty with|difficulty in|limited|lack|"
        r"users need|customers need|users have|customers have)\s+",
        "",
        text,
        flags=re.IGNORECASE,
    )

    words = text.split()

    if len(words) > max_words:
        text = " ".join(words[:max_words])

    text = text.strip(" .,:;-")

    if not text:
        return "identified requirement"

    return text


def _contains_any(
    text: str,
    keywords: List[str],
) -> bool:
    """
    Return True when any keyword occurs in text.
    """

    normalized = _normalize_text(text)

    return any(
        _normalize_text(keyword) in normalized
        for keyword in keywords
    )


# =====================================================================
# Feature creation
# =====================================================================

def _create_feature(
    feature: str,
    priority: str,
    reason: str,
    customer_value: str,
    complexity: str,
) -> Dict[str, str]:
    """
    Create a feature dictionary matching MVPFeature.
    """

    if priority not in VALID_PRIORITIES:
        priority = "Could Have"

    if customer_value not in VALID_CUSTOMER_VALUES:
        customer_value = "Medium"

    if complexity not in VALID_COMPLEXITIES:
        complexity = "Medium"

    return {
        "feature": _clean_text(feature),
        "priority": priority,
        "reason": _clean_text(reason),
        "customer_value": customer_value,
        "complexity": complexity,
    }


def _add_feature(
    candidates: List[Dict[str, Any]],
    seen: set,
    feature: str,
    priority: str,
    reason: str,
    customer_value: str,
    complexity: str,
    score: float,
    evidence_type: str,
) -> None:
    """
    Add a feature candidate while preventing duplicates.
    """

    feature = _clean_text(feature)

    if not feature:
        return

    normalized = _normalize_text(feature)

    if not normalized:
        return

    if normalized in seen:
        return

    seen.add(normalized)

    candidates.append(
        {
            "feature": feature,
            "priority": priority,
            "reason": reason,
            "customer_value": customer_value,
            "complexity": complexity,
            "score": score,
            "evidence_type": evidence_type,
        }
    )


# =====================================================================
# Main recommendation generation
# =====================================================================

def _generate_features(
    idea: str,
    market_analysis: Optional[Any],
    competitor_analysis: Optional[Any],
    swot_analysis: Optional[Any],
    risk_analysis: Optional[Any],
) -> List[Dict[str, Any]]:
    """
    Generate context-aware MVP feature candidates.

    The algorithm deliberately combines multiple evidence sources:

        Customer pain point
            ↓
        Customer need
            ↓
        Market gap
            ↓
        Competitor weakness/features
            ↓
        SWOT
            ↓
        Risk
            ↓
        Feature candidate
            ↓
        Priority
    """

    candidates: List[Dict[str, Any]] = []
    seen = set()

    # ---------------------------------------------------------------
    # Extract context
    # ---------------------------------------------------------------

    customer_segments = _get_customer_segments(
        market_analysis
    )

    customer_needs = _get_customer_needs(
        market_analysis
    )

    pain_points = _get_pain_points(
        market_analysis
    )

    competitors = _get_competitors(
        competitor_analysis
    )

    competitor_features = _get_competitor_features(
        competitor_analysis
    )

    competitor_weaknesses = _get_competitor_weaknesses(
        competitor_analysis
    )

    market_gaps = _get_market_gaps(
        competitor_analysis
    )

    (
        swot_strengths,
        swot_weaknesses,
        swot_opportunities,
        swot_threats,
    ) = _get_swot_items(
        swot_analysis
    )

    risks = _get_risks(
        risk_analysis
    )

    # ---------------------------------------------------------------
    # 1. Core product functionality
    # ---------------------------------------------------------------

    _add_feature(
        candidates=candidates,
        seen=seen,
        feature="Core Product Functionality",
        priority="Must Have",
        reason=(
            "The MVP must provide the primary functionality "
            "described in the startup idea so that the core "
            "value proposition can be validated."
        ),
        customer_value="High",
        complexity=_estimate_complexity(
            "Core Product Functionality",
            idea,
        ),
        score=100,
        evidence_type="core",
    )

    # ---------------------------------------------------------------
    # 2. Customer pain points
    # ---------------------------------------------------------------

    for index, pain_point in enumerate(
        pain_points[:5]
    ):

        phrase = _make_short_phrase(
            pain_point
        )

        feature_name = (
            f"Pain Point Resolution: {phrase}"
        )

        reason = (
            f"Market analysis identified the customer pain point "
            f"'{pain_point}'. Addressing this problem directly "
            f"helps the MVP solve a validated customer problem."
        )

        _add_feature(
            candidates=candidates,
            seen=seen,
            feature=feature_name,
            priority="Must Have",
            reason=reason,
            customer_value="High",
            complexity=_estimate_complexity(
                feature_name,
                reason,
            ),
            score=95 - index * 2,
            evidence_type="pain_point",
        )

    # ---------------------------------------------------------------
    # 3. Customer needs
    # ---------------------------------------------------------------

    for index, need in enumerate(
        customer_needs[:5]
    ):

        phrase = _make_short_phrase(
            need
        )

        feature_name = (
            f"Customer Need Support: {phrase}"
        )

        reason = (
            f"Market analysis identified the customer need "
            f"'{need}'. Supporting this need helps align the "
            f"initial product with the intended users."
        )

        _add_feature(
            candidates=candidates,
            seen=seen,
            feature=feature_name,
            priority="Must Have",
            reason=reason,
            customer_value="High",
            complexity=_estimate_complexity(
                feature_name,
                reason,
            ),
            score=90 - index * 2,
            evidence_type="customer_need",
        )

    # ---------------------------------------------------------------
    # 4. Customer profile and segmentation
    # ---------------------------------------------------------------

    if customer_segments:

        segment_text = ", ".join(
            customer_segments[:3]
        )

        _add_feature(
            candidates=candidates,
            seen=seen,
            feature="Customer Profile and Preferences",
            priority="Must Have",
            reason=(
                f"Market analysis identified target customer "
                f"segments including {segment_text}. Capturing "
                f"relevant customer profile information allows "
                f"the MVP experience to be aligned with those users."
            ),
            customer_value="High",
            complexity="Medium",
            score=87,
            evidence_type="customer_segment",
        )

    # ---------------------------------------------------------------
    # 5. Market gaps
    # ---------------------------------------------------------------

    for index, gap in enumerate(
        market_gaps[:5]
    ):

        phrase = _make_short_phrase(
            gap
        )

        feature_name = (
            f"Market Gap Differentiation: {phrase}"
        )

        reason = (
            f"Competitor and market analysis identified the gap "
            f"'{gap}'. Addressing this gap can differentiate the "
            f"MVP from the alternatives identified during validation."
        )

        _add_feature(
            candidates=candidates,
            seen=seen,
            feature=feature_name,
            priority="Should Have",
            reason=reason,
            customer_value="High",
            complexity=_estimate_complexity(
                feature_name,
                reason,
            ),
            score=82 - index * 2,
            evidence_type="market_gap",
        )

    # ---------------------------------------------------------------
    # 6. Competitor weaknesses
    # ---------------------------------------------------------------

    for index, weakness in enumerate(
        competitor_weaknesses[:4]
    ):

        phrase = _make_short_phrase(
            weakness
        )

        feature_name = (
            f"Competitor Gap Improvement: {phrase}"
        )

        reason = (
            f"Competitor analysis identified the limitation "
            f"'{weakness}'. A focused MVP capability addressing "
            f"this limitation can provide a differentiated user "
            f"experience without attempting to replicate every "
            f"competitor capability."
        )

        _add_feature(
            candidates=candidates,
            seen=seen,
            feature=feature_name,
            priority="Should Have",
            reason=reason,
            customer_value="High",
            complexity=_estimate_complexity(
                feature_name,
                reason,
            ),
            score=80 - index * 2,
            evidence_type="competitor_weakness",
        )

    # ---------------------------------------------------------------
    # 7. Competitor-informed comparison
    # ---------------------------------------------------------------

    if competitors or competitor_features:

        competitor_names = []

        for competitor in competitors[:3]:

            name = (
                competitor.get("name")
                or competitor.get("competitor")
                or competitor.get("title")
            )

            if name:
                competitor_names.append(
                    _clean_text(name)
                )

        if competitor_names:

            competitor_text = ", ".join(
                competitor_names
            )

            reason = (
                f"Competitor analysis identified alternatives "
                f"including {competitor_text}. A focused comparison "
                f"capability helps the MVP understand and communicate "
                f"how its core offering differs from existing options."
            )

        else:

            reason = (
                "Competitor analysis identified existing product "
                "features. A focused comparison capability can help "
                "the MVP understand competitive differences."
            )

        _add_feature(
            candidates=candidates,
            seen=seen,
            feature="Competitor-Informed Feature Comparison",
            priority="Should Have",
            reason=reason,
            customer_value="Medium",
            complexity="Medium",
            score=75,
            evidence_type="competitor",
        )

    # ---------------------------------------------------------------
    # 8. Competitor feature awareness
    # ---------------------------------------------------------------

    if competitor_features:

        feature_sample = ", ".join(
            competitor_features[:3]
        )

        reason = (
            f"Competitor analysis identified capabilities such as "
            f"'{feature_sample}'. Tracking these capabilities helps "
            f"the MVP avoid overlooking important competitive "
            f"expectations while keeping the initial scope focused."
        )

        _add_feature(
            candidates=candidates,
            seen=seen,
            feature="Competitive Feature Benchmarking",
            priority="Could Have",
            reason=reason,
            customer_value="Medium",
            complexity="Medium",
            score=62,
            evidence_type="competitor",
        )

    # ---------------------------------------------------------------
    # 9. SWOT strengths
    # ---------------------------------------------------------------

    for index, strength in enumerate(
        swot_strengths[:3]
    ):

        phrase = _make_short_phrase(
            strength
        )

        feature_name = (
            f"Strength Enablement: {phrase}"
        )

        reason = (
            f"SWOT analysis identified the product strength "
            f"'{strength}'. The MVP should expose or support this "
            f"strength where it directly contributes to the core "
            f"value proposition."
        )

        _add_feature(
            candidates=candidates,
            seen=seen,
            feature=feature_name,
            priority="Should Have",
            reason=reason,
            customer_value="High",
            complexity=_estimate_complexity(
                feature_name,
                reason,
            ),
            score=73 - index * 2,
            evidence_type="swot_strength",
        )

    # ---------------------------------------------------------------
    # 10. SWOT weaknesses
    # ---------------------------------------------------------------

    for index, weakness in enumerate(
        swot_weaknesses[:3]
    ):

        phrase = _make_short_phrase(
            weakness
        )

        feature_name = (
            f"Weakness Reduction: {phrase}"
        )

        reason = (
            f"SWOT analysis identified the weakness "
            f"'{weakness}'. Addressing this weakness can reduce "
            f"an identified product limitation before broader rollout."
        )

        _add_feature(
            candidates=candidates,
            seen=seen,
            feature=feature_name,
            priority="Should Have",
            reason=reason,
            customer_value="Medium",
            complexity=_estimate_complexity(
                feature_name,
                reason,
            ),
            score=70 - index * 2,
            evidence_type="swot_weakness",
        )

    # ---------------------------------------------------------------
    # 11. SWOT opportunities
    # ---------------------------------------------------------------

    for index, opportunity in enumerate(
        swot_opportunities[:4]
    ):

        phrase = _make_short_phrase(
            opportunity
        )

        feature_name = (
            f"Opportunity Enablement: {phrase}"
        )

        reason = (
            f"SWOT analysis identified the opportunity "
            f"'{opportunity}'. A focused capability can help the "
            f"MVP test this opportunity without expanding the product "
            f"into unnecessary functionality."
        )

        _add_feature(
            candidates=candidates,
            seen=seen,
            feature=feature_name,
            priority="Should Have",
            reason=reason,
            customer_value="High",
            complexity=_estimate_complexity(
                feature_name,
                reason,
            ),
            score=72 - index * 2,
            evidence_type="swot_opportunity",
        )

    # ---------------------------------------------------------------
    # 12. SWOT threats
    # ---------------------------------------------------------------

    for index, threat in enumerate(
        swot_threats[:3]
    ):

        phrase = _make_short_phrase(
            threat
        )

        feature_name = (
            f"Threat Mitigation: {phrase}"
        )

        reason = (
            f"SWOT analysis identified the threat "
            f"'{threat}'. A targeted mitigation capability can "
            f"reduce exposure to the identified threat while keeping "
            f"the initial scope controlled."
        )

        _add_feature(
            candidates=candidates,
            seen=seen,
            feature=feature_name,
            priority="Should Have",
            reason=reason,
            customer_value="Medium",
            complexity=_estimate_complexity(
                feature_name,
                reason,
            ),
            score=68 - index * 2,
            evidence_type="swot_threat",
        )

    # ---------------------------------------------------------------
    # 13. Risk mitigation
    # ---------------------------------------------------------------

    for index, risk_data in enumerate(
        risks[:6]
    ):

        risk = _clean_text(
            risk_data.get("risk")
        )

        severity = _clean_text(
            risk_data.get("severity")
        )

        impact = _clean_text(
            risk_data.get("impact")
        )

        mitigation = _clean_text(
            risk_data.get("mitigation")
        )

        if not risk:
            continue

        risk_text = (
            f"{risk} {impact} {mitigation}"
        ).lower()

        # -----------------------------------------------------------
        # Detect security/privacy risks specifically.
        # -----------------------------------------------------------

        security_risk = _contains_any(
            risk_text,
            [
                "security",
                "unauthorized access",
                "access control",
                "authentication",
                "authorization",
                "privacy",
                "data breach",
                "cyber",
                "confidential",
                "personal information",
                "user information",
            ],
        )

        if security_risk:

            feature_name = (
                "Security and Access Control"
            )

            if mitigation:

                reason = (
                    f"Risk analysis identified the risk "
                    f"'{risk}' with "
                    f"{severity or 'unspecified'} severity. "
                    f"The stated mitigation is '{mitigation}'. "
                    f"Implementing security and access controls "
                    f"addresses the identified risk before wider use."
                )

            else:

                reason = (
                    f"Risk analysis identified the security/privacy "
                    f"risk '{risk}'. Security and access controls "
                    f"should be considered in the MVP to reduce "
                    f"exposure to this identified risk."
                )

            priority = (
                "Must Have"
                if severity.lower() in {
                    "high",
                    "critical",
                    "severe",
                }
                else "Should Have"
            )

            score = (
                94
                if priority == "Must Have"
                else 78
            )

            _add_feature(
                candidates=candidates,
                seen=seen,
                feature=feature_name,
                priority=priority,
                reason=reason,
                customer_value="High",
                complexity="Medium",
                score=score,
                evidence_type="high_risk",
            )

            continue

        # -----------------------------------------------------------
        # Generic risk mitigation
        # -----------------------------------------------------------

        phrase = _make_short_phrase(
            risk
        )

        feature_name = (
            f"Risk Mitigation: {phrase}"
        )

        if mitigation:

            reason = (
                f"Risk analysis identified the risk '{risk}' "
                f"with {severity or 'unspecified'} severity. "
                f"The analysis suggests '{mitigation}' as a mitigation. "
                f"Including an appropriate control in the product "
                f"reduces exposure to the identified risk."
            )

        else:

            reason = (
                f"Risk analysis identified the risk '{risk}' "
                f"with {severity or 'unspecified'} severity. "
                f"A focused mitigation capability should be considered "
                f"before broader product rollout."
            )

        high_risk = severity.lower() in {
            "high",
            "critical",
            "severe",
        }

        priority = (
            "Must Have"
            if high_risk
            else "Should Have"
        )

        score = (
            92 - index * 2
            if high_risk
            else 74 - index * 2
        )

        _add_feature(
            candidates=candidates,
            seen=seen,
            feature=feature_name,
            priority=priority,
            reason=reason,
            customer_value="High" if high_risk else "Medium",
            complexity=_estimate_complexity(
                feature_name,
                reason,
            ),
            score=score,
            evidence_type="high_risk" if high_risk else "risk",
        )

    # ---------------------------------------------------------------
    # 14. User feedback
    # ---------------------------------------------------------------

    _add_feature(
        candidates=candidates,
        seen=seen,
        feature="User Feedback Collection",
        priority="Should Have",
        reason=(
            "Early user feedback helps validate whether the MVP "
            "solves the intended problem and identifies improvements "
            "before wider launch."
        ),
        customer_value="High",
        complexity="Low",
        score=76,
        evidence_type="validation",
    )

    # ---------------------------------------------------------------
    # 15. Analytics
    # ---------------------------------------------------------------

    _add_feature(
        candidates=candidates,
        seen=seen,
        feature="Basic Usage Analytics",
        priority="Could Have",
        reason=(
            "Basic analytics can help measure user behavior and "
            "MVP adoption, but detailed analytics are not required "
            "for the first release."
        ),
        customer_value="Medium",
        complexity="Low",
        score=55,
        evidence_type="analytics",
    )

    # ---------------------------------------------------------------
    # 16. Notifications
    # ---------------------------------------------------------------

    _add_feature(
        candidates=candidates,
        seen=seen,
        feature="Notifications and Reminders",
        priority="Could Have",
        reason=(
            "Notifications may improve engagement after the core "
            "product experience has been validated."
        ),
        customer_value="Medium",
        complexity="Medium",
        score=52,
        evidence_type="engagement",
    )

    # ---------------------------------------------------------------
    # 17. Advanced AI personalization
    # ---------------------------------------------------------------

    _add_feature(
        candidates=candidates,
        seen=seen,
        feature="Advanced AI Personalization",
        priority="Future Features",
        reason=(
            "Advanced personalization can be introduced after "
            "sufficient user data and MVP validation have been "
            "collected."
        ),
        customer_value="Low",
        complexity="High",
        score=40,
        evidence_type="future",
    )

    # ---------------------------------------------------------------
    # 18. Third-party integrations
    # ---------------------------------------------------------------

    _add_feature(
        candidates=candidates,
        seen=seen,
        feature="Third-Party Integrations",
        priority="Future Features",
        reason=(
            "External integrations can expand the product ecosystem "
            "after the core MVP has been validated."
        ),
        customer_value="Low",
        complexity="High",
        score=35,
        evidence_type="future",
    )

    # ---------------------------------------------------------------
    # Sort by evidence score.
    # ---------------------------------------------------------------

    candidates.sort(
        key=lambda item: (
            _priority_rank(item["priority"]),
            -item["score"],
        )
    )

    return candidates


# =====================================================================
# Category balancing
# =====================================================================

def _build_recommendations(
    candidates: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, str]]]:
    """
    Build the final four MVP categories.

    Important:
        We preserve the priority assigned by the recommendation
        engine instead of blindly moving every feature based only
        on its score.
    """

    categories = {
        "must_have": [],
        "should_have": [],
        "could_have": [],
        "future_features": [],
    }

    mapping = {
        "Must Have": "must_have",
        "Should Have": "should_have",
        "Could Have": "could_have",
        "Future Features": "future_features",
    }

    for candidate in candidates:

        priority = candidate["priority"]

        category = mapping.get(priority)

        if not category:
            continue

        feature = _create_feature(
            feature=candidate["feature"],
            priority=priority,
            reason=candidate["reason"],
            customer_value=candidate["customer_value"],
            complexity=candidate["complexity"],
        )

        categories[category].append(
            feature
        )

    return categories


# =====================================================================
# Final validation
# =====================================================================

def _validate_recommendations(
    recommendations: Dict[str, List[Dict[str, str]]],
) -> MVPRecommendations:
    """
    Validate final output through Pydantic.

    This guarantees that the agent returns the same structure
    expected by the FastAPI layer and frontend.
    """

    mvp = MVPRecommendations(
        must_have=recommendations.get(
            "must_have",
            [],
        ),

        should_have=recommendations.get(
            "should_have",
            [],
        ),

        could_have=recommendations.get(
            "could_have",
            [],
        ),

        future_features=recommendations.get(
            "future_features",
            [],
        ),
    )

    return mvp


# =====================================================================
# Public agent function
# =====================================================================

async def run_mvp_recommendation_agent(
    idea: str,
    market_analysis: Optional[Any] = None,
    competitor_analysis: Optional[Any] = None,
    swot_analysis: Optional[Any] = None,
    risk_analysis: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Run the NEXUS MVP Recommendation Agent.

    Parameters
    ----------
    idea:
        Startup idea supplied by the user.

    market_analysis:
        Output from the Market Analysis / Customer Segmentation
        stage.

    competitor_analysis:
        Output from the Competitor Analysis stage.

    swot_analysis:
        Output from the SWOT Analysis stage.

    risk_analysis:
        Output from the Risk Analysis stage.

    Returns
    -------
    dict
        {
            "mvp_recommendations": {
                "must_have": [...],
                "should_have": [...],
                "could_have": [...],
                "future_features": [...]
            }
        }

    Raises
    ------
    ValueError
        If startup idea is empty or too short.
    """

    # ---------------------------------------------------------------
    # Validate startup idea
    # ---------------------------------------------------------------

    if idea is None:
        raise ValueError(
            "Startup idea cannot be empty"
        )

    cleaned_idea = _clean_text(idea)

    if not cleaned_idea:
        raise ValueError(
            "Startup idea cannot be empty"
        )

    if len(cleaned_idea) < 10:
        raise ValueError(
            "Startup idea is too short"
        )

    try:

        logger.info(
            "Running MVP Recommendation Agent"
        )

        logger.debug(
            "Startup idea: %s",
            cleaned_idea,
        )

        # -----------------------------------------------------------
        # Generate recommendations
        # -----------------------------------------------------------

        candidates = _generate_features(
            idea=cleaned_idea,
            market_analysis=market_analysis,
            competitor_analysis=competitor_analysis,
            swot_analysis=swot_analysis,
            risk_analysis=risk_analysis,
        )

        # -----------------------------------------------------------
        # Build four categories
        # -----------------------------------------------------------

        recommendations = _build_recommendations(
            candidates
        )

        # -----------------------------------------------------------
        # Validate using Pydantic
        # -----------------------------------------------------------

        validated = _validate_recommendations(
            recommendations
        )

        logger.info(
            "MVP recommendation completed: "
            "%d Must Have, %d Should Have, "
            "%d Could Have, %d Future Features",
            len(validated.must_have),
            len(validated.should_have),
            len(validated.could_have),
            len(validated.future_features),
        )

        # -----------------------------------------------------------
        # Return exact structure expected by orchestrator
        # -----------------------------------------------------------

        return {
            "mvp_recommendations": validated.model_dump()
            if hasattr(validated, "model_dump")
            else validated.dict()
        }

    except ValueError:
        raise

    except Exception as exc:

        logger.exception(
            "MVP Recommendation Agent failed: %s",
            exc,
        )

        # -----------------------------------------------------------
        # Safe fallback
        #
        # Even if an unexpected context shape is received from
        # another agent, NEXUS should still return a valid MVP.
        # -----------------------------------------------------------

        fallback = MVPRecommendations(
            must_have=[
                MVPFeature(
                    feature="Core Product Functionality",
                    priority="Must Have",
                    reason=(
                        "The MVP must provide the primary "
                        "functionality described in the startup "
                        "idea so that the core value proposition "
                        "can be validated."
                    ),
                    customer_value="High",
                    complexity="Medium",
                )
            ],

            should_have=[
                MVPFeature(
                    feature="User Feedback Collection",
                    priority="Should Have",
                    reason=(
                        "Early user feedback helps validate whether "
                        "the MVP solves the intended problem."
                    ),
                    customer_value="High",
                    complexity="Low",
                )
            ],

            could_have=[
                MVPFeature(
                    feature="Basic Usage Analytics",
                    priority="Could Have",
                    reason=(
                        "Basic analytics can help measure user "
                        "behavior and MVP adoption."
                    ),
                    customer_value="Medium",
                    complexity="Low",
                )
            ],

            future_features=[
                MVPFeature(
                    feature="Advanced AI Personalization",
                    priority="Future Features",
                    reason=(
                        "Advanced personalization can be introduced "
                        "after sufficient user data and MVP validation "
                        "have been collected."
                    ),
                    customer_value="Low",
                    complexity="High",
                )
            ],
        )

        return {
            "mvp_recommendations": (
                fallback.model_dump()
                if hasattr(fallback, "model_dump")
                else fallback.dict()
            )
        }