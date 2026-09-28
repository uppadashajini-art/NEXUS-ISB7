function severityColor(severity) {
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
      {risks.map((r, i) => (
        <div className={`risk-item ${severityColor(r.severity)}`} key={i}>
          <div className="risk-header">
            <strong>{r.risk}</strong>
            {r.severity && <span className="risk-badge">{r.severity}</span>}
          </div>
          {r.category && (
            <p>
              <strong>Category:</strong> {r.category}
            </p>
          )}
          {r.impact && (
            <p>
              <strong>Impact:</strong> {r.impact}
            </p>
          )}
          {r.mitigation && (
            <p>
              <strong>Suggested Mitigation:</strong> {r.mitigation}
            </p>
          )}
        </div>
      ))}
    </section>
  );
}