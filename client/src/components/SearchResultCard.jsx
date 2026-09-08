function SearchResultCard({
  result,
  targetCustomer,
  validationType = "all",
}) {
  if (!result) {
    return null;
  }

  const userTargetCustomer =
    targetCustomer?.trim() || "General Users";

  // -----------------------------------------
  // Detect a simple research category
  // -----------------------------------------
  const text = `
    ${result.title || ""}
    ${result.content || ""}
    ${result.description || ""}
  `.toLowerCase();

  let category = "MARKET SIGNAL";
  let categoryIcon = "📈";

  if (
    text.includes("competitor") ||
    text.includes("competition") ||
    text.includes("market share") ||
    text.includes("alternative")
  ) {
    category = "COMPETITION";
    categoryIcon = "🏢";
  } else if (
    text.includes("customer") ||
    text.includes("consumer") ||
    text.includes("user") ||
    text.includes("buyer")
  ) {
    category = "CUSTOMER INSIGHT";
    categoryIcon = "👥";
  } else if (
    text.includes("revenue") ||
    text.includes("pricing") ||
    text.includes("subscription") ||
    text.includes("profit") ||
    text.includes("monetization")
  ) {
    category = "BUSINESS POTENTIAL";
    categoryIcon = "💰";
  } else if (
    text.includes("risk") ||
    text.includes("challenge") ||
    text.includes("privacy") ||
    text.includes("regulation")
  ) {
    category = "RISK SIGNAL";
    categoryIcon = "⚠️";
  }

  // -----------------------------------------
  // Get content
  // -----------------------------------------
  const rawContent =
    result.content ||
    result.description ||
    "No additional information was provided for this source.";

  // -----------------------------------------
  // Create a short readable summary
  // -----------------------------------------
  const cleanContent = rawContent
    .replace(/\s+/g, " ")
    .replace(/\[\.\.\.\]/g, "")
    .trim();

  const summary =
    cleanContent.length > 260
      ? `${cleanContent.substring(0, 260).trim()}...`
      : cleanContent;

  // -----------------------------------------
  // Extract useful metric
  // -----------------------------------------
  const metricPatterns = [
    /\$[\d,.]+\s*(?:billion|million|trillion)?/i,
    /\d+(?:\.\d+)?%\s*(?:CAGR|growth)?/i,
    /\d+(?:\.\d+)?%\s*CAGR/i,
    /USD\s*[\d,.]+\s*(?:billion|million|trillion)?/i,
  ];

  let metric = null;

  for (const pattern of metricPatterns) {
    const match = cleanContent.match(pattern);

    if (match) {
      metric = match[0];
      break;
    }
  }

  // -----------------------------------------
  // Key insight
  // -----------------------------------------
  let keyInsight =
    "This research provides useful market intelligence for evaluating the startup opportunity.";

  if (
    text.includes("growth") ||
    text.includes("cagr") ||
    text.includes("forecast") ||
    text.includes("projected")
  ) {
    keyInsight =
      "The research indicates measurable market growth, supporting further validation of the opportunity.";
  } else if (
    text.includes("competitor") ||
    text.includes("competition") ||
    text.includes("market share")
  ) {
    keyInsight =
      "The research highlights an existing competitive landscape that should be considered when positioning the product.";
  } else if (
    text.includes("customer") ||
    text.includes("consumer") ||
    text.includes("user")
  ) {
    keyInsight =
      "The research provides signals about customer needs and behavior relevant to the proposed product.";
  } else if (
    text.includes("pricing") ||
    text.includes("subscription") ||
    text.includes("revenue")
  ) {
    keyInsight =
      "The research reveals potential pricing and monetization patterns that can inform the business model.";
  } else if (
    text.includes("risk") ||
    text.includes("challenge") ||
    text.includes("privacy")
  ) {
    keyInsight =
      "The research identifies factors that may create challenges or risks for the startup.";
  }

  return (
    <article className="search-result-card">

      {/* =========================================
          CARD HEADER
      ========================================= */}
      <div className="search-card-header">

        <div className="research-category">
          <span className="category-icon">
            {categoryIcon}
          </span>

          <span>
            {category}
          </span>
        </div>

        <span className="source-badge">
          WEB SOURCE
        </span>

      </div>

      {/* =========================================
          TITLE
      ========================================= */}
      <h3 className="search-result-title">
        {result.title ||
          "Untitled Research Result"}
      </h3>

      {/* =========================================
          SUMMARY
      ========================================= */}
      <p className="search-result-summary">
        {summary}
      </p>

      {/* =========================================
          TARGET CUSTOMER
      ========================================= */}
      <div className="target-customer-box">

        <span className="target-customer-icon">
          👥
        </span>

        <div>
          <span className="target-customer-label">
            TARGET
          </span>

          <strong>
            {userTargetCustomer}
          </strong>
        </div>

      </div>

      {/* =========================================
          KEY INSIGHT
      ========================================= */}
      <div className="key-insight-box">

        <div className="key-insight-label">
          <span>💡</span>
          KEY INSIGHT
        </div>

        <p>
          {keyInsight}
        </p>

      </div>

      {/* =========================================
          CARD FOOTER
      ========================================= */}
      <div className="search-card-footer">

        {metric ? (
          <div className="research-metric">
            <span>
              SIGNAL
            </span>

            <strong>
              {metric}
            </strong>
          </div>
        ) : (
          <div className="research-metric">
            <span>
              SIGNAL
            </span>

            <strong>
              RELEVANT
            </strong>
          </div>
        )}

        {result.url && (
          <a
            href={result.url}
            target="_blank"
            rel="noopener noreferrer"
            className="source-link"
          >
            View Source
            <span>→</span>
          </a>
        )}

      </div>

    </article>
  );
}

export default SearchResultCard;