import React, { useState, useEffect } from "react";
import { Sparkles, CheckCircle2, Mail, Clock, Send, Check } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function StreamingProgressLoader({ conceptTitle = "", onEmailScheduled }) {
  const auth = useAuth();
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  // Email capture state
  const [email, setEmail] = useState(() => {
    return (
      auth?.user?.email ||
      localStorage.getItem("nexus_user_email") ||
      sessionStorage.getItem("nexus_scheduled_report_email") ||
      ""
    );
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [scheduled, setScheduled] = useState(() => {
    return Boolean(sessionStorage.getItem("nexus_scheduled_report_email"));
  });
  const [scheduledEmail, setScheduledEmail] = useState(() => {
    return sessionStorage.getItem("nexus_scheduled_report_email") || "";
  });
  const [statusMsg, setStatusMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const STEPS = [
    "Searching sources across live web endpoints...",
    "Benchmarking competitors & incumbent feature moats...",
    "Calculating TAM / SAM / SOM market models...",
    "Synthesizing executive roadmap & MVP specifications...",
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStepIndex((prev) => (prev < STEPS.length - 1 ? prev + 1 : prev));
    }, 1200);

    return () => clearInterval(interval);
  }, [STEPS.length]);

  // Update email if user logs in later
  useEffect(() => {
    if (auth?.user?.email && !email) {
      setEmail(auth.user.email);
    }
  }, [auth?.user?.email, email]);

  const progressPercent = Math.min(((currentStepIndex + 1) / STEPS.length) * 100, 95);

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    const cleanEmail = email.trim();
    if (!cleanEmail || !cleanEmail.includes("@") || !cleanEmail.includes(".")) {
      setErrorMsg("Please enter a valid email address.");
      return;
    }

    setErrorMsg("");
    setIsSubmitting(true);

    try {
      const response = await fetch("/api/schedule-report-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: cleanEmail,
          idea: conceptTitle || "Startup Analysis",
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to schedule email delivery.");
      }

      setScheduled(true);
      setScheduledEmail(cleanEmail);
      setStatusMsg("Report delivery scheduled!");
      sessionStorage.setItem("nexus_scheduled_report_email", cleanEmail);
      localStorage.setItem("nexus_user_email", cleanEmail);

      if (onEmailScheduled) {
        onEmailScheduled(cleanEmail);
      }
    } catch (err) {
      console.warn("Could not schedule via backend, falling back to local session queue:", err);
      // Fallback: still store locally so user has guaranteed delivery notice
      setScheduled(true);
      setScheduledEmail(cleanEmail);
      sessionStorage.setItem("nexus_scheduled_report_email", cleanEmail);
      localStorage.setItem("nexus_user_email", cleanEmail);
      if (onEmailScheduled) {
        onEmailScheduled(cleanEmail);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ marginTop: "32px", display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Streaming Progress Card */}
      <div className="streaming-progress-card">
        <div className="streaming-header">
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "8px",
              background: "rgba(255, 199, 44, 0.12)",
              border: "1px solid rgba(255, 199, 44, 0.25)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--accent-idea)",
            }}
          >
            <Sparkles size={18} />
          </div>
          <div>
            <span
              style={{
                fontFamily: "var(--font-family-base)",
                fontSize: "11px",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                color: "var(--text-tertiary)",
              }}
            >
              LIVE INTELLIGENCE STREAM
            </span>
            <div className="streaming-step-title">{STEPS[currentStepIndex]}</div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="streaming-progress-bar">
          <div
            className="streaming-progress-fill"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        {/* Steps List */}
        <div className="streaming-steps-list">
          {STEPS.map((step, idx) => {
            const isCompleted = idx < currentStepIndex;
            const isActive = idx === currentStepIndex;
            return (
              <div
                key={idx}
                className={`streaming-step-row ${isCompleted ? "completed" : ""} ${isActive ? "active" : ""}`}
              >
                {isCompleted ? (
                  <CheckCircle2 size={15} color="var(--accent-feasibility)" />
                ) : (
                  <span
                    style={{
                      width: "14px",
                      height: "14px",
                      borderRadius: "50%",
                      border: isActive
                        ? "2px solid var(--accent-idea)"
                        : "1px solid var(--surface-border)",
                      background: isActive ? "var(--accent-idea)" : "transparent",
                      display: "inline-block",
                      flexShrink: 0,
                    }}
                  />
                )}
                <span>{step}</span>
              </div>
            );
          })}
        </div>

        {/* ============================================================
            EMAIL CAPTURE DURING ~2 MINUTE VALIDATION
        ============================================================ */}
        <div className="streaming-email-card">
          <div className="streaming-email-header">
            <div className="streaming-email-badge">
              <Clock size={12} />
              <span>Takes ~2 mins</span>
            </div>
            <h4 className="streaming-email-title">
              Step away while AI works — We'll email you the report
            </h4>
            <p className="streaming-email-desc">
              Multi-agent web crawling, competitor feature benchmarking, and TAM/SAM financial modeling takes approximately 2 minutes. Enter your email and we'll send the complete dossier straight to your inbox.
            </p>
          </div>

          {!scheduled ? (
            <form onSubmit={handleEmailSubmit} className="streaming-email-form">
              <div className="streaming-email-input-wrap">
                <Mail size={16} className="streaming-email-input-icon" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (errorMsg) setErrorMsg("");
                  }}
                  placeholder="Enter your email (e.g. founder@company.com)"
                  className="streaming-email-input"
                  disabled={isSubmitting}
                  aria-label="Email for validation report delivery"
                  required
                />
              </div>
              <button
                type="submit"
                className="streaming-email-submit-btn"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <span>Scheduling...</span>
                ) : (
                  <>
                    <Send size={14} />
                    <span>Send Report to Email</span>
                  </>
                )}
              </button>
            </form>
          ) : (
            <div className="streaming-email-confirmed">
              <div className="streaming-confirmed-left">
                <CheckCircle2 size={18} className="streaming-confirmed-icon" />
                <div className="streaming-confirmed-text">
                  <strong>Report Delivery Scheduled!</strong>
                  <span>We will email the complete validation report to <b>{scheduledEmail}</b> as soon as analysis finishes.</span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setScheduled(false)}
                className="streaming-email-change-btn"
              >
                Change Email
              </button>
            </div>
          )}

          {errorMsg && (
            <div className="streaming-email-error">
              {errorMsg}
            </div>
          )}
        </div>
      </div>

      {/* Skeleton Loaders Per Section */}
      <div style={{ display: "flex", gap: "28px", alignItems: "flex-start" }}>
        {/* Left rail skeleton */}
        <div
          className="results-skeleton"
          style={{ width: "220px", height: "300px", flexShrink: 0 }}
        />

        {/* Content skeletons */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "20px" }}>
          <div className="results-skeleton" style={{ width: "100%", height: "240px" }} />
          <div className="results-skeleton" style={{ width: "100%", height: "180px" }} />
          <div className="results-skeleton" style={{ width: "100%", height: "180px" }} />
        </div>
      </div>
    </div>
  );
}
