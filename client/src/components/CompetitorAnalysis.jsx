import React from "react";

function getCleanDomain(url) {
  if (!url) return null;
  try {
    const parsed = new URL(url.startsWith("http") ? url : `https://${url}`);
    return parsed.hostname.replace(/^www\./, "");
  } catch {
    return url.replace(/^https?:\/\/(?:www\.)?/, "").split("/")[0];
  }
}

function CompetitorCard({ competitor }) {
  const {
    name,
    url,
    target_customers,
    product_service,
    key_features = [],
    strengths = [],
    weaknesses = [],
  } = competitor;

  const cleanDomain = getCleanDomain(url);

  return (
    <div className="competitor-card">
      <div className="competitor-card-header">
        <div className="competitor-identity">
          <span className="competitor-avatar">🏢</span>
          <div>
            <h3 className="competitor-name">{name}</h3>
            {target_customers && (
              <span className="competitor-target-badge">
                🎯 {target_customers}
              </span>
            )}
          </div>
        </div>

        {cleanDomain && (
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="competitor-domain-link"
          >
            <span>{cleanDomain}</span>
            <span className="link-arrow">↗</span>
          </a>
        )}
      </div>

      {product_service && (
        <p className="competitor-description">{product_service}</p>
      )}

      {key_features.length > 0 && (
        <div className="competitor-features-group">
          <span className="feature-group-label">KEY CAPABILITIES</span>
          <div className="competitor-feature-pills">
            {key_features.map((f, i) => (
              <span key={i} className="competitor-pill">
                {f}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="competitor-factors-grid">
        {strengths.length > 0 && (
          <div className="factor-box strengths-box">
            <div className="factor-header">
              <span className="factor-icon strength-icon">✓</span>
              <span className="factor-title">STRENGTHS</span>
            </div>
            <ul className="factor-list">
              {strengths.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
        )}

        {weaknesses.length > 0 && (
          <div className="factor-box weaknesses-box">
            <div className="factor-header">
              <span className="factor-icon weakness-icon">⚠</span>
              <span className="factor-title">WEAKNESSES & GAPS</span>
            </div>
            <ul className="factor-list">
              {weaknesses.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default function CompetitorAnalysis({ data }) {
  if (!data) return null;

  const { direct_competitors = [], indirect_competitors = [] } = data;

  if (direct_competitors.length === 0 && indirect_competitors.length === 0) {
    return null;
  }

  return (
    <section className="analysis-card competitor-analysis-card">
      <div className="section-title-wrap">
        <span className="card-mini-badge">COMPETITIVE BENCHMARKING</span>
        <h2>Commercial Competitor Landscape</h2>
      </div>

      {direct_competitors.length > 0 && (
        <div className="competitor-group">
          <div className="group-heading-row">
            <h3>Direct Competitors</h3>
            <span className="group-counter-pill">
              {direct_competitors.length} Companies
            </span>
          </div>
          <div className="competitors-list">
            {direct_competitors.map((c, i) => (
              <CompetitorCard competitor={c} key={i} />
            ))}
          </div>
        </div>
      )}

      {indirect_competitors.length > 0 && (
        <div className="competitor-group">
          <div className="group-heading-row">
            <h3>Indirect Alternatives & Legacy Methods</h3>
            <span className="group-counter-pill">
              {indirect_competitors.length} Alternatives
            </span>
          </div>
          <div className="competitors-list">
            {indirect_competitors.map((c, i) => (
              <CompetitorCard competitor={c} key={i} />
            ))}
          </div>
        </div>
      )}
    </section>
  );
}