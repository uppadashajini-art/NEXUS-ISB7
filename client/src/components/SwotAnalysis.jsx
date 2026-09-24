import React from "react";

export default function SwotAnalysis({ data }) {
  if (!data) return null;

  const {
    strengths = [],
    weaknesses = [],
    opportunities = [],
    threats = []
  } = data;

  const totalPoints = strengths.length + weaknesses.length + opportunities.length + threats.length;
  if (totalPoints === 0) return null;

  return (
    <section className="analysis-card swot-analysis-card" style={{ marginTop: "24px" }}>
      <div className="section-header-row" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <div>
          <span className="mini-label" style={{ color: "var(--gold)", fontSize: "0.75rem", fontWeight: 700, letterSpacing: "1px", textTransform: "uppercase" }}>
            STRATEGIC POSITIONING
          </span>
          <h2 style={{ margin: "4px 0 0", fontSize: "1.4rem", color: "var(--text)" }}>SWOT Analysis</h2>
        </div>
        <div style={{ background: "rgba(232, 199, 123, 0.1)", border: "1px solid var(--border-light)", padding: "6px 14px", borderRadius: "12px", color: "var(--gold)", fontSize: "0.85rem", fontWeight: 600 }}>
          {totalPoints} Strategic Vectors
        </div>
      </div>

      <div className="swot-grid" style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
        gap: "18px"
      }}>
        {/* STRENGTHS */}
        <div className="swot-quadrant" style={{
          background: "rgba(159, 214, 164, 0.05)",
          border: "1px solid rgba(159, 214, 164, 0.25)",
          borderRadius: "var(--radius-md)",
          padding: "18px"
        }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "1.2rem" }}>🛡️</span>
              <h3 style={{ margin: 0, fontSize: "1.05rem", color: "var(--success)" }}>Strengths</h3>
            </div>
            <span style={{ background: "rgba(159, 214, 164, 0.2)", color: "var(--success)", padding: "2px 8px", borderRadius: "8px", fontSize: "0.75rem", fontWeight: 700 }}>
              {strengths.length}
            </span>
          </div>
          <ul style={{ margin: 0, paddingLeft: "18px", color: "var(--text)", lineHeight: "1.6", fontSize: "0.92rem" }}>
            {strengths.map((item, idx) => (
              <li key={idx} style={{ marginBottom: "8px" }}>{item}</li>
            ))}
          </ul>
        </div>

        {/* WEAKNESSES */}
        <div className="swot-quadrant" style={{
          background: "rgba(255, 180, 167, 0.05)",
          border: "1px solid rgba(255, 180, 167, 0.25)",
          borderRadius: "var(--radius-md)",
          padding: "18px"
        }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "1.2rem" }}>⚠️</span>
              <h3 style={{ margin: 0, fontSize: "1.05rem", color: "var(--coral-light)" }}>Weaknesses</h3>
            </div>
            <span style={{ background: "rgba(255, 180, 167, 0.2)", color: "var(--coral-light)", padding: "2px 8px", borderRadius: "8px", fontSize: "0.75rem", fontWeight: 700 }}>
              {weaknesses.length}
            </span>
          </div>
          <ul style={{ margin: 0, paddingLeft: "18px", color: "var(--text)", lineHeight: "1.6", fontSize: "0.92rem" }}>
            {weaknesses.map((item, idx) => (
              <li key={idx} style={{ marginBottom: "8px" }}>{item}</li>
            ))}
          </ul>
        </div>

        {/* OPPORTUNITIES */}
        <div className="swot-quadrant" style={{
          background: "rgba(100, 181, 246, 0.05)",
          border: "1px solid rgba(100, 181, 246, 0.25)",
          borderRadius: "var(--radius-md)",
          padding: "18px"
        }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "1.2rem" }}>🚀</span>
              <h3 style={{ margin: 0, fontSize: "1.05rem", color: "#64b5f6" }}>Opportunities</h3>
            </div>
            <span style={{ background: "rgba(100, 181, 246, 0.2)", color: "#64b5f6", padding: "2px 8px", borderRadius: "8px", fontSize: "0.75rem", fontWeight: 700 }}>
              {opportunities.length}
            </span>
          </div>
          <ul style={{ margin: 0, paddingLeft: "18px", color: "var(--text)", lineHeight: "1.6", fontSize: "0.92rem" }}>
            {opportunities.map((item, idx) => (
              <li key={idx} style={{ marginBottom: "8px" }}>{item}</li>
            ))}
          </ul>
        </div>

        {/* THREATS */}
        <div className="swot-quadrant" style={{
          background: "rgba(255, 118, 87, 0.05)",
          border: "1px solid rgba(255, 118, 87, 0.25)",
          borderRadius: "var(--radius-md)",
          padding: "18px"
        }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "1.2rem" }}>⚡</span>
              <h3 style={{ margin: 0, fontSize: "1.05rem", color: "var(--coral)" }}>Threats</h3>
            </div>
            <span style={{ background: "rgba(255, 118, 87, 0.2)", color: "var(--coral)", padding: "2px 8px", borderRadius: "8px", fontSize: "0.75rem", fontWeight: 700 }}>
              {threats.length}
            </span>
          </div>
          <ul style={{ margin: 0, paddingLeft: "18px", color: "var(--text)", lineHeight: "1.6", fontSize: "0.92rem" }}>
            {threats.map((item, idx) => (
              <li key={idx} style={{ marginBottom: "8px" }}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
