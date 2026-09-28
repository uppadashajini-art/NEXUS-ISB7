export default function ValidationReport({ report }) {
  if (!report) return null;

  const sections = [
    ["Executive Summary", report.executive_summary],
    ["Market Summary", report.market_summary],
    ["Competitor Summary", report.competitor_summary],
    ["SWOT Summary", report.swot_summary],
    ["Risk Summary", report.risk_summary],
    ["MVP Summary", report.mvp_summary],
    ["Go-To-Market Summary", report.gtm_summary],
    ["Key Recommendations", report.recommendations],
    ["Conclusion", report.conclusion],
  ];

  return (
    <section className="analysis-card validation-report">
      <h2>Startup Validation Report</h2>
      {sections.map(([title, text], i) =>
        text ? (
          <div className="report-section" key={i}>
            <h3>{title}</h3>
            <p>{text}</p>
          </div>
        ) : null
      )}
    </section>
  );
}