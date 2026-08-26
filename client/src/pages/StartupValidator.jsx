import { useState } from "react";
import IdeaInput from "../components/IdeaInput";
import SearchResultCard from "../components/SearchResultCard";

function StartupValidator() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleIdeaSubmit = (idea) => {
    console.log("Startup idea:", idea);

    setLoading(true);

    // Temporary mock data.
    // This will later be replaced with the FastAPI API call.
    setTimeout(() => {
      setResults([
        {
          title: "Example Market Result",
          content:
            "This is temporary mock data. Later, real information will come from the Web Search Agent.",
          url: "https://example.com",
        },
        {
          title: "Example Competitor Result",
          content:
            "Real Tavily/DuckDuckGo search results will appear here after backend integration.",
          url: "https://example.com",
        },
      ]);

      setLoading(false);
    }, 1000);
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