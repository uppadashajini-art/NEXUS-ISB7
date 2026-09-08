import { useState } from "react";
import SearchResultCard from "../components/SearchResultCard";
import { searchStartupIdea } from "../services/api";
import MarketAnalysis from "../components/MarketAnalysis";
import CustomerSegments from "../components/CustomerSegments";
import CompetitorAnalysis from "../components/CompetitorAnalysis";
import MarketGaps from "../components/MarketGaps";
import { validateIdea } from "../services/validationService";

function StartupValidator() {
  // =========================================
  // FORM STATE
  // =========================================
  const [idea, setIdea] = useState("");
  const [domain, setDomain] = useState("");
  const [targetCustomers, setTargetCustomers] = useState("");

  // =========================================
  // SEARCH STATE
  // =========================================
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // =========================================
  // SUBMITTED VALUES
  // Keep these separate so result cards
  // always use the values submitted by user
  // =========================================
  const [submittedIdea, setSubmittedIdea] = useState("");
  const [submittedDomain, setSubmittedDomain] = useState("");
  const [submittedCustomers, setSubmittedCustomers] = useState("");
  const [submittedValidation, setSubmittedValidation] =
    useState("all");

  // =========================================
  // VALIDATION STATE
  // =========================================
  const [searchCompleted, setSearchCompleted] = useState(false);
  const [selectedOption, setSelectedOption] = useState("all");

  const [validationResult, setValidationResult] =
    useState(null);

  const [validationLoading, setValidationLoading] =
    useState(false);

  const [validationError, setValidationError] =
    useState("");

  // =========================================
  // VALIDATION OPTIONS
  // =========================================
  const validationOptions = [
    {
      id: "all",
      icon: "✦",
      title: "All",
      description:
        "Complete validation across all areas",
    },
    {
      id: "market",
      icon: "📈",
      title: "Market Demand",
      description:
        "Analyze market size, demand and trends",
    },
    {
      id: "competition",
      icon: "🏢",
      title: "Competition",
      description:
        "Find competitors and alternative solutions",
    },
    {
      id: "customers",
      icon: "👥",
      title: "Target Customers",
      description:
        "Identify users, needs and pain points",
    },
    {
      id: "business",
      icon: "💰",
      title: "Business Potential",
      description:
        "Explore monetization and opportunities",
    },
    {
      id: "risks",
      icon: "⚠️",
      title: "Risks",
      description:
        "Identify challenges and potential risks",
    },
  ];

  // =========================================
  // SELECTED VALIDATION
  // =========================================
  const selectedValidation =
    validationOptions.find(
      (option) => option.id === selectedOption
    ) || validationOptions[0];

  // =========================================
  // FORM SUBMIT
  // =========================================
  const handleSubmit = async (e) => {
    e.preventDefault();

    const trimmedIdea = idea.trim();
    const trimmedDomain = domain.trim();
    const trimmedCustomers = targetCustomers.trim();

    // -----------------------------------------
    // IDEA VALIDATION
    // -----------------------------------------
    if (!trimmedIdea) {
      setError("Please enter your startup idea.");
      return;
    }

    if (trimmedIdea.length < 10) {
      setError(
        "Please provide a little more detail about your startup idea."
      );
      return;
    }

    // -----------------------------------------
    // START LOADING
    // -----------------------------------------
    setLoading(true);
    setError("");
    setResults([]);
    setSearchCompleted(false);

    setValidationResult(null);
    setValidationError("");

    // -----------------------------------------
    // SAVE SUBMITTED VALUES
    // -----------------------------------------
    setSubmittedIdea(trimmedIdea);
    setSubmittedDomain(trimmedDomain);
    setSubmittedCustomers(trimmedCustomers);
    setSubmittedValidation(selectedOption);

    console.log("=================================");
    console.log("NEXUS STARTUP VALIDATION");
    console.log("=================================");
    console.log("Startup Idea:", trimmedIdea);
    console.log("Domain / Industry:", trimmedDomain);
    console.log(
      "Target Customers:",
      trimmedCustomers
    );
    console.log(
      "Validation Type:",
      selectedOption
    );

    try {
      // =========================================
      // WEB SEARCH
      // =========================================
      const data = await searchStartupIdea(
        trimmedIdea,
        trimmedDomain,
        trimmedCustomers,
        selectedOption
      );

      console.log("Backend response:", data);

      const searchResults = Array.isArray(
        data?.results
      )
        ? data.results
        : [];

      setResults(searchResults);
      setSearchCompleted(true);

      // =========================================
      // AI VALIDATION / MILESTONE 2
      // =========================================
      setValidationLoading(true);
      setValidationError("");

      try {
        const analysisData =
          await validateIdea(trimmedIdea);

        setValidationResult(analysisData);
      } catch (analysisErr) {
        console.error(
          "Validation analysis error:",
          analysisErr
        );

        setValidationError(
          analysisErr?.message ||
            "Unable to complete market and competitor analysis."
        );

        setValidationResult(null);
      } finally {
        setValidationLoading(false);
      }
    } catch (err) {
      console.error("Search error:", err);

      setError(
        err?.message ||
          "Unable to validate the startup idea. Please try again."
      );

      setSearchCompleted(false);
    } finally {
      setLoading(false);
    }
  };

  // =========================================
  // RETRY
  // =========================================
  const handleRetry = () => {
    if (!submittedIdea) {
      return;
    }

    setIdea(submittedIdea);
    setDomain(submittedDomain);
    setTargetCustomers(submittedCustomers);
    setSelectedOption(
      submittedValidation || "all"
    );

    setTimeout(() => {
      document
        .getElementById("validator-form")
        ?.requestSubmit();
    }, 0);
  };

  // =========================================
  // CLEAR
  // =========================================
  const handleClear = () => {
    setIdea("");
    setDomain("");
    setTargetCustomers("");

    setResults([]);

    setValidationResult(null);
    setValidationLoading(false);
    setValidationError("");

    setError("");

    setSubmittedIdea("");
    setSubmittedDomain("");
    setSubmittedCustomers("");
    setSubmittedValidation("all");

    setSearchCompleted(false);
    setSelectedOption("all");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  // =========================================
  // IDEA CHANGE
  // =========================================
  const handleIdeaChange = (e) => {
    setIdea(e.target.value);

    if (error) {
      setError("");
    }
  };

  // =========================================
  // TARGET CUSTOMER CHANGE
  // =========================================
  const handleCustomerChange = (e) => {
    setTargetCustomers(e.target.value);

    if (error) {
      setError("");
    }
  };

  return (
    <main className="startup-validator">

      {/* =========================================
          HERO
      ========================================= */}
      <section className="hero">
        <div className="hero-badge">
          <span className="status-dot"></span>
          NEXUS AI • STARTUP INTELLIGENCE
        </div>

        <h1>
          AI Startup
          <span> Idea Validator</span>
        </h1>

        <p>
          Validate your startup idea using AI-powered
          market intelligence and real-time web research.
        </p>

        <div className="hero-features">
          <div className="hero-feature">
            <span>✦</span>
            Market Research
          </div>

          <div className="hero-feature">
            <span>◈</span>
            Competition Analysis
          </div>

          <div className="hero-feature">
            <span>⌁</span>
            AI Insights
          </div>
        </div>
      </section>

      {/* =========================================
          INPUT SECTION
      ========================================= */}
      <section className="input-section">

        <div className="section-header">
          <div className="section-number">
            01
          </div>

          <div>
            <h2>
              Describe Your Startup
            </h2>

            <p>
              Enter your startup idea and provide optional
              customer details for better validation.
            </p>
          </div>
        </div>

        <form
          id="validator-form"
          className="validator-form"
          onSubmit={handleSubmit}
        >

          {/* =========================================
              STARTUP IDEA
          ========================================= */}
          <div className="idea-input-wrapper">

            <div className="field-heading">
              <label htmlFor="startup-idea">
                Enter your startup idea
              </label>

              <span className="required-label">
                Required
              </span>
            </div>

            <textarea
              id="startup-idea"
              value={idea}
              onChange={handleIdeaChange}
              placeholder="Example: AI platform that provides personalized fitness plans for college students"
              rows={5}
              disabled={loading}
              aria-required="true"
            />

            <div className="textarea-footer">
              <span>
                {idea.length} characters
              </span>

              <span>
                Be specific for better results
              </span>
            </div>
          </div>

          {/* =========================================
              DOMAIN / INDUSTRY
          ========================================= */}
          <div className="domain-input-wrapper">

            <div className="field-heading">
              <label htmlFor="startup-domain">
                Domain / Industry
              </label>

              <span className="optional-label">
                Optional
              </span>
            </div>

            <input
              id="startup-domain"
              type="text"
              value={domain}
              onChange={(e) =>
                setDomain(e.target.value)
              }
              placeholder="e.g. EdTech, HealthTech, FinTech, B2B SaaS, E-Commerce, DevTools"
              disabled={loading}
            />

            <div className="input-description">
              <span className="description-icon">
                🌐
              </span>

              <span>
                Specify your startup domain or industry
                sector to target market and competitor
                intelligence.
              </span>
            </div>
          </div>

          {/* =========================================
              TARGET CUSTOMERS
              ALWAYS VISIBLE
          ========================================= */}
          <div className="customer-input-wrapper">

            <div className="field-heading">

              <label htmlFor="target-customers">
                <span>👥</span>{" "}
                Target Customers
              </label>

              <span className="optional-label">
                Optional
              </span>

            </div>

            <input
              id="target-customers"
              type="text"
              value={targetCustomers}
              onChange={handleCustomerChange}
              placeholder="e.g. College students and working professionals"
              disabled={loading}
            />

            <div className="input-description">

              <span className="description-icon">
                👥
              </span>

              <span>
                Specify who is most likely to use or pay
                for your product. This helps NEXUS tailor
                its market, customer, and competitor
                research.
              </span>

            </div>
          </div>

          {/* =========================================
              VALIDATION FOCUS
          ========================================= */}
          <div className="validation-focus">

            <div className="options-header">

              <div>

                <span className="mini-label">
                  VALIDATION FOCUS
                </span>

                <h3>
                  What do you want to analyze?
                </h3>

                <p>
                  Select one area or choose All for
                  complete startup validation.
                </p>

              </div>

            </div>

            <div className="validation-options">

              {validationOptions.map(
                (option) => {

                  const isSelected =
                    selectedOption === option.id;

                  return (
                    <button
                      key={option.id}
                      type="button"
                      disabled={loading}
                      className={`validation-option ${
                        isSelected
                          ? "selected"
                          : ""
                      }`}
                      onClick={() =>
                        setSelectedOption(
                          option.id
                        )
                      }
                    >

                      <div className="option-icon">
                        {option.icon}
                      </div>

                      <div className="option-content">

                        <h4>
                          {option.title}
                        </h4>

                        <p>
                          {option.description}
                        </p>

                      </div>

                      <div className="option-check">
                        {isSelected
                          ? "✓"
                          : "→"}
                      </div>

                    </button>
                  );
                }
              )}

            </div>
          </div>

          {/* =========================================
              SELECTED VALIDATION
          ========================================= */}
          <div className="selected-validation">

            <div className="selected-icon">
              {selectedValidation.icon}
            </div>

            <div className="selected-info">

              <span>
                SELECTED VALIDATION
              </span>

              <strong>
                {selectedValidation.title}
              </strong>

              <p>
                {selectedValidation.description}
              </p>

            </div>

          </div>

          {/* =========================================
              ERROR
          ========================================= */}
          {error && (
            <div
              className="inline-error"
              role="alert"
            >
              <span>
                !
              </span>

              <p>
                {error}
              </p>
            </div>
          )}

          {/* =========================================
              SUBMIT BUTTON
          ========================================= */}
          <div className="validate-action">

            <button
              type="submit"
              className={`validate-button ${
                idea.trim().length >= 10
                  ? "active"
                  : ""
              }`}
              disabled={
                loading ||
                idea.trim().length < 10
              }
            >

              {loading ? (
                <>
                  <span className="button-spinner"></span>
                  Researching...
                </>
              ) : (
                <>
                  <span>
                    ✦
                  </span>

                  Validate Idea

                  <span className="button-arrow">
                    →
                  </span>
                </>
              )}

            </button>

            <p className="validate-caption">
              NEXUS will research real-time web sources
              based on your selected validation focus.
            </p>

          </div>

          {/* =========================================
              INPUT HINT
          ========================================= */}
          <div className="input-hint">

            <span>
              💡
            </span>

            <p>
              Include your target users, problem,
              industry, or business model for better
              research results.
            </p>

          </div>

        </form>
      </section>

      {/* =========================================
          LOADING
      ========================================= */}
      {loading && (
        <section className="loading-section">

          <div className="loading-card">

            <div className="loading-animation">
              <div className="loading-spinner"></div>
            </div>

            <div className="loading-content">

              <span className="mini-label">
                NEXUS RESEARCH ENGINE
              </span>

              <h2>
                Researching Your Idea
              </h2>

              <p>
                Searching real-time web sources for
                relevant startup and market information.
              </p>

              <div className="research-target">

                <span>
                  ANALYZING
                </span>

                <strong>
                  {selectedValidation.title}
                </strong>

              </div>

              {/* TARGET CUSTOMER DURING LOADING */}
              {targetCustomers.trim() && (
                <div className="research-target">

                  <span>
                    TARGET AUDIENCE
                  </span>

                  <strong>
                    {targetCustomers.trim()}
                  </strong>

                </div>
              )}

              <div className="loading-steps">

                <div className="loading-step completed">
                  <span>✓</span>
                  Processing startup idea
                </div>

                <div className="loading-step active">
                  <span>◌</span>
                  Searching web sources
                </div>

                <div className="loading-step">
                  <span>○</span>
                  Identifying market signals
                </div>

                <div className="loading-step">
                  <span>○</span>
                  Preparing validation
                </div>

              </div>

            </div>
          </div>

        </section>
      )}

      {/* =========================================
          ERROR SECTION
      ========================================= */}
      {error && !loading && (
        <section className="error-section">

          <div className="error-card">

            <div className="error-icon">
              !
            </div>

            <div className="error-content">

              <span className="mini-label">
                VALIDATION ERROR
              </span>

              <h3>
                Something went wrong
              </h3>

              <p>
                {error}
              </p>

              <div className="error-actions">

                <button
                  type="button"
                  className="retry-button"
                  onClick={handleRetry}
                >
                  Try Again
                </button>

                <button
                  type="button"
                  className="secondary-button"
                  onClick={handleClear}
                >
                  Clear
                </button>

              </div>

            </div>

          </div>

        </section>
      )}

      {/* =========================================
          RESULTS
      ========================================= */}
      {searchCompleted &&
        !loading &&
        !error && (

          <section className="validation-dashboard">

            {/* HEADER */}
            <div className="section-header">

              <div className="section-number">
                02
              </div>

              <div>

                <h2>
                  Validation Results
                </h2>

                <p>
                  Research collected for your startup idea.
                </p>

              </div>

              <div className="header-score-actions">

                <div className="top-score-badge general-score">

                  <span className="score-icon">
                    ✦
                  </span>

                  <div className="score-info">

                    <span className="score-label">
                      RESEARCH CONFIDENCE
                    </span>

                    <strong className="score-value">
                      HIGH
                    </strong>

                  </div>

                </div>

                <button
                  type="button"
                  className="clear-button"
                  onClick={handleClear}
                >
                  ↻ New Idea
                </button>

              </div>

            </div>

            {/* IDEA */}
            <div className="idea-display">

              <span>
                ANALYZED STARTUP IDEA
              </span>

              <h3>
                {submittedIdea}
              </h3>

            </div>

            {/* DOMAIN */}
            {submittedDomain && (
              <div className="idea-display domain-result">

                <span>
                  DOMAIN / INDUSTRY
                </span>

                <h3>
                  {submittedDomain}
                </h3>

              </div>
            )}

            {/* TARGET CUSTOMER */}
            {submittedCustomers && (
              <div className="idea-display customer-result">

                <span>
                  TARGET CUSTOMERS
                </span>

                <h3>
                  {submittedCustomers}
                </h3>

              </div>
            )}

            {/* SELECTED ANALYSIS */}
            <div className="selected-analysis">

              <div className="selected-analysis-icon">
                {selectedValidation.icon}
              </div>

              <div>

                <span>
                  VALIDATION AREA
                </span>

                <h3>
                  {selectedValidation.title}
                </h3>

                <p>
                  {selectedValidation.description}
                </p>

              </div>

            </div>

            {/* DASHBOARD */}
            <div className="dashboard-grid">

              <div className="dashboard-card">

                <div className="card-icon">
                  🔎
                </div>

                <span className="card-label">
                  SOURCES
                </span>

                <strong className="big-number">
                  {results.length}
                </strong>

                <p>
                  Relevant web sources found
                </p>

              </div>

              <div className="dashboard-card">

                <div className="card-icon">
                  ✓
                </div>

                <span className="card-label">
                  STATUS
                </span>

                <strong className="status-success">
                  COMPLETE
                </strong>

                <p>
                  Research completed
                </p>

              </div>

              <div className="dashboard-card">

                <div className="card-icon">
                  🎯
                </div>

                <span className="card-label">
                  CONFIDENCE
                </span>

                <strong className="big-number score-number">
                  HIGH
                </strong>

                <p>
                  Research confidence level
                </p>

              </div>

              <div className="dashboard-card">

                <div className="card-icon">
                  🤖
                </div>

                <span className="card-label">
                  ENGINE
                </span>

                <strong>
                  NEXUS AI
                </strong>

                <p>
                  AI-powered intelligence
                </p>

              </div>

            </div>

            {/* =========================================
                WEB RESEARCH SOURCES
            ========================================= */}
            {results.length > 0 && (

              <div className="results-section">

                <div className="results-header">

                  <div>

                    <span className="mini-label">
                      WEB INTELLIGENCE
                    </span>

                    <h3>
                      Research Sources
                    </h3>

                  </div>

                  <div className="result-count">

                    <strong>
                      {results.length}
                    </strong>

                    <span>
                      {results.length === 1
                        ? "Source"
                        : "Sources"}
                    </span>

                  </div>

                </div>

                <div className="results-list">

                  {results.map(
                    (result, index) => (

                      <SearchResultCard
                        key={`${
                          result?.url ||
                          "result"
                        }-${index}`}
                        result={result}
                        validationType={
                          submittedValidation
                        }
                        targetCustomer={
                          submittedCustomers
                        }
                      />

                    )
                  )}

                </div>

              </div>
            )}

            {/* =========================================
                AI ANALYSIS LOADING
            ========================================= */}
            {validationLoading && (
              <p className="analysis-loading">
                Analyzing market and competitors...
              </p>
            )}

            {/* =========================================
                AI ANALYSIS ERROR
            ========================================= */}
            {validationError && (
              <p className="inline-error">
                {validationError}
              </p>
            )}

            {/* =========================================
                AI ANALYSIS RESULTS
            ========================================= */}
            {validationResult && (
              <>

                <MarketAnalysis
                  data={
                    validationResult.market_analysis
                  }
                />

                <CustomerSegments
                  segments={
                    validationResult
                      .market_analysis
                      ?.customer_segments
                  }
                />

                <CompetitorAnalysis
                  data={
                    validationResult
                      .competitor_analysis
                  }
                />

                <MarketGaps
                  gaps={
                    validationResult
                      .competitor_analysis
                      ?.market_gaps
                  }
                />

              </>
            )}

          </section>
        )}

      {/* =========================================
          NO RESULTS
      ========================================= */}
      {!loading &&
        !error &&
        searchCompleted &&
        results.length === 0 && (

          <section className="empty-results">

            <div className="empty-icon">
              🔍
            </div>

            <h2>
              No Relevant Information Found
            </h2>

            <p>
              We couldn't find enough relevant
              information for this startup idea.
              Try adding more details.
            </p>

            <button
              type="button"
              className="primary-button"
              onClick={handleClear}
            >
              Try Another Idea
            </button>

          </section>
        )}

    </main>
  );
}

export default StartupValidator;