function SearchResultCard({ result }) {
  if (!result) {
    return null;
  }

  return (
    <article className="search-result-card">

      {/* =========================================
          STATUS
      ========================================= */}
      <div className="status-badge">
        Web Research Source
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