import React, { useState } from "react";

/**
 * DeepValidationCard Component
 * Displays:
 * 1. Adversarial Kill-Switch & 14-Day Falsification Test
 * 2. Technical Feasibility Matrix
 * 3. Scientific Validation Index
 * 4. Regulatory Risk & Compliance
 * 5. Unit Economics & Margin Viability Matrix
 * 6. Regulatory Runway & Clearance Timeline
 * 7. NASA/DoD TRL Readiness & Bottlenecks
 */
export default function DeepValidationCard({
  technical,
  scientific,
  regulatory,
  killSwitch,
  unitEconomics,
  regulatoryRunway,
  trlReadiness,
  moatDurability,
  pivotPlan,
  consistencyWarnings = [],
  is_cached = false,
  isCached = false,
  from_cache = false,
}) {
  const cachedFlag = is_cached || isCached || from_cache;
  const [showKillEvidence, setShowKillEvidence] = useState(false);
  const [showUeEvidence, setShowUeEvidence] = useState(false);
  const [showAssumptions, setShowAssumptions] = useState(false);
  const [showRegEvidence, setShowRegEvidence] = useState(false);
  const [showTrlEvidence, setShowTrlEvidence] = useState(false);
  const [showMoatEvidence, setShowMoatEvidence] = useState(false);
  const [expandedMoatVector, setExpandedMoatVector] = useState(null);

  if (
    !technical &&
    !scientific &&
    !regulatory &&
    !killSwitch &&
    !unitEconomics &&
    !regulatoryRunway &&
    !trlReadiness &&
    !moatDurability &&
    !pivotPlan
  ) {
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
    if (l.includes("fact") || l.includes("standard") || l.includes("validated")) return "badge-fact";
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

  const getConfidenceBadgeClass = (conf) => {
    const c = (conf || "").toLowerCase();
    if (c === "high") return "badge-conf-high";
    if (c === "medium") return "badge-conf-med";
    return "badge-conf-low";
  };

  const getMoatTierBadgeClass = (tier) => {
    const t = (tier || "").toLowerCase();
    if (t === "durable") return "badge-moat-durable";
    if (t === "defensible") return "badge-moat-defensible";
    return "badge-moat-fragile";
  };

  const getMarginGradeClass = (grade) => {
    const g = (grade || "").toLowerCase();
    if (g === "healthy" || g.includes("70")) return "badge-margin-healthy";
    if (g === "thin" || g.includes("30")) return "badge-margin-thin";
    return "badge-margin-trap";
  };

  const formatMarginPct = (pct) => {
    if (pct === undefined || pct === null) return "N/A";
    return `${Number(pct).toFixed(1)}%`;
  };

  const currencySymbol = unitEconomics?.currency_symbol || "$";
  const unitLabel = unitEconomics?.unit_label || "user";
  const formatCurrency = (val) => {
    if (val === undefined || val === null) return `${currencySymbol}0.00`;
    return `${currencySymbol}${Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };
  const formatUSD = formatCurrency;

  const renderSourceTypeTag = (sourceType) => {
    if (sourceType === "heuristic_fallback") {
      return (
        <span
          className="source-fallback-tag"
          style={{
            display: "inline-flex",
            alignItems: "center",
            padding: "2px 8px",
            borderRadius: "4px",
            fontSize: "11px",
            fontWeight: 600,
            background: "rgba(245, 158, 11, 0.15)",
            color: "#F59E0B",
            border: "1px solid rgba(245, 158, 11, 0.3)",
            marginRight: "6px"
          }}
          title="Derived via deterministic structural taxonomy / labeled heuristic fallback"
        >
          [Heuristic Fallback]
        </span>
      );
    }
    return null;
  };

  const getBottleneckTypeIcon = (type) => {
    const t = (type || "").toLowerCase();
    if (t === "hardware") return "⚙️";
    if (t === "data") return "📊";
    if (t === "compute") return "💻";
    if (t === "talent") return "👤";
    if (t === "regulatory") return "📜";
    return "⚠️";
  };

  const SOFTWARE_STEPS = [
    { level: 1, label: "Stage 1", short: "Concept Research", desc: "Technical architecture spec & requirements formulation" },
    { level: 2, label: "Stage 2", short: "Tech Spec", desc: "Data schemas & core logic formulated" },
    { level: 3, label: "Stage 3", short: "Arch Spike / PoC", desc: "Proof of concept & algorithm validation in sandbox" },
    { level: 4, label: "Stage 4", short: "Alpha Prototype", desc: "Core engine alpha & mock API endpoints functional" },
    { level: 5, label: "Stage 5", short: "Integration Sandbox", desc: "Integration sandbox & end-to-end user journeys tested" },
    { level: 6, label: "Stage 6", short: "Beta Customer Trial", desc: "Closed customer beta / field pilot in staging env" },
    { level: 7, label: "Stage 7", short: "Production MVP", desc: "Validated MVP in live production with initial users" },
    { level: 8, label: "Stage 8", short: "Commercial Scale", desc: "Hardened system handling real-world traffic & billing" },
    { level: 9, label: "Stage 9", short: "Enterprise SLA", desc: "Battle-tested multi-tenant enterprise infrastructure" },
  ];

  const TRL_STEPS = [
    { level: 1, label: "TRL 1", short: "Basic Principles", desc: "Scientific discovery begins translation to R&D" },
    { level: 2, label: "TRL 2", short: "Concept Formulated", desc: "Practical application identified & formulated" },
    { level: 3, label: "TRL 3", short: "Proof of Concept", desc: "Active R&D initiates lab validation" },
    { level: 4, label: "TRL 4", short: "Lab Validation", desc: "Basic prototype components integrated in lab" },
    { level: 5, label: "TRL 5", short: "Relevant Env", desc: "Fidelity of component tech tested in relevant env" },
    { level: 6, label: "TRL 6", short: "System Prototype", desc: "Representative prototype demonstrated in relevant env" },
    { level: 7, label: "TRL 7", short: "Operational Demo", desc: "Prototype demonstrated in live operational environment" },
    { level: 8, label: "TRL 8", short: "System Qualified", desc: "Actual system completed and qualified through test" },
    { level: 9, label: "TRL 9", short: "Mission Proven", desc: "Actual system proven through successful commercial ops" },
  ];

  const getReadinessStageInfo = (level, stage, isHardware = false) => {
    const lvl = Number(level) || 1;
    if (isHardware) {
      if (lvl <= 3 || stage === "lab_hypothesis") {
        return { label: "Lab Hypothesis", tagClass: "badge-stage-lab", range: "TRL 1–3" };
      }
      if (lvl <= 6 || stage === "component_prototype") {
        return { label: "Component Prototype", tagClass: "badge-stage-proto", range: "TRL 4–6" };
      }
      return { label: "Deployment Ready", tagClass: "badge-stage-deploy", range: "TRL 7–9" };
    }
    // Software stage ladder
    if (lvl <= 3 || stage === "prototype") {
      return { label: "Prototype", tagClass: "badge-stage-lab", range: "Stages 1–3" };
    }
    if (lvl <= 5 || stage === "validated model" || stage === "validated_model") {
      return { label: "Validated Model", tagClass: "badge-stage-proto", range: "Stages 4–5" };
    }
    if (lvl <= 7 || stage === "pilot") {
      return { label: "Pilot", tagClass: "badge-stage-proto", range: "Stages 6–7" };
    }
    return { label: "Production", tagClass: "badge-stage-deploy", range: "Stages 8–9" };
  };

  const getTrlStageInfo = (level, stage) => getReadinessStageInfo(level, stage, false);

  return (
    <section className="deep-validation-card" id="deep-validation-section">
      <div className="deep-validation-header">
        <div className="header-badge" style={{ display: "inline-flex", gap: "10px", alignItems: "center" }}>
          <span><span className="dot-pulse"></span> DEEP VALIDATION MATRIX 2.0</span>
          {cachedFlag && (
            <span style={{
              background: "rgba(56, 189, 248, 0.15)",
              border: "1px solid rgba(56, 189, 248, 0.4)",
              color: "#38BDF8",
              padding: "2px 8px",
              borderRadius: "12px",
              fontSize: "11px",
              fontWeight: 800,
              textTransform: "uppercase"
            }}>
              ⚡ Cached result
            </span>
          )}
        </div>
        <h2>Technical, Economic & Empirical Feasibility</h2>
        <p>
          Rigorous multi-vector stress testing covering adversarial kill-switch failure modes,
          compute and unit economics viability, regulatory runway timelines, TRL maturity, and empirical trials.
        </p>
      </div>

      {/* Consistency Warnings Banner */}
      {consistencyWarnings && consistencyWarnings.length > 0 && (
        <div style={{
          background: "rgba(245, 158, 11, 0.1)",
          border: "1px solid rgba(245, 158, 11, 0.35)",
          borderRadius: "10px",
          padding: "16px 20px",
          marginBottom: "24px"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#F59E0B", fontWeight: 700, fontSize: "14px", marginBottom: "8px" }}>
            <span>⚠️</span>
            <span>Cross-Tab Consistency Warnings ({consistencyWarnings.length})</span>
          </div>
          <ul style={{ margin: 0, paddingLeft: "20px", color: "#CBD5E1", fontSize: "13px", lineHeight: "1.6" }}>
            {consistencyWarnings.map((warn, idx) => (
              <li key={idx} style={{ marginBottom: "4px" }}>{warn}</li>
            ))}
          </ul>
        </div>
      )}

      {/* =========================================================
          MODULE: KILL-SWITCH & FALSIFICATION TEST (ADVERSARIAL)
      ========================================================= */}
      {killSwitch && (
        <div className="kill-switch-banner">
          <div className="ks-header">
            <div className="ks-title-wrap">
              <span className="ks-alert-icon">⚡</span>
              <div>
                <span className="ks-eyebrow">ADVERSARIAL PRE-MORTEM & FALSIFICATION TEST</span>
                <h3 className="ks-title">Startup Kill-Switch Trigger</h3>
              </div>
            </div>
            <div className="ks-meta-wrap">
              {renderSourceTypeTag(killSwitch.source_type)}
              <span className={`confidence-pill ${getConfidenceBadgeClass(killSwitch.confidence)}`}>
                ● {killSwitch.confidence ? `${killSwitch.confidence.toUpperCase()} CONFIDENCE` : "EVALUATED"}
              </span>
              {killSwitch.test_budget_usd !== undefined && (
                <span className="ks-budget-pill">
                  Budget: ${killSwitch.test_budget_usd} USD
                </span>
              )}
            </div>
          </div>

          {/* Fatal Assumption Callout */}
          <div className="fatal-assumption-box">
            <div className="fatal-label">
              <span className="fatal-dot"></span> FATAL UNPROVEN ASSUMPTION
            </div>
            <p className="fatal-text">{killSwitch.fatal_assumption}</p>
          </div>

          {/* 14-Day Cheap Test & Walk-Away Threshold Grid */}
          <div className="ks-grid">
            <div className="ks-grid-card cheap-test-card">
              <div className="ks-card-tag">
                <span>⏱️</span> 14-DAY MICRO-TEST PROTOCOL
              </div>
              <p className="ks-card-body">{killSwitch.cheap_test}</p>
            </div>

            <div className="ks-grid-card kill-threshold-card">
              <div className="ks-card-tag">
                <span>🛑</span> QUANTITATIVE KILL THRESHOLD
              </div>
              <p className="ks-card-body kill-metric">{killSwitch.kill_threshold}</p>
              <span className="kill-metric-sub">Walk away or pivot if condition is triggered</span>
            </div>
          </div>

          {/* Expandable Evidence Drawer */}
          {killSwitch.evidence?.length > 0 && (
            <div className="evidence-drawer">
              <button
                type="button"
                className="evidence-toggle-btn"
                onClick={() => setShowKillEvidence(!showKillEvidence)}
                aria-expanded={showKillEvidence}
              >
                <span>{showKillEvidence ? "▼ Hide Grounding Evidence & Citations" : "▶ View Grounding Evidence & Citations"} ({killSwitch.evidence.length})</span>
                <span className="evidence-count-tag">{killSwitch.evidence.length} sources</span>
              </button>
              {showKillEvidence && (
                <ul className="evidence-list">
                  {killSwitch.evidence.map((ev, idx) => (
                    <li key={idx} className="evidence-item">
                      <span className="ev-claim">{ev.claim || ev.text || ev}</span>
                      {ev.source_url && (
                        <a
                          href={ev.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="ev-source-link"
                        >
                          Source Link ↗
                        </a>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      )}

      {/* =========================================================
          1. FOUNDATIONAL FEASIBILITY PILLARS (TECH, SCI, REG)
      ========================================================= */}
      {(technical || scientific || regulatory) && (
        <div className={`deep-validation-feasibility-grid pillars-${[technical, scientific, regulatory].filter(Boolean).length}`}>
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

            {/* Scientific Risk Flags */}
            {scientific.risk_flags?.length > 0 && (
              <div className="module-section">
                <h4>
                  <span className="icon-bullet">🚩</span> Scientific Risk Flags
                </h4>
                <ul className="risk-flags-list">
                  {scientific.risk_flags.map((flag, idx) => (
                    <li key={idx} className="risk-flag-item">
                      {flag}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Required Validation Trials */}
            {scientific.required_trials?.length > 0 && (
              <div className="module-section">
                <h4>
                  <span className="icon-bullet">🔬</span> Required Validation Trials
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
                <h3>Regulatory Risk & Governance</h3>
              </div>
              <div className="module-score-wrap">
                <span className={`status-pill ${getRiskBadgeClass(regulatory.risk_level)}`}>
                  {regulatory.risk_level || "Medium"} Risk
                </span>
              </div>
            </div>

            <div className="rating-row">
              <span className="metric-label">Governing Regime:</span>
              <span className="reg-class-badge">
                {Array.isArray(regulatory.applicable_regimes) && regulatory.applicable_regimes.length > 0
                  ? regulatory.applicable_regimes.map((r) => (typeof r === "string" ? r : r.name)).join(" / ")
                  : (regulatory.fda_classification || regulatory.regulatory_classification || "Standard Industry Governance")}
              </span>
            </div>

            {/* Applicable Regimes List with Why Applies */}
            {Array.isArray(regulatory.applicable_regimes) && regulatory.applicable_regimes.length > 0 && (
              <div className="module-section" style={{ marginTop: "12px", marginBottom: "12px" }}>
                <h4>
                  <span className="icon-bullet">📜</span> Applicable Regimes & Standards
                </h4>
                <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                  {regulatory.applicable_regimes.map((reg, idx) => {
                    const rName = typeof reg === "string" ? reg : reg.name;
                    const rWhy = typeof reg === "object" ? reg.why_applies : null;
                    const rType = typeof reg === "object" ? reg.type : null;
                    return (
                      <div
                        key={idx}
                        style={{
                          padding: "8px 10px",
                          borderRadius: "6px",
                          background: "rgba(255, 255, 255, 0.03)",
                          borderLeft: rType === "mandatory" ? "3px solid #EF4444" : "3px solid #38BDF8",
                          fontSize: "12px",
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                          <span style={{ fontWeight: 600, color: "#F8FAFC" }}>{rName}</span>
                          {rType && (
                            <span
                              style={{
                                fontSize: "10px",
                                textTransform: "uppercase",
                                padding: "2px 6px",
                                borderRadius: "4px",
                                background: rType === "mandatory" ? "rgba(239, 68, 68, 0.15)" : "rgba(56, 189, 248, 0.15)",
                                color: rType === "mandatory" ? "#EF4444" : "#38BDF8",
                                fontWeight: 600,
                              }}
                            >
                              {rType}
                            </span>
                          )}
                        </div>
                        {rWhy && (
                          <div style={{ color: "#94A3B8", fontSize: "11px", marginTop: "3px" }}>
                            {rWhy}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Recommended Pathway */}
            {regulatory.recommended_pathway && (
              <div className="module-section pathway-section">
                <h4>
                  <span className="icon-bullet">🧭</span> Recommended Pathway
                </h4>
                <p className="pathway-text">{regulatory.recommended_pathway}</p>
              </div>
            )}

            {/* Compliance Requirements */}
            {regulatory.compliance_requirements?.length > 0 && (
              <div className="module-section">
                <h4>
                  <span className="icon-bullet">📋</span> Compliance Requirements
                </h4>
                <ul className="compliance-list">
                  {regulatory.compliance_requirements.map((req, idx) => (
                    <li key={idx} className="compliance-item">
                      {req}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
        </div>
      )}

      {/* =========================================================
          2. FINANCIAL & REGULATORY OPERATIONS (UNIT ECON, RUNWAY)
      ========================================================= */}
      {(unitEconomics || regulatoryRunway) && (
        <div className={`deep-validation-ops-grid ${unitEconomics && regulatoryRunway ? "two-col" : "single-col"}`}>
          {/* 4. UNIT ECONOMICS & MARGIN VIABILITY */}
          {unitEconomics && (
          <div className="validation-module unit-economics-module">
            <div className="module-top">
              <div className="module-icon">💰</div>
              <div className="module-title-wrap">
                <span className="module-tag">PILLAR 04</span>
                <h3>Unit Economics & Margin Viability</h3>
              </div>
              <div className="module-score-wrap">
                <span className={`status-pill ${getMarginGradeClass(unitEconomics.margin_grade)}`}>
                  {(unitEconomics.margin_grade || "healthy").toUpperCase().replace("_", " ")}
                </span>
              </div>
            </div>

            <div className="rating-row" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className="metric-label">Estimated Gross Margin:</span>
              <span className="gross-margin-metric" style={{ display: "inline-flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
                <span>{formatMarginPct(unitEconomics.gross_margin_pct)}</span>
                {unitEconomics.margin_range_formatted && (
                  <span className="margin-range-badge" style={{
                    fontSize: "12px",
                    fontWeight: 600,
                    padding: "2px 8px",
                    borderRadius: "4px",
                    background: "rgba(56, 189, 248, 0.15)",
                    color: "#38BDF8",
                    border: "1px solid rgba(56, 189, 248, 0.3)"
                  }}>
                    Range: {unitEconomics.margin_range_formatted}
                  </span>
                )}
                {(unitEconomics.wide_uncertainty || (unitEconomics.margin_spread != null && unitEconomics.margin_spread > 40) || ((unitEconomics.scenarios?.high?.gross_margin_pct != null && unitEconomics.scenarios?.low?.gross_margin_pct != null) && (unitEconomics.scenarios.high.gross_margin_pct - unitEconomics.scenarios.low.gross_margin_pct > 40))) && (
                  <span className="wide-uncertainty-badge" style={{
                    fontSize: "11px",
                    fontWeight: 700,
                    padding: "2px 8px",
                    borderRadius: "4px",
                    background: "rgba(245, 158, 11, 0.2)",
                    color: "#F59E0B",
                    border: "1px solid rgba(245, 158, 11, 0.5)",
                    textTransform: "uppercase"
                  }}>
                    ⚠️ Wide uncertainty
                  </span>
                )}
              </span>
            </div>

            {/* Margin Gauge Visual */}
            <div className="margin-gauge-container">
              <div className="margin-gauge-bar-track">
                <div
                  className={`margin-gauge-bar-fill ${getMarginGradeClass(unitEconomics.margin_grade)}`}
                  style={{ width: `${Math.min(100, Math.max(0, unitEconomics.gross_margin_pct || 0))}%` }}
                ></div>
              </div>
              <div className="margin-price-compare">
                <div className="compare-col">
                  <span className="compare-label">Cost-to-Serve:</span>
                  <span className="compare-val cost-val">{formatCurrency(unitEconomics.cost_to_serve_per_user_usd)} <small>/ {unitLabel}</small></span>
                </div>
                <div className="compare-col text-right">
                  <span className="compare-label">Suggested Price:</span>
                  <span className="compare-val price-val">{formatCurrency(unitEconomics.suggested_price_usd)} <small>/ {unitLabel}</small></span>
                </div>
              </div>
            </div>

            {/* One-Driver-at-a-Time Sensitivity Table */}
            {Array.isArray(unitEconomics.sensitivity_table) && unitEconomics.sensitivity_table.length > 0 ? (
              <div
                className="module-section sensitivity-table-section"
                style={{
                  background: "rgba(15, 23, 42, 0.5)",
                  padding: "12px 14px",
                  borderRadius: "8px",
                  border: "1px solid rgba(255, 255, 255, 0.08)",
                  marginTop: "12px",
                }}
              >
                <h4
                  style={{
                    fontSize: "12px",
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    color: "#94A3B8",
                    marginBottom: "10px",
                    display: "flex",
                    justifyContent: "space-between",
                  }}
                >
                  <span>
                    <span className="icon-bullet">📊</span> One-Driver-at-a-Time Margin Sensitivity
                  </span>
                  {unitEconomics.break_even_default_rate_pct != null && (
                    <span style={{ color: "#F59E0B", fontWeight: 600 }}>
                      Break-Even Default: {unitEconomics.break_even_default_rate_pct}%
                    </span>
                  )}
                </h4>
                <div style={{ overflowX: "auto" }}>
                  <table
                    style={{
                      width: "100%",
                      borderCollapse: "collapse",
                      fontSize: "11px",
                      textAlign: "left",
                    }}
                  >
                    <thead>
                      <tr style={{ borderBottom: "1px solid rgba(255, 255, 255, 0.1)", color: "#94A3B8" }}>
                        <th style={{ padding: "6px 8px" }}>Risk Driver</th>
                        <th style={{ padding: "6px 8px" }}>Base</th>
                        <th style={{ padding: "6px 8px" }}>Stressed</th>
                        <th style={{ padding: "6px 8px" }}>Impact (Δ)</th>
                        <th style={{ padding: "6px 8px" }}>Severity</th>
                      </tr>
                    </thead>
                    <tbody>
                      {unitEconomics.sensitivity_table.map((row, idx) => (
                        <tr key={idx} style={{ borderBottom: "1px solid rgba(255, 255, 255, 0.04)" }}>
                          <td style={{ padding: "6px 8px", color: "#E2E8F0" }}>{row.driver}</td>
                          <td style={{ padding: "6px 8px", color: "#94A3B8" }}>{row.base_margin_pct}%</td>
                          <td
                            style={{
                              padding: "6px 8px",
                              color:
                                row.stressed_margin_pct >= 70
                                  ? "#10B981"
                                  : row.stressed_margin_pct >= 30
                                  ? "#F59E0B"
                                  : "#EF4444",
                              fontWeight: 600,
                            }}
                          >
                            {row.stressed_margin_pct}%
                          </td>
                          <td
                            style={{
                              padding: "6px 8px",
                              color: row.margin_delta_pct < 0 ? "#EF4444" : "#10B981",
                            }}
                          >
                            {row.margin_delta_pct > 0 ? `+${row.margin_delta_pct}%` : `${row.margin_delta_pct}%`}
                          </td>
                          <td style={{ padding: "6px 8px" }}>
                            <span
                              style={{
                                padding: "2px 6px",
                                borderRadius: "4px",
                                fontSize: "10px",
                                textTransform: "uppercase",
                                background:
                                  row.severity?.toLowerCase() === "high"
                                    ? "rgba(239, 68, 68, 0.2)"
                                    : "rgba(245, 158, 11, 0.2)",
                                color:
                                  row.severity?.toLowerCase() === "high" ? "#EF4444" : "#F59E0B",
                              }}
                            >
                              {row.severity || "Medium"}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : unitEconomics.scenarios ? (
              <div
                className="module-section ue-scenarios-section"
                style={{
                  background: "rgba(15, 23, 42, 0.5)",
                  padding: "12px 14px",
                  borderRadius: "8px",
                  border: "1px solid rgba(255, 255, 255, 0.08)",
                  marginTop: "12px",
                }}
              >
                <h4
                  style={{
                    fontSize: "12px",
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    color: "#94A3B8",
                    marginBottom: "10px",
                    display: "flex",
                    justifyContent: "space-between",
                  }}
                >
                  <span>
                    <span className="icon-bullet">📈</span> Scenario Stress-Test Range (Python Computed)
                  </span>
                  {unitEconomics.break_even_default_rate_pct != null && (
                    <span style={{ color: "#F59E0B", fontWeight: 600 }}>
                      Break-Even Default: {unitEconomics.break_even_default_rate_pct}%
                    </span>
                  )}
                </h4>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "8px" }}>
                  {["low", "base", "high"].map((scenarioKey) => {
                    const sc = unitEconomics.scenarios[scenarioKey];
                    if (!sc) return null;
                    const isBase = scenarioKey === "base";
                    return (
                      <div
                        key={scenarioKey}
                        style={{
                          padding: "10px",
                          borderRadius: "6px",
                          background: isBase ? "rgba(56, 189, 248, 0.1)" : "rgba(30, 41, 59, 0.5)",
                          border: isBase
                            ? "1px solid rgba(56, 189, 248, 0.3)"
                            : "1px solid rgba(255, 255, 255, 0.06)",
                          fontSize: "11px",
                        }}
                      >
                        <div
                          style={{
                            fontWeight: 600,
                            color: isBase ? "#38BDF8" : "#E2E8F0",
                            marginBottom: "4px",
                          }}
                        >
                          {sc.label || scenarioKey.toUpperCase()}
                        </div>
                        <div
                          style={{
                            fontSize: "13px",
                            fontWeight: "bold",
                            color:
                              sc.gross_margin_pct >= 70
                                ? "#10B981"
                                : sc.gross_margin_pct >= 30
                                ? "#F59E0B"
                                : "#EF4444",
                          }}
                        >
                          {formatMarginPct(sc.gross_margin_pct)} Margin
                        </div>
                        <div
                          style={{
                            color: "#94A3B8",
                            marginTop: "4px",
                            fontSize: "10px",
                            lineHeight: "1.3",
                          }}
                        >
                          {sc.description ||
                            `${currencySymbol}${sc.loan_size || 0} loan, ${sc.default_rate_pct || 0}% default`}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : null}

            {/* Micro-Lending Breakdown (if applicable) */}
            {unitEconomics.loan_size != null && (
              <div className="module-section lending-breakdown-section" style={{
                background: "rgba(15, 23, 42, 0.4)",
                padding: "12px 14px",
                borderRadius: "8px",
                border: "1px solid rgba(255, 255, 255, 0.08)",
                marginTop: "12px"
              }}>
                <h4 style={{ fontSize: "12px", textTransform: "uppercase", letterSpacing: "0.05em", color: "#94A3B8", marginBottom: "10px" }}>
                  <span className="icon-bullet">📊</span> Per-Loan Economics ({currencySymbol}{Number(unitEconomics.loan_size).toLocaleString()} Principal)
                </h4>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", fontSize: "12px" }}>
                  <div><span style={{ color: "#94A3B8" }}>Revenue / Loan:</span> <strong style={{ color: "#10B981" }}>{formatCurrency(unitEconomics.revenue_per_loan)}</strong></div>
                  <div><span style={{ color: "#94A3B8" }}>Cost of Capital:</span> <strong style={{ color: "#EF4444" }}>{formatCurrency(unitEconomics.cost_of_capital)}</strong></div>
                  <div><span style={{ color: "#94A3B8" }}>Default Loss:</span> <strong style={{ color: "#EF4444" }}>{formatCurrency(unitEconomics.expected_default_loss)}</strong></div>
                  <div><span style={{ color: "#94A3B8" }}>Collections Cost:</span> <strong style={{ color: "#F59E0B" }}>{formatCurrency(unitEconomics.collections_cost)}</strong></div>
                  <div><span style={{ color: "#94A3B8" }}>CAC / Loan:</span> <strong style={{ color: "#F59E0B" }}>{formatCurrency(unitEconomics.cac)}</strong></div>
                  <div><span style={{ color: "#94A3B8" }}>Net Contribution:</span> <strong style={{ color: "#38BDF8" }}>{formatCurrency(unitEconomics.net_contribution_per_loan)}</strong></div>
                </div>
                {unitEconomics.effective_apr != null && (
                  <div style={{ marginTop: "8px", paddingTop: "8px", borderTop: "1px solid rgba(255, 255, 255, 0.06)", fontSize: "11px", color: "#CBD5E1" }}>
                    <span>Effective Annualized Rate: </span>
                    <strong style={{ color: "#FBBF24" }}>{unitEconomics.effective_apr}% p.a. APR</strong>
                    <span style={{ color: "#94A3B8" }}> (30-day single bullet repayment)</span>
                  </div>
                )}
              </div>
            )}

            {/* Platform Dependency Risk */}
            {unitEconomics.platform_dependency_risk && (
              <div className="module-section">
                <h4>
                  <span className="icon-bullet">🔌</span> Platform Dependency Risk
                </h4>
                <div className="dependency-risk-box">
                  <p>{unitEconomics.platform_dependency_risk}</p>
                </div>
              </div>
            )}

            {/* Collapsible Assumptions */}
            {unitEconomics.assumptions?.length > 0 && (
              <div className="module-section">
                <button
                  type="button"
                  className="assumptions-toggle-btn"
                  onClick={() => setShowAssumptions(!showAssumptions)}
                  aria-expanded={showAssumptions}
                >
                  <span>{showAssumptions ? "▼ Hide Cost Assumptions" : "▶ View Cost Assumptions"} ({unitEconomics.assumptions.length})</span>
                </button>
                {showAssumptions && (
                  <ul className="assumptions-list">
                    {unitEconomics.assumptions.map((item, idx) => (
                      <li key={idx} className="assumption-item">
                        <span className="bullet-dot">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {/* Confidence & Evidence Drawer */}
            <div className="ue-footer-meta">
              <div className="ue-conf-wrap">
                {renderSourceTypeTag(unitEconomics.source_type)}
                <span className="meta-sublabel">Confidence:</span>
                <span className={`confidence-pill ${getConfidenceBadgeClass(unitEconomics.confidence)}`}>
                  ● {unitEconomics.confidence ? `${unitEconomics.confidence.toUpperCase()}` : "EVALUATED"}
                </span>
              </div>
              {unitEconomics.evidence?.length > 0 && (
                <div className="evidence-drawer">
                  <button
                    type="button"
                    className="evidence-toggle-btn sm"
                    onClick={() => setShowUeEvidence(!showUeEvidence)}
                    aria-expanded={showUeEvidence}
                  >
                    <span>{showUeEvidence ? "▼ Hide Sources" : "▶ Sources"} ({unitEconomics.evidence.length})</span>
                  </button>
                  {showUeEvidence && (
                    <ul className="evidence-list">
                      {unitEconomics.evidence.map((ev, idx) => (
                        <li key={idx} className="evidence-item">
                          <span className="ev-claim">{ev.claim || ev.text || ev}</span>
                          {ev.source_url && (
                            <a
                              href={ev.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="ev-source-link"
                            >
                              Source Link ↗
                            </a>
                          )}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* 5. REGULATORY RUNWAY & CLEARANCE TIMELINE */}
        {regulatoryRunway && (
          <div className="validation-module regulatory-runway-module">
            <div className="module-top">
              <div className="module-icon">⏱️</div>
              <div className="module-title-wrap">
                <span className="module-tag">PILLAR 05</span>
                <h3>Regulatory Runway & CapEx Penalty</h3>
              </div>
              <div className="module-score-wrap">
                <span className="cost-burn-badge">
                  {regulatoryRunway.pre_revenue_burn_usd_max > 0
                    ? `$${(regulatoryRunway.pre_revenue_burn_usd_min || 0).toLocaleString()} – $${(regulatoryRunway.pre_revenue_burn_usd_max || 0).toLocaleString()} USD`
                    : "$0 USD (Pure Software)"}
                </span>
              </div>
            </div>

            {/* Mandatory Regulations Group */}
            {regulatoryRunway.mandatory_regulations?.length > 0 && (
              <div style={{ marginBottom: "16px", marginTop: "12px" }}>
                <h4 style={{ fontSize: "11px", textTransform: "uppercase", letterSpacing: "0.05em", color: "#EF4444", marginBottom: "8px", fontWeight: 700 }}>
                  ⚖️ Mandatory Regulations (Legally Enforced)
                </h4>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                  {regulatoryRunway.mandatory_regulations.map((regime, idx) => (
                    <div key={idx} style={{ background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.3)", borderRadius: "6px", padding: "8px 12px", flex: "1 1 260px" }}>
                      <div style={{ color: "#FCA5A5", fontWeight: 700, fontSize: "12px" }}>🛡️ {regime.name || regime}</div>
                      {regime.why_applies && (
                        <div style={{ color: "#94A3B8", fontSize: "11px", marginTop: "4px" }}>{regime.why_applies}</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Voluntary Standards Group */}
            {regulatoryRunway.voluntary_standards?.length > 0 && (
              <div style={{ marginBottom: "16px", marginTop: "12px" }}>
                <h4 style={{ fontSize: "11px", textTransform: "uppercase", letterSpacing: "0.05em", color: "#38BDF8", marginBottom: "8px", fontWeight: 700 }}>
                  📜 Voluntary Certifications & Standards
                </h4>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                  {regulatoryRunway.voluntary_standards.map((regime, idx) => (
                    <div key={idx} style={{ background: "rgba(56, 189, 248, 0.1)", border: "1px solid rgba(56, 189, 248, 0.3)", borderRadius: "6px", padding: "8px 12px", flex: "1 1 260px" }}>
                      <div style={{ color: "#7DD3FC", fontWeight: 700, fontSize: "12px" }}>🏅 {regime.name || regime}</div>
                      {regime.why_applies && (
                        <div style={{ color: "#94A3B8", fontSize: "11px", marginTop: "4px" }}>{regime.why_applies}</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Fallback chip list if mandatory/voluntary not explicitly provided */}
            {(!regulatoryRunway.mandatory_regulations?.length && !regulatoryRunway.voluntary_standards?.length && regulatoryRunway.applicable_regimes?.length > 0) && (
              <div className="regimes-chip-row" style={{ marginTop: "12px" }}>
                {regulatoryRunway.applicable_regimes.map((regime, idx) => (
                  <span key={idx} className="regime-chip">
                    🛡️ {regime}
                  </span>
                ))}
              </div>
            )}

            {/* Horizontal Timeline Bar */}
            <div className="timeline-container">
              <div className="timeline-meta-row">
                <span className="timeline-label">Clearance Delay Timeline:</span>
                <span className="timeline-months-val">
                  {regulatoryRunway.time_to_clearance_months_max > 0
                    ? `${regulatoryRunway.time_to_clearance_months_min} – ${regulatoryRunway.time_to_clearance_months_max} Months`
                    : "0 Months (Immediate Launch)"}
                </span>
              </div>
              <div className="timeline-track">
                <div
                  className={`timeline-fill ${regulatoryRunway.time_to_clearance_months_max === 0 ? "zero-fill" : ""}`}
                  style={{
                    width: regulatoryRunway.time_to_clearance_months_max === 0
                      ? "100%"
                      : `${Math.min(100, Math.max(15, (regulatoryRunway.time_to_clearance_months_max / 24) * 100))}%`
                  }}
                ></div>
                <div className="timeline-markers">
                  <span className="timeline-node start">Start (M0)</span>
                  {regulatoryRunway.time_to_clearance_months_max > 0 && (
                    <span className="timeline-node mid">
                      Audit / Filing (~M{Math.round((regulatoryRunway.time_to_clearance_months_min + regulatoryRunway.time_to_clearance_months_max) / 2)})
                    </span>
                  )}
                  <span className="timeline-node end">
                    {regulatoryRunway.time_to_clearance_months_max > 0
                      ? `Clearance (M${regulatoryRunway.time_to_clearance_months_max})`
                      : "Direct Live"}
                  </span>
                </div>
              </div>
            </div>

            {/* Runway Penalty Summary */}
            {regulatoryRunway.runway_penalty_summary && (
              <div className="runway-penalty-box">
                <span className="penalty-icon">⚠️</span>
                <span className="penalty-text">{regulatoryRunway.runway_penalty_summary}</span>
              </div>
            )}

            {/* Required Hires Chips */}
            {regulatoryRunway.required_hires?.length > 0 && (
              <div className="module-section">
                <h4>
                  <span className="icon-bullet">👥</span> Required Compliance & Regulatory Hires
                </h4>
                <div className="hires-chips-container">
                  {regulatoryRunway.required_hires.map((hire, idx) => (
                    <span key={idx} className="hire-chip">
                      <span className="hire-avatar">👤</span> {hire}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Faster Path / Non-Regulated Bridge Card */}
            {regulatoryRunway.non_regulated_bridge && (
              <div className="faster-path-card">
                <div className="faster-path-header">
                  <span className="faster-path-icon">⚡</span>
                  <span className="faster-path-title">Faster Path / Non-Regulated Bridge</span>
                </div>
                <p className="faster-path-body">{regulatoryRunway.non_regulated_bridge}</p>
              </div>
            )}

            {/* Footer Confidence & Evidence */}
            <div className="ue-footer-meta">
              <div className="ue-conf-wrap">
                {renderSourceTypeTag(regulatoryRunway.source_type)}
                <span className="meta-sublabel">Confidence:</span>
                <span className={`confidence-pill ${getConfidenceBadgeClass(regulatoryRunway.confidence)}`}>
                  ● {regulatoryRunway.confidence ? `${regulatoryRunway.confidence.toUpperCase()}` : "EVALUATED"}
                </span>
              </div>
              {regulatoryRunway.evidence?.length > 0 && (
                <div className="evidence-drawer">
                  <button
                    type="button"
                    className="evidence-toggle-btn sm"
                    onClick={() => setShowRegEvidence(!showRegEvidence)}
                    aria-expanded={showRegEvidence}
                  >
                    <span>{showRegEvidence ? "▼ Hide Sources" : "▶ Sources"} ({regulatoryRunway.evidence.length})</span>
                  </button>
                  {showRegEvidence && (
                    <ul className="evidence-list">
                      {regulatoryRunway.evidence.map((ev, idx) => (
                        <li key={idx} className="evidence-item">
                          <span className="ev-claim">{ev.claim || ev.text || ev}</span>
                          {ev.source_url && (
                            <a
                              href={ev.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="ev-source-link"
                            >
                              Source Link ↗
                            </a>
                          )}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
        </div>
      )}

      {/* =========================================================
          3. TECHNOLOGY READINESS LEVEL (TRL - PILLAR 06)
      ========================================================= */}
      {trlReadiness && (
        <div className="deep-validation-trl-wrapper">
          <div className="validation-module trl-readiness-module">
            <div className="module-top">
              <div className="module-icon">🚀</div>
              <div className="module-title-wrap">
                <span className="module-tag">PILLAR 06</span>
                <h3>{Boolean(trlReadiness.is_hardware) ? "Hardware Readiness Level (TRL)" : "Software Readiness Level"}</h3>
              </div>
              <div className="module-score-wrap">
                <div className="score-circle trl-circle">
                  <span className="score-val">{trlReadiness.trl_level || 1}</span>
                  <span className="score-max">/9</span>
                </div>
              </div>
            </div>

            {/* Stage Derived Badge */}
            <div className="rating-row">
              <span className="metric-label">Current Stage:</span>
              <span className={`status-pill ${getReadinessStageInfo(trlReadiness.trl_level, trlReadiness.trl_stage, Boolean(trlReadiness.is_hardware)).tagClass}`}>
                {getReadinessStageInfo(trlReadiness.trl_level, trlReadiness.trl_stage, Boolean(trlReadiness.is_hardware)).label} ({getReadinessStageInfo(trlReadiness.trl_level, trlReadiness.trl_stage, Boolean(trlReadiness.is_hardware)).range})
              </span>
              {trlReadiness.software_stage_label && !trlReadiness.is_hardware && (
                <span style={{ fontSize: "11px", color: "#38BDF8", marginLeft: "8px", fontWeight: 600 }}>
                  — {trlReadiness.software_stage_label}
                </span>
              )}
            </div>

            {/* 9-Step Ladder */}
            <div className="trl-ladder-container">
              <div className="trl-ladder">
                {(Boolean(trlReadiness.is_hardware) ? TRL_STEPS : SOFTWARE_STEPS).map((step) => {
                  const isCurrent = step.level === trlReadiness.trl_level;
                  const isCompleted = step.level < trlReadiness.trl_level;
                  return (
                    <div
                      key={step.level}
                      className={`trl-step ${isCurrent ? "current" : ""} ${isCompleted ? "completed" : ""}`}
                      title={`${step.label}: ${step.short} — ${step.desc}`}
                    >
                      <div className="trl-step-node">
                        {isCompleted ? "✓" : step.level}
                      </div>
                      <span className="trl-step-short">{step.short}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Diagnostics Row: Single Point of Failure & Bottlenecks */}
            {(trlReadiness.single_point_of_failure || trlReadiness.bottlenecks?.length > 0) && (
              <div className="trl-diagnostics-row">
                {trlReadiness.single_point_of_failure && (
                  <div className="spof-card">
                    <div className="spof-header">
                      <span className="spof-icon">🚨</span>
                      <span className="spof-title">Single Point of Failure (SPOF)</span>
                    </div>
                    <p className="spof-body">{trlReadiness.single_point_of_failure}</p>
                  </div>
                )}

                {trlReadiness.bottlenecks?.length > 0 && (
                  <div className="module-section" style={{ margin: 0 }}>
                    <h4>
                      <span className="icon-bullet">🚧</span> Critical Bottlenecks & Hazards
                    </h4>
                    <div className="bottlenecks-chips-container">
                      {trlReadiness.bottlenecks.map((b, idx) => (
                        <span
                          key={idx}
                          className={`bottleneck-chip severity-${b.severity || "medium"}`}
                        >
                          <span className="b-icon">{getBottleneckTypeIcon(b.type)}</span>
                          <span className="b-name">{b.name}</span>
                          <span className="b-sev-pill">{(b.severity || "medium").toUpperCase()}</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Footer Confidence & Evidence */}
            <div className="ue-footer-meta">
              <div className="ue-conf-wrap">
                {renderSourceTypeTag(trlReadiness.source_type)}
                <span className="meta-sublabel">Confidence:</span>
                <span className={`confidence-pill ${getConfidenceBadgeClass(trlReadiness.confidence)}`}>
                  ● {trlReadiness.confidence ? `${trlReadiness.confidence.toUpperCase()}` : "EVALUATED"}
                </span>
              </div>
              {trlReadiness.evidence?.length > 0 && (
                <div className="evidence-drawer">
                  <button
                    type="button"
                    className="evidence-toggle-btn sm"
                    onClick={() => setShowTrlEvidence(!showTrlEvidence)}
                    aria-expanded={showTrlEvidence}
                  >
                    <span>{showTrlEvidence ? "▼ Hide Sources" : "▶ Sources"} ({trlReadiness.evidence.length})</span>
                  </button>
                  {showTrlEvidence && (
                    <ul className="evidence-list">
                      {trlReadiness.evidence.map((ev, idx) => (
                        <li key={idx} className="evidence-item">
                          <span className="ev-claim">{ev.claim || ev.text || ev}</span>
                          {ev.source_url && (
                            <a
                              href={ev.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="ev-source-link"
                            >
                              Source Link ↗
                            </a>
                          )}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* =================================================================
          4. DEFENSIBILITY & STRATEGIC CONTINGENCY (MOAT, PIVOT)
      ================================================================== */}
      {(moatDurability || (pivotPlan && pivotPlan.triggered)) && (
        <div className={`deep-validation-resilience-grid ${(moatDurability && pivotPlan && pivotPlan.triggered) ? "two-col" : "single-col"}`}>
          {moatDurability && (
            <div className="validation-module moat-durability-module">
            <div className="module-header">
              <div className="module-title-wrap">
                <span className="module-icon">🛡️</span>
                <div>
                  <div className="module-badge-top">DEEP VALIDATION MATRIX • NOVELTY MOAT</div>
                  <h3>Moat Durability & Defensibility Matrix</h3>
                </div>
              </div>
              <div className="module-badges-right">
                <span
                  className={`moat-tier-pill ${getMoatTierBadgeClass(moatDurability.moat_tier)}`}
                  title="Overall Defensibility Tier"
                >
                  ● {(moatDurability.moat_tier || "DEFENSIBLE").toUpperCase()}
                </span>
                <span className="moat-overall-score-badge">
                  Score: {Number(moatDurability.moat_score || 0).toFixed(1)}/100
                </span>
              </div>
            </div>

            <p className="module-desc">
              Weighted composite defensibility (Data 35%, Workflow Lock-in 35%, Regulatory/IP 30%)
              and estimated timeline for well-funded rivals to clone or absorb the product.
            </p>

            {/* Overall Durability Bar (0-100) */}
            <div className="moat-bar-container">
              <div className="moat-bar-header">
                <span className="moat-bar-title">Overall Defensibility Durability</span>
                <span className="moat-bar-value">{Number(moatDurability.moat_score || 0).toFixed(1)}%</span>
              </div>
              <div className="moat-overall-track">
                <div
                  className={`moat-overall-fill ${getMoatTierBadgeClass(moatDurability.moat_tier)}`}
                  style={{ width: `${Math.max(5, Math.min(100, Number(moatDurability.moat_score || 0)))}%` }}
                />
              </div>
            </div>

            {/* Three Vectors Sub-bars with hover / click-to-expand reasons */}
            <div className="moat-vectors-grid">
              {/* Vector 1: Data Network Effect */}
              {moatDurability.data_network_effect && (
                <div
                  className={`moat-vector-card ${expandedMoatVector === "data" ? "expanded" : ""}`}
                  onClick={() => setExpandedMoatVector(expandedMoatVector === "data" ? null : "data")}
                  title="Click to toggle strategic rationale"
                >
                  <div className="vector-card-head">
                    <span className="vector-icon">📊</span>
                    <span className="vector-name">Data Network Effect</span>
                    <span className="vector-score">{moatDurability.data_network_effect.score || 0}/100</span>
                  </div>
                  <div className="vector-track">
                    <div
                      className="vector-fill data-fill"
                      style={{ width: `${Math.max(4, Math.min(100, Number(moatDurability.data_network_effect.score || 0)))}%` }}
                    />
                  </div>
                  <p className="vector-reason-preview">
                    {moatDurability.data_network_effect.reason || "Compounding dataset advantage and feedback loops."}
                  </p>
                </div>
              )}

              {/* Vector 2: Workflow Lock-in */}
              {moatDurability.workflow_lockin && (
                <div
                  className={`moat-vector-card ${expandedMoatVector === "lockin" ? "expanded" : ""}`}
                  onClick={() => setExpandedMoatVector(expandedMoatVector === "lockin" ? null : "lockin")}
                  title="Click to toggle strategic rationale"
                >
                  <div className="vector-card-head">
                    <span className="vector-icon">🔒</span>
                    <span className="vector-name">Workflow Lock-in</span>
                    <span className="vector-score">{moatDurability.workflow_lockin.score || 0}/100</span>
                  </div>
                  <div className="vector-track">
                    <div
                      className="vector-fill lockin-fill"
                      style={{ width: `${Math.max(4, Math.min(100, Number(moatDurability.workflow_lockin.score || 0)))}%` }}
                    />
                  </div>
                  <p className="vector-reason-preview">
                    {moatDurability.workflow_lockin.reason || "Operational switching friction and process entanglement."}
                  </p>
                </div>
              )}

              {/* Vector 3: Regulatory / IP Moat */}
              {moatDurability.regulatory_ip_moat && (
                <div
                  className={`moat-vector-card ${expandedMoatVector === "regulatory" ? "expanded" : ""}`}
                  onClick={() => setExpandedMoatVector(expandedMoatVector === "regulatory" ? null : "regulatory")}
                  title="Click to toggle strategic rationale"
                >
                  <div className="vector-card-head">
                    <span className="vector-icon">⚖️</span>
                    <span className="vector-name">Regulatory & IP Moat</span>
                    <span className="vector-score">{moatDurability.regulatory_ip_moat.score || 0}/100</span>
                  </div>
                  <div className="vector-track">
                    <div
                      className="vector-fill reg-fill"
                      style={{ width: `${Math.max(4, Math.min(100, Number(moatDurability.regulatory_ip_moat.score || 0)))}%` }}
                    />
                  </div>
                  <p className="vector-reason-preview">
                    {moatDurability.regulatory_ip_moat.reason || "Compliance barriers, trade secrets, and exclusive certifications."}
                  </p>
                </div>
              )}
            </div>

            {/* Replication Window & Likely Replicator Badge */}
            <div className="replication-window-card">
              <div className="replication-icon-wrap">⏱️</div>
              <div className="replication-info">
                <div className="rep-label">Estimated Replication Window</div>
                <div className="rep-value">
                  {moatDurability.replication_window_months_min}-{moatDurability.replication_window_months_max} Months
                  <span className="rep-threat-chip">
                    Likely cloned by: <strong>{moatDurability.likely_replicator || "Market Incumbents"}</strong>
                  </span>
                </div>
              </div>
            </div>

            {/* Footer Confidence & Evidence Drawer */}
            <div className="ue-footer-meta">
              <div className="ue-conf-wrap">
                {renderSourceTypeTag(moatDurability.source_type)}
                <span className="meta-sublabel">Confidence:</span>
                <span className={`confidence-pill ${getConfidenceBadgeClass(moatDurability.confidence)}`}>
                  ● {moatDurability.confidence ? `${moatDurability.confidence.toUpperCase()}` : "EVALUATED"}
                </span>
              </div>
              {moatDurability.evidence?.length > 0 && (
                <div className="evidence-drawer">
                  <button
                    type="button"
                    className="evidence-toggle-btn sm"
                    onClick={() => setShowMoatEvidence(!showMoatEvidence)}
                    aria-expanded={showMoatEvidence}
                  >
                    <span>{showMoatEvidence ? "▼ Hide Sources" : "▶ Sources"} ({moatDurability.evidence.length})</span>
                  </button>
                  {showMoatEvidence && (
                    <ul className="evidence-list">
                      {moatDurability.evidence.map((ev, idx) => (
                        <li key={idx} className="evidence-item">
                          <span className="ev-claim">{ev.claim || ev.text || ev}</span>
                          {ev.source_url && (
                            <a
                              href={ev.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="ev-source-link"
                            >
                              Source Link ↗
                            </a>
                          )}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

          {/* =================================================================
              MODULE 9: STRATEGIC PIVOT PLAN (ACTIVATED WHEN TRIGGERED)
          ================================================================== */}
          {pivotPlan && pivotPlan.triggered && (
            <div className="validation-module strategic-pivot-module">
            <div className="module-header">
              <div className="module-title-wrap">
                <span className="module-icon pivot-pulse-icon">🧭</span>
                <div>
                  <div className="module-badge-top pivot-alert-badge">AUTOMATED RISK TRIGGER ACTIVATED</div>
                  <h3>Strategic Pivot: {pivotPlan.pivot_name || "Target Pivot Architecture"}</h3>
                </div>
              </div>
              <div className="module-badges-right">
                <span className="pivot-time-saved-badge">
                  ⏱️ Saves {pivotPlan.months_saved || 6} Months
                </span>
              </div>
            </div>

            <p className="module-desc">
              High-risk vulnerabilities breached in TRL, regulatory clearance, unit economics, or moat durability.
              NEXUS has generated a strategic contingency pivot designed to bypass these fatal bottlenecks.
            </p>

            {/* Trigger Reason Chips */}
            {pivotPlan.trigger_reasons?.length > 0 && (
              <div className="pivot-triggers-container">
                <div className="pivot-triggers-label">Critical Breach Triggers:</div>
                <div className="pivot-trigger-chips">
                  {pivotPlan.trigger_reasons.map((reason, idx) => (
                    <span key={idx} className="pivot-trigger-chip">
                      <span className="trig-icon">⚠️</span>
                      <span className="trig-text">{reason}</span>
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Pivot Details: What Changes & New Regulatory Exposure */}
            <div className="pivot-details-grid">
              <div className="pivot-detail-card what-changes-card">
                <div className="detail-head">
                  <span className="detail-icon">✂️</span>
                  <span className="detail-title">What Changes (Cut or Swap)</span>
                </div>
                <p className="detail-body">{pivotPlan.what_changes || "De-scopes high-risk operational burdens."}</p>
              </div>

              <div className="pivot-detail-card reg-exposure-card">
                <div className="detail-head">
                  <span className="detail-icon">⚖️</span>
                  <span className="detail-title">New Regulatory Exposure</span>
                </div>
                <p className="detail-body">{pivotPlan.new_regulatory_exposure || "Lighter compliance posture."}</p>
              </div>
            </div>

            {/* 14-Day Validation Test Card */}
            {pivotPlan.first_test && (
              <div className="pivot-first-test-card">
                <div className="first-test-head">
                  <span className="test-badge">14-DAY EXPERIMENT</span>
                  <h4>First Validation Test for the Pivot</h4>
                </div>
                <p className="first-test-body">{pivotPlan.first_test}</p>
              </div>
            )}

            {/* Footer */}
            <div className="ue-footer-meta">
              <div className="ue-conf-wrap">
                {renderSourceTypeTag(pivotPlan.source_type)}
                <span className="meta-sublabel">Pivot Confidence:</span>
                <span className={`confidence-pill ${getConfidenceBadgeClass(pivotPlan.confidence)}`}>
                  ● {pivotPlan.confidence ? `${pivotPlan.confidence.toUpperCase()}` : "LOW"}
                </span>
              </div>
            </div>
          </div>
        )}
        </div>
      )}
    </section>
  );
}
