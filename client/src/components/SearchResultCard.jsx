function SearchResultCard({
  result,
  targetCustomer,
  validationType = "all",
}) {
  if (!result) {
    return null;
  }

  const userTargetCustomer =
    result?.target_audience?.trim() ||
    targetCustomer?.trim() ||
    "Target Industry Buyers";

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
  // Extract useful metric / substantive signal
  // -----------------------------------------
  const metricPatterns = [
    /\$[\d,.]+\s*(?:billion|million|trillion)/i,
    /\d+(?:\.\d+)?%\s*(?:CAGR|growth|increase|share|market)/i,
    /\d+(?:\.\d+)?%\s*CAGR/i,
    /USD\s*[\d,.]+\s*(?:billion|million|trillion)/i,
  ];

  let metric = null;

  for (const pattern of metricPatterns) {
    const match = cleanContent.match(pattern);
    if (match) {
      metric = match[0];
      break;
    }
  }

  let signalBadge = metric;
  if (!signalBadge) {
    if (category === "COMPETITION") signalBadge = "COMPETITOR BENCHMARK";
    else if (category === "CUSTOMER INSIGHT") signalBadge = "WORKFLOW PAIN POINT";
    else if (category === "BUSINESS POTENTIAL") signalBadge = "MONETIZATION SIGNAL";
    else if (category === "RISK SIGNAL") signalBadge = "RISK FACTOR";
    else signalBadge = "GROWTH PROJECTION";
  }

  // -----------------------------------------
  // Key insight synthesis (Dynamic sentence extraction)
  // -----------------------------------------
  let keyInsight = "";

  const sentences = cleanContent.split(/(?<=[.!?])\s+/).filter(s => s.trim().length > 20);
  const relevantSentence = sentences.find(s => {
    const sLower = s.toLowerCase();
    return sLower.includes("growth") || sLower.includes("competitor") || sLower.includes("market") ||
           sLower.includes("platform") || sLower.includes("demand") || sLower.includes("user") ||
           sLower.includes("tool") || sLower.includes("pricing") || sLower.includes("trend");
  });

  if (relevantSentence) {
    keyInsight = relevantSentence.trim();
    if (keyInsight.length > 180) {
      keyInsight = `${keyInsight.substring(0, 180).trim()}...`;
    }
  } else if (sentences.length > 0) {
    keyInsight = sentences[0].trim();
  } else {
    keyInsight = "Identified grounded web research evidence relevant to evaluating product positioning and market demand.";
  }

  return (
    <article className="search-result-card">

      {/* =========================================
          CARD HEADER
      ========================================= */}
      <div className="search-card-header">
        <div className="research-category-badge">
          <span className="category-icon">{categoryIcon}</span>
          <span className="category-text">{category}</span>
        </div>

        <span className="source-type-pill">
          <span className="source-dot"></span>
          WEB SOURCE
        </span>
      </div>

      {/* =========================================
          TITLE
      ========================================= */}
      <h3 className="search-result-title">
        {result.title || "Untitled Research Result"}
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
        <div className="target-customer-tag">
          <span className="target-customer-icon">👥</span>
          <span className="target-customer-label">TARGET AUDIENCE</span>
        </div>

        <span className="target-customer-value">
          {userTargetCustomer}
        </span>
      </div>

      {/* =========================================
          KEY INSIGHT
      ========================================= */}
      <div className="key-insight-box">
        <div className="key-insight-header">
          <span className="key-insight-icon">💡</span>
          <span className="key-insight-title">KEY INSIGHT</span>
        </div>

        <p className="key-insight-text">
          {keyInsight}
        </p>
      </div>

      {/* =========================================
          CARD FOOTER
      ========================================= */}
      <div className="search-card-footer">
        <div className="signal-metric-box">
          <span className="signal-label">SIGNAL</span>
          <strong className="signal-value">{signalBadge}</strong>
        </div>

        {result.url && (
          <a
            href={result.url}
            target="_blank"
            rel="noopener noreferrer"
            className="source-action-btn"
          >
            <span>View Source</span>
            <span className="arrow-icon">→</span>
          </a>
        )}
      </div>

    </article>
  );
}

export default SearchResultCard;