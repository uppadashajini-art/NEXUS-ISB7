import { useState } from "react";

function IdeaInput({ onSubmit, loading }) {
  const [idea, setIdea] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    const trimmedIdea = idea.trim();

    if (!trimmedIdea) {
      setError("Please enter your startup idea.");
      return;
    }

    if (trimmedIdea.length < 10) {
      setError("Please provide a little more detail about your startup idea.");
      return;
    }

    setError("");
    onSubmit(trimmedIdea);
  };

  return (
    <form onSubmit={handleSubmit} className="idea-form">
      <label htmlFor="startup-idea">
        Enter your startup idea
      </label>

      <textarea
        id="startup-idea"
        value={idea}
        onChange={(e) => setIdea(e.target.value)}
        placeholder="Example: AI platform that provides personalized fitness plans for college students"
        rows={5}
        disabled={loading}
      />

      {error && <p className="error-message">{error}</p>}

      <button type="submit" disabled={loading}>
        {loading ? "Searching..." : "Validate Idea"}
      </button>
    </form>
  );
}

export default IdeaInput;