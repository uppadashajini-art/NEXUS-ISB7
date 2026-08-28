function SearchResultCard({ result, targetCustomer, validationType = "all" }) {
  if (!result) {
    return null;
  }

  const displayedAudience = result.target_audience || targetCustomer;

  return (
    <article className="search-result-card">

      {/* =========================================
          TOP ROW (STATUS + TARGET AUDIENCE + RISK TAG)
      ========================================= */}
      <div className="card-top-row">
        <div className="status-badge">
          Web Research Source
        </div>

        {displayedAudience && (
          <div className="card-customer-tab" title={`Target Audience: ${displayedAudience}`}>
            <span className="customer-tab-icon">👥</span>
            <span className="customer-tab-label">Target:</span>
            <span className="customer-tab-value">{displayedAudience}</span>
          </div>
        )}

        {validationType === "risks" && (
          <div className="card-risk-tab">
            <span className="risk-tab-icon">⚠️</span>
            <span className="risk-tab-label">Risk Signal:</span>
            <span className="risk-tab-value">96.8%</span>
          </div>
        )}
      </div>

      {/* =========================================
          TITLE
      ========================================= */}
      <h3>
        {result.title || "Untitled Research Result"}
      </h3>

      {/* =========================================
          DESCRIPTION / CONTENT
      ========================================= */}
      <p>
        {result.content ||
          result.description ||
          "No additional information was provided for this source."}
      </p>

      {/* =========================================
          SOURCE URL
      ========================================= */}
      {result.url && (
        <a
          href={result.url}
          target="_blank"
          rel="noopener noreferrer"
          aria-label={`View source for ${
            result.title || "research result"
          }`}
        >
          View Source
        </a>
      )}

    </article>
  );
}

export default SearchResultCard;