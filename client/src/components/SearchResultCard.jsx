function SearchResultCard({ result }) {
  return (
    <article className="search-result-card">
      <h3>{result.title}</h3>

      <p>{result.content}</p>

      {result.url && (
        <a
          href={result.url}
          target="_blank"
          rel="noopener noreferrer"
        >
          View Source
        </a>
      )}
    </article>
  );
}

export default SearchResultCard;