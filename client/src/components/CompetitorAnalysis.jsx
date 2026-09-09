
import React from "react";

/* =====================================================
   Utility: Clean website domain
===================================================== */

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

/* =====================================================
   Utility: Normalize values for safe rendering
===================================================== */

function displayValue(
  value,
  fallback = "Not available in retrieved sources"
) {
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

/* =====================================================
   Utility: Convert values to comparable text
===================================================== */

function normalizeText(value) {
  if (!value) return "";

  return String(value)
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ");
}

/* =====================================================
   Utility: Find competitor matching comparison row
===================================================== */

function findMatchingCompetitor(name, competitors = []) {
  const normalizedName = normalizeText(name);

  if (!normalizedName) return null;

  return (
    competitors.find((competitor) => {
      const competitorName = normalizeText(competitor?.name);

      return (
        competitorName === normalizedName ||
        competitorName.includes(normalizedName) ||
        normalizedName.includes(competitorName)
      );
    }) || null
  );
}

/* =====================================================
   Utility: Get first usable value
===================================================== */

function firstAvailable(...values) {
  for (const value of values) {
    if (value === null || value === undefined) continue;

    if (typeof value === "string" && value.trim() === "") {
      continue;
    }

    if (Array.isArray(value) && value.length === 0) {
      continue;
    }

    return value;
  }

  return null;
}

/* =====================================================
   Small information row
===================================================== */

function InfoRow({ icon, label, value }) {
  const cleanValue = displayValue(value);

  return (
    <div className="competitor-info-row">
      <div className="competitor-info-label">
        <span className="competitor-info-icon">
          {icon}
        </span>

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

/* =====================================================
   Feature pills
===================================================== */

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
        <span
          className="competitor-pill"
          key={index}
        >
          {feature}
        </span>
      ))}
    </div>
  );
}

/* =====================================================
   Strength / weakness box
===================================================== */

function FactorBox({ type, items }) {
  if (!Array.isArray(items) || items.length === 0) {
    return null;
  }

  const isStrength = type === "strength";

  return (
    <div
      className={`factor-box ${
        isStrength
          ? "strengths-box"
          : "weaknesses-box"
      }`}
    >
      <div className="factor-header">
        <span
          className={`factor-icon ${
            isStrength
              ? "strength-icon"
              : "weakness-icon"
          }`}
        >
          {isStrength ? "✓" : "⚠"}
        </span>

        <span className="factor-title">
          {isStrength
            ? "STRENGTHS"
            : "WEAKNESSES & GAPS"}
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

/* =====================================================
   Competitor card
===================================================== */

function CompetitorCard({
  competitor,
  type = "direct",
}) {
  const {
    name,
    url,
    website,

    target_customers,
    targetCustomers,

    product_service,
    productService,
    product,
    service,

    key_features = [],
    keyFeatures = [],

    strengths = [],
    weaknesses = [],

    pricing,
    price,

    competitive_advantage,
    competitiveAdvantage,
  } = competitor || {};

  const competitorUrl = url || website;

  const cleanDomain =
    getCleanDomain(competitorUrl);

  const targetCustomersValue = firstAvailable(
    target_customers,
    targetCustomers
  );

  const productServiceValue = firstAvailable(
    product_service,
    productService,
    product,
    service
  );

  const featuresValue =
    Array.isArray(key_features) &&
    key_features.length > 0
      ? key_features
      : keyFeatures;

  const pricingValue =
    firstAvailable(pricing, price) ||
    "Not available in retrieved sources";

  const strengthsValue = Array.isArray(strengths)
    ? strengths
    : [];

  const weaknessesValue = Array.isArray(
    weaknesses
  )
    ? weaknesses
    : [];

  const competitiveAdvantageValue =
    firstAvailable(
      competitive_advantage,
      competitiveAdvantage
    );

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

            {targetCustomersValue && (
              <span className="competitor-target-badge">
                🎯 {targetCustomersValue}
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
            <span className="link-arrow">
              ↗
            </span>
          </a>
        )}
      </div>

      {/* Product / Service */}
      {productServiceValue && (
        <div className="competitor-product-section">
          <div className="competitor-section-label">
            WHAT THEY OFFER
          </div>

          <p className="competitor-description">
            {productServiceValue}
          </p>
        </div>
      )}

      {/* Pricing */}
      <div className="competitor-pricing-box">
        <div className="pricing-icon">
          💰
        </div>

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
          value={targetCustomersValue}
        />

        <InfoRow
          icon="💰"
          label="Pricing"
          value={pricingValue}
        />

        {competitiveAdvantageValue && (
          <InfoRow
            icon="⭐"
            label="Competitive Advantage"
            value={competitiveAdvantageValue}
          />
        )}
      </div>

      {/* Capabilities */}
      <div className="competitor-features-group">
        <span className="feature-group-label">
          KEY CAPABILITIES
        </span>

        <FeatureList
          features={featuresValue}
        />
      </div>

      {/* Strengths and weaknesses */}
      <div className="competitor-factors-grid">

        <FactorBox
          type="strength"
          items={strengthsValue}
        />

        <FactorBox
          type="weakness"
          items={weaknessesValue}
        />

      </div>
    </article>
  );
}

/* =====================================================
   Comparison table
===================================================== */

function ComparisonTable({
  comparison = [],
  competitors = [],
}) {
  if (
    !Array.isArray(comparison) ||
    comparison.length === 0
  ) {
    return null;
  }

  return (
    <div className="competitor-comparison-section">

      <div className="comparison-heading">
        <div>
          <span className="card-mini-badge">
            COMPARISON
          </span>

          <h3>
            Competitor Comparison
          </h3>

          <p>
            Side-by-side comparison based only
            on the information available in
            retrieved sources.
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
                firstAvailable(
                  item?.competitor,
                  item?.name
                ) ||
                "Competitor";

              /*
                Find the same competitor from
                direct/indirect competitor arrays.

                This is the important fix:
                the comparison table can now use
                information already displayed
                correctly in the competitor cards.
              */
              const matchedCompetitor =
                findMatchingCompetitor(
                  name,
                  competitors
                );

              /* -----------------------------
                 TARGET CUSTOMERS
              ----------------------------- */

              const target =
                firstAvailable(
                  item?.target_customers,
                  item?.targetCustomers,

                  matchedCompetitor?.target_customers,
                  matchedCompetitor?.targetCustomers
                ) ||
                "Not available";

              /* -----------------------------
                 PRODUCT / SERVICE
              ----------------------------- */

              const product =
                firstAvailable(
                  item?.product_service,
                  item?.productService,
                  item?.product,
                  item?.service,

                  matchedCompetitor?.product_service,
                  matchedCompetitor?.productService,
                  matchedCompetitor?.product,
                  matchedCompetitor?.service
                ) ||
                "Not available";

              /* -----------------------------
                 PRICING
              ----------------------------- */

              const pricing =
                firstAvailable(
                  item?.pricing,
                  item?.price,

                  matchedCompetitor?.pricing,
                  matchedCompetitor?.price
                ) ||
                "Not available in retrieved sources";

              /* -----------------------------
                 STRENGTHS
              ----------------------------- */

              const strengths =
                firstAvailable(
                  item?.strengths,
                  matchedCompetitor?.strengths
                ) ||
                "Not available";

              /* -----------------------------
                 WEAKNESSES
              ----------------------------- */

              const weaknesses =
                firstAvailable(
                  item?.weaknesses,
                  item?.gaps,

                  matchedCompetitor?.weaknesses,
                  matchedCompetitor?.gaps
                ) ||
                "Not available";

              return (
                <tr
                  key={`${name}-${index}`}
                >

                  <td>
                    <strong>
                      {name}
                    </strong>
                  </td>

                  <td>
                    {Array.isArray(target)
                      ? target.join(", ")
                      : target}
                  </td>

                  <td>
                    {Array.isArray(product)
                      ? product.join(", ")
                      : product}
                  </td>

                  <td>
                    <span className="comparison-price">
                      💰 {pricing}
                    </span>
                  </td>

                  <td>
                    {Array.isArray(strengths)
                      ? strengths.join("; ")
                      : strengths}
                  </td>

                  <td>
                    {Array.isArray(weaknesses)
                      ? weaknesses.join("; ")
                      : weaknesses}
                  </td>

                </tr>
              );
            })}

          </tbody>
        </table>
      </div>
    </div>
  );
}

/* =====================================================
   Empty state
===================================================== */

function EmptyCompetitorState() {
  return (
    <div className="competitor-empty-state">

      <span className="empty-icon">
        🔎
      </span>

      <h3>
        No commercial competitors identified
      </h3>

      <p>
        NEXUS could not identify reliable
        commercial competitors from the
        retrieved web sources.
      </p>

    </div>
  );
}

/* =====================================================
   Main Component
===================================================== */

export default function CompetitorAnalysis({
  data,
}) {
  if (!data) return null;

  const {
    direct_competitors = [],
    indirect_competitors = [],
    comparison = [],
    market_gaps = [],
  } = data;

  /* =================================================
     Competitor arrays
  ================================================= */

  const safeDirectCompetitors =
    Array.isArray(direct_competitors)
      ? direct_competitors
      : [];

  const safeIndirectCompetitors =
    Array.isArray(indirect_competitors)
      ? indirect_competitors
      : [];

  const safeComparison =
    Array.isArray(comparison)
      ? comparison
      : [];

  const safeMarketGaps =
    Array.isArray(market_gaps)
      ? market_gaps
      : [];

  /*
    Combine both lists.

    Used by the comparison table to find
    the original competitor data.
  */
  const allCompetitors = [
    ...safeDirectCompetitors,
    ...safeIndirectCompetitors,
  ];

  /* =================================================
     State checks
  ================================================= */

  const hasDirectCompetitors =
    safeDirectCompetitors.length > 0;

  const hasIndirectCompetitors =
    safeIndirectCompetitors.length > 0;

  const hasComparison =
    safeComparison.length > 0;

  const hasAnything =
    hasDirectCompetitors ||
    hasIndirectCompetitors ||
    hasComparison;

  /* =================================================
     Empty state
  ================================================= */

  if (!hasAnything) {
    return (
      <section className="analysis-card competitor-analysis-card">

        <div className="section-title-wrap">

          <span className="card-mini-badge">
            COMPETITIVE BENCHMARKING
          </span>

          <h2>
            Commercial Competitor Landscape
          </h2>

        </div>

        <EmptyCompetitorState />

      </section>
    );
  }

  /* =================================================
     Main render
  ================================================= */

  return (
    <section className="analysis-card competitor-analysis-card">

      {/* Main heading */}

      <div className="section-title-wrap">

        <span className="card-mini-badge">
          COMPETITIVE BENCHMARKING
        </span>

        <h2>
          Commercial Competitor Landscape
        </h2>

        <p className="section-description">
          NEXUS identifies businesses solving
          the same or related problem and
          compares their offerings, customers,
          pricing, strengths, and weaknesses.
        </p>

      </div>

      {/* =================================================
          Summary
      ================================================= */}

      <div className="competitor-summary-grid">

        <div className="competitor-summary-item">

          <span className="summary-icon">
            🏢
          </span>

          <div>

            <span className="summary-label">
              DIRECT COMPETITORS
            </span>

            <strong className="summary-value">
              {safeDirectCompetitors.length}
            </strong>

          </div>

        </div>

        <div className="competitor-summary-item">

          <span className="summary-icon">
            🔄
          </span>

          <div>

            <span className="summary-label">
              INDIRECT ALTERNATIVES
            </span>

            <strong className="summary-value">
              {safeIndirectCompetitors.length}
            </strong>

          </div>

        </div>

        <div className="competitor-summary-item">

          <span className="summary-icon">
            📊
          </span>

          <div>

            <span className="summary-label">
              COMPARISON RECORDS
            </span>

            <strong className="summary-value">
              {safeComparison.length}
            </strong>

          </div>

        </div>

      </div>

      {/* =================================================
          Direct competitors
      ================================================= */}

      {hasDirectCompetitors && (
        <div className="competitor-group">

          <div className="group-heading-row">

            <div>

              <span className="group-kicker">
                SAME CORE PROBLEM
              </span>

              <h3>
                Direct Competitors
              </h3>

            </div>

            <span className="group-counter-pill">

              {safeDirectCompetitors.length}{" "}

              {safeDirectCompetitors.length === 1
                ? "Company"
                : "Companies"}

            </span>

          </div>

          <div className="competitors-list">

            {safeDirectCompetitors.map(
              (competitor, index) => (
                <CompetitorCard
                  competitor={competitor}
                  type="direct"
                  key={`direct-${index}`}
                />
              )
            )}

          </div>

        </div>
      )}

      {/* =================================================
          Indirect competitors
      ================================================= */}

      {hasIndirectCompetitors && (
        <div className="competitor-group">

          <div className="group-heading-row">

            <div>

              <span className="group-kicker">
                ALTERNATIVE SOLUTIONS
              </span>

              <h3>
                Indirect Alternatives & Legacy
                Methods
              </h3>

            </div>

            <span className="group-counter-pill">

              {safeIndirectCompetitors.length}{" "}

              {safeIndirectCompetitors.length === 1
                ? "Alternative"
                : "Alternatives"}

            </span>

          </div>

          <div className="competitors-list">

            {safeIndirectCompetitors.map(
              (competitor, index) => (
                <CompetitorCard
                  competitor={competitor}
                  type="indirect"
                  key={`indirect-${index}`}
                />
              )
            )}

          </div>

        </div>
      )}

      {/* =================================================
          Comparison
      ================================================= */}

      {hasComparison && (
        <ComparisonTable
          comparison={safeComparison}
          competitors={allCompetitors}
        />
      )}

      {/* =================================================
          Competitive insights
      ================================================= */}

      {safeMarketGaps.length > 0 && (
        <div className="competitor-insight-box">

          <div className="competitor-insight-header">

            <span className="insight-icon">
              💡
            </span>

            <div>

              <span className="insight-kicker">
                COMPETITIVE INSIGHT
              </span>

              <h3>
                Opportunities identified from
                the competitor landscape
              </h3>

            </div>

          </div>

          <div className="competitor-insight-list">

            {safeMarketGaps
              .slice(0, 4)
              .map((gap, index) => (

                <div
                  className="competitor-insight-item"
                  key={index}
                >

                  <span className="insight-number">
                    {String(index + 1).padStart(
                      2,
                      "0"
                    )}
                  </span>

                  <p>
                    {gap}
                  </p>

                </div>

              ))}

          </div>

        </div>
      )}

      {/* =================================================
          Disclaimer
      ================================================= */}

      <div className="competitor-disclaimer">

        <span>
          ⓘ
        </span>

        <p>
          Competitor information is based on
          the web sources retrieved during
          validation. Pricing and other details
          may be unavailable or change over
          time. Verify important business
          information directly with the
          competitor before making decisions.
        </p>

      </div>

    </section>
  );
}
