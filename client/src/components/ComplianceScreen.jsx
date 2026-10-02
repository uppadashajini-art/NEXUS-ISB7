import React from "react";
import { ShieldCheck, ShieldAlert, CheckCircle2, AlertCircle, FileLock, Lock, Brain, CreditCard } from "lucide-react";
import "../styles/compliance.css";

const FRAMEWORKS = [
  {
    id: "gdpr",
    name: "GDPR / Global Privacy",
    icon: FileLock,
    accent: "var(--accent-idea)",
    severity: "medium",
    severityLabel: "Medium Severity",
    desc: "Governs data collection consent, telemetry anonymization, and user deletion rights across European and global user cohorts.",
    checklist: [
      { text: "Explicit cookie & telemetry opt-in consent flow", done: true },
      { text: "Automated 'Right-to-be-Forgotten' erasure API", done: true },
      { text: "EU-US Data Privacy Framework contractual clauses", done: false },
    ],
    remediation: "Ensure all practitioner analytics ingest hashed identifiers and purge debug logs after 30 days.",
  },
  {
    id: "hipaa",
    name: "HIPAA / Medical Data",
    icon: Lock,
    accent: "var(--accent-competitor)",
    severity: "critical",
    severityLabel: "Critical Severity",
    desc: "Strict federal standards for handling Protected Health Information (PHI). Failure to isolate PHI triggers mandatory reporting penalties.",
    checklist: [
      { text: "End-to-end data encryption at rest (AES-256) & transit (TLS 1.3)", done: true },
      { text: "Signed Business Associate Agreement (BAA) with infrastructure host", done: false },
      { text: "Automated PHI redaction scrub pipeline before model inference", done: false },
    ],
    remediation: "Enforce zero-PHI storage boundary. If processing clinical records, isolate tenant environments onto dedicated VPCs.",
  },
  {
    id: "financial",
    name: "Financial / SOC 2 & PCI-DSS",
    icon: CreditCard,
    accent: "var(--accent-market)",
    severity: "high",
    severityLabel: "High Severity",
    desc: "Standards for payment card processing security and internal SaaS access controls, tenant isolation, and audit trail capture.",
    checklist: [
      { text: "Card checkout fully offloaded to Stripe Elements / PCI-DSS Level 1", done: true },
      { text: "Role-based access control (RBAC) & mandatory MFA for admins", done: true },
      { text: "SOC 2 Type II continuous evidence collection and annual audit", done: false },
    ],
    remediation: "Never log raw credit card numbers or banking secrets. Maintain tamper-evident audit trails for all billing transactions.",
  },
  {
    id: "ai_gov",
    name: "AI Governance & EU AI Act",
    icon: Brain,
    accent: "var(--accent-market)",
    severity: "high",
    severityLabel: "High Severity",
    desc: "Regulatory transparency requirements for AI-generated benchmarks, model hallucination prevention, and training data provenance.",
    checklist: [
      { text: "Clear labeling on all AI-synthesized market benchmarks", done: true },
      { text: "Prompt injection guardrails on user input fields", done: true },
      { text: "Documented accuracy benchmarks and human-in-the-loop fallback", done: false },
    ],
    remediation: "Display explicit confidence ratings alongside synthetic outputs and cite verifiable web sources for evidence backing.",
  },
];

export default function ComplianceScreen({ ideaDomain = "" }) {
  return (
    <section className="compliance-container" id="section-compliance">
      {/* Header */}
      <div className="compliance-header-wrap">
        <span className="compliance-eyebrow">
          <span className="compliance-eyebrow-dot" aria-hidden="true" />
          <span>GOVERNANCE & STANDARDS AUDIT</span>
        </span>
        <h3 className="compliance-title">Regulatory & Compliance Risk Screen</h3>
        <p className="compliance-subcopy">
          Automated evaluation of cross-jurisdictional compliance friction across data privacy, healthcare, payments, and AI governance frameworks.
        </p>
      </div>

      {/* Summary Matrix Strip */}
      <div className="compliance-summary-strip">
        <div className="compliance-metric-card">
          <span className="compliance-metric-label">TOTAL FRAMEWORKS</span>
          <span className="compliance-metric-val">4 Evaluated</span>
        </div>
        <div className="compliance-metric-card">
          <span className="compliance-metric-label">CRITICAL HURDLES</span>
          <span className="compliance-metric-val" style={{ color: "var(--accent-competitor)" }}>1 Blocker (HIPAA)</span>
        </div>
        <div className="compliance-metric-card">
          <span className="compliance-metric-label">HIGH CAUTION</span>
          <span className="compliance-metric-val" style={{ color: "var(--accent-market)" }}>2 Frameworks</span>
        </div>
        <div className="compliance-metric-card">
          <span className="compliance-metric-label">CLEARANCE RATE</span>
          <span className="compliance-metric-val" style={{ color: "var(--accent-feasibility)" }}>62% Ready</span>
        </div>
      </div>

      {/* 4 Frameworks Grid */}
      <div className="compliance-frameworks-grid">
        {FRAMEWORKS.map((fw) => {
          const IconComp = fw.icon;
          return (
            <div key={fw.id} className="compliance-chip-card">
              <div className="compliance-chip-top">
                <div className="compliance-chip-name-row">
                  <div
                    className="compliance-chip-icon-box"
                    style={{
                      background: `rgba(${fw.severity === "critical" ? "242, 61, 92" : fw.severity === "high" ? "255, 138, 31" : "255, 199, 44"}, 0.12)`,
                      color: fw.accent,
                    }}
                  >
                    <IconComp size={16} strokeWidth={1.5} />
                  </div>
                  <span className="compliance-chip-title">{fw.name}</span>
                </div>

                {/* Severity Badge */}
                <span className={`compliance-severity-badge ${fw.severity}`}>
                  <span>{fw.severityLabel}</span>
                </span>
              </div>

              <p className="compliance-chip-desc">{fw.desc}</p>

              {/* Requirement Checklist */}
              <ul className="compliance-checklist">
                {fw.checklist.map((item, idx) => (
                  <li key={idx} className="compliance-check-item">
                    {item.done ? (
                      <CheckCircle2 className="compliance-check-icon" size={14} color="var(--accent-feasibility)" />
                    ) : (
                      <AlertCircle className="compliance-check-icon" size={14} color="var(--text-tertiary)" />
                    )}
                    <span style={{ color: item.done ? "var(--text-primary)" : "var(--text-secondary)" }}>
                      {item.text}
                    </span>
                  </li>
                ))}
              </ul>

              {/* Founder Remediation Action */}
              <div className="compliance-remediation-box">
                <span className="compliance-remediation-label">RECOMMENDED ACTION</span>
                <span className="compliance-remediation-text">{fw.remediation}</span>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
