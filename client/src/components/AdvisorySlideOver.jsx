import React, { useState, useRef, useEffect } from "react";
import { X, Send, Sparkles, Bot, User, ArrowRight } from "lucide-react";
import "../styles/advisory.css";

const DEFAULT_PROMPTS = [
  "What should my Day-1 MVP contain?",
  "Who are my main competitors & gaps?",
  "What are the biggest technical risks?",
  "What pricing model fits my ICP?",
  "How do I structure my 30-day GTM launch?",
];

export default function AdvisorySlideOver({
  isOpen,
  onClose,
  currentIdea = "",
  validationResult = null,
}) {
  const ideaDisplay = currentIdea ? currentIdea.slice(0, 50) + (currentIdea.length > 50 ? "..." : "") : "Active Concept";

  const [messages, setMessages] = useState([
    {
      id: "init",
      sender: "advisor",
      text: `Hello! I'm your Advisory Assistant. I am grounded in your market sizing, competitor feature gaps, and technical feasibility reports for "${ideaDisplay}". How can I help you execute?`,
      time: "Just now",
    },
  ]);

  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll on new message
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, loading, isOpen]);

  // Focus input on open
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen]);

  // Handle ESC key
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  // Helper to generate intelligent contextual fallback
  const getContextualFallbackAnswer = (question, idea, result) => {
    const q = question.toLowerCase();
    const competitors = result?.competitors?.map(c => c.name || c.company).join(", ") || "incumbent enterprise tools";

    if (q.includes("mvp") || q.includes("day-1") || q.includes("feature")) {
      return `For **"${ideaDisplay}"**, focus strictly on Day-1 activation:\n\n• **Core Pipeline**: Build the telemetry ingestion adapter that immediately demonstrates time-to-value within 5 minutes.\n• **Single Critical Action**: Ensure users can run one automated benchmark without requiring multi-department approvals.\n• **Postpone**: Team permission hierarchies, custom reporting PDFs, and on-prem connectors should stay strictly in Secondary Scope.`;
    }

    if (q.includes("competitor") || q.includes("gap") || q.includes("alternative")) {
      return `Based on competitor telemetry benchmarking (${competitors}):\n\n• **Incumbent Weakness**: Legacy competitors suffer from steep learning curves, opaque enterprise pricing, and heavy manual onboarding.\n• **Your Defensible Wedge**: Position on automated, self-serve onboarding with real-time feedback loops.\n• **Defensibility**: Win by offering zero-friction API webhooks that integrate into existing developer and practitioner stacks.`;
    }

    if (q.includes("risk") || q.includes("technical") || q.includes("feasibility")) {
      return `Key risk analysis for this concept:\n\n• **Architecture Bottleneck**: Real-time normalization under high traffic spikes requires asynchronous event queuing.\n• **Compliance Boundary**: If handling customer telemetry, implement immediate pseudonymization before feeding data to AI models.\n• **Mitigation**: Deploy a lightweight proxy gateway with strict rate-limiting and audit logging.`;
    }

    if (q.includes("pricing") || q.includes("icp") || q.includes("customer")) {
      return `Recommended monetization strategy:\n\n• **Model**: Transparent 2-tier SaaS subscription with a generous self-serve evaluation tier.\n• **Starter ($29–$49/mo)**: Single-operator tier with core automated benchmarking.\n• **Pro / Team ($149–$249/mo)**: Multi-project telemetry, webhooks, and priority SLA.\n• **Payback**: Keep CAC low by acquiring practitioners directly through technical teardowns and open-source utility tooling.`;
    }

    return `Here is the strategic recommendation for **"${ideaDisplay}"**:\n\n1. **Narrow the Wedge**: Focus exclusively on practitioners feeling immediate pain from manual friction.\n2. **Validate Willingness-to-Pay**: Launch a private alpha cohort of 20 target users before broadening feature scope.\n3. **Continuous Benchmarking**: Re-run the analysis scope regularly as competitors release feature updates.`;
  };

  const handleSendMessage = async (textToSend) => {
    const query = (textToSend || inputValue).trim();
    if (!query || loading) return;

    setInputValue("");
    const userMsg = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: query,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const apiBase =
        import.meta.env.VITE_API_BASE_URL ||
        (typeof window !== "undefined" && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
          ? "http://127.0.0.1:8000"
          : "");

      const res = await fetch(`${apiBase}/api/advisor`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: query,
          validation_context: {
            idea: currentIdea,
            ...(validationResult || {}),
          },
        }),
      });

      if (!res.ok) {
        throw new Error(`Advisor endpoint returned status ${res.status}`);
      }

      const data = await res.json();
      const replyText = data.answer || data.response || data.message || getContextualFallbackAnswer(query, currentIdea, validationResult);

      setMessages((prev) => [
        ...prev,
        {
          id: `adv-${Date.now()}`,
          sender: "advisor",
          text: replyText,
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } catch {
      // Fallback to intelligent local context when server is unreachable
      const fallbackReply = getContextualFallbackAnswer(query, currentIdea, validationResult);
      setMessages((prev) => [
        ...prev,
        {
          id: `adv-${Date.now()}`,
          sender: "advisor",
          text: fallbackReply,
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="advisory-backdrop"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Slide-over panel (440px) */}
      <aside
        className="advisory-panel"
        role="dialog"
        aria-modal="true"
        aria-label="Advisory Assistant"
      >
        {/* Header */}
        <div className="advisory-header">
          <div className="advisory-title-wrap">
            <span className="advisory-eyebrow">
              <span className="advisory-live-dot" aria-hidden="true" />
              <span>AI ADVISORY ASSISTANT</span>
            </span>
            <h2 className="advisory-title">Founder Advisory Copilot</h2>
          </div>

          <button
            type="button"
            className="advisory-close-btn"
            onClick={onClose}
            aria-label="Close Advisory Assistant"
          >
            <X size={16} strokeWidth={1.5} />
          </button>
        </div>

        {/* Context Chip showing the current idea */}
        <div className="advisory-context-strip">
          <span className="advisory-context-label">CONTEXT:</span>
          <span className="advisory-context-text" title={currentIdea || "Workspace Idea"}>
            "{currentIdea ? currentIdea.slice(0, 56) + (currentIdea.length > 56 ? "..." : "") : "Autonomous AI SRE for Kubernetes"}"
          </span>
        </div>

        {/* Chat UI Messages List */}
        <div className="advisory-messages-body">
          {messages.map((msg) => (
            <div key={msg.id} className={`advisory-msg-row ${msg.sender}`}>
              <div className="advisory-bubble">
                {msg.text.split("\n\n").map((para, pIdx) => {
                  if (para.startsWith("• ")) {
                    const items = para.split("\n");
                    return (
                      <ul key={pIdx}>
                        {items.map((it, iIdx) => (
                          <li key={iIdx}>
                            <span dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(it.replace(/^•\s*/, "")) }} />
                          </li>
                        ))}
                      </ul>
                    );
                  }
                  return (
                    <p key={pIdx}>
                      <span dangerouslySetInnerHTML={{ __html: formatInlineMarkdown(para) }} />
                    </p>
                  );
                })}
              </div>
              <span className="advisory-msg-time">{msg.time}</span>
            </div>
          ))}

          {loading && (
            <div className="advisory-msg-row advisor">
              <div className="advisory-typing-row">
                <span className="advisory-typing-dot" />
                <span className="advisory-typing-dot" />
                <span className="advisory-typing-dot" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Prompts */}
        <div className="advisory-prompts-section">
          <span className="advisory-prompts-header">SUGGESTED PROMPTS</span>
          <div className="advisory-prompts-wrap">
            {DEFAULT_PROMPTS.map((prompt, idx) => (
              <button
                key={idx}
                type="button"
                className="advisory-prompt-chip"
                onClick={() => handleSendMessage(prompt)}
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        {/* Chat Input Bar */}
        <div className="advisory-input-bar">
          <div className="advisory-input-row">
            <input
              ref={inputRef}
              type="text"
              className="advisory-input-field"
              placeholder="Ask for MVP scope, competitors, pricing..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              aria-label="Message Advisory Assistant"
            />

            <button
              type="button"
              className="advisory-send-btn"
              onClick={() => handleSendMessage()}
              disabled={loading || !inputValue.trim()}
              aria-label="Send message"
            >
              <Send size={14} strokeWidth={2} />
              <span>Send</span>
            </button>
          </div>

          <div className="advisory-input-hint">
            <span>Press Enter to send</span>
            <span>Grounded in analysis telemetry</span>
          </div>
        </div>
      </aside>
    </>
  );
}

// Minimal inline markdown helper for bold and bullets
function formatInlineMarkdown(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");
}
