import { useState } from "react";

function IdeaInput({ onSubmit, loading }) {
  const [idea, setIdea] = useState("");
  const [targetCustomer, setTargetCustomer] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    const trimmedIdea = idea.trim();
    const trimmedTargetCustomer = targetCustomer.trim();

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

    setError("");

    onSubmit({
      idea: trimmedIdea,
      targetCustomer: trimmedTargetCustomer,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="idea-form">

      <div className="idea-input-wrapper">
        <label htmlFor="startup-idea">
          Enter your startup idea
        </label>

        <textarea
          id="startup-idea"
          value={idea}
          onChange={(e) => {
            setIdea(e.target.value);
            setError("");
          }}
          placeholder="Example: AI platform that provides personalized fitness plans for college students"
          rows={5}
          disabled={loading}
        />

        <div className="textarea-footer">
          <span>{idea.length} characters</span>
          <span>Be specific for better results</span>
        </div>
      </div>

      <div className="target-customer-wrapper">

        <div className="target-customer-label-row">
          <label htmlFor="target-customer">
            Target Customers
          </label>

          <span className="optional-label">
            Optional
          </span>
        </div>

        <p className="target-customer-description">
          👥 Who are the people most likely to use or pay for your product?
        </p>

        <input
          id="target-customer"
          type="text"
          value={targetCustomer}
          onChange={(e) => {
            setTargetCustomer(e.target.value);
            setError("");
          }}
          placeholder="Example: College students, working professionals, small businesses"
          disabled={loading}
        />
      </div>

      {error && (
        <div className="inline-error">
          <span>!</span>
          <p>{error}</p>
        </div>
      )}

      <button
        type="submit"
        className="validate-button"
        disabled={loading || !idea.trim()}
      >
        {loading ? (
          <>
            <span className="button-spinner"></span>
            Researching...
          </>
        ) : (
          <>
            <span>✦</span>
            Validate Idea
            <span className="button-arrow">→</span>
          </>
        )}
      </button>

      <div className="input-hint">
        <span>💡</span>
        <p>
          Include your target users, problem, industry,
          or business model for better research results.
        </p>
      </div>

    </form>
  );
}

export default IdeaInput;