"""
Comprehensive Regression Test Suite for GTM Strategy Agent
Validates 15 distinct startup ideas across diverse business archetypes:
1. B2C Creative: Dream-to-Game Studio AI
2. B2B Enterprise SaaS: Enterprise Cloud Compliance & Audit Automation
3. B2B Product-Led Growth (PLG): Collaborative Developer Code Review Tool
4. Two-Sided Marketplace: Heavy Construction Equipment Peer-to-Peer Rental
5. DeepTech / Hardware: Compact Fusion Reactor Diagnostic Sensors
6. Local Services: On-Demand Emergency Commercial HVAC Dispatch
7. Creator Economy: AI Voice Cloning & Licensing for Voice Actors
8. API / Developer Infrastructure: High-Throughput Vector Embedding Gateway
9. Fintech: Cross-Border SME Invoice Factoring Platform
10. Healthcare: Remote Pediatric Asthma Tele-monitoring Sensor
11. D2C E-commerce: 3D-Printed Biodegradable Ergonomic Footwear
12. Novel Idea 1: Agritech AI Autonomous Drone Soil Nutrient Scanner
13. Novel Idea 2: EdTech Peer-to-Peer Math Olympiad Competitive Arena
14. Novel Idea 3: LegalTech AI Automated Contract Redlining & Risk Scorer
15. Novel Idea 4: CyberSecurity Zero-Trust Cloud Privilege Access Broker
"""

import pytest
import re
from typing import Dict, Any

from server.agents.gtm_agent import (
    run_gtm_agent,
    classify_business_archetype,
    derive_customer_segments,
    validate_gtm_consistency,
    ARCHETYPES,
    PUBLISHER_NAME_BLACKLIST,
    B2C_FORBIDDEN_TERMS,
    INVALID_SEGMENT_TERMS
)


# ============================================================================
# 1. B2C CREATIVE REGRESSION TEST (Dream-to-Game Studio AI)
# ============================================================================

@pytest.mark.asyncio
async def test_regression_b2c_dream_to_game(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    idea = (
        "An AI platform that transforms users' dreams into personalized playable mini-games, "
        "allowing casual gamers and dreamers to play, edit, and share interactive dreamscapes."
    )
    validation_context = {
        "idea": idea,
        "market_analysis": {
            "industry": "Gaming, Entertainment & Creative AI",
            "customer_segments": [
                {"segment": "Casual Gamers and Creative Dreamers", "needs": ["Fast game generation", "No coding needed"]},
                {"segment": "Social Media Streamers & Viewers", "needs": ["Viral interactive content", "Community sharing"]}
            ]
        },
        "competitor_analysis": {
            "direct_competitors": [
                {"name": "Roblox Studio", "product": "User-generated game engine", "pricing": "Free with Robux split"},
                {"name": "Forbes", "product": "Media publication", "pricing": None}  # Blacklisted publisher
            ]
        }
    }

    result = await run_gtm_agent(validation_context=validation_context)
    assert "gtm_strategy" in result
    gtm = result["gtm_strategy"]

    # 1. Archetype consistency: primary must be B2C or Creator Economy (never Marketplace or Enterprise)
    arch = gtm["business_archetype"]
    assert arch["primary"] in ["B2C Consumer / Mobile", "Creator Economy / Creative Platform"]
    assert arch["primary"] != "Two-Sided Marketplace / Network"
    assert arch["primary"] != "B2B Enterprise / High-ACV SaaS"
    assert "Hybrid" not in arch["primary"]  # Hybrid is represented by secondary list

    # 2. Customer segments must be people or groups, NOT capabilities
    segments = gtm["customer_segments"]
    assert len(segments) >= 2
    for s in segments:
        sname = s["segment"].lower()
        for inv in INVALID_SEGMENT_TERMS:
            assert inv not in sname, f"Segment contains invalid feature name: {inv}"
        assert "why_they_care" in s
        assert "core_problem" in s
        assert "buying_behavior" in s

    # 3. No B2C forbidden terms (no C-suite outbound, no $149+ tier, no provider recruitment)
    gtm_json_str = str(gtm).lower()
    for term in ["c-suite outbound", "icp decision-makers", "booking liquidity", "$149+ enterprise tier"]:
        assert term not in gtm_json_str, f"Found forbidden term '{term}' in B2C GTM strategy"

    # 4. Competitor validation: Forbes must be rejected
    comps = gtm["competitors"]
    comp_names = [c["name"].lower() for c in comps]
    assert "forbes" not in comp_names
    assert any("roblox" in c for c in comp_names) or len(comps) >= 1

    # 5. Pricing evidence is structured
    pe = gtm["pricing_evidence"]
    assert len(pe) >= 1
    assert "pricing_status" in pe[0]

    # 6. Measurable Roadmap contains numeric metrics
    roadmap = gtm["launch_roadmap"]
    assert len(roadmap["phases"]) == 4
    all_actions = " ".join([" ".join(p["key_actions"]) for p in roadmap["phases"]])
    assert re.search(r"\d+", all_actions), "Roadmap must contain numeric targets"

    # 7. Startup-specific risks
    risks = gtm["risks"]
    assert len(risks) >= 2
    for r in risks:
        assert "risk" in r and len(r["risk"]) > 5
        assert "cheap_test" in r and len(r["cheap_test"]) > 10
        assert "success_metric" in r

    # 8. Unit economics & Viability
    assert "unit_economics" in gtm
    assert "viability" in gtm
    assert "components" in gtm["viability"]
    assert gtm["viability"]["overall"] == "Hypothesis Stage"  # Capped in fallback mode

    # 9. GTM Validation status
    assert gtm["gtm_validation"]["status"] in ["PASS", "PASS_WITH_WARNINGS"]
    assert gtm["generation_mode"] in ["llm", "deterministic_fallback"]


# ============================================================================
# 2. B2B ENTERPRISE SAAS REGRESSION TEST
# ============================================================================

@pytest.mark.asyncio
async def test_regression_b2b_enterprise_saas(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    idea = "Continuous enterprise compliance automation and audit verification platform for Fortune 500 financial institutions."
    result = await run_gtm_agent(idea=idea)
    gtm = result["gtm_strategy"]

    arch = gtm["business_archetype"]
    assert arch["primary"] == "B2B Enterprise / High-ACV SaaS"
    assert "annual" in gtm["pricing_strategy"].lower() or "acv" in gtm["pricing_strategy"].lower() or "12,000" in gtm["pricing_strategy"]
    assert "unit_economics" in gtm


# ============================================================================
# 3. B2B PRODUCT-LED GROWTH (PLG) REGRESSION TEST
# ============================================================================

@pytest.mark.asyncio
async def test_regression_b2b_plg_saas(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    idea = "Collaborative developer workspace and automated pull-request code reviewer with seamless GitHub integration."
    result = await run_gtm_agent(idea=idea)
    gtm = result["gtm_strategy"]

    arch = gtm["business_archetype"]
    assert arch["primary"] in ["B2B Product-Led Growth", "API / Developer Infrastructure"]
    assert any("seat" in str(gtm["pricing_strategy"]).lower() or "free developer" in str(gtm["pricing_strategy"]).lower() for _ in [1])


# ============================================================================
# 4. TWO-SIDED MARKETPLACE REGRESSION TEST
# ============================================================================

@pytest.mark.asyncio
async def test_regression_two_sided_marketplace(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    idea = "Two-sided peer-to-peer heavy construction equipment and bulldozer rental marketplace."
    result = await run_gtm_agent(idea=idea)
    gtm = result["gtm_strategy"]

    arch = gtm["business_archetype"]
    assert arch["primary"] == "Two-Sided Marketplace / Network"
    # Marketplace should have take-rate or booking fee
    assert "take-rate" in gtm["pricing_strategy"].lower() or "commission" in gtm["pricing_strategy"].lower() or "take rate" in gtm["pricing_strategy"].lower()


# ============================================================================
# 5. DEEPTECH / HARDWARE REGRESSION TEST
# ============================================================================

@pytest.mark.asyncio
async def test_regression_deeptech_hardware(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    idea = "Compact sensor hardware and magnetic diagnostic arrays for experimental commercial nuclear fusion reactors."
    result = await run_gtm_agent(idea=idea)
    gtm = result["gtm_strategy"]

    arch = gtm["business_archetype"]
    assert arch["primary"] == "DeepTech / Hardware / Regulated Infrastructure"


# ============================================================================
# 6. LOCAL SERVICES REGRESSION TEST
# ============================================================================

@pytest.mark.asyncio
async def test_regression_local_services(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    idea = "On-demand emergency commercial HVAC repair dispatch and certified technician network."
    result = await run_gtm_agent(idea=idea)
    gtm = result["gtm_strategy"]

    arch = gtm["business_archetype"]
    assert arch["primary"] == "Local Services / SMB"


# ============================================================================
# 7. CREATOR ECONOMY REGRESSION TEST
# ============================================================================

@pytest.mark.asyncio
async def test_regression_creator_economy(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    idea = "AI voice cloning and royalty monetization platform for professional voice actors and creative animators."
    result = await run_gtm_agent(idea=idea)
    gtm = result["gtm_strategy"]

    arch = gtm["business_archetype"]
    assert arch["primary"] in ["Creator Economy / Creative Platform", "B2C Consumer / Mobile"]


# ============================================================================
# 8. API / DEVELOPER INFRASTRUCTURE REGRESSION TEST
# ============================================================================

@pytest.mark.asyncio
async def test_regression_api_dev_infra(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    idea = "Ultra-low-latency vector embedding API and distributed index gateway for production LLM search applications."
    result = await run_gtm_agent(idea=idea)
    gtm = result["gtm_strategy"]

    arch = gtm["business_archetype"]
    assert arch["primary"] in ["API / Developer Infrastructure", "B2B Product-Led Growth"]


# ============================================================================
# 9. FINTECH REGRESSION TEST
# ============================================================================

@pytest.mark.asyncio
async def test_regression_fintech(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    idea = "Cross-border B2B invoice factoring and instant working capital financing platform for import-export SMEs."
    result = await run_gtm_agent(idea=idea)
    gtm = result["gtm_strategy"]

    arch = gtm["business_archetype"]
    assert arch["primary"] == "Fintech"


# ============================================================================
# 10. HEALTHCARE REGRESSION TEST
# ============================================================================

@pytest.mark.asyncio
async def test_regression_healthcare(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    idea = "Remote pediatric asthma tele-monitoring smart inhaler sensor and clinical dashboard with automated triage."
    result = await run_gtm_agent(idea=idea)
    gtm = result["gtm_strategy"]

    arch = gtm["business_archetype"]
    assert arch["primary"] == "Healthcare"
    assert "pmpm" in gtm["pricing_strategy"].lower() or "clinic" in gtm["pricing_strategy"].lower()


# ============================================================================
# 11. D2C E-COMMERCE REGRESSION TEST
# ============================================================================

@pytest.mark.asyncio
async def test_regression_d2c_ecommerce(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    idea = "Direct-to-consumer 3D-printed custom ergonomic footwear crafted from 100% biodegradable ocean polymers."
    result = await run_gtm_agent(idea=idea)
    gtm = result["gtm_strategy"]

    arch = gtm["business_archetype"]
    assert arch["primary"] == "D2C E-commerce"


# ============================================================================
# 12-15. DYNAMIC NOVEL IDEAS (UNSEEN AT TEST TIME)
# ============================================================================

@pytest.mark.asyncio
async def test_regression_novel_agritech_drone(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    idea = "Autonomous hyperspectral drone scanner for agricultural soil nutrient mapping and precision fertilizer micro-dosing."
    result = await run_gtm_agent(idea=idea)
    gtm = result["gtm_strategy"]

    assert gtm["business_archetype"]["primary"] in ARCHETYPES
    assert len(gtm["customer_segments"]) >= 1
    assert gtm["gtm_validation"]["status"] in ["PASS", "PASS_WITH_WARNINGS"]


@pytest.mark.asyncio
async def test_regression_novel_edtech_math(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    idea = "Peer-to-peer competitive math olympiad arena with live 1v1 matchmaking and student micro-scholarships."
    result = await run_gtm_agent(idea=idea)
    gtm = result["gtm_strategy"]

    assert gtm["business_archetype"]["primary"] in ARCHETYPES
    assert gtm["gtm_validation"]["status"] in ["PASS", "PASS_WITH_WARNINGS"]


@pytest.mark.asyncio
async def test_regression_novel_legaltech_redlining(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    idea = "AI automated commercial contract redlining and liability clause risk-scoring engine for corporate legal counsels."
    result = await run_gtm_agent(idea=idea)
    gtm = result["gtm_strategy"]

    assert gtm["business_archetype"]["primary"] in ["B2B Enterprise / High-ACV SaaS", "B2B Product-Led Growth"]
    assert gtm["gtm_validation"]["status"] in ["PASS", "PASS_WITH_WARNINGS"]


@pytest.mark.asyncio
async def test_regression_novel_cybersecurity_privilege(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    idea = "Just-in-time zero-trust cloud privilege access broker with automated ephemeral credential revocation."
    result = await run_gtm_agent(idea=idea)
    gtm = result["gtm_strategy"]

    assert gtm["business_archetype"]["primary"] in ["B2B Enterprise / High-ACV SaaS", "API / Developer Infrastructure", "B2B Product-Led Growth"]
    assert gtm["gtm_validation"]["status"] in ["PASS", "PASS_WITH_WARNINGS"]
