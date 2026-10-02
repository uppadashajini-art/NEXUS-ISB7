import React, { useState, useEffect } from "react";
import { Sparkles, CheckCircle2 } from "lucide-react";

export default function StreamingProgressLoader({ conceptTitle = "" }) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

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

  const progressPercent = Math.min(((currentStepIndex + 1) / STEPS.length) * 100, 95);

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
