// Place this file at: client/src/components/RiskAnalysis.jsx
//
// Styled to exactly match GtmStrategy.jsx's design language
// (.gtm-card, .risk-item, .risk-severity classes copied from there
// so this component looks visually identical, and is self-contained
// even if GtmStrategy isn't rendered on the same page).

function severityClass(severity) {
  const s = (severity || "").toLowerCase();
  if (s === "high" || s === "critical") return "risk-high";
  if (s === "medium") return "risk-medium";
  return "risk-low";
}

export default function RiskAnalysis({ risks }) {
  if (!risks || risks.length === 0) return null;

  return (
    <section className="analysis-card">
      <h2>Risk Analysis</h2>

      <div className="gtm-card">
        <div className="gtm-card-header">
          <div className="gtm-card-icon">⚠️</div>
          <h3 className="gtm-card-title">Identified Risks &amp; Mitigations</h3>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: "12px",
          }}
        >
          {risks.map((r, i) => (
            <div key={i} className="risk-item">
              <div className="risk-top">
                <span className="risk-name" style={{ fontWeight: 700, fontSize: "0.92rem", color: "#f5f1e8" }}>
                  {r.risk}
                </span>
                <span className={`risk-severity ${severityClass(r.severity)}`}>
                  {r.severity || "medium"}
                </span>
              </div>

              {r.category && (
                <p style={{ margin: "4px 0 8px 0", fontSize: "0.78rem", color: "#a8a29e" }}>
                  <strong style={{ color: "#e28743" }}>Category:</strong> {r.category}
                </p>
              )}

              {r.impact && (
                <p style={{ margin: "0 0 8px 0", fontSize: "0.82rem", color: "#b8b2a7", lineHeight: 1.4 }}>
                  {r.impact}
                </p>
              )}

              {r.mitigation && (
                <div
                  className="risk-mitigation-box"
                  style={{
                    fontSize: "0.8rem",
                    background: "rgba(255,255,255,0.02)",
                    padding: "8px 10px",
                    borderRadius: "6px",
                    border: "1px solid rgba(255,255,255,0.04)",
                  }}
                >
                  <strong style={{ color: "#34d399" }}>Mitigation:</strong>{" "}
                  <span className="risk-mitigation-text" style={{ color: "#e6e0d4" }}>{r.mitigation}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <style>{`
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

        /* -----------------------------------------------
           LIGHT THEME OVERRIDES
        ----------------------------------------------- */
        [data-theme="light"] .gtm-card {
          background: #ffffff;
          border-color: rgba(0, 0, 0, 0.08);
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        }
        [data-theme="light"] .gtm-card:hover {
          border-color: rgba(226, 135, 67, 0.35);
          background: #faf9f5;
        }
        [data-theme="light"] .gtm-card-title {
          color: #18181b;
        }
        [data-theme="light"] .risk-item {
          background: #f8f9fb;
          border-color: rgba(0, 0, 0, 0.06);
        }
        [data-theme="light"] .risk-name {
          color: #18181b !important;
        }
        [data-theme="light"] .risk-item p {
          color: #52525b !important;
        }
        [data-theme="light"] .risk-mitigation-box {
          background: rgba(16, 185, 129, 0.08) !important;
          border-color: rgba(16, 185, 129, 0.25) !important;
        }
        [data-theme="light"] .risk-mitigation-text {
          color: #18181b !important;
        }
      `}</style>
    </section>
  );
}