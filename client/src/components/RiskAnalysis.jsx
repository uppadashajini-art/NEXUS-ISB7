import React from "react";

export default function RiskAnalysis({ risks }) {
  if (!risks || !Array.isArray(risks) || risks.length === 0) return null;

  const getSeverityStyle = (severity = "") => {
    const s = severity.toLowerCase();
    if (s === "high") {
      return {
        bg: "rgba(255, 118, 87, 0.15)",
        border: "rgba(255, 118, 87, 0.4)",
        text: "var(--coral)",
        label: "HIGH SEVERITY"
      };
    }
    if (s === "low") {
      return {
        bg: "rgba(159, 214, 164, 0.15)",
        border: "rgba(159, 214, 164, 0.4)",
        text: "var(--success)",
        label: "LOW SEVERITY"
      };
    }
    return {
      bg: "rgba(232, 199, 123, 0.15)",
      border: "rgba(232, 199, 123, 0.4)",
      text: "var(--gold)",
      label: "MEDIUM SEVERITY"
    };
  };

  return (
    <section className="analysis-card risk-analysis-card" style={{ marginTop: "24px" }}>
      <div className="section-header-row" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <div>
          <span className="mini-label" style={{ color: "var(--gold)", fontSize: "0.75rem", fontWeight: 700, letterSpacing: "1px", textTransform: "uppercase" }}>
            OPERATIONAL & MARKET EXPOSURE
          </span>
          <h2 style={{ margin: "4px 0 0", fontSize: "1.4rem", color: "var(--text)" }}>Risk Matrix & Strategic Mitigations</h2>
        </div>
        <div style={{ background: "rgba(255, 118, 87, 0.1)", border: "1px solid rgba(255, 118, 87, 0.3)", padding: "6px 14px", borderRadius: "12px", color: "var(--coral)", fontSize: "0.85rem", fontWeight: 600 }}>
          {risks.length} Critical Risks Evaluated
        </div>
      </div>

      <div className="risks-grid" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        {risks.map((item, idx) => {
          const sev = getSeverityStyle(item.severity);
          return (
            <div
              key={idx}
              className="risk-card-item"
              style={{
                background: "var(--card-light)",
                border: "1px solid var(--border)",
                borderRadius: "var(--radius-md)",
                padding: "20px",
                display: "flex",
                flexDirection: "column",
                gap: "12px",
                transition: "border-color 0.2s ease"
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "12px", flexWrap: "wrap" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
                  <span style={{
                    background: "rgba(255,255,255,0.06)",
                    border: "1px solid var(--border-light)",
                    color: "var(--text)",
                    padding: "3px 10px",
                    borderRadius: "8px",
                    fontSize: "0.75rem",
                    fontWeight: 600,
                    textTransform: "uppercase"
                  }}>
                    {item.category || "General"} Risk
                  </span>
                  <h3 style={{ margin: 0, fontSize: "1.1rem", color: "var(--text)", fontWeight: 600 }}>
                    {item.risk}
                  </h3>
                </div>

                <span style={{
                  background: sev.bg,
                  border: `1px solid ${sev.border}`,
                  color: sev.text,
                  padding: "3px 10px",
                  borderRadius: "8px",
                  fontSize: "0.72rem",
                  fontWeight: 700,
                  letterSpacing: "0.5px"
                }}>
                  {sev.label}
                </span>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "14px", marginTop: "4px" }}>
                {item.impact && (
                  <div style={{ background: "rgba(0,0,0,0.2)", padding: "12px 16px", borderRadius: "10px", borderLeft: "3px solid var(--coral)" }}>
                    <strong style={{ display: "block", color: "var(--secondary)", fontSize: "0.78rem", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "4px" }}>
                      Potential Impact
                    </strong>
                    <p style={{ margin: 0, color: "var(--text)", fontSize: "0.9rem", lineHeight: "1.5" }}>
                      {item.impact}
                    </p>
                  </div>
                )}

                {item.mitigation && (
                  <div style={{ background: "rgba(0,0,0,0.2)", padding: "12px 16px", borderRadius: "10px", borderLeft: "3px solid var(--success)" }}>
                    <strong style={{ display: "block", color: "var(--secondary)", fontSize: "0.78rem", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "4px" }}>
                      Recommended Mitigation
                    </strong>
                    <p style={{ margin: 0, color: "var(--text)", fontSize: "0.9rem", lineHeight: "1.5" }}>
                      {item.mitigation}
                    </p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
