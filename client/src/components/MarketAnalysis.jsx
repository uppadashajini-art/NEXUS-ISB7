import React from "react";

function renderSafe(val, fallback = "") {
  if (val === null || val === undefined) return fallback;
  if (typeof val === "string") return val;
  if (typeof val === "number" || typeof val === "boolean") return String(val);
  if (Array.isArray(val)) return val.map((v) => renderSafe(v)).filter(Boolean).join(", ");
  if (typeof val === "object") {
    return val.text || val.point || val.title || val.name || val.driver || val.challenge || val.trend || JSON.stringify(val);
  }
  return String(val);
}

export default function MarketAnalysis({ data }) {
  if (!data) return null;

  const {
    industry,
    market_opportunity,
    market_trends = [],
    growth_drivers = [],
    market_challenges = [],
  } = data;

  return (
    <section className="analysis-card market-analysis-card">
      <div className="section-title-wrap" style={{ marginBottom: "20px" }}>
        <span className="card-mini-badge" style={{ background: "linear-gradient(135deg, rgba(255,199,44,0.15), rgba(255,138,31,0.15))", color: "#FFC72C", border: "1px solid rgba(255,199,44,0.3)" }}>
          MARKET INTELLIGENCE
        </span>
        <h2 className="analysis-card-title">Market Analysis</h2>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
        {industry && (
          <div className="analysis-block">
            <h3 style={{ fontSize: "0.8rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#FFC72C", marginBottom: "6px" }}>
              Industry
            </h3>
            <p className="analysis-body-text">{renderSafe(industry)}</p>
          </div>
        )}

        {market_opportunity && (
          <div className="analysis-block">
            <h3 style={{ fontSize: "0.8rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#FFC72C", marginBottom: "6px" }}>
              Market Opportunity
            </h3>
            <p className="analysis-body-text">{renderSafe(market_opportunity)}</p>
          </div>
        )}

        {market_trends.length > 0 && (
          <div className="analysis-block">
            <h3 style={{ fontSize: "0.8rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#FFC72C", marginBottom: "6px" }}>
              Market Trends
            </h3>
            <ul className="analysis-list">
              {market_trends.map((trend, i) => (
                <li key={i} style={{ marginBottom: "6px" }}>{renderSafe(trend)}</li>
              ))}
            </ul>
          </div>
        )}

        {growth_drivers.length > 0 && (
          <div className="analysis-block">
            <h3 style={{ fontSize: "0.8rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#34d399", marginBottom: "6px" }}>
              Growth Drivers
            </h3>
            <ul className="analysis-list">
              {growth_drivers.map((driver, i) => (
                <li key={i} style={{ marginBottom: "6px" }}>{renderSafe(driver)}</li>
              ))}
            </ul>
          </div>
        )}

        {market_challenges.length > 0 && (
          <div className="analysis-block">
            <h3 style={{ fontSize: "0.8rem", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.06em", color: "#f87171", marginBottom: "6px" }}>
              Market Challenges
            </h3>
            <ul className="analysis-list">
              {market_challenges.map((challenge, i) => (
                <li key={i} style={{ marginBottom: "6px" }}>{renderSafe(challenge)}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <style>{`
        .market-analysis-card {
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: 14px;
          padding: 24px;
        }
        .analysis-card-title {
          font-size: 1.4rem;
          font-weight: 700;
          margin: 6px 0 0 0;
          color: #f5f1e8;
        }
        .analysis-body-text {
          margin: 0;
          font-size: 0.94rem;
          color: #e6e0d4;
          line-height: 1.6;
        }
        .analysis-list {
          margin: 0;
          padding-left: 18px;
          color: #d1c7b7;
          font-size: 0.88rem;
          line-height: 1.6;
        }

        [data-theme="light"] .market-analysis-card {
          background: #ffffff !important;
          border-color: rgba(0, 0, 0, 0.08) !important;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
        }
        [data-theme="light"] .analysis-card-title {
          color: #18181b !important;
        }
        [data-theme="light"] .analysis-body-text {
          color: #27272a !important;
        }
        [data-theme="light"] .analysis-list {
          color: #3f3f46 !important;
        }
        [data-theme="light"] .analysis-list li {
          color: #3f3f46 !important;
        }
      `}</style>
    </section>
  );
}