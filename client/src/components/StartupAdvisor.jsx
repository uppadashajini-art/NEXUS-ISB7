import React, { useState, useRef, useEffect } from "react";

/**
 * StartupAdvisor Component
 * Member 3 — NEXUS AI Startup Idea Validator
 *
 * Interactive conversational startup mentor connected to POST /api/advisor.
 * Grounded in the full validation context (competitors, market gaps, target segments, pricing).
 */

const QUICK_QUESTIONS = [
  "What should my MVP contain?",
  "Who are my main competitors?",
  "What are the biggest risks?",
  "Who should I target first?",
  "How can I launch my product?",
  "How is my idea different from existing products?"
];

export default function StartupAdvisor({ validationContext }) {
  const ideaTitle = validationContext?.idea || "your startup idea";

  const [messages, setMessages] = useState([
    {
      id: "init",
      sender: "advisor",
      text: `Hello! I'm your AI Startup Advisor. I have evaluated the market, competitors, and target audience for **"${ideaTitle}"**. How can I help you execute your vision?`,
      followups: [
        "What should my MVP contain?",
        "Who are my main competitors?",
        "What are the biggest risks?"
      ]
    }
  ]);

  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const chatEndRef = useRef(null);

  // Auto-scroll on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (questionText) => {
    const textToSend = (questionText || inputValue).trim();
    if (!textToSend || loading) return;

    setErrorMsg("");
    setInputValue("");

    const userMessageId = `user-${Date.now()}`;
    const newMessages = [
      ...messages,
      { id: userMessageId, sender: "user", text: textToSend }
    ];
    setMessages(newMessages);
    setLoading(true);

    try {
      const apiBase = (typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"))
        ? "http://127.0.0.1:8000"
        : "";

      const response = await fetch(`${apiBase}/api/advisor`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: textToSend,
          validation_context: validationContext || {}
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const data = await response.json();
      const advisorMessageId = `advisor-${Date.now()}`;

      setMessages([
        ...newMessages,
        {
          id: advisorMessageId,
          sender: "advisor",
          text: data.answer || "No response generated.",
          followups: data.suggested_followups || []
        }
      ]);
    } catch (err) {
      console.error("Advisor API call error:", err);
      setErrorMsg("Unable to reach the advisor service. Please check your backend connection or try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Helper to format markdown bolding, links, and bullet points cleanly
  const renderFormattedText = (rawText) => {
    if (!rawText) return null;

    const lines = rawText.split("\n");
    return lines.map((line, idx) => {
      const trimmed = line.trim();
      if (!trimmed) return <div key={idx} style={{ height: "6px" }} />;

      // Header lines
      if (trimmed.startsWith("### ")) {
        return (
          <h4 key={idx} style={{ color: "#d4a359", margin: "14px 0 6px 0", fontSize: "0.95rem" }}>
            {trimmed.slice(4)}
          </h4>
        );
      }

      // Bullet point line
      const isBullet = trimmed.startsWith("•") || trimmed.startsWith("-") || trimmed.startsWith("*") || /^\d+\./.test(trimmed);

      // Regex splitting bold **text** and links [text](url)
      const parts = line.split(/(\*\*.*?\*\*|\[.*?\]\(.*?\))/g);
      const renderedParts = parts.map((part, pIdx) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          return <strong key={pIdx} style={{ color: "#f5f1e8" }}>{part.slice(2, -2)}</strong>;
        }
        const linkMatch = part.match(/^\[(.*?)\]\((.*?)\)$/);
        if (linkMatch) {
          return (
            <a
              key={pIdx}
              href={linkMatch[2]}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "#d4a359", textDecoration: "underline", wordBreak: "break-all" }}
            >
              {linkMatch[1]}
            </a>
          );
        }
        return part;
      });

      return (
        <div key={idx} style={{ marginBottom: isBullet ? "5px" : "8px", paddingLeft: isBullet ? "8px" : "0", lineHeight: "1.55" }}>
          {renderedParts}
        </div>
      );
    });
  };

  return (
    <section className="startup-advisor-section">
      <style>{`
        .startup-advisor-section {
          background: linear-gradient(180deg, rgba(22, 20, 18, 0.95) 0%, rgba(14, 13, 11, 0.98) 100%);
          border: 1px solid rgba(245, 241, 232, 0.09);
          border-radius: 18px;
          padding: 28px 24px;
          margin-top: 32px;
          color: #f5f1e8;
          box-shadow: 0 12px 36px -10px rgba(0, 0, 0, 0.5);
          font-family: inherit;
        }

        .advisor-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 12px;
          margin-bottom: 20px;
          border-bottom: 1px solid rgba(245, 241, 232, 0.07);
          padding-bottom: 16px;
        }

        .advisor-kicker {
          font-size: 0.75rem;
          font-weight: 700;
          letter-spacing: 0.12em;
          text-transform: uppercase;
          color: #10b981;
          display: block;
          margin-bottom: 4px;
        }

        .advisor-title {
          font-family: "Outfit", sans-serif;
          font-size: 1.6rem;
          font-weight: 700;
          margin: 0;
          letter-spacing: -0.02em;
          background: linear-gradient(135deg, #f5f1e8 40%, #10b981 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .advisor-status {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 0.78rem;
          color: #10b981;
          background: rgba(16, 185, 129, 0.1);
          border: 1px solid rgba(16, 185, 129, 0.25);
          padding: 5px 12px;
          border-radius: 999px;
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #10b981;
          box-shadow: 0 0 8px #10b981;
        }

        /* Quick Pills */
        .quick-questions-wrapper {
          margin-bottom: 18px;
        }

        .quick-label {
          font-size: 0.75rem;
          font-weight: 700;
          text-transform: uppercase;
          color: #b8b2a7;
          margin-bottom: 8px;
          display: block;
        }

        .quick-pills {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .quick-pill {
          background: rgba(255, 255, 255, 0.04);
          border: 1px solid rgba(255, 255, 255, 0.08);
          color: #d1c7b7;
          padding: 6px 14px;
          border-radius: 999px;
          font-size: 0.8rem;
          cursor: pointer;
          transition: all 0.2s ease;
          font-weight: 500;
        }

        .quick-pill:hover:not(:disabled) {
          background: rgba(16, 185, 129, 0.15);
          border-color: rgba(16, 185, 129, 0.4);
          color: #f5f1e8;
          transform: translateY(-1px);
        }

        .quick-pill:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        /* Message Stream */
        .messages-container {
          background: rgba(0, 0, 0, 0.35);
          border: 1px solid rgba(255, 255, 255, 0.05);
          border-radius: 14px;
          padding: 20px;
          max-height: 440px;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 16px;
          margin-bottom: 18px;
        }

        .message-bubble {
          max-width: 86%;
          padding: 14px 18px;
          border-radius: 14px;
          font-size: 0.9rem;
          line-height: 1.5;
        }

        .msg-advisor {
          align-self: flex-start;
          background: rgba(255, 255, 255, 0.035);
          border: 1px solid rgba(255, 255, 255, 0.07);
          color: #d6cfc4;
          border-top-left-radius: 4px;
        }

        .msg-user {
          align-self: flex-end;
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.25) 0%, rgba(5, 150, 105, 0.35) 100%);
          border: 1px solid rgba(16, 185, 129, 0.4);
          color: #f5f1e8;
          border-top-right-radius: 4px;
        }

        .msg-author {
          font-size: 0.72rem;
          font-weight: 700;
          text-transform: uppercase;
          margin-bottom: 6px;
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .author-advisor {
          color: #10b981;
        }

        .author-user {
          color: #a7f3d0;
          justify-content: flex-end;
        }

        .followup-chips {
          margin-top: 12px;
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
        }

        .followup-chip {
          background: rgba(16, 185, 129, 0.08);
          border: 1px solid rgba(16, 185, 129, 0.25);
          color: #6ee7b7;
          font-size: 0.76rem;
          padding: 4px 10px;
          border-radius: 999px;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .followup-chip:hover:not(:disabled) {
          background: rgba(16, 185, 129, 0.2);
          border-color: #10b981;
          color: #f5f1e8;
        }

        /* Typing indicator */
        .typing-box {
          align-self: flex-start;
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 10px 16px;
          background: rgba(255, 255, 255, 0.035);
          border: 1px solid rgba(255, 255, 255, 0.07);
          border-radius: 12px;
          font-size: 0.84rem;
          color: #10b981;
        }

        .typing-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #10b981;
          animation: pulse 1.4s infinite ease-in-out;
        }

        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }

        @keyframes pulse {
          0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
          40% { transform: scale(1); opacity: 1; }
        }

        /* Input Form */
        .advisor-form {
          display: flex;
          gap: 10px;
        }

        .advisor-input {
          flex: 1;
          background: rgba(0, 0, 0, 0.4);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 10px;
          padding: 12px 16px;
          color: #f5f1e8;
          font-size: 0.9rem;
          font-family: inherit;
          outline: none;
          transition: border-color 0.2s ease;
        }

        .advisor-input:focus {
          border-color: #10b981;
        }

        .advisor-send-btn {
          background: #10b981;
          color: #0d1e16;
          border: none;
          border-radius: 10px;
          padding: 0 22px;
          font-weight: 700;
          font-size: 0.9rem;
          cursor: pointer;
          transition: all 0.2s ease;
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .advisor-send-btn:hover:not(:disabled) {
          background: #059669;
          transform: translateY(-1px);
        }

        .advisor-send-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .advisor-error {
          color: #ef4444;
          font-size: 0.8rem;
          margin-top: 8px;
        }
      `}</style>

      {/* Header */}
      <div className="advisor-header">
        <div>
          <span className="advisor-kicker">AI ADVISORY BOARD</span>
          <h2 className="advisor-title">Conversational Startup Advisor</h2>
        </div>
        <div className="advisor-status">
          <span className="status-dot"></span>
          <span>Grounded in Validation Context</span>
        </div>
      </div>

      {/* Quick Questions Pills */}
      <div className="quick-questions-wrapper">
        <span className="quick-label">Suggested Questions:</span>
        <div className="quick-pills">
          {QUICK_QUESTIONS.map((q, idx) => (
            <button
              key={idx}
              type="button"
              className="quick-pill"
              disabled={loading}
              onClick={() => handleSend(q)}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Messages Stream */}
      <div className="messages-container">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`message-bubble ${m.sender === "advisor" ? "msg-advisor" : "msg-user"}`}
          >
            <div className={`msg-author ${m.sender === "advisor" ? "author-advisor" : "author-user"}`}>
              {m.sender === "advisor" ? "⚡ AI Startup Advisor" : "👤 Founder"}
            </div>
            <div>{renderFormattedText(m.text)}</div>

            {/* Follow-up suggestions */}
            {m.sender === "advisor" && m.followups && m.followups.length > 0 && (
              <div className="followup-chips">
                {m.followups.map((f, fIdx) => (
                  <button
                    key={fIdx}
                    type="button"
                    className="followup-chip"
                    disabled={loading}
                    onClick={() => handleSend(f)}
                  >
                    ↳ {f}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="typing-box">
            <span className="typing-dot"></span>
            <span className="typing-dot"></span>
            <span className="typing-dot"></span>
            <span style={{ marginLeft: "4px" }}>Analyzing context & generating advice...</span>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Input Field */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="advisor-form"
      >
        <input
          type="text"
          className="advisor-input"
          placeholder="Ask a question about your startup, MVP, competitors, or launch..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button
          type="submit"
          className="advisor-send-btn"
          disabled={loading || !inputValue.trim()}
        >
          {loading ? "Thinking..." : "Ask Advisor"}
        </button>
      </form>

      {errorMsg && <div className="advisor-error">{errorMsg}</div>}
    </section>
  );
}
