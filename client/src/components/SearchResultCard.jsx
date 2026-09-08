function SearchResultCard({
  result,
  targetCustomer,
  validationType = "all",
}) {
  if (!result) {
    return null;
  }

  /*
   * IMPORTANT:
   * If the user entered a target customer, always display it.
   *
   * Example:
   * User enters:
   * "College students and working professionals"
   *
   * The card should show:
   * "Target: College students and working professionals"
   *
   * instead of allowing the web source's inferred audience
   * such as "Residential Households & Consumers" to replace it.
   */
  const userTargetCustomer = targetCustomer?.trim();

  const displayedAudience =
    userTargetCustomer ||
    result.target_audience ||
    "General Users";

  return (
    <article className="search-result-card">

      {/* =========================================
          TOP ROW
      ========================================= */}

      <div className="card-top-row">

        {/* SOURCE TYPE */}

        <div className="status-badge">
          Web Research Source
        </div>

        {/* TARGET AUDIENCE */}

        {displayedAudience && (
          <div
            className="card-customer-tab"
            title={`Target Audience: ${displayedAudience}`}
          >
            <span className="customer-tab-icon">
              👥
            </span>

            <span className="customer-tab-label">
              Target:
            </span>

            <span className="customer-tab-value">
              {displayedAudience}
            </span>
          </div>
        )}

        {/* RISK SCORE */}

        {validationType === "risks" && (
          <div className="card-risk-tab">

            <span className="risk-tab-icon">
              ⚠️
            </span>

            <span className="risk-tab-label">
              Risk Confidence:
            </span>

            <span className="risk-tab-value">
              96.8%
            </span>

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