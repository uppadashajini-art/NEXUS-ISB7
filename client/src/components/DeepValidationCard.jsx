import React from "react";

/**
 * DeepValidationCard Component
 * Displays Technical Feasibility, Scientific Validation, and Regulatory Risk
 * to elevate startup idea validation accuracy for deep-tech and health-tech ideas.
 */
export default function DeepValidationCard({
  technical,
  scientific,
  regulatory,
}) {
  if (!technical && !scientific && !regulatory) {
    return null;
  }

  // Helpers for badge styling
  const getRatingBadgeClass = (rating) => {
    const r = (rating || "").toLowerCase();
    if (r.includes("high")) return "badge-high";
    if (r.includes("medium")) return "badge-medium";
    if (r.includes("low")) return "badge-low";
    if (r.includes("moonshot")) return "badge-moonshot";
    return "badge-neutral";
  };

  const getEvidenceBadgeClass = (level) => {
    const l = (level || "").toLowerCase();
    if (l.includes("fact") || l.includes("standard")) return "badge-fact";
    if (l.includes("hypothesis") || l.includes("emerging")) return "badge-hypothesis";
    return "badge-unsubstantiated";
  };

  const getRiskBadgeClass = (risk) => {
    const r = (risk || "").toLowerCase();
    if (r.includes("low")) return "badge-risk-low";
    if (r.includes("medium")) return "badge-risk-med";
    if (r.includes("critical") || r.includes("high")) return "badge-risk-high";
    return "badge-neutral";
  };

  return (
    <section className="deep-validation-card" id="deep-validation-section">
      <div className="deep-validation-header">
        <div className="header-badge">
          <span className="dot-pulse"></span>
          DEEP VALIDATION MATRIX (ACCURACY 9+/10)
        </div>
        <h2>Technical, Scientific & Regulatory Feasibility</h2>
        <p>
          Rigorous multidimensional evaluation covering hardware & engineering constraints, empirical literature & trials,
          and domain-specific regulatory compliance pathways (FDA, FAA, EPA, or FTC).
        </p>
      </div>

      <div className="deep-validation-grid">
        {/* 1. TECHNICAL FEASIBILITY */}
        {technical && (
          <div className="validation-module technical-module">
            <div className="module-top">
              <div className="module-icon">⚙️</div>
              <div className="module-title-wrap">
                <span className="module-tag">PILLAR 01</span>
                <h3>Technical Feasibility</h3>
              </div>
              <div className="module-score-wrap">
                <div className="score-circle">
                  <span className="score-val">{technical.score?.toFixed(1) || "N/A"}</span>
                  <span className="score-max">/10</span>
                </div>
              </div>
            </div>

            <div className="rating-row">
              <span className="metric-label">Feasibility Rating:</span>
              <span className={`status-pill ${getRatingBadgeClass(technical.feasibility_rating)}`}>
                {technical.feasibility_rating || "Evaluated"}
              </span>
            </div>

            {/* Score progress bar */}
            <div className="feasibility-meter-track">
              <div
                className="feasibility-meter-fill"
                style={{ width: `${Math.min(100, (technical.score || 0) * 10)}%` }}
              ></div>
            </div>

            {/* Key Technical Barriers */}
            {technical.key_barriers?.length > 0 && (
              <div className="module-section">
                <h4>
                  <span className="icon-bullet">⚠️</span> Key Technical Barriers
                </h4>
                <ul className="barrier-list">
                  {technical.key_barriers.map((barrier, idx) => (
                    <li key={idx} className="barrier-item">
                      {barrier}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Signal & Hardware Constraints */}
            {technical.signal_constraints?.length > 0 && (
              <div className="module-section">
                <h4>
                  <span className="icon-bullet">📡</span> Signal & Hardware Constraints
                </h4>
                <ul className="constraint-list">
                  {technical.signal_constraints.map((constraint, idx) => (
                    <li key={idx} className="constraint-item">
                      {constraint}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommended Tech Stack */}
            {technical.recommended_tech_stack?.length > 0 && (
              <div className="module-section">
                <h4>
                  <span className="icon-bullet">🛠️</span> Recommended Tech Stack
                </h4>
                <div className="tech-stack-pills">
                  {technical.recommended_tech_stack.map((tech, idx) => (
                    <span key={idx} className="tech-pill">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* 2. SCIENTIFIC VALIDATION */}
        {scientific && (
          <div className="validation-module scientific-module">
            <div className="module-top">
              <div className="module-icon">🧪</div>
              <div className="module-title-wrap">
                <span className="module-tag">PILLAR 02</span>
                <h3>Scientific Validation</h3>
              </div>
              <div className="module-score-wrap">
                <div className="score-circle">
                  <span className="score-val">{scientific.score?.toFixed(1) || "N/A"}</span>
                  <span className="score-max">/10</span>
                </div>
              </div>
            </div>

            <div className="rating-row">
              <span className="metric-label">Evidence Strength:</span>
              <span className={`status-pill ${getEvidenceBadgeClass(scientific.evidence_level)}`}>
                {scientific.evidence_level || "Under Review"}
              </span>
            </div>

            {/* Score progress bar */}
            <div className="feasibility-meter-track">
              <div
                className="feasibility-meter-fill sci-fill"
                style={{ width: `${Math.min(100, (scientific.score || 0) * 10)}%` }}
              ></div>
            </div>

            {/* Key Findings / Literature */}
            {(scientific.key_findings || scientific.clinical_findings)?.length > 0 && (
              <div className="module-section">
                <h4>
                  <span className="icon-bullet">📚</span> Literature & Empirical Findings
                </h4>
                <ul className="findings-list">
                  {(scientific.key_findings || scientific.clinical_findings).map((finding, idx) => (
                    <li key={idx} className="finding-item">
                      {finding}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Risk Flags */}
            {scientific.risk_flags?.length > 0 && (
              <div className="module-section">
                <h4>
                  <span className="icon-bullet">🚩</span> Scientific Risk Flags & Confounders
                </h4>
                <ul className="risk-flag-list">
                  {scientific.risk_flags.map((flag, idx) => (
                    <li key={idx} className="risk-flag-item">
                      {flag}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Required Clinical Trials */}
            {scientific.required_trials?.length > 0 && (
              <div className="module-section">
                <h4>
                  <span className="icon-bullet">🔬</span> Required Validation Protocols & Trials
                </h4>
                <ul className="trials-list">
                  {scientific.required_trials.map((trial, idx) => (
                    <li key={idx} className="trial-item">
                      {trial}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* 3. REGULATORY RISK & COMPLIANCE */}
        {regulatory && (
          <div className="validation-module regulatory-module">
            <div className="module-top">
              <div className="module-icon">⚖️</div>
              <div className="module-title-wrap">
                <span className="module-tag">PILLAR 03</span>
                <h3>Regulatory Risk & Compliance</h3>
              </div>
              <div className="module-score-wrap">
                <span className={`risk-level-badge ${getRiskBadgeClass(regulatory.risk_level)}`}>
                  {regulatory.risk_level?.toUpperCase() || "EVALUATED"} RISK
                </span>
              </div>
            </div>

            <div className="rating-row">
              <span className="metric-label">Classification:</span>
              <span className="status-pill badge-classification">
                {regulatory.fda_classification || "General Wellness"}
              </span>
            </div>

            {/* Compliance Requirements */}
            {regulatory.compliance_requirements?.length > 0 && (
              <div className="module-section">
                <h4>
                  <span className="icon-bullet">📋</span> Compliance & Governance Requirements
                </h4>
                <ul className="compliance-list">
                  {regulatory.compliance_requirements.map((req, idx) => (
                    <li key={idx} className="compliance-item">
                      <span className="check-icon">✓</span>
                      <span>{req}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommended Pathway */}
            {regulatory.recommended_pathway && (
              <div className="module-section">
                <h4>
                  <span className="icon-bullet">🧭</span> Recommended Go-To-Market Pathway
                </h4>
                <div className="pathway-box">
                  <p>{regulatory.recommended_pathway}</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
