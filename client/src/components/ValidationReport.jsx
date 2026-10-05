import React from "react";
import { Download } from "lucide-react";

// Place this file at: client/src/components/ValidationReport.jsx
//
// Cards render one after another (stacked, full-width) instead of a grid.
// Known sub-labels inside each summary's text (e.g. "Key trends:",
// "Suggested marketing channels:") are highlighted as green inline
// headings so the reader can scan each card quickly.

const SECTION_CONFIG = [
  { key: "executive_summary", title: "Executive Summary", icon: "📋", kicker: "OVERVIEW" },
  { key: "market_summary", title: "Market Summary", icon: "📈", kicker: "MARKET" },
  { key: "competitor_summary", title: "Competitor Summary", icon: "🏢", kicker: "COMPETITION" },
  { key: "swot_summary", title: "SWOT Summary", icon: "🧭", kicker: "SWOT" },
  { key: "risk_summary", title: "Risk Summary", icon: "⚠️", kicker: "RISK" },
  { key: "mvp_summary", title: "MVP Summary", icon: "🚀", kicker: "MVP" },
  { key: "gtm_summary", title: "Go-To-Market Summary", icon: "📣", kicker: "GTM" },
  { key: "recommendations", title: "Key Recommendations", icon: "💡", kicker: "ACTION" },
  { key: "conclusion", title: "Conclusion", icon: "✅", kicker: "VERDICT" },
];

// Known sub-label phrases that should be pulled out as highlighted
// inline headings wherever they appear inside a summary's text.
const KNOWN_LABELS = [
  "Key trends:",
  "Key strengths:",
  "Key threats to monitor:",
  "Potential market gaps include:",
  "Recommended MVP must-have features:",
  "Suggested marketing channels:",
  "Note:",
];

const LABEL_SPLIT_PATTERN = new RegExp(
  "(" + KNOWN_LABELS.map((l) => l.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")"
);

function renderWithHighlightedLabels(text) {
  if (!text) return null;
  const parts = String(text).split(LABEL_SPLIT_PATTERN);

  const nodes = [];
  parts.forEach((part, i) => {
    if (KNOWN_LABELS.includes(part)) {
      nodes.push(
        <span className="report-label" key={`label-${i}`}>
          {part}
        </span>
      );
    } else if (part.trim()) {
      nodes.push(<span key={`text-${i}`}>{part}</span>);
    }
  });
  return nodes;
}

export default function ValidationReport({ report, onDownload }) {
  if (!report) return null;

  const sections = SECTION_CONFIG.filter((s) => report[s.key] && String(report[s.key]).trim());

  if (sections.length === 0) return null;

  return (
    <section className="analysis-card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px", flexWrap: "wrap", gap: "12px" }}>
        <h2 style={{ margin: 0 }}>Startup Validation Report</h2>
        {onDownload && (
          <button
            type="button"
            onClick={onDownload}
            className="report-download-btn"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              padding: "6px 14px",
              borderRadius: "20px",
              background: "rgba(255, 199, 44, 0.12)",
              border: "1px solid rgba(255, 199, 44, 0.35)",
              color: "#e28743",
              fontSize: "12px",
              fontWeight: 700,
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
          >
            <Download size={14} />
            <span>Download Dossier (.md)</span>
          </button>
        )}
      </div>

      <div className="report-stack">
        {sections.map((s) => (
          <div key={s.key} className="gtm-card report-card">
            <div className="gtm-card-header">
              <div className="gtm-card-icon">{s.icon}</div>
              <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                <span className="report-kicker">{s.kicker}</span>
                <h3 className="gtm-card-title">{s.title}</h3>
              </div>
            </div>
            <p className="report-body">{renderWithHighlightedLabels(report[s.key])}</p>
          </div>
        ))}
      </div>

      <style>{`
        .report-stack {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .report-card {
          display: flex;
          flex-direction: column;
        }
        .report-kicker {
          font-size: 0.65rem;
          font-weight: 700;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          color: #e28743;
        }
        .report-body {
          margin: 0;
          font-size: 0.88rem;
          color: #e6e0d4;
          line-height: 1.6;
        }
        .report-label {
          display: block;
          font-weight: 700;
          color: #34d399;
          margin-top: 12px;
          margin-bottom: 4px;
          font-size: 0.8rem;
          text-transform: uppercase;
          letter-spacing: 0.03em;
        }
        .gtm-card {
          background: rgba(255, 255, 255, 0.025);
          border: 1px solid rgba(255, 255, 255, 0.06);
          border-radius: 14px;
          padding: 20px;
          transition: all 0.25s ease;
        }
        .gtm-card:hover {
          border-color: rgba(226, 135, 67, 0.25);
          background: rgba(255, 255, 255, 0.04);
        }
        .gtm-card-header {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 12px;
        }
        .gtm-card-icon {
          width: 32px;
          height: 32px;
          border-radius: 8px;
          background: rgba(226, 135, 67, 0.15);
          color: #e28743;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 0.95rem;
          flex-shrink: 0;
        }
        .gtm-card-title {
          font-size: 1rem;
          font-weight: 600;
          margin: 0;
          color: #f5f1e8;
        }

        /* -----------------------------------------------
           LIGHT THEME OVERRIDES
        ----------------------------------------------- */
        [data-theme="light"] .gtm-card {
          background: #ffffff;
          border-color: rgba(0, 0, 0, 0.08);
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        }
        [data-theme="light"] .gtm-card:hover {
          border-color: rgba(226, 135, 67, 0.35);
          background: #faf9f5;
        }
        [data-theme="light"] .gtm-card-title {
          color: #18181b;
        }
        [data-theme="light"] .report-body {
          color: #27272a;
        }
        [data-theme="light"] .report-kicker {
          color: #c25e1a;
        }
        [data-theme="light"] .report-label {
          color: #059669;
        }
      `}</style>
    </section>
  );
}