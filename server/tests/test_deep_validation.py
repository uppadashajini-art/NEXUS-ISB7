"""
NEXUS-ISB7 — Deep Validation Test Suite (Elevating Accuracy to 9+/10)
Covers:
- Technical Feasibility Matrix
- Scientific Validation Index (PubMed & clinical literature)
- Regulatory Risk & Compliance Pathway (FDA SaMD)
- Adversarial Kill-Switch & 14-Day Falsification Test
- Unit Economics & Compute Margin Viability Matrix (Deterministic Margin Computation)
- Search query decomposition with deep-tech validation vectors
- Bio-acoustic & AcoustiGut evaluation heuristics
- End-to-end Orchestrator integration and schema conformance
"""

import pytest
from unittest.mock import AsyncMock, patch

from server.models.validation import (
    TechnicalFeasibility,
    ScientificValidation,
    RegulatoryRisk,
    KillSwitch,
    UnitEconomics,
    EvidenceItem,
    RegulatoryRunway,
    TRLReadiness,
    TRLBottleneck,
    MoatVector,
    MoatDurability,
    compute_moat_score,
    PivotPlan,
    evaluate_pivot_triggers,
    detect_regulatory_requirements,
    ensure_regulatory_compliance_for_idea,
    derive_trl_stage,
    filter_grounded_evidence,
    compute_unit_economics_margin,
    ValidationResponse,
    MarketAnalysis,
    CompetitorAnalysis,
)
from server.agents.web_search_agent import (
    decompose_startup_idea,
    generate_search_queries,
)
from server.agents.market_analysis_agent import (
    _generate_heuristic_deep_validation,
    _validate_and_sanitize_gemini_output,
    run_market_analysis_agent,
)
from server.agents.orchestrator import run_orchestrator


def test_deep_validation_pydantic_models():
    """Verify TechnicalFeasibility, ScientificValidation, RegulatoryRisk, KillSwitch, and UnitEconomics models."""
    tech = TechnicalFeasibility(
        score=6.5,
        feasibility_rating="Medium",
        key_barriers=["SNR degradation from ambient room noise"],
        signal_constraints=["Acoustic attenuation in 100-1500 Hz range"],
        recommended_tech_stack=["Discrete Wavelet Transform", "ONNX Runtime"],
    )
    assert tech.score == 6.5
    assert tech.feasibility_rating == "Medium"
    assert len(tech.key_barriers) == 1
    assert len(tech.signal_constraints) == 1
    assert len(tech.recommended_tech_stack) == 2

    # Verify synchronization of key_findings and clinical_findings
    sci = ScientificValidation(
        score=5.0,
        evidence_level="Emerging Hypothesis",
        key_findings=["PubMed study correlates acoustic bowel intervals with peristaltic motility."],
        risk_flags=["Lack of gold-standard clinical database"],
        required_trials=["Prospective multi-center benchmarking against digital stethoscopes"],
    )
    assert sci.score == 5.0
    assert sci.evidence_level == "Emerging Hypothesis"
    assert len(sci.clinical_findings) == 1
    assert sci.clinical_findings[0] == sci.key_findings[0]

    # Verify initialization with clinical_findings synchronizes to key_findings
    sci2 = ScientificValidation(
        score=7.0,
        evidence_level="Clinical Fact",
        clinical_findings=["Direct clinical observation confirmed in randomized trial."],
    )
    assert len(sci2.key_findings) == 1
    assert sci2.key_findings[0] == "Direct clinical observation confirmed in randomized trial."

    reg = RegulatoryRisk(
        risk_level="High",
        fda_classification="SaMD Class II",
        compliance_requirements=["FDA 510(k)", "HIPAA AES-256", "ISO 13485"],
        recommended_pathway="Dual-track: initial wellness disclaimer followed by 510(k) clearance.",
    )
    assert reg.risk_level == "High"
    assert reg.fda_classification == "SaMD Class II"
    assert len(reg.compliance_requirements) == 3

    # Test KillSwitch model
    kill = KillSwitch(
        fatal_assumption="Assumes smartphone microphone can capture acoustic frequencies through abdominal tissue.",
        cheap_test="Record 20 acoustic audio samples on 10 subjects and calculate SNR.",
        test_budget_usd=150,
        kill_threshold="< 10 dB SNR ratio in > 30% of tests",
        confidence="high",
        evidence=[EvidenceItem(claim="PubMed acoustical study", source_url="https://pubmed.ncbi.nlm.nih.gov/123")],
    )
    assert kill.test_budget_usd == 150
    assert kill.confidence == "high"
    assert "10" in kill.kill_threshold
    assert len(kill.evidence) == 1
    assert kill.evidence[0].source_url == "https://pubmed.ncbi.nlm.nih.gov/123"

    # Test KillSwitch numeric validator fallback
    kill_nonumeric = KillSwitch(
        fatal_assumption="Core user retention assumption",
        cheap_test="Landing page interview test",
        test_budget_usd=100,
        kill_threshold="Low customer demand",
        confidence="medium",
    )
    assert any(c.isdigit() for c in kill_nonumeric.kill_threshold)

    # Test UnitEconomics model with deterministic margin calculation
    ue = UnitEconomics(
        cost_to_serve_per_user_usd=6.0,
        suggested_price_usd=30.0,
        assumptions=["Inference: $3.00/mo", "Storage: $3.00/mo"],
        platform_dependency_risk="medium: Dependent on external APIs",
        confidence="medium",
        evidence=[EvidenceItem(claim="Market pricing benchmark", source_url="https://example.com/pricing")],
    )
    assert ue.gross_margin_pct == 80.0
    assert ue.margin_grade == "healthy"

    # Test Thin and Margin Trap grades
    ue_thin = UnitEconomics(
        cost_to_serve_per_user_usd=60.0,
        suggested_price_usd=100.0,
        platform_dependency_risk="high: High BOM cost",
    )
    assert ue_thin.gross_margin_pct == 40.0
    assert ue_thin.margin_grade == "thin"

    ue_trap = UnitEconomics(
        cost_to_serve_per_user_usd=90.0,
        suggested_price_usd=100.0,
        platform_dependency_risk="critical: Inference costs eat all revenue",
    )
    assert ue_trap.gross_margin_pct == 10.0
    assert ue_trap.margin_grade == "margin_trap"


def test_deterministic_margin_helper():
    """Verify compute_unit_economics_margin boundary conditions."""
    m_pct, grade = compute_unit_economics_margin(cost_to_serve=20.0, suggested_price=100.0)
    assert m_pct == 80.0
    assert grade == "healthy"

    m_pct, grade = compute_unit_economics_margin(cost_to_serve=50.0, suggested_price=100.0)
    assert m_pct == 50.0
    assert grade == "thin"

    m_pct, grade = compute_unit_economics_margin(cost_to_serve=75.0, suggested_price=100.0)
    assert m_pct == 25.0
    assert grade == "margin_trap"

    # Edge cases: zero or negative price
    m_pct, grade = compute_unit_economics_margin(cost_to_serve=10.0, suggested_price=0.0)
    assert m_pct == 0.0
    assert grade == "margin_trap"


def test_search_query_generation_deep_vectors():
    """Verify generate_search_queries produces scientific, technical feasibility, and regulatory queries when validation_type='all'."""
    decomposed = {
        "domain": "digital health",
        "solution": "acoustic gut sound sensor",
        "problem": "gut microbiome disorder detection",
        "audience": "gastroenterology patients",
    }

    queries = generate_search_queries(decomposed, validation_type="all")
    queries_str = " ".join(queries).lower()

    # Scientific Validation query check
    assert "scientific validation" in queries_str or "clinical literature" in queries_str or "pubmed" in queries_str
    # Technical Feasibility query check
    assert "technical feasibility" in queries_str or "signal processing" in queries_str or "sensor" in queries_str
    # Regulatory Risk query check
    assert "fda" in queries_str or "samd" in queries_str or "medical device" in queries_str


def test_acoustigut_deep_validation_heuristics():
    """Verify that AcoustiGut bio-acoustic ideas receive specialized deep validation metrics including KillSwitch and UnitEconomics."""
    idea = "AcoustiGut: Smartphone microphone acoustic sensing for gut microbiome sound analysis and IBS detection"
    search_results = [
        {
            "title": "PubMed Study: Phonoenterography and Bowel Sound Acoustic Analysis",
            "url": "https://pubmed.ncbi.nlm.nih.gov/123456",
            "content": "Clinical trial demonstrates that acoustic frequency features between 100 Hz and 1500 Hz correlate with intestinal motility.",
        },
        {
            "title": "FDA Guidance: Software as a Medical Device (SaMD) Classification",
            "url": "https://fda.gov/samd",
            "content": "SaMD diagnostic screening tools for gastrointestinal disease typically require 510(k) premarket clearance.",
        },
        {
            "title": "Acoustic Signal Processing for Biomedical Sensors",
            "url": "https://ieee.org/acoustics",
            "content": "Signal to noise ratio is severely degraded by ambient background noise and clothing friction.",
        }
    ]

    deep_eval = _generate_heuristic_deep_validation(idea=idea, search_results=search_results, industry="HealthTech & Digital Health")

    tech = deep_eval["technical_feasibility"]
    sci = deep_eval["scientific_validation"]
    reg = deep_eval["regulatory_risk"]
    kill = deep_eval["kill_switch"]
    ue = deep_eval["unit_economics"]

    # Technical Feasibility assertions
    assert "feasibility_rating" in tech
    assert tech["score"] < 8.0  # AcoustiGut is technically challenging due to acoustic SNR constraints
    assert any("signal" in b.lower() or "acoustic" in b.lower() or "snr" in b.lower() or "noise" in b.lower() for b in tech["key_barriers"])
    assert any("100" in s or "hz" in s.lower() or "vocal" in s.lower() or "mems" in s.lower() for s in tech["signal_constraints"])
    assert len(tech["recommended_tech_stack"]) >= 2

    # Scientific Validation assertions
    assert sci["evidence_level"] == "Emerging Hypothesis"
    assert any("phonoentero" in f.lower() or "bowel" in f.lower() or "motility" in f.lower() or "pubmed" in f.lower() for f in sci["key_findings"])
    assert len(sci["risk_flags"]) >= 1
    assert len(sci["required_trials"]) >= 1

    # Regulatory Risk assertions
    assert reg["risk_level"] in ("High", "Critical", "Medium")
    assert "samd" in reg["fda_classification"].lower() or "class ii" in reg["fda_classification"].lower()
    assert any("510(k)" in c or "hipaa" in c.lower() or "iso" in c.lower() for c in reg["compliance_requirements"])

    # Kill-Switch assertions
    assert "fatal_assumption" in kill
    assert "cheap_test" in kill
    assert kill["test_budget_usd"] > 0
    assert any(c.isdigit() for c in kill["kill_threshold"])
    assert kill["confidence"] in ("low", "medium", "high")
    assert kill["evidence"] == []
    assert kill["source_type"] == "heuristic_fallback"

    # Unit Economics assertions
    assert ue["cost_to_serve_per_user_usd"] > 0
    assert ue["suggested_price_usd"] > ue["cost_to_serve_per_user_usd"]
    assert ue["gross_margin_pct"] >= 70.0  # acoustic software SaaS has strong gross margin
    assert ue["margin_grade"] == "healthy"
    assert "platform_dependency_risk" in ue


def test_derive_trl_stage():
    """Verify deterministic mapping of 1-9 TRL levels to standard TRL stages."""
    # Lab hypothesis (1-3)
    assert derive_trl_stage(1) == "lab_hypothesis"
    assert derive_trl_stage(2) == "lab_hypothesis"
    assert derive_trl_stage(3) == "lab_hypothesis"

    # Component prototype (4-6)
    assert derive_trl_stage(4) == "component_prototype"
    assert derive_trl_stage(5) == "component_prototype"
    assert derive_trl_stage(6) == "component_prototype"

    # Deployment ready (7-9)
    assert derive_trl_stage(7) == "deployment_ready"
    assert derive_trl_stage(8) == "deployment_ready"
    assert derive_trl_stage(9) == "deployment_ready"

    # Boundary and out-of-range clamping
    assert derive_trl_stage(0) == "lab_hypothesis"
    assert derive_trl_stage(12) == "deployment_ready"


def test_filter_grounded_evidence():
    """Verify evidence URLs not found in Tavily search results are dropped, and confidence defaults to low if none remain."""
    search_results = [
        {"url": "https://pubmed.ncbi.nlm.nih.gov/12345", "title": "Bowel sounds clinical study"},
        {"url": "https://fda.gov/guidance/samd-clinical-evaluation", "title": "FDA SaMD Guidance"},
    ]

    raw_evidence = [
        {"claim": "Clinical bowel motility correlation", "source_url": "https://pubmed.ncbi.nlm.nih.gov/12345/"},
        {"claim": "Invented citation", "source_url": "https://fake-citation-news.org/article-999"},
        {"claim": "Another ungrounded claim", "source_url": "https://unverified-blog.io/post"},
    ]

    clean_ev, conf = filter_grounded_evidence(raw_evidence, search_results, "high")
    assert len(clean_ev) == 1
    assert clean_ev[0]["claim"] == "Clinical bowel motility correlation"
    assert clean_ev[0]["source_url"] == "https://pubmed.ncbi.nlm.nih.gov/12345/"
    assert conf == "high"

    # If all items are ungrounded, drop all and force confidence="low"
    ungrounded = [
        {"claim": "Invented claim", "source_url": "https://fake.org/1"},
    ]
    empty_ev, low_conf = filter_grounded_evidence(ungrounded, search_results, "high")
    assert len(empty_ev) == 0
    assert low_conf == "low"


def test_source_type_and_confidence_fallback_rule():
    """Verify that source_type='heuristic_fallback' forces confidence='low' across all models."""
    # KillSwitch
    ks = KillSwitch(
        fatal_assumption="Assumes users switch from spreadsheet",
        cheap_test="Run ads to waitlist",
        test_budget_usd=150,
        kill_threshold="< 3% conversion",
        confidence="high",  # Attempting high confidence with heuristic fallback
        source_type="heuristic_fallback",
    )
    assert ks.source_type == "heuristic_fallback"
    assert ks.confidence == "low"  # Model validator forces low

    # UnitEconomics
    ue = UnitEconomics(
        cost_to_serve_per_user_usd=5.0,
        suggested_price_usd=25.0,
        platform_dependency_risk="low",
        confidence="medium",
        source_type="heuristic_fallback",
    )
    assert ue.source_type == "heuristic_fallback"
    assert ue.confidence == "low"

    # RegulatoryRunway
    rr = RegulatoryRunway(
        applicable_regimes=["FDA Class II 510(k)"],
        time_to_clearance_months_min=12,
        time_to_clearance_months_max=24,
        pre_revenue_burn_usd_min=100000,
        pre_revenue_burn_usd_max=250000,
        runway_penalty_summary="adds 12-24 months and $100k-$250k",
        confidence="high",
        source_type="heuristic_fallback",
    )
    assert rr.source_type == "heuristic_fallback"
    assert rr.confidence == "low"

    # TRLReadiness
    trl = TRLReadiness(
        trl_level=5,
        single_point_of_failure="Sensor drift under temperature shifts",
        confidence="medium",
        source_type="heuristic_fallback",
    )
    assert trl.source_type == "heuristic_fallback"
    assert trl.confidence == "low"
    assert trl.trl_stage == "component_prototype"


def test_pure_software_zero_regulatory_runway():
    """Verify that pure software ideas with no regulated domain have applicable_regimes=['none'] and zero runway values."""
    rr = RegulatoryRunway(
        applicable_regimes=["none"],
        time_to_clearance_months_min=0,
        time_to_clearance_months_max=0,
        pre_revenue_burn_usd_min=0,
        pre_revenue_burn_usd_max=0,
        runway_penalty_summary="",
        non_regulated_bridge="",
    )
    assert rr.applicable_regimes == ["none"]
    assert rr.time_to_clearance_months_min == 0
    assert rr.time_to_clearance_months_max == 0
    assert rr.pre_revenue_burn_usd_min == 0
    assert rr.pre_revenue_burn_usd_max == 0
    assert rr.non_regulated_bridge == ""


def test_legaltech_non_archetype_idea_specific_fallback():
    """
    Test the fallback with a non-archetype idea (legal-tech contract review app)
    and verify outputs are idea-specific and NOT generic.
    """
    legal_idea = "Automated AI legal-tech contract review and redlining tool for corporate NDAs and commercial enterprise agreements"
    deep_eval = _generate_heuristic_deep_validation(idea=legal_idea, industry="Legal Technology & LegalTech", search_results=[])

    kill = deep_eval["kill_switch"]
    ue = deep_eval["unit_economics"]
    rr = deep_eval["regulatory_runway"]
    trl = deep_eval["trl_readiness"]

    # Verify idea-specific content
    assert any(w in kill["fatal_assumption"].lower() for w in ["contract", "legal", "redlin", "attorney", "liability"])
    assert any(w in kill["cheap_test"].lower() for w in ["contract", "attorney", "redlin", "clause"])
    assert kill["source_type"] == "heuristic_fallback"
    assert kill["confidence"] == "low"

    # Verify unit economics is tailored to legal documents
    assert any(w in " ".join(ue["assumptions"]).lower() for w in ["legal", "contract", "doc", "soc 2", "token"])
    assert ue["source_type"] == "heuristic_fallback"
    assert ue["confidence"] == "low"

    # Verify regulatory runway mentions legal ethics / ABA / bar
    assert any(w in " ".join(rr["applicable_regimes"]).lower() for w in ["aba", "legal", "law", "privilege", "gdpr", "soc 2"])
    assert any(w in " ".join(rr["required_hires"]).lower() for w in ["legal", "ethics", "bar", "compliance"])
    assert len(rr["non_regulated_bridge"]) > 0
    assert "paralegal" in rr["non_regulated_bridge"].lower() or "contract" in rr["non_regulated_bridge"].lower()
    assert rr["source_type"] == "heuristic_fallback"
    assert rr["confidence"] == "low"

    # Verify TRL is derived and bottlenecks are legal-tech specific
    assert trl["trl_level"] == 6
    assert trl["trl_stage"] == "component_prototype"
    assert any("legal" in b["name"].lower() or "precedent" in b["name"].lower() or "contract" in b["name"].lower() for b in trl["bottlenecks"])
    assert "liability" in trl["single_point_of_failure"].lower() or "malpractice" in trl["single_point_of_failure"].lower()
    assert trl["source_type"] == "heuristic_fallback"
    assert trl["confidence"] == "low"


@pytest.mark.asyncio
async def test_run_market_analysis_agent_returns_deep_validation():
    """Verify run_market_analysis_agent populates all deep validation modules including Moat Durability and Pivot Plan."""
    idea = "AcoustiGut: Smartphone microphone acoustic sensing for gut sound analysis"
    result = await run_market_analysis_agent(idea=idea, search_results=[])

    assert isinstance(result, dict)
    assert "market_analysis" in result
    assert "technical_feasibility" in result
    assert "scientific_validation" in result
    assert "regulatory_risk" in result
    assert "kill_switch" in result
    assert "unit_economics" in result
    assert "regulatory_runway" in result
    assert "trl_readiness" in result
    assert "moat_durability" in result
    assert "pivot_plan" in result

    # Verify Pydantic model validation of deep fields
    tech = TechnicalFeasibility(**result["technical_feasibility"])
    sci = ScientificValidation(**result["scientific_validation"])
    reg = RegulatoryRisk(**result["regulatory_risk"])
    kill = KillSwitch(**result["kill_switch"])
    ue = UnitEconomics(**result["unit_economics"])
    rr = RegulatoryRunway(**result["regulatory_runway"])
    trl = TRLReadiness(**result["trl_readiness"])
    moat = MoatDurability(**result["moat_durability"])
    pivot = PivotPlan(**result["pivot_plan"])

    assert 1.0 <= tech.score <= 10.0
    assert 1.0 <= sci.score <= 10.0
    assert reg.risk_level in ("Low", "Medium", "High", "Critical")
    assert len(kill.fatal_assumption) > 0
    assert any(c.isdigit() for c in kill.kill_threshold)
    assert ue.gross_margin_pct > 0
    assert len(rr.applicable_regimes) > 0
    assert 1 <= trl.trl_level <= 9
    assert trl.trl_stage in ("lab_hypothesis", "component_prototype", "deployment_ready")
    assert 0.0 <= moat.moat_score <= 100.0
    assert moat.moat_tier in ("fragile", "defensible", "durable")
    assert moat.replication_window_months_min <= moat.replication_window_months_max
    assert isinstance(pivot.triggered, bool)


@pytest.mark.asyncio
async def test_orchestrator_end_to_end_deep_validation():
    """Verify run_orchestrator integrates all deep validation modules into the final ValidationResponse."""
    mock_search = {
        "results": [
            {
                "title": "Acoustic Bio-signal Analysis",
                "url": "https://example.com/bio-signal",
                "target_audience": "Gastroenterologists",
                "content": "Digital stethoscopes and mobile acoustic processing algorithms for patient monitoring.",
            }
        ]
    }

    # Mock external sub-agents to execute deterministic fast integration test
    with patch("server.agents.orchestrator.run_web_search_agent", new_callable=AsyncMock) as mock_web_search, \
         patch("server.agents.orchestrator._dispatch_competitor_analysis", new_callable=AsyncMock) as mock_comp, \
         patch("server.agents.orchestrator.run_swot_risk_agent", new_callable=AsyncMock) as mock_swot, \
         patch("server.agents.orchestrator.run_mvp_recommendation_agent", new_callable=AsyncMock) as mock_mvp:

        mock_web_search.return_value = mock_search
        mock_comp.return_value = {
            "direct_competitors": [],
            "indirect_competitors": [],
            "comparison": [],
            "market_gaps": [],
        }
        mock_swot.return_value = {
            "strengths": ["Strong domain opportunity"],
            "weaknesses": ["Early-stage verification required"],
            "opportunities": ["Rapid market expansion"],
            "threats": ["Incumbent alternatives"],
            "risks": [],
        }
        mock_mvp.return_value = {
            "mvp_features": ["Core detection telemetry"],
            "timeline_weeks": 8,
            "estimated_cost_usd": 15000,
        }

        idea = "Acoustic gut sound sensing app for non-invasive digestion health monitoring"
        result = await run_orchestrator(idea)

        assert isinstance(result, dict)
        assert result["idea"] == idea
        assert "market_analysis" in result
        assert "competitor_analysis" in result
        assert "technical_feasibility" in result
        assert "scientific_validation" in result
        assert "regulatory_risk" in result
        assert "kill_switch" in result
        assert "unit_economics" in result
        assert "regulatory_runway" in result
        assert "trl_readiness" in result
        assert "moat_durability" in result
        assert "pivot_plan" in result

        # Validate against strict ValidationResponse with automatic sub-model parsing
        validated = ValidationResponse(**result)
        assert validated.technical_feasibility is not None
        assert validated.technical_feasibility.score > 0
        assert validated.scientific_validation is not None
        assert validated.scientific_validation.score > 0
        assert validated.regulatory_risk is not None
        assert validated.regulatory_risk.fda_classification != ""
        assert validated.kill_switch is not None
        assert len(validated.kill_switch.fatal_assumption) > 0
        assert validated.unit_economics is not None
        assert validated.unit_economics.gross_margin_pct > 0
        assert validated.regulatory_runway is not None
        assert validated.trl_readiness.trl_stage == derive_trl_stage(validated.trl_readiness.trl_level)
        assert validated.trl_readiness.trl_stage in ("lab_hypothesis", "component_prototype", "deployment_ready")
        assert validated.moat_durability is not None
        assert validated.moat_durability.moat_score >= 0.0
        assert validated.moat_durability.moat_tier in ("fragile", "defensible", "durable")
        assert validated.pivot_plan is not None
        assert isinstance(validated.pivot_plan.triggered, bool)


# =====================================================================
# NEW MODULE TESTS: MOAT DURABILITY & PIVOT PLAN + FIXES
# =====================================================================

def test_moat_score_and_tier_derivation():
    """
    Verify:
    1. Weighted average calculation: data 35%, lock-in 35%, regulatory/IP 30% in Python.
    2. Tier boundaries:
       - < 35: fragile
       - 35 - 65: defensible
       - > 65: durable
    3. Pydantic validator computes moat_score and moat_tier (overriding any LLM spoofing).
    4. Replication window is a range (min and max).
    5. source_type='heuristic_fallback' forces confidence='low'.
    """
    # Test raw compute helper
    score_fragile, tier_fragile = compute_moat_score(data_score=20.0, lockin_score=30.0, reg_score=25.0)
    # 20*0.35 + 30*0.35 + 25*0.30 = 7.0 + 10.5 + 7.5 = 25.0
    assert score_fragile == 25.0
    assert tier_fragile == "fragile"

    score_defensible, tier_defensible = compute_moat_score(data_score=50.0, lockin_score=60.0, reg_score=40.0)
    # 50*0.35 + 60*0.35 + 40*0.30 = 17.5 + 21.0 + 12.0 = 50.5
    assert score_defensible == 50.5
    assert tier_defensible == "defensible"

    score_durable, tier_durable = compute_moat_score(data_score=80.0, lockin_score=85.0, reg_score=70.0)
    # 80*0.35 + 85*0.35 + 70*0.30 = 28.0 + 29.75 + 21.0 = 78.8
    assert score_durable == 78.8
    assert tier_durable == "durable"

    # Exact boundary tests:
    # 34.9 is fragile, 35.0 is defensible
    # 65.0 is defensible, 65.1 is durable
    s_b1, t_b1 = compute_moat_score(34.0, 34.0, 34.0)
    assert t_b1 == "fragile"
    s_b2, t_b2 = compute_moat_score(35.0, 35.0, 35.0)
    assert t_b2 == "defensible"
    s_b3, t_b3 = compute_moat_score(65.0, 65.0, 65.0)
    assert t_b3 == "defensible"
    s_b4, t_b4 = compute_moat_score(66.0, 66.0, 66.0)
    assert t_b4 == "durable"

    # Test Pydantic model overrides LLM-spoofed values
    moat = MoatDurability(
        data_network_effect={"score": 20, "reason": "Sparse user data"},
        workflow_lockin={"score": 25, "reason": "No deep integrations"},
        regulatory_ip_moat={"score": 20, "reason": "Unprotected open source"},
        replication_window_months_min=3,
        replication_window_months_max=6,
        likely_replicator="OpenAI or Google",
        moat_score=99.0,  # Spoofed by hypothetical bad LLM
        moat_tier="durable",  # Spoofed
        confidence="high",
        source_type="heuristic_fallback",
    )
    # Must be recomputed to 21.8 and fragile
    assert moat.moat_score == 21.8
    assert moat.moat_tier == "fragile"
    # Fallback must force confidence="low"
    assert moat.confidence == "low"
    assert moat.replication_window_months_min == 3
    assert moat.replication_window_months_max == 6


def test_pivot_trigger_conditions():
    """
    Verify each of the 4 pivot trigger conditions individually and in combination:
    - trl_level <= 3
    - regulatory time_to_clearance_months_max >= 12
    - margin_grade == "margin_trap"
    - moat_tier == "fragile"
    And verify untriggered state returns triggered=False and empty reasons.
    """
    # Baseline non-triggering values:
    # trl_level=7, reg_max=6, margin_grade="healthy", moat_tier="durable"
    base_trl = 7
    base_reg_max = 6
    base_margin = "healthy"
    base_moat = "durable"

    # 1. Test trl_level <= 3
    trig_trl, reasons_trl = evaluate_pivot_triggers(
        trl_level=3,
        regulatory_clearance_months_max=base_reg_max,
        margin_grade=base_margin,
        moat_tier=base_moat,
    )
    assert trig_trl is True
    assert any("TRL Level 3 <= 3" in r for r in reasons_trl)

    # 2. Test regulatory clearance >= 12
    trig_reg, reasons_reg = evaluate_pivot_triggers(
        trl_level=base_trl,
        regulatory_clearance_months_max=18,
        margin_grade=base_margin,
        moat_tier=base_moat,
    )
    assert trig_reg is True
    assert any("18 months" in r for r in reasons_reg)

    # 3. Test margin_grade == "margin_trap"
    trig_margin, reasons_margin = evaluate_pivot_triggers(
        trl_level=base_trl,
        regulatory_clearance_months_max=base_reg_max,
        margin_grade="margin_trap",
        moat_tier=base_moat,
    )
    assert trig_margin is True
    assert any("margin_trap" in r for r in reasons_margin)

    # 4. Test moat_tier == "fragile"
    trig_moat, reasons_moat = evaluate_pivot_triggers(
        trl_level=base_trl,
        regulatory_clearance_months_max=base_reg_max,
        margin_grade=base_margin,
        moat_tier="fragile",
    )
    assert trig_moat is True
    assert any("fragile" in r for r in reasons_moat)

    # 5. Multi-trigger condition: TRL 2 and fragile moat
    trig_multi, reasons_multi = evaluate_pivot_triggers(
        trl_level=2,
        regulatory_clearance_months_max=base_reg_max,
        margin_grade=base_margin,
        moat_tier="fragile",
    )
    assert trig_multi is True
    assert len(reasons_multi) == 2

    # 6. Untriggered condition: All healthy/defensible
    trig_none, reasons_none = evaluate_pivot_triggers(
        trl_level=7,
        regulatory_clearance_months_max=6,
        margin_grade="healthy",
        moat_tier="defensible",
    )
    assert trig_none is False
    assert len(reasons_none) == 0

    # 7. PivotPlan model validation with triggered=False
    plan_off = PivotPlan(triggered=False)
    assert plan_off.triggered is False
    assert plan_off.months_saved == 0

    # 8. PivotPlan model validation with triggered=True
    plan_on = PivotPlan(
        triggered=True,
        trigger_reasons=["Moat defensibility is fragile (<35 score)"],
        pivot_name="B2B Embedded Workflow SDK",
        what_changes="Cut consumer app, offer developer API",
        months_saved=8,
        new_regulatory_exposure="Standard B2B SaaS agreements",
        first_test="Interview 10 developers in 14 days",
        confidence="medium",
        source_type="heuristic_fallback",
    )
    assert plan_on.triggered is True
    assert plan_on.months_saved == 8
    # Heuristic fallback forces confidence="low"
    assert plan_on.confidence == "low"


def test_evidence_relevance_keyword_filter():
    """
    Verify:
    1. filter_grounded_evidence drops items where claim shares < 2 meaningful keywords with Tavily title/content.
    2. Items with matching URL AND >= 2 shared meaningful keywords are kept.
    3. If none pass, returns empty evidence list and forces confidence='low'.
    """
    search_results = [
        {
            "url": "https://pubmed.ncbi.nlm.nih.gov/987654",
            "title": "Acoustic Phonoenterography and Bowel Sound Signal Processing",
            "content": "Acoustic analysis shows intestinal motility frequency peaks between 100 Hz and 1500 Hz.",
        },
        {
            "url": "https://example.com/fintech-reg",
            "title": "RBI Guidelines for Digital Lending and Non-Banking Financial Companies",
            "content": "Digital lending platforms must ensure direct disbursement into borrower accounts without synthetic pools.",
        }
    ]

    raw_evidence = [
        # Case A: Matches URL and shares >= 2 keywords ("acoustic", "bowel", "motility", "phonoenterography") -> KEEP
        {
            "claim": "Acoustic bowel sound analysis indicates intestinal motility frequency",
            "source_url": "https://pubmed.ncbi.nlm.nih.gov/987654",
        },
        # Case B: Matches URL, but only shares 1 keyword ("digital") -> DROP
        {
            "claim": "Digital blockchain crypto coin mining hardware",
            "source_url": "https://example.com/fintech-reg",
        },
        # Case C: Matches URL, but shares 0 meaningful keywords -> DROP
        {
            "claim": "Space exploration rocket engine thrust optimization",
            "source_url": "https://pubmed.ncbi.nlm.nih.gov/987654",
        },
        # Case D: Shares keywords with RBI article ("lending", "borrower", "disbursement") -> KEEP
        {
            "claim": "Direct lending disbursement to borrower account",
            "source_url": "https://example.com/fintech-reg",
        },
        # Case E: Completely fake ungrounded URL -> DROP
        {
            "claim": "Hallucinated citation",
            "source_url": "https://completely-fake-url.org/article",
        }
    ]

    filtered_ev, conf = filter_grounded_evidence(raw_evidence, search_results, original_confidence="high")
    assert len(filtered_ev) == 2
    assert filtered_ev[0]["claim"] == "Acoustic bowel sound analysis indicates intestinal motility frequency"
    assert filtered_ev[1]["claim"] == "Direct lending disbursement to borrower account"
    assert conf == "high"

    # If all items fail keyword check, all are dropped and confidence is forced to 'low'
    failing_evidence = [
        {
            "claim": "Random unrelated text with zero overlap",
            "source_url": "https://pubmed.ncbi.nlm.nih.gov/987654",
        }
    ]
    empty_ev, low_conf = filter_grounded_evidence(failing_evidence, search_results, original_confidence="high")
    assert len(empty_ev) == 0
    assert low_conf == "low"


def test_pure_software_regulatory_no_blanket_none():
    """
    Verify:
    1. 'none' is ONLY allowed if the idea has:
       - no payments/lending/investing
       - no health data
       - no minors' data
       - no personal data processing
    2. If payments/lending/investing present -> requires RBI/SEBI/PCI-DSS/Fintech regimes.
    3. If health data present -> requires HIPAA/FDA/health regimes.
    4. If minors' data present -> requires COPPA/FERPA.
    5. If personal data present -> requires GDPR/DPDP Act/SOC 2.
    6. ensure_regulatory_compliance_for_idea sanitizes ['none'] when regulated features exist.
    """
    # 1. Truly non-regulated software: pure offline developer tool
    offline_idea = "Offline command-line code formatter and linter for Rust projects with zero network access and local disk storage"
    req_offline = detect_regulatory_requirements(offline_idea)
    assert req_offline["is_regulated"] is False
    assert req_offline["applicable_regimes"] == ["none"]

    # 2. Software with payments
    payment_idea = "Micro-SaaS invoice generator with Stripe checkout payment processing and credit card billing"
    req_payment = detect_regulatory_requirements(payment_idea)
    assert req_payment["is_regulated"] is True
    assert "none" not in req_payment["applicable_regimes"]
    assert any("pci-dss" in r.lower() or "payment" in r.lower() for r in req_payment["applicable_regimes"])

    # 3. Software with minors' data
    minors_idea = "Gamified elementary school math practice app for children aged 6 to 10"
    req_minors = detect_regulatory_requirements(minors_idea)
    assert req_minors["is_regulated"] is True
    assert any("coppa" in r.lower() or "ferpa" in r.lower() for r in req_minors["applicable_regimes"])

    # 4. Software with personal data processing (e.g. CRM storing customer email/phone)
    crm_idea = "B2B sales CRM platform storing enterprise customer contact info and employee profiles"
    req_crm = detect_regulatory_requirements(crm_idea)
    assert req_crm["is_regulated"] is True
    assert any("gdpr" in r.lower() or "dpdp" in r.lower() or "soc 2" in r.lower() for r in req_crm["applicable_regimes"])

    # 5. Test sanitizer function: ensure_regulatory_compliance_for_idea
    # If LLM erroneously returns applicable_regimes=['none'] for a lending app, sanitizer fixes it:
    lending_idea = "P2P micro-lending platform for merchants"
    spoofed_rr = {
        "applicable_regimes": ["none"],
        "time_to_clearance_months_min": 0,
        "time_to_clearance_months_max": 0,
        "pre_revenue_burn_usd_min": 0,
        "pre_revenue_burn_usd_max": 0,
    }
    sanitized_rr = ensure_regulatory_compliance_for_idea(lending_idea, spoofed_rr)
    assert "none" not in sanitized_rr["applicable_regimes"]
    assert any("rbi" in r.lower() or "nbfc" in r.lower() or "pci" in r.lower() or "lending" in r.lower() for r in sanitized_rr["applicable_regimes"])
    assert sanitized_rr["time_to_clearance_months_max"] > 0
    assert sanitized_rr["pre_revenue_burn_usd_max"] > 0


def test_generic_fallback_fintech_lending_idea():
    """
    Test generic fallback with a fintech lending idea.
    Verifies idea-specific outputs across all modules without hardcoded archetypes:
    - kill_switch
    - unit_economics
    - regulatory_runway (disallowing 'none')
    - moat_durability
    - pivot_plan
    - source_type='heuristic_fallback' and confidence='low'
    """
    fintech_idea = "P2P micro-lending app offering 30-day working capital loans to street vendors based on UPI QR code cashflow analysis"
    deep_eval = _generate_heuristic_deep_validation(idea=fintech_idea, industry="FinTech & Lending", search_results=[])

    kill = deep_eval["kill_switch"]
    ue = deep_eval["unit_economics"]
    rr = deep_eval["regulatory_runway"]
    moat = deep_eval["moat_durability"]
    pivot = deep_eval["pivot_plan"]

    # Kill-Switch: idea-specific
    assert any(w in kill["fatal_assumption"].lower() for w in ["lending", "loan", "underwrit", "default", "merchant", "vendor", "upi"])
    assert any(c.isdigit() for c in kill["kill_threshold"])
    assert kill["source_type"] == "heuristic_fallback"
    assert kill["confidence"] == "low"

    # Unit Economics
    assert ue["cost_to_serve_per_user_usd"] > 0
    assert ue["suggested_price_usd"] > 0
    assert ue["gross_margin_pct"] > 0
    assert ue["source_type"] == "heuristic_fallback"
    assert ue["confidence"] == "low"

    # Regulatory Runway: must NOT be 'none'
    assert "none" not in [r.lower() for r in rr["applicable_regimes"]]
    assert any(w in " ".join(rr["applicable_regimes"]).lower() for w in ["rbi", "nbfc", "lending", "kyc", "pci", "dpdp"])
    assert rr["time_to_clearance_months_max"] > 0
    assert rr["source_type"] == "heuristic_fallback"
    assert rr["confidence"] == "low"

    # Moat Durability: computed in Python
    assert "data_network_effect" in moat
    assert "workflow_lockin" in moat
    assert "regulatory_ip_moat" in moat
    assert 0.0 <= moat["moat_score"] <= 100.0
    assert moat["moat_tier"] in ("fragile", "defensible", "durable")
    assert moat["replication_window_months_min"] < moat["replication_window_months_max"]
    assert len(moat["likely_replicator"]) > 0
    assert moat["source_type"] == "heuristic_fallback"
    assert moat["confidence"] == "low"

    # Pivot Plan
    assert isinstance(pivot["triggered"], bool)
    if pivot["triggered"]:
        assert len(pivot["trigger_reasons"]) > 0
        assert len(pivot["pivot_name"]) > 0
        assert pivot["months_saved"] > 0


def test_generic_fallback_edtech_idea():
    """
    Test generic fallback with an edtech idea.
    Verifies idea-specific outputs across all modules without hardcoded archetypes:
    - regulatory_runway requires COPPA/FERPA/student privacy
    - kill_switch relates to student/parent engagement or learning outcomes
    - moat durability and pivot plan
    """
    edtech_idea = "AI adaptive algebra learning tutor for middle school students with real-time step-by-step math hints and parent dashboards"
    deep_eval = _generate_heuristic_deep_validation(idea=edtech_idea, industry="EdTech & K-12", search_results=[])

    kill = deep_eval["kill_switch"]
    rr = deep_eval["regulatory_runway"]
    moat = deep_eval["moat_durability"]
    pivot = deep_eval["pivot_plan"]

    # Kill-Switch: educational retention / mastery
    assert any(w in kill["fatal_assumption"].lower() for w in ["student", "math", "learn", "tutor", "parent", "school", "curriculum"])
    assert kill["source_type"] == "heuristic_fallback"
    assert kill["confidence"] == "low"

    # Regulatory Runway: must require COPPA/FERPA for minors' software
    assert "none" not in [r.lower() for r in rr["applicable_regimes"]]
    assert any(w in " ".join(rr["applicable_regimes"]).lower() for w in ["coppa", "ferpa", "student", "minor", "privacy"])
    assert rr["time_to_clearance_months_max"] > 0
    assert rr["source_type"] == "heuristic_fallback"
    assert rr["confidence"] == "low"

    # Moat Durability
    assert 0.0 <= moat["moat_score"] <= 100.0
    assert moat["moat_tier"] in ("fragile", "defensible", "durable")
    assert moat["source_type"] == "heuristic_fallback"
    assert moat["confidence"] == "low"

    # Pivot Plan
    assert isinstance(pivot["triggered"], bool)


