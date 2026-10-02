"""
NEXUS-ISB7 — Deep Validation Test Suite (Elevating Accuracy to 9+/10)
Covers:
- Technical Feasibility Matrix
- Scientific Validation Index (PubMed & clinical literature)
- Regulatory Risk & Compliance Pathway (FDA SaMD)
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
    """Verify TechnicalFeasibility, ScientificValidation, RegulatoryRisk, and ValidationResponse models."""
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
    """Verify that AcoustiGut bio-acoustic ideas receive specialized deep validation metrics."""
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

    # Technical Feasibility assertions
    assert "feasibility_rating" in tech
    assert tech["score"] < 8.0  # AcoustiGut is technically challenging due to acoustic SNR constraints
    assert any("signal" in b.lower() or "acoustic" in b.lower() or "snr" in b.lower() or "noise" in b.lower() for b in tech["key_barriers"])
    assert any("100" in s or "hz" in s.lower() or "vocal" in s.lower() or "mems" in s.lower() for s in tech["signal_constraints"])
    assert len(tech["recommended_tech_stack"]) >= 2

    # Scientific Validation assertions
    assert sci["evidence_level"] == "Emerging Hypothesis"  # Linking mic sounds directly to microbiome is an emerging hypothesis
    assert any("phonoentero" in f.lower() or "bowel" in f.lower() or "motility" in f.lower() or "pubmed" in f.lower() for f in sci["key_findings"])
    assert len(sci["risk_flags"]) >= 1
    assert len(sci["required_trials"]) >= 1

    # Regulatory Risk assertions
    assert reg["risk_level"] in ("High", "Critical", "Medium")
    assert "samd" in reg["fda_classification"].lower() or "class ii" in reg["fda_classification"].lower()
    assert any("510(k)" in c or "hipaa" in c.lower() or "iso" in c.lower() for c in reg["compliance_requirements"])
    assert "wellness" in reg["recommended_pathway"].lower() or "clearance" in reg["recommended_pathway"].lower()


@pytest.mark.asyncio
async def test_run_market_analysis_agent_returns_deep_validation():
    """Verify run_market_analysis_agent populates deep validation modules in its returned dictionary."""
    idea = "AcoustiGut: Smartphone microphone acoustic sensing for gut sound analysis"
    result = await run_market_analysis_agent(idea=idea, search_results=[])

    assert isinstance(result, dict)
    assert "market_analysis" in result
    assert "technical_feasibility" in result
    assert "scientific_validation" in result
    assert "regulatory_risk" in result

    # Verify Pydantic model validation of deep fields
    tech = TechnicalFeasibility(**result["technical_feasibility"])
    sci = ScientificValidation(**result["scientific_validation"])
    reg = RegulatoryRisk(**result["regulatory_risk"])

    assert 1.0 <= tech.score <= 10.0
    assert 1.0 <= sci.score <= 10.0
    assert reg.risk_level in ("Low", "Medium", "High", "Critical")


@pytest.mark.asyncio
async def test_orchestrator_end_to_end_deep_validation():
    """Verify run_orchestrator integrates all 3 deep validation modules into the final ValidationResponse."""
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

    with patch("server.agents.orchestrator.run_web_search_agent", new_callable=AsyncMock) as mock_web_search:
        mock_web_search.return_value = mock_search

        idea = "Acoustic gut sound sensing app for non-invasive digestion health monitoring"
        result = await run_orchestrator(idea)

        assert isinstance(result, dict)
        assert result["idea"] == idea
        assert "market_analysis" in result
        assert "competitor_analysis" in result
        assert "technical_feasibility" in result
        assert "scientific_validation" in result
        assert "regulatory_risk" in result

        # Validate against strict ValidationResponse
        validated = ValidationResponse(**result)
        assert validated.technical_feasibility is not None
        assert validated.technical_feasibility.score > 0
        assert validated.scientific_validation is not None
        assert validated.scientific_validation.score > 0
        assert validated.regulatory_risk is not None
        assert validated.regulatory_risk.fda_classification != ""
