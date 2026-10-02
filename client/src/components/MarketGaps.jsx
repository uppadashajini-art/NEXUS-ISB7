import React from "react";

export default function MarketGaps({ gaps }) {
  if (!gaps || gaps.length === 0) return null;

  return (
    <section className="analysis-card market-gaps-card">
      <div className="section-title-wrap">
        <span className="card-mini-badge">WHITE-SPACE OPPORTUNITIES</span>
        <h2>Market Gaps & Unserved Needs</h2>
      </div>

      <div className="market-gaps-grid">
        {gaps.map((gap, i) => (
          <div key={i} className="gap-card">
            <div className="gap-badge">
              <span className="gap-icon">✦</span>
              <span className="gap-num">GAP 0{i + 1}</span>
            </div>
            <p className="gap-text">{gap}</p>
          </div>
        ))}
      </div>
    </section>
  );
}