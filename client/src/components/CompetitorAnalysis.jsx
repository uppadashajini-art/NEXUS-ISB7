
import React from "react";

/* -------------------------------------------------------
   Utility: Clean website domain
------------------------------------------------------- */
function getCleanDomain(url) {
  if (!url) return null;

  try {
    const parsed = new URL(
      url.startsWith("http") ? url : `https://${url}`
    );

    return parsed.hostname.replace(/^www\./, "");
  } catch {
    return String(url)
      .replace(/^https?:\/\//, "")
      .replace(/^www\./, "")
      .split("/")[0];
  }
}

/* -------------------------------------------------------
   Utility: Normalize values for safe rendering
------------------------------------------------------- */
function displayValue(value, fallback = "Not available in retrieved sources") {
  if (value === null || value === undefined) {
    return fallback;
  }

  if (typeof value === "string" && value.trim() === "") {
    return fallback;
  }

  if (Array.isArray(value)) {
    if (value.length === 0) return fallback;
    return value;
  }

  return value;
}

/* -------------------------------------------------------
   Small information row
------------------------------------------------------- */
function InfoRow({ icon, label, value }) {
  const cleanValue = displayValue(value);

  return (
    <div className="competitor-info-row">
      <div className="competitor-info-label">
        <span className="competitor-info-icon">{icon}</span>
        <span>{label}</span>
      </div>

      <div className="competitor-info-value">
        {Array.isArray(cleanValue) ? (
          <ul className="competitor-info-list">
            {cleanValue.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        ) : (
          <span>{cleanValue}</span>
        )}
      </div>
    </div>
  );
}

/* -------------------------------------------------------
   Feature pills
------------------------------------------------------- */
function FeatureList({ features }) {
  if (!Array.isArray(features) || features.length === 0) {
    return (
      <span className="competitor-muted">
        No capabilities identified in retrieved sources
      </span>
    );
  }

  return (
    <div className="competitor-feature-pills">
      {features.map((feature, index) => (
        <span className="competitor-pill" key={index}>
          {feature}
        </span>
      ))}
    </div>
  );
}

/* -------------------------------------------------------
   Strength / weakness box
------------------------------------------------------- */
function FactorBox({ type, items }) {
  if (!Array.isArray(items) || items.length === 0) {
    return null;
  }

  const isStrength = type === "strength";

  return (
    <div
      className={`factor-box ${
        isStrength ? "strengths-box" : "weaknesses-box"
      }`}
    >
      <div className="factor-header">
        <span
          className={`factor-icon ${
            isStrength ? "strength-icon" : "weakness-icon"
          }`}
        >
          {isStrength ? "✓" : "⚠"}
        </span>

        <span className="factor-title">
          {isStrength ? "STRENGTHS" : "WEAKNESSES & GAPS"}
        </span>
      </div>

      <ul className="factor-list">
        {items.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

/* -------------------------------------------------------
   Competitor card
------------------------------------------------------- */
function CompetitorCard({ competitor, type = "direct" }) {
  const {
    name,
    url,
    website,
    target_customers,
    product_service,
    key_features = [],
    strengths = [],
    weaknesses = [],
    pricing,
    price,
    competitive_advantage,
  } = competitor || {};

  const competitorUrl = url || website;
  const cleanDomain = getCleanDomain(competitorUrl);

  const pricingValue =
    pricing ||
    price ||
    "Not available in retrieved sources";

  return (
    <article className="competitor-card">
      {/* Header */}
      <div className="competitor-card-header">
        <div className="competitor-identity">
          <span className="competitor-avatar">
            {type === "direct" ? "🏢" : "🔄"}
          </span>

          <div>
            <div className="competitor-type-label">
              {type === "direct"
                ? "DIRECT COMPETITOR"
                : "INDIRECT ALTERNATIVE"}
            </div>

            <h3 className="competitor-name">
              {name || "Unnamed competitor"}
            </h3>

            {target_customers && (
              <span className="competitor-target-badge">
                🎯 {target_customers}
              </span>
            )}
          </div>
        </div>

        {cleanDomain && (
          <a
            href={
              competitorUrl.startsWith("http")
                ? competitorUrl
                : `https://${competitorUrl}`
            }
            target="_blank"
            rel="noopener noreferrer"
            className="competitor-domain-link"
          >
            <span>{cleanDomain}</span>
            <span className="link-arrow">↗</span>
          </a>
        )}
      </div>

      {/* Product / Service */}
      {product_service && (
        <div className="competitor-product-section">
          <div className="competitor-section-label">
            WHAT THEY OFFER
          </div>

          <p className="competitor-description">
            {product_service}
          </p>
        </div>
      )}

      {/* Pricing */}
      <div className="competitor-pricing-box">
        <div className="pricing-icon">💰</div>

        <div className="pricing-content">
          <span className="pricing-label">
            PRICING INFORMATION
          </span>

          <strong className="pricing-value">
            {pricingValue}
          </strong>
        </div>
      </div>

      {/* Key information */}
      <div className="competitor-info-section">
        <InfoRow
          icon="🎯"
          label="Target Customers"
          value={target_customers}
        />

        <InfoRow
          icon="💰"
          label="Pricing"
          value={pricingValue}
        />

        {competitive_advantage && (
          <InfoRow
            icon="⭐"
            label="Competitive Advantage"
            value={competitive_advantage}
          />
        )}
      </div>

      {/* Capabilities */}
      <div className="competitor-features-group">
        <span className="feature-group-label">
          KEY CAPABILITIES
        </span>

        <FeatureList features={key_features} />
      </div>

      {/* Strengths and weaknesses */}
      <div className="competitor-factors-grid">
        <FactorBox
          type="strength"
          items={strengths}
        />

        <FactorBox
          type="weakness"
          items={weaknesses}
        />
      </div>
    </article>
  );
}

/* -------------------------------------------------------
   Comparison table
------------------------------------------------------- */
function ComparisonTable({ comparison = [] }) {
  if (!Array.isArray(comparison) || comparison.length === 0) {
    return null;
  }

  return (
    <div className="competitor-comparison-section">
      <div className="comparison-heading">
        <div>
          <span className="card-mini-badge">
            COMPARISON
          </span>

          <h3>Competitor Comparison</h3>

          <p>
            Side-by-side comparison based only on the
            information available in retrieved sources.
          </p>
        </div>
      </div>

      <div className="comparison-table-wrapper">
        <table className="competitor-comparison-table">
          <thead>
            <tr>
              <th>Competitor</th>
              <th>Target Customers</th>
              <th>Product / Service</th>
              <th>Pricing</th>
              <th>Strengths</th>
              <th>Weaknesses</th>
            </tr>
          </thead>

          <tbody>
            {comparison.map((item, index) => {
              const name =
                item.competitor ||
                item.name ||
                "Competitor";

              const target =
                item.target_customers ||
                item.targetCustomers ||
                "Not available";

              const product =
                item.product_service ||
                item.productService ||
                item.product ||
                "Not available";

              const pricing =
                item.pricing ||
                item.price ||
                "Not available in retrieved sources";

              const strengths =
                item.strengths ||
                "Not available";

              const weaknesses =
                item.weaknesses ||
                item.gaps ||
                "Not available";

              return (
                <tr key={index}>
                  <td>
                    <strong>{name}</strong>
                  </td>

                  <td>{target}</td>

                  <td>{product}</td>

                  <td>
                    <span className="comparison-price">
                      💰 {pricing}
                    </span>
                  </td>

                  <td>{strengths}</td>

                  <td>{weaknesses}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* -------------------------------------------------------
   Empty state
------------------------------------------------------- */
function EmptyCompetitorState() {
  return (
    <div className="competitor-empty-state">
      <span className="empty-icon">🔎</span>

      <h3>No commercial competitors identified</h3>

      <p>
        NEXUS could not identify reliable commercial
        competitors from the retrieved web sources.
      </p>
    </div>
  );
}

/* -------------------------------------------------------
   Main Component
------------------------------------------------------- */
export default function CompetitorAnalysis({ data }) {
  if (!data) return null;

  const {
    direct_competitors = [],
    indirect_competitors = [],
    comparison = [],
    market_gaps = [],
  } = data;

  const hasDirectCompetitors =
    Array.isArray(direct_competitors) &&
    direct_competitors.length > 0;

  const hasIndirectCompetitors =
    Array.isArray(indirect_competitors) &&
    indirect_competitors.length > 0;

  const hasComparison =
    Array.isArray(comparison) &&
    comparison.length > 0;

  const hasAnything =
    hasDirectCompetitors ||
    hasIndirectCompetitors ||
    hasComparison;

  if (!hasAnything) {
    return (
      <section className="analysis-card competitor-analysis-card">
        <div className="section-title-wrap">
          <span className="card-mini-badge">
            COMPETITIVE BENCHMARKING
          </span>

          <h2>Commercial Competitor Landscape</h2>
        </div>

        <EmptyCompetitorState />
      </section>
    );
  }

  return (
    <section className="analysis-card competitor-analysis-card">

      {/* Main heading */}
      <div className="section-title-wrap">
        <span className="card-mini-badge">
          COMPETITIVE BENCHMARKING
        </span>

        <h2>Commercial Competitor Landscape</h2>

        <p className="section-description">
          NEXUS identifies businesses solving the same or
          related problem and compares their offerings,
          customers, pricing, strengths, and weaknesses.
        </p>
      </div>

      {/* Summary */}
      <div className="competitor-summary-grid">

        <div className="competitor-summary-item">
          <span className="summary-icon">🏢</span>

          <div>
            <span className="summary-label">
              DIRECT COMPETITORS
            </span>

            <strong className="summary-value">
              {direct_competitors.length}
            </strong>
          </div>
        </div>

        <div className="competitor-summary-item">
          <span className="summary-icon">🔄</span>

          <div>
            <span className="summary-label">
              INDIRECT ALTERNATIVES
            </span>

            <strong className="summary-value">
              {indirect_competitors.length}
            </strong>
          </div>
        </div>

        <div className="competitor-summary-item">
          <span className="summary-icon">📊</span>

          <div>
            <span className="summary-label">
              COMPARISON RECORDS
            </span>

            <strong className="summary-value">
              {comparison.length}
            </strong>
          </div>
        </div>
      </div>

      {/* Direct competitors */}
      {hasDirectCompetitors && (
        <div className="competitor-group">

          <div className="group-heading-row">
            <div>
              <span className="group-kicker">
                SAME CORE PROBLEM
              </span>

              <h3>Direct Competitors</h3>
            </div>

            <span className="group-counter-pill">
              {direct_competitors.length}{" "}
              {direct_competitors.length === 1
                ? "Company"
                : "Companies"}
            </span>
          </div>

          <div className="competitors-list">
            {direct_competitors.map((competitor, index) => (
              <CompetitorCard
                competitor={competitor}
                type="direct"
                key={`direct-${index}`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Indirect competitors */}
      {hasIndirectCompetitors && (
        <div className="competitor-group">

          <div className="group-heading-row">
            <div>
              <span className="group-kicker">
                ALTERNATIVE SOLUTIONS
              </span>

              <h3>
                Indirect Alternatives & Legacy Methods
              </h3>
            </div>

            <span className="group-counter-pill">
              {indirect_competitors.length}{" "}
              {indirect_competitors.length === 1
                ? "Alternative"
                : "Alternatives"}
            </span>
          </div>

          <div className="competitors-list">
            {indirect_competitors.map((competitor, index) => (
              <CompetitorCard
                competitor={competitor}
                type="indirect"
                key={`indirect-${index}`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Comparison */}
      {hasComparison && (
        <ComparisonTable comparison={comparison} />
      )}

      {/* Market gap connection */}
      {Array.isArray(market_gaps) &&
        market_gaps.length > 0 && (
          <div className="competitor-insight-box">
            <div className="competitor-insight-header">
              <span className="insight-icon">💡</span>

              <div>
                <span className="insight-kicker">
                  COMPETITIVE INSIGHT
                </span>

                <h3>
                  Opportunities identified from the
                  competitor landscape
                </h3>
              </div>
            </div>

            <div className="competitor-insight-list">
              {market_gaps.slice(0, 4).map((gap, index) => (
                <div
                  className="competitor-insight-item"
                  key={index}
                >
                  <span className="insight-number">
                    {String(index + 1).padStart(2, "0")}
                  </span>

                  <p>{gap}</p>
                </div>
              ))}
            </div>
          </div>
        )}

      {/* Disclaimer */}
      <div className="competitor-disclaimer">
        <span>ⓘ</span>

        <p>
          Competitor information is based on the web
          sources retrieved during validation. Pricing and
          other details may be unavailable or change over
          time. Verify important business information
          directly with the competitor before making
          decisions.
        </p>
      </div>
    </section>
  );
}
