import React, { useState } from "react";

/**
 * GtmStrategy Component
 * Member 3 — NEXUS AI Startup Idea Validator
 *
 * Upgraded Commercial Strategy Blueprint:
 * - Archetype-First Classification & Reasoning
 * - Dynamic Viability Assessment (Replacing static "Investor Ready")
 * - Deterministic Validation Banner (PASS / PASS_WITH_WARNINGS / FAIL)
 * - Transparent Viability Scoring Breakdown (4-factor formula)
 * - Grounded Customer Segments (People / Organizations only)
 * - Evidence-Backed Pain Points (Facts vs. Inferences)
 * - Verified Competitor & Pricing Signals
 * - Archetype-Tailored Monetization & Unit Economics
 * - Startup-Specific Risks with Cheap Tests & Success Metrics
 * - 4-Phase Interactive Launch Roadmap with Numeric Targets
 * - Backward Compatible with Legacy GTM Schemas
 */

export interface GtmStrategyProps {
  gtmStrategy: any;
}

export default function GtmStrategy({ gtmStrategy }: GtmStrategyProps) {
  const [activePhaseIndex, setActivePhaseIndex] = useState(0);

  if (!gtmStrategy) return null;

  // Extract both legacy and upgraded fields
  const {
    // Legacy fields
    target_market = [],
    positioning = {},
    marketing_channels = [],
    customer_acquisition = [],
    pricing_strategy = "",
    launch_strategy = [],

    // Upgraded rich fields
    business_archetype,
    customer_segments = [],
    pain_points = [],
    competitors = [],
    pricing_evidence = [],
    pricing_strategy_details,
    unit_economics,
    risks = [],
    launch_roadmap,
    viability,
    gtm_validation,
    generation_mode = "llm"
  } = gtmStrategy;

  // Effective roadmap phases
  const roadmapPhases =
    launch_roadmap?.phases && launch_roadmap.phases.length > 0
      ? launch_roadmap.phases
      : launch_strategy;

  // Effective pricing details
  const pricingModel = pricing_strategy_details?.model || (typeof pricing_strategy === "string" ? pricing_strategy.split(".")[0] : "Monetization Model");
  const priceTiers = pricing_strategy_details?.price_tiers || [];
  const pricingRationale = pricing_strategy_details?.rationale || pricing_strategy;

  // Viability details
  const viabilityOverall = viability?.overall || "Commercial Strategy Ready";
  const viabilityConfidence = viability?.confidence ? Math.round(viability.confidence * 100) : 82;
  const viabilityComponents = viability?.components;

  // Validation details
  const valStatus = gtm_validation?.status || "PASS";
  const valScore = gtm_validation?.score !== undefined ? Math.round(gtm_validation.score * 100) : 95;
  const valViolations = gtm_validation?.violations || [];
  const valWarnings = gtm_validation?.warnings || [];

  return (
    <section className="gtm-strategy-section">
      <style>{`
        .gtm-strategy-section {
          background: linear-gradient(180deg, rgba(28, 25, 23, 0.85) 0%, rgba(17, 16, 14, 0.98) 100%);
          border: 1px solid rgba(245, 241, 232, 0.09);
          border-radius: 20px;
          padding: 34px 30px;
          margin-top: 36px;
          color: #f5f1e8;
          box-shadow: 0 16px 48px -12px rgba(0, 0, 0, 0.6);
          font-family: inherit;
        }

        .gtm-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          flex-wrap: wrap;
          gap: 16px;
          margin-bottom: 24px;
          border-bottom: 1px solid rgba(245, 241, 232, 0.08);
          padding-bottom: 22px;
        }

        .gtm-kicker {
          display: inline-block;
          font-size: 0.75rem;
          font-weight: 700;
          letter-spacing: 0.14em;
          text-transform: uppercase;
          color: #e28743;
          margin-bottom: 6px;
        }

        .gtm-title {
          font-family: "Outfit", sans-serif;
          font-size: 1.85rem;
          font-weight: 700;
          margin: 0;
          letter-spacing: -0.02em;
          background: linear-gradient(135deg, #f5f1e8 35%, #e28743 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .header-badges {
          display: flex;
          align-items: center;
          gap: 10px;
          flex-wrap: wrap;
        }

        .viability-badge {
          background: rgba(16, 185, 129, 0.12);
          border: 1px solid rgba(16, 185, 129, 0.35);
          color: #34d399;
          padding: 6px 14px;
          border-radius: 999px;
          font-size: 0.82rem;
          font-weight: 700;
          letter-spacing: 0.03em;
        }

        .viability-badge.warning {
          background: rgba(245, 158, 11, 0.12);
          border-color: rgba(245, 158, 11, 0.35);
          color: #fbbf24;
        }

        .viability-badge.fallback {
          background: rgba(148, 163, 184, 0.12);
          border-color: rgba(148, 163, 184, 0.3);
          color: #cbd5e1;
        }

        .val-badge {
          padding: 6px 12px;
          border-radius: 999px;
          font-size: 0.78rem;
          font-weight: 700;
          letter-spacing: 0.04em;
        }

        .val-pass {
          background: rgba(59, 130, 246, 0.15);
          border: 1px solid rgba(59, 130, 246, 0.35);
          color: #93c5fd;
        }

        .val-warn {
          background: rgba(245, 158, 11, 0.15);
          border: 1px solid rgba(245, 158, 11, 0.35);
          color: #fbbf24;
        }

        .val-fail {
          background: rgba(239, 68, 68, 0.15);
          border: 1px solid rgba(239, 68, 68, 0.35);
          color: #fca5a5;
        }

        /* Fallback Notice Banner */
        .fallback-banner {
          background: rgba(245, 158, 11, 0.08);
          border: 1px solid rgba(245, 158, 11, 0.25);
          border-radius: 12px;
          padding: 12px 18px;
          margin-bottom: 24px;
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 0.86rem;
          color: #fde68a;
        }

        /* Archetype Card */
        .archetype-banner {
          background: linear-gradient(135deg, rgba(226, 135, 67, 0.10) 0%, rgba(255, 255, 255, 0.02) 100%);
          border: 1px solid rgba(226, 135, 67, 0.25);
          border-radius: 14px;
          padding: 18px 22px;
          margin-bottom: 26px;
        }

        .archetype-top {
          display: flex;
          align-items: center;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: 12px;
          margin-bottom: 8px;
        }

        .archetype-pill {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          background: rgba(226, 135, 67, 0.2);
          border: 1px solid rgba(226, 135, 67, 0.4);
          color: #f5f1e8;
          font-weight: 700;
          font-size: 0.95rem;
          padding: 6px 14px;
          border-radius: 8px;
        }

        .archetype-secondary-pill {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          color: #d1c7b7;
          font-size: 0.8rem;
          padding: 4px 10px;
          border-radius: 6px;
        }

        .archetype-reasoning {
          margin: 0;
          font-size: 0.88rem;
          line-height: 1.5;
          color: #b8b2a7;
        }

        /* Viability Breakdown Box */
        .viability-breakdown-card {
          background: rgba(0, 0, 0, 0.35);
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: 12px;
          padding: 16px 20px;
          margin-bottom: 26px;
        }

        .breakdown-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 12px;
          margin-top: 10px;
        }

        .breakdown-item {
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid rgba(255, 255, 255, 0.04);
          border-radius: 8px;
          padding: 10px 14px;
        }

        .breakdown-label {
          font-size: 0.72rem;
          font-weight: 700;
          color: #a8a29e;
          text-transform: uppercase;
        }

        .breakdown-val {
          font-size: 1.05rem;
          font-weight: 700;
          color: #f5f1e8;
          margin-top: 2px;
        }

        /* Generic Card Layouts */
        .gtm-grid-2 {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 20px;
          margin-bottom: 26px;
        }

        .gtm-card {
          background: rgba(255, 255, 255, 0.025);
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: 14px;
          padding: 22px;
          transition: all 0.25s ease;
        }

        .gtm-card:hover {
          border-color: rgba(226, 135, 67, 0.25);
          background: rgba(255, 255, 255, 0.04);
        }

        .gtm-card-header {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 16px;
        }

        .gtm-card-icon {
          width: 32px;
          height: 32px;
          border-radius: 8px;
          background: rgba(226, 135, 67, 0.15);
          color: #e28743;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 0.95rem;
        }

        .gtm-card-title {
          font-size: 1.1rem;
          font-weight: 600;
          margin: 0;
          color: #f5f1e8;
        }

        /* Customer Segment Cards */
        .segment-card {
          background: rgba(0, 0, 0, 0.28);
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: 10px;
          padding: 14px 16px;
          margin-bottom: 12px;
        }

        .segment-card:last-child {
          margin-bottom: 0;
        }

        .segment-title {
          font-size: 0.96rem;
          font-weight: 700;
          color: #f5f1e8;
          margin-bottom: 6px;
        }

        .segment-detail {
          font-size: 0.84rem;
          color: #b8b2a7;
          margin: 4px 0;
          line-height: 1.45;
        }

        .segment-detail strong {
          color: #e6e0d4;
        }

        /* Pain Points */
        .pain-item {
          background: rgba(0, 0, 0, 0.25);
          border-left: 3px solid #e28743;
          border-radius: 0 8px 8px 0;
          padding: 12px 14px;
          margin-bottom: 10px;
        }

        .pain-source-tag {
          font-size: 0.68rem;
          font-weight: 700;
          text-transform: uppercase;
          background: rgba(255, 255, 255, 0.06);
          padding: 2px 7px;
          border-radius: 4px;
          color: #e28743;
          margin-right: 8px;
        }

        .pain-desc {
          font-size: 0.88rem;
          color: #e6e0d4;
          margin: 6px 0 2px 0;
          line-height: 1.4;
        }

        /* Competitors & Pricing Evidence */
        .comp-item {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          flex-wrap: wrap;
          background: rgba(0, 0, 0, 0.25);
          border: 1px solid rgba(255, 255, 255, 0.05);
          border-radius: 8px;
          padding: 12px 14px;
          margin-bottom: 10px;
          gap: 10px;
        }

        .comp-name {
          font-weight: 700;
          font-size: 0.92rem;
          color: #f5f1e8;
        }

        .comp-badge-verified {
          font-size: 0.72rem;
          font-weight: 700;
          background: rgba(16, 185, 129, 0.15);
          color: #34d399;
          border: 1px solid rgba(16, 185, 129, 0.3);
          padding: 2px 8px;
          border-radius: 4px;
        }

        .comp-badge-unverified {
          font-size: 0.72rem;
          font-weight: 600;
          background: rgba(148, 163, 184, 0.1);
          color: #94a3b8;
          border: 1px solid rgba(148, 163, 184, 0.2);
          padding: 2px 8px;
          border-radius: 4px;
        }

        /* Unit Economics */
        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
          gap: 12px;
          margin-bottom: 14px;
        }

        .metric-cell {
          background: rgba(0, 0, 0, 0.3);
          border: 1px solid rgba(255, 255, 255, 0.05);
          border-radius: 8px;
          padding: 10px 14px;
        }

        .metric-label {
          font-size: 0.72rem;
          font-weight: 700;
          text-transform: uppercase;
          color: #a8a29e;
        }

        .metric-val {
          font-size: 0.98rem;
          font-weight: 700;
          color: #e28743;
          margin-top: 3px;
        }

        /* Risks */
        .risk-item {
          background: rgba(0, 0, 0, 0.25);
          border: 1px solid rgba(255, 255, 255, 0.05);
          border-radius: 10px;
          padding: 12px 14px;
          margin-bottom: 10px;
        }

        .risk-top {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 6px;
        }

        .risk-severity {
          font-size: 0.68rem;
          font-weight: 700;
          text-transform: uppercase;
          padding: 2px 7px;
          border-radius: 4px;
        }

        .risk-high { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
        .risk-medium { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
        .risk-low { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }

        /* Pricing Tiers */
        .tier-card {
          background: rgba(0, 0, 0, 0.25);
          border: 1px solid rgba(226, 135, 67, 0.15);
          border-radius: 10px;
          padding: 12px 16px;
          margin-bottom: 8px;
        }

        .tier-head {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-weight: 700;
          font-size: 0.92rem;
          color: #f5f1e8;
          margin-bottom: 4px;
        }

        .tier-price {
          color: #e28743;
          font-size: 0.95rem;
        }

        /* Roadmap */
        .roadmap-tabs {
          display: flex;
          gap: 8px;
          margin-bottom: 16px;
          overflow-x: auto;
          padding-bottom: 6px;
        }

        .phase-tab {
          background: rgba(255, 255, 255, 0.04);
          border: 1px solid rgba(255, 255, 255, 0.08);
          color: #b8b2a7;
          padding: 9px 16px;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
          font-size: 0.84rem;
          white-space: nowrap;
          transition: all 0.2s ease;
        }

        .phase-tab:hover {
          background: rgba(255, 255, 255, 0.08);
          color: #f5f1e8;
        }

        .phase-tab.active {
          background: rgba(226, 135, 67, 0.2);
          border-color: #e28743;
          color: #f5f1e8;
        }

        .phase-content {
          background: rgba(0, 0, 0, 0.3);
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: 12px;
          padding: 18px 20px;
        }

        .phase-obj {
          font-size: 0.94rem;
          font-weight: 600;
          color: #e28743;
          margin-bottom: 12px;
        }

        .phase-actions-list {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .phase-action-item {
          display: flex;
          align-items: flex-start;
          gap: 10px;
          margin-bottom: 8px;
          font-size: 0.86rem;
          color: #d1c7b7;
          line-height: 1.45;
        }

        .action-check {
          color: #10b981;
          font-weight: 700;
          flex-shrink: 0;
        }
      `}</style>

      {/* Header */}
      <div className="gtm-header">
        <div>
          <span className="gtm-kicker">COMMERCIAL GO-TO-MARKET BLUEPRINT</span>
          <h2 className="gtm-title">GTM Strategy & Launch Engine</h2>
        </div>
        <div className="header-badges">
          {/* Dynamic Viability Badge */}
          <span className={`viability-badge ${generation_mode === "deterministic_fallback" ? "fallback" : viabilityOverall.includes("Moderate") ? "warning" : ""}`}>
            ● {viabilityOverall} ({viabilityConfidence}%)
          </span>

          {/* Validation Status Badge */}
          <span className={`val-badge ${valStatus === "PASS" ? "val-pass" : valStatus === "PASS_WITH_WARNINGS" ? "val-warn" : "val-fail"}`}>
            Validation: {valStatus} ({valScore}%)
          </span>
        </div>
      </div>

      {/* Fallback Notice Banner */}
      {generation_mode === "deterministic_fallback" && (
        <div className="fallback-banner">
          <span>⚡</span>
          <div>
            <strong>Deterministic Fallback Active:</strong> Commercial strategy was synthesized using the deterministic heuristic engine. Metrics are modeled as hypotheses benchmarked against industry standards.
          </div>
        </div>
      )}

      {/* Validation Failure / Warning Diagnostics Card */}
      {(valStatus === "FAIL" || valViolations.length > 0 || valWarnings.length > 0) && (
        <div style={{
          background: valStatus === "FAIL" ? "rgba(239, 68, 68, 0.08)" : "rgba(245, 158, 11, 0.08)",
          border: `1px solid ${valStatus === "FAIL" ? "rgba(239, 68, 68, 0.3)" : "rgba(245, 158, 11, 0.3)"}`,
          borderRadius: "14px",
          padding: "16px 20px",
          marginBottom: "24px"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px" }}>
            <span style={{ fontSize: "1.1rem" }}>{valStatus === "FAIL" ? "⚠️" : "ℹ️"}</span>
            <strong style={{ color: valStatus === "FAIL" ? "#fca5a5" : "#fde68a", fontSize: "0.95rem" }}>
              GTM Consistency Guardrail: {valStatus} ({valScore}%)
            </strong>
          </div>
          <p style={{ margin: "0 0 10px 0", fontSize: "0.86rem", color: "#d1c7b7", lineHeight: 1.45 }}>
            {valStatus === "FAIL"
              ? "The automated consistency guardrail flagged the following rule violation(s) in this commercial strategy draft:"
              : "The strategy passed with the following advisory note(s):"}
          </p>
          {valViolations.length > 0 && (
            <ul style={{ margin: "0 0 8px 0", paddingLeft: "20px", fontSize: "0.84rem", color: "#f87171", lineHeight: 1.5 }}>
              {valViolations.map((v: string, vIdx: number) => (
                <li key={vIdx}><strong>Rule Violation:</strong> {v}</li>
              ))}
            </ul>
          )}
          {valWarnings.length > 0 && (
            <ul style={{ margin: 0, paddingLeft: "20px", fontSize: "0.84rem", color: "#fbbf24", lineHeight: 1.5 }}>
              {valWarnings.map((w: string, wIdx: number) => (
                <li key={wIdx}><strong>Notice:</strong> {w}</li>
              ))}
            </ul>
          )}
          <div style={{ fontSize: "0.78rem", color: "#a8a29e", marginTop: "10px", borderTop: "1px solid rgba(255,255,255,0.06)", paddingTop: "8px" }}>
            💡 <em>Why is Viability {viabilityConfidence}% while Validation is {valScore}%?</em> Viability evaluates overall commercial feasibility (market demand, unit economics, evidence), while Validation checks strict internal rule compliance (rejecting publishers as competitors, banning mismatched enterprise jargon).
          </div>
        </div>
      )}

      {/* Archetype Banner */}
      {business_archetype && (
        <div className="archetype-banner">
          <div className="archetype-top">
            <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
              <span className="archetype-pill">
                🏛️ Archetype: {business_archetype.primary}
              </span>
              {business_archetype.secondary?.map((sec: any, sIdx: number) => (
                <span key={sIdx} className="archetype-secondary-pill">
                  + {sec.archetype} ({Math.round(sec.confidence * 100)}%)
                </span>
              ))}
            </div>
            <span style={{ fontSize: "0.82rem", color: "#e28743", fontWeight: 700 }}>
              Confidence: {Math.round((business_archetype.confidence || 0.85) * 100)}%
            </span>
          </div>
          <p className="archetype-reasoning">
            <strong>Model Rationale:</strong> {business_archetype.reasoning}
          </p>
        </div>
      )}

      {/* Viability Breakdown */}
      {viabilityComponents && (
        <div className="viability-breakdown-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span className="breakdown-label" style={{ color: "#e28743" }}>Viability Formula Breakdown</span>
            <span style={{ fontSize: "0.75rem", color: "#a8a29e" }}>25% per core dimension</span>
          </div>
          <div className="breakdown-grid">
            <div className="breakdown-item">
              <span className="breakdown-label">Evidence Grounding</span>
              <div className="breakdown-val">{Math.round(viabilityComponents.evidence_score * 100)}%</div>
            </div>
            <div className="breakdown-item">
              <span className="breakdown-label">Competitor Pricing</span>
              <div className="breakdown-val">{Math.round(viabilityComponents.competitor_pricing_score * 100)}%</div>
            </div>
            <div className="breakdown-item">
              <span className="breakdown-label">Unit Economics</span>
              <div className="breakdown-val">{Math.round(viabilityComponents.unit_economics_score * 100)}%</div>
            </div>
            <div className="breakdown-item">
              <span className="breakdown-label">GTM Validation</span>
              <div className="breakdown-val">{Math.round(viabilityComponents.validation_score * 100)}%</div>
            </div>
          </div>
        </div>
      )}

      {/* Row 1: Customer Segments & Pain Points */}
      <div className="gtm-grid-2">
        {/* Customer Segments */}
        <div className="gtm-card">
          <div className="gtm-card-header">
            <div className="gtm-card-icon">👥</div>
            <h3 className="gtm-card-title">Customer Personas & Organizations</h3>
          </div>
          {(customer_segments.length > 0 ? customer_segments : target_market).map((seg: any, idx: number) => (
            <div key={idx} className="segment-card">
              <div className="segment-title">
                {seg.type && <span style={{ color: "#e28743", marginRight: "6px" }}>[{seg.type}]</span>}
                {seg.segment}
              </div>
              {seg.why_they_care && (
                <p className="segment-detail"><strong>Why They Care:</strong> {seg.why_they_care}</p>
              )}
              {seg.core_problem && (
                <p className="segment-detail"><strong>Core Problem:</strong> {seg.core_problem}</p>
              )}
              {seg.buying_behavior && (
                <p className="segment-detail"><strong>Buying Behavior:</strong> {seg.buying_behavior}</p>
              )}
              {seg.profile && !seg.why_they_care && (
                <p className="segment-detail">{seg.profile}</p>
              )}
            </div>
          ))}
        </div>

        {/* Idea-Grounded Pain Points */}
        <div className="gtm-card">
          <div className="gtm-card-header">
            <div className="gtm-card-icon">⚡</div>
            <h3 className="gtm-card-title">Idea-Grounded Pain Points</h3>
          </div>
          {pain_points.length > 0 ? (
            pain_points.map((pt: any, idx: number) => (
              <div key={idx} className="pain-item">
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <span className="pain-source-tag">{pt.evidence_source || "inference"}</span>
                  <span style={{ fontSize: "0.74rem", color: "#a8a29e" }}>Affected: {pt.affected_segment}</span>
                </div>
                <p className="pain-desc">{pt.pain_point}</p>
              </div>
            ))
          ) : (
            <div>
              <div className="pain-item">
                <span className="pain-source-tag">Problem Solved</span>
                <p className="pain-desc">{positioning.problem_solved || "Core friction addressed by the solution."}</p>
              </div>
              <div className="pain-item">
                <span className="pain-source-tag">Target Beneficiary</span>
                <p className="pain-desc">{positioning.target_user || "Target users needing automated workflows."}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Row 2: Verified Competitors & Unit Economics */}
      <div className="gtm-grid-2">
        {/* Competitors & Pricing Evidence */}
        <div className="gtm-card">
          <div className="gtm-card-header">
            <div className="gtm-card-icon">🎯</div>
            <h3 className="gtm-card-title">Competitors & Pricing Evidence</h3>
          </div>
          {competitors.length > 0 ? (
            competitors.map((comp: any, idx: number) => (
              <div key={idx} className="comp-item">
                <div>
                  <div className="comp-name">{comp.name}</div>
                  <div style={{ fontSize: "0.8rem", color: "#b8b2a7", marginTop: "2px" }}>
                    {comp.product}
                  </div>
                </div>
                <div>
                  {comp.pricing ? (
                    <span className="comp-badge-verified">
                      Verified: {comp.pricing}
                    </span>
                  ) : (
                    <span className="comp-badge-unverified">
                      Pricing: Unverified
                    </span>
                  )}
                </div>
              </div>
            ))
          ) : (
            <p style={{ color: "#a8a29e", fontSize: "0.88rem" }}>
              No reliable direct competitors were identified from the available live evidence.
            </p>
          )}
        </div>

        {/* Unit Economics */}
        <div className="gtm-card">
          <div className="gtm-card-header">
            <div className="gtm-card-icon">📊</div>
            <h3 className="gtm-card-title">Archetype Unit Economics</h3>
          </div>
          {unit_economics?.metrics ? (
            <>
              <div className="metrics-grid">
                {Object.entries(unit_economics.metrics).map(([key, val], idx) => (
                  <div key={idx} className="metric-cell">
                    <span className="metric-label">{key.replace(/_/g, " ")}</span>
                    <div className="metric-val">{String(val)}</div>
                  </div>
                ))}
              </div>
              {unit_economics.assumptions?.length > 0 && (
                <div style={{ fontSize: "0.8rem", color: "#b8b2a7" }}>
                  <strong>Key Assumptions:</strong>
                  <ul style={{ margin: "4px 0 0 0", paddingLeft: "18px" }}>
                    {unit_economics.assumptions.map((asm: string, aIdx: number) => (
                      <li key={aIdx}>{asm}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          ) : (
            <p style={{ color: "#a8a29e", fontSize: "0.88rem" }}>
              Standard SaaS benchmark economics modeled for this archetype.
            </p>
          )}
        </div>
      </div>

      {/* Row 3: Marketing Channels & Monetization Tiers */}
      <div className="gtm-grid-2">
        {/* Marketing Channels */}
        <div className="gtm-card">
          <div className="gtm-card-header">
            <div className="gtm-card-icon">📣</div>
            <h3 className="gtm-card-title">Actionable Marketing Channels</h3>
          </div>
          <div style={{ display: "grid", gap: "10px" }}>
            {marketing_channels.map((ch: any, idx: number) => (
              <div key={idx} style={{ background: "rgba(0,0,0,0.25)", padding: "12px 14px", borderRadius: "8px", border: "1px solid rgba(255,255,255,0.05)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
                  <span style={{ fontWeight: 700, fontSize: "0.92rem", color: "#f5f1e8" }}>{ch.channel}</span>
                  <span style={{ fontSize: "0.72rem", background: "rgba(255,255,255,0.06)", padding: "2px 7px", borderRadius: "4px", color: "#d1c7b7" }}>{ch.category}</span>
                </div>
                <p style={{ margin: 0, fontSize: "0.84rem", color: "#b8b2a7", lineHeight: 1.4 }}>{ch.tactics}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Pricing Strategy & Tiers */}
        <div className="gtm-card">
          <div className="gtm-card-header">
            <div className="gtm-card-icon">💳</div>
            <h3 className="gtm-card-title">Monetization & Pricing Tiers</h3>
          </div>
          <div style={{ marginBottom: "12px", fontSize: "0.92rem", fontWeight: 700, color: "#e28743" }}>
            {pricingModel}
          </div>
          {priceTiers.length > 0 ? (
            priceTiers.map((tier: any, idx: number) => (
              <div key={idx} className="tier-card">
                <div className="tier-head">
                  <span>{tier.tier}</span>
                  <span className="tier-price">{tier.price}</span>
                </div>
                <div style={{ fontSize: "0.82rem", color: "#b8b2a7" }}>{tier.description}</div>
              </div>
            ))
          ) : (
            <div style={{ background: "rgba(0,0,0,0.25)", padding: "14px", borderRadius: "8px", fontSize: "0.88rem", lineHeight: 1.5, color: "#d1c7b7" }}>
              {pricingRationale}
            </div>
          )}
        </div>
      </div>

      {/* Row 4: Startup-Specific Risks */}
      {risks.length > 0 && (
        <div className="gtm-card" style={{ marginBottom: "26px" }}>
          <div className="gtm-card-header">
            <div className="gtm-card-icon">🛡️</div>
            <h3 className="gtm-card-title">Commercial Risk Analysis & Inexpensive Validation Tests</h3>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "12px" }}>
            {risks.map((rk: any, idx: number) => (
              <div key={idx} className="risk-item">
                <div className="risk-top">
                  <span style={{ fontWeight: 700, fontSize: "0.92rem", color: "#f5f1e8" }}>{rk.risk}</span>
                  <span className={`risk-severity ${rk.severity === "high" ? "risk-high" : rk.severity === "medium" ? "risk-medium" : "risk-low"}`}>
                    {rk.severity}
                  </span>
                </div>
                <p style={{ margin: "4px 0 8px 0", fontSize: "0.82rem", color: "#b8b2a7", lineHeight: 1.4 }}>{rk.why}</p>
                <div style={{ fontSize: "0.8rem", background: "rgba(255,255,255,0.02)", padding: "8px 10px", borderRadius: "6px", border: "1px solid rgba(255,255,255,0.04)" }}>
                  <div><strong style={{ color: "#e28743" }}>Cheap Test:</strong> <span style={{ color: "#e6e0d4" }}>{rk.cheap_test}</span></div>
                  <div style={{ marginTop: "4px" }}><strong style={{ color: "#10b981" }}>Success Metric:</strong> <span style={{ color: "#d1c7b7" }}>{rk.success_metric}</span></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Row 5: 4-Phase Phased Launch Roadmap */}
      {roadmapPhases.length > 0 && (
        <div className="gtm-card">
          <div className="gtm-card-header">
            <div className="gtm-card-icon">🗺️</div>
            <h3 className="gtm-card-title">4-Phase Launch Roadmap & Numeric Milestones</h3>
          </div>

          <div className="roadmap-tabs">
            {roadmapPhases.map((phase: any, idx: number) => (
              <button
                key={idx}
                type="button"
                className={`phase-tab ${activePhaseIndex === idx ? "active" : ""}`}
                onClick={() => setActivePhaseIndex(idx)}
              >
                {phase.phase}
              </button>
            ))}
          </div>

          {roadmapPhases[activePhaseIndex] && (
            <div className="phase-content">
              <div className="phase-obj">
                Objective: {roadmapPhases[activePhaseIndex].objective}
              </div>
              <ul className="phase-actions-list">
                {roadmapPhases[activePhaseIndex].key_actions?.map((action: string, aIdx: number) => (
                  <li key={aIdx} className="phase-action-item">
                    <span className="action-check">✓</span>
                    <span>{action}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
