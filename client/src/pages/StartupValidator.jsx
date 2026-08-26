import { useState } from "react";
import IdeaInput from "../components/IdeaInput";
import SearchResultCard from "../components/SearchResultCard";
import { searchStartupIdea } from "../services/api";

function StartupValidator() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleIdeaSubmit = async (idea) => {
    console.log("Startup idea:", idea);

    setLoading(true);
    setError("");
    setResults([]);

    try {
      const data = await searchStartupIdea(idea);

      console.log("Backend response:", data);

      setResults(data.results || []);
    } catch (err) {
      console.error("Search error:", err);

      setError(
        err.message || "Unable to validate the startup idea."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="startup-validator">

      {/* Hero Section */}
      <section className="hero">
        <h1>AI Startup Idea Validator</h1>

        <p>
          Validate your startup idea using real-time web search
          information.
        </p>
      </section>

      {/* Idea Input */}
      <section className="input-section">
        <IdeaInput
          onSubmit={handleIdeaSubmit}
          loading={loading}
        />
      </section>

      {/* Loading */}
      {loading && (
        <section className="loading-section">
          <p>Searching the web for your startup idea...</p>
        </section>
      )}

      {/* Error */}
      {error && (
        <section className="error-section">
          <p>{error}</p>
        </section>
      )}

      {/* Results */}
      {results.length > 0 && (
        <section className="results-section">
          <h2>Web Search Results</h2>

          <div className="results-list">
            {results.map((result, index) => (
              <SearchResultCard
                key={`${result.url || "result"}-${index}`}
                result={result}
              />
            ))}
          </div>
        </section>
      )}

      {/* No Results */}
      {!loading &&
        !error &&
        results.length === 0 && (
          <section className="empty-results">
            <p>
              Enter your startup idea and click
              <strong> Validate Idea </strong>
              to search for relevant market information.
            </p>
          </section>
        )}

    </main>
  );
}

export default StartupValidator;