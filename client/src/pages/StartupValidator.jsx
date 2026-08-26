import { useState } from "react";
import IdeaInput from "../components/IdeaInput";
import SearchResultCard from "../components/SearchResultCard";

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
      const response = await fetch("http://localhost:8000/api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          idea: idea,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to validate startup idea.");
      }

      setResults(data.results || []);
    } catch (err) {
      console.error("Search error:", err);
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="startup-validator">
      <section className="hero">
        <h1>AI Startup Idea Validator</h1>

        <p>
          Validate your startup idea using real-time web search
          information.
        </p>
      </section>

      <section className="input-section">
        <IdeaInput
          onSubmit={handleIdeaSubmit}
          loading={loading}
        />
      </section>

      {error && (
        <section className="error-section">
          <p>{error}</p>
        </section>
      )}

      {results.length > 0 && (
        <section className="results-section">
          <h2>Web Search Results</h2>

          <div className="results-list">
            {results.map((result, index) => (
              <SearchResultCard
                key={index}
                result={result}
              />
            ))}
          </div>
        </section>
      )}
    </main>
  );
}

export default StartupValidator;