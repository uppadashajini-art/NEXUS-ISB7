import { useState, useEffect } from "react";
import confetti from "canvas-confetti";

import StartupAdvisor from "../components/StartupAdvisor";
import ResultsDashboard from "../components/ResultsDashboard";

import Navbar from "../components/Navbar";
import AuthModal from "../components/AuthModal";
import SupabaseConfigModal from "../components/SupabaseConfigModal";
import ActivityLogModal from "../components/ActivityLogModal";
import AdvisorySlideOver from "../components/AdvisorySlideOver";

import { useAuth } from "../context/AuthContext";
import {
  saveValidationActivity,
} from "../services/supabaseClient";
import { validateIdea } from "../services/validationService";

import {
  SparklesIcon,
  HistoryIcon,
  ArrowRightIcon,
  CloseIcon,
} from "../components/Icons";

const INSPIRATION_IDEAS = [
  {
    id: "sre",
    badge: "DevOps & Cloud",
    badgeClass: "studio-badge-idea",
    title: "Kubernetes AI SRE",
    idea:
      "Autonomous AI site reliability engineer for Kubernetes clusters that predicts outages from Prometheus metrics and auto-submits GitOps PRs.",
    domain: "DevOps & Cloud Infrastructure",
    target: "Enterprise DevOps & Platform Engineers",
  },
  {
    id: "scribe",
    badge: "HealthTech",
    badgeClass: "studio-badge-customer",
    title: "Ambient Oncology Scribe",
    idea:
      "Ambient voice AI for specialist oncologists that automatically produces structured clinical EHR notes and matches rare disease patients to open clinical trials.",
    domain: "Healthcare & BioTech",
    target: "Private Oncology & Specialty Clinics",
  },
  {
    id: "escrow",
    badge: "FinTech",
    badgeClass: "studio-badge-market",
    title: "Cross-Border Escrow Micro-SaaS",
    idea:
      "Instant cross-border B2B settlement agent with automated invoice OCR reconciliation and smart dispute escrow.",
    domain: "FinTech & Payments",
    target: "SMB Exporters and Global Freelance Agencies",
  },
  {
    id: "carbon",
    badge: "ClimateTech",
    badgeClass: "studio-badge-feasibility",
    title: "Real-time Cloud Carbon API",
    idea:
      "Developer API that hooks into AWS and GCP billing lines to quantify Scope 1-3 cloud carbon emissions and recommend green workload scheduling.",
    domain: "ClimateTech & SaaS",
    target: "Engineering Leaders at ESG-committed Enterprises",
  },
];

function StartupValidator({ onNavigateToStyleguide }) {
  const {
    user,
    updateActivityCount,
    activityCount,
  } = useAuth();

  // =========================================
  // MODALS / NAVIGATION STATE
  // =========================================

  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [supabaseModalOpen, setSupabaseModalOpen] = useState(false);
  const [historyModalOpen, setHistoryModalOpen] = useState(false);

  const [activeTab, setActiveTab] = useState("validator");

  const [toastMessage, setToastMessage] = useState("");
  const [loadedFromHistoryMeta, setLoadedFromHistoryMeta] =
    useState(null);

  // =========================================
  // FORM STATE
  // =========================================

  const [idea, setIdea] = useState("");
  const [domain, setDomain] = useState("");
  const [targetCustomers, setTargetCustomers] = useState("");

  const [animatingField, setAnimatingField] = useState(null);
  const [activeTemplateIdx, setActiveTemplateIdx] = useState(null);

  const [isAdvisoryOpen, setIsAdvisoryOpen] = useState(false);

  // =========================================
  // SEARCH / LOADING STATE
  // =========================================

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // =========================================
  // SUBMITTED VALUES
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

  const [validationResult, setValidationResult] = useState(null);

  const [validationLoading, setValidationLoading] =
    useState(false);

  const [validationError, setValidationError] = useState("");

  // =========================================
  // VALIDATION OPTIONS
  // =========================================

  const validationOptions = [
    {
      id: "all",
      title: "Full Analysis",
      dotColor: "#FFC72C",
      description:
        "Holistic multi-vector synthesis across market demand, competitor moats, ICPs, and launch strategy.",
    },
    {
      id: "market",
      title: "Market Sizing",
      dotColor: "#FF8A1F",
      description:
        "TAM, SAM, SOM quantitative projections, market CAGR velocity, and adoption tailwinds.",
    },
    {
      id: "competition",
      title: "Competitors & Gaps",
      dotColor: "#F23D5C",
      description:
        "Direct and indirect feature benchmark, incumbent moats, and unaddressed market white-spaces.",
    },
    {
      id: "customers",
      title: "Target Customers",
      dotColor: "#FF5A4E",
      description:
        "Detailed ICP profiles, customer pain severity breakdown, and high-conversion acquisition loops.",
    },
    {
      id: "feasibility",
      title: "Tech Feasibility",
      dotColor: "#2DD4BF",
      description:
        "Architecture constraints, API dependency risks, compliance friction, and implementation hurdles.",
    },
    {
      id: "mvp",
      title: "MVP & Scope",
      dotColor: "#8B7CF6",
      description:
        "Prioritized MVP feature cut, non-essential backlog pruning, and 90-day milestone roadmap.",
    },
  ];

  const selectedValidation =
    validationOptions.find(
      (option) => option.id === selectedOption
    ) || validationOptions[0];

  const isIdeaValid = idea.trim().length >= 40;

  // =========================================
  // ADVISORY COPILOT SHORTCUT
  // =========================================

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (
        (e.metaKey || e.ctrlKey) &&
        e.key.toLowerCase() === "j"
      ) {
        e.preventDefault();

        setIsAdvisoryOpen((prev) => !prev);
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  // =========================================
  // CTRL / CMD + ENTER
  // =========================================

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (
        (e.ctrlKey || e.metaKey) &&
        e.key === "Enter"
      ) {
        e.preventDefault();

        const formEl =
          document.getElementById("validator-form");

        if (formEl) {
          if (formEl.requestSubmit) {
            formEl.requestSubmit();
          } else {
            formEl.dispatchEvent(
              new Event("submit", {
                cancelable: true,
                bubbles: true,
              })
            );
          }
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  // =========================================
  // TEMPLATE SELECTION
  // =========================================

  const handleSelectInspiration = (item, idx) => {
    setActiveTemplateIdx(idx);

    setError("");
    setValidationError("");
    setLoadedFromHistoryMeta(null);

    setIdea(item.idea);
    setAnimatingField("idea");

    setTimeout(() => {
      setDomain(item.domain);
      setAnimatingField("domain");
    }, 200);

    setTimeout(() => {
      setTargetCustomers(item.target);
      setAnimatingField("target");
    }, 400);

    setTimeout(() => {
      setAnimatingField(null);
    }, 700);

    setTimeout(() => {
      document.getElementById("startup-idea")?.focus();
    }, 450);
  };

  // =========================================
  // SCROLL TO INPUT
  // =========================================

  const handleScrollToInput = () => {
    const el = document.getElementById("startup-idea");

    if (el) {
      el.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });

      el.focus();
    }
  };

  // =========================================
  // LOAD IDEA FROM HISTORY
  // =========================================

  const handleLoadIdeaFromHistory = (activity) => {
    setIdea(activity.idea || "");
    setDomain(activity.domain || "");
    setTargetCustomers(
      activity.target_customer || ""
    );

    setSelectedOption(
      activity.validation_type || "all"
    );

    setSubmittedIdea(activity.idea || "");
    setSubmittedDomain(activity.domain || "");
    setSubmittedCustomers(
      activity.target_customer || ""
    );

    setSubmittedValidation(
      activity.validation_type || "all"
    );

    const full = activity.full_result || {};

    setValidationResult(full);

    setResults(
      Array.isArray(full.search_results)
        ? full.search_results
        : []
    );

    setSearchCompleted(true);

    setLoading(false);
    setValidationLoading(false);

    setError("");
    setValidationError("");

    setLoadedFromHistoryMeta({
      id: activity.id,
      title: activity.idea_title,
      score: activity.viability_score,
      overallScore: activity.viability_score,
      domain: activity.domain,
      created_at: activity.created_at,
    });

    setToastMessage(
      `📂 Restored "${activity.idea_title}" from Activity Log!`
    );

    setTimeout(() => {
      setToastMessage("");
    }, 5000);

    setTimeout(() => {
      document
        .getElementById("results-dashboard")
        ?.scrollIntoView({
          behavior: "smooth",
        });
    }, 120);
  };

  // =========================================
  // DUPLICATE IDEA
  // =========================================

  const handleDuplicateIdea = (activity) => {
    setIdea(activity.idea || "");
    setDomain(activity.domain || "");

    setTargetCustomers(
      activity.target_customer || ""
    );

    setSelectedOption(
      activity.validation_type || "all"
    );

    setError("");
    setValidationError("");

    setLoadedFromHistoryMeta(null);

    setToastMessage(
      `📋 Cloned "${
        activity.idea_title || "idea"
      }" into form for iteration!`
    );

    setTimeout(() => {
      setToastMessage("");
    }, 5000);

    setTimeout(() => {
      handleScrollToInput();
    }, 150);
  };

  // =========================================
  // EXPORT MARKDOWN DOSSIER
  // =========================================

  const handleExportActiveDossier = () => {
    if (!validationResult) return;

    const report =
      validationResult.validation_report || {};

    let content =
      `# NEXUS Startup Validation Dossier\n\n`;

    content += `**Startup Idea**: ${
      submittedIdea || idea
    }\n`;

    content += `**Domain / Industry**: ${
      submittedDomain ||
      domain ||
      "Technology"
    }\n`;

    content += `**Target Customer**: ${
      submittedCustomers ||
      targetCustomers ||
      "General Market"
    }\n`;

    content += `**Generated Date**: ${new Date().toLocaleString()}\n\n`;

    content += `---\n\n`;

    content += `## Executive Summary\n${
      report.executive_summary ||
      "Complete AI validation dossier."
    }\n\n`;

    if (validationResult.market_analysis) {
      content += `## Market Opportunity\n${
        validationResult.market_analysis
          .market_opportunity || ""
      }\n\n`;

      if (
        validationResult.market_analysis.market_trends
      ) {
        content += `### Market Trends\n`;

        validationResult.market_analysis.market_trends.forEach(
          (trend) => {
            content += `- ${trend}\n`;
          }
        );

        content += `\n`;
      }
    }

    if (
      validationResult.competitor_analysis
        ?.direct_competitors
    ) {
      content += `## Competitor Landscape\n`;

      validationResult.competitor_analysis.direct_competitors.forEach(
        (competitor) => {
          content += `### ${competitor.name}\n`;

          if (competitor.strengths) {
            content += `- Strengths: ${competitor.strengths.join(
              ", "
            )}\n`;
          }

          if (competitor.weaknesses) {
            content += `- Weaknesses: ${competitor.weaknesses.join(
              ", "
            )}\n`;
          }
        }
      );

      content += `\n`;
    }

    if (
      validationResult.mvp_recommendations
        ?.must_have
    ) {
      content += `## Must-Have MVP Features\n`;

      validationResult.mvp_recommendations.must_have.forEach(
        (feature) => {
          content += `- **${feature.feature}**: ${
            feature.reason || ""
          }\n`;
        }
      );

      content += `\n`;
    }

    content += `---\n`;

    content +=
      `*Generated by NEXUS AI Intelligence Engine*\n`;

    const blob = new Blob([content], {
      type: "text/markdown",
    });

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");

    a.href = url;

    a.download = `nexus_validation_${
      (
        submittedDomain ||
        domain ||
        "startup"
      ).replace(/[^a-zA-Z0-9]/g, "_")
    }.md`;

    a.click();

    URL.revokeObjectURL(url);

    setToastMessage(
      "📄 Markdown dossier exported successfully!"
    );

    setTimeout(() => {
      setToastMessage("");
    }, 4000);
  };

  // =========================================
  // FORM SUBMIT
  // =========================================

  const handleSubmit = async (e) => {
    e.preventDefault();

    const trimmedIdea = idea.trim();
    const trimmedDomain = domain.trim();
    const trimmedCustomers =
      targetCustomers.trim();

    if (!trimmedIdea) {
      setError(
        "Please describe your startup concept."
      );
      return;
    }

    if (trimmedIdea.length < 40) {
      setError(
        `Please provide at least 40 characters describing your concept (${trimmedIdea.length}/40).`
      );
      return;
    }

    // =========================================
    // START LOADING
    // =========================================

    setLoading(true);
    setValidationLoading(true);

    setError("");
    setValidationError("");

    setResults([]);
    setSearchCompleted(false);
    setValidationResult(null);

    setLoadedFromHistoryMeta(null);

    setSubmittedIdea(trimmedIdea);
    setSubmittedDomain(trimmedDomain);
    setSubmittedCustomers(trimmedCustomers);
    setSubmittedValidation(selectedOption);

    // Scroll to top of analysis workspace
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });

    try {
      const analysisData = await validateIdea(
        trimmedIdea,
        trimmedDomain,
        trimmedCustomers,
        selectedOption
      );

      const searchResults =
        Array.isArray(
          analysisData?.search_results
        )
          ? analysisData.search_results
          : [];

      setResults(searchResults);

      setValidationResult(analysisData);

      setSearchCompleted(true);

      // =========================================
      // AUTO SAVE TO SUPABASE
      // =========================================

      try {
        const currentUserId =
          user?.id ||
          (user?.email
            ? user.email
            : "active_founder_id");

        const currentUserEmail =
          user?.email ||
          "founder@nexus-intelligence.ai";

        const saveRes =
          await saveValidationActivity({
            userId: currentUserId,
            userEmail: currentUserEmail,
            idea: trimmedIdea,
            domain: trimmedDomain,
            targetCustomer:
              trimmedCustomers,
            validationType: selectedOption,
            fullResult: analysisData,
          });

        if (saveRes?.savedToSupabase) {
          setToastMessage(
            "✨ Idea validated & saved to your Supabase Cloud Activity Log!"
          );
        } else {
          setToastMessage(
            "✨ Idea validated & saved to your Activity Log!"
          );
        }

        updateActivityCount(
          activityCount + 1
        );

        // =========================================
        // CONFETTI
        // =========================================

        try {
          confetti({
            particleCount: 80,
            spread: 70,
            origin: {
              y: 0.65,
            },
            colors: [
              "#6366f1",
              "#e8c77b",
              "#38bdf8",
              "#ec4899",
              "#10b981",
            ],
          });
        } catch {
          // Ignore confetti errors
        }
      } catch (saveErr) {
        console.warn(
          "Could not save to activity log:",
          saveErr
        );
      }

      setTimeout(() => {
        setToastMessage("");
      }, 6000);
    } catch (err) {
      console.error(
        "Validation error:",
        err
      );

      const errorMessage =
        err?.message ||
        "Unable to validate the startup idea. Please try again.";

      if (
        errorMessage
          .toLowerCase()
          .includes("analysis")
      ) {
        setValidationError(
          errorMessage
        );

        setValidationResult(null);
      } else {
        setError(errorMessage);

        setSearchCompleted(false);
      }
    } finally {
      setLoading(false);
      setValidationLoading(false);
    }
  };

  // =========================================
  // RETRY
  // =========================================

  const handleRetry = () => {
    if (!submittedIdea) return;

    setIdea(submittedIdea);
    setDomain(submittedDomain);
    setTargetCustomers(
      submittedCustomers
    );

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
  // CLEAR / NEW ANALYSIS
  // =========================================

  const handleClear = () => {
    setIdea("");
    setDomain("");
    setTargetCustomers("");

    setResults([]);

    setValidationResult(null);

    setLoading(false);
    setValidationLoading(false);

    setValidationError("");
    setError("");

    setSubmittedIdea("");
    setSubmittedDomain("");
    setSubmittedCustomers("");

    setSubmittedValidation("all");

    setSearchCompleted(false);

    setSelectedOption("all");

    setActiveTemplateIdx(null);

    setLoadedFromHistoryMeta(null);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  // =========================================
  // INPUT CHANGE
  // =========================================

  const handleIdeaChange = (e) => {
    setIdea(e.target.value);

    if (error) {
      setError("");
    }
  };

  const handleCustomerChange = (e) => {
    setTargetCustomers(
      e.target.value
    );

    if (error) {
      setError("");
    }
  };

  // =========================================
  // RENDER
  // =========================================

  return (
    <div className="nexus-app-wrapper nexus-app-shell">

      {/* =================================================
          NAVBAR
          ================================================= */}

      <Navbar
        onOpenAuth={() =>
          setAuthModalOpen(true)
        }
        onOpenHistory={() =>
          setHistoryModalOpen(true)
        }
        onOpenSupabase={() =>
          setSupabaseModalOpen(true)
        }
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onNavigateToStyleguide={
          onNavigateToStyleguide
        }
      />

      {/* =================================================
          FLOATING SYSTEM TOAST
          ================================================= */}

      {toastMessage && (
        <aside
          aria-label="System notification"
          className="nexus-floating-toast"
        >
          <div className="toast-sparkle">
            <SparklesIcon size={16} />
          </div>

          <p className="toast-text">
            {toastMessage}
          </p>

          <button
            type="button"
            className="toast-action-btn"
            onClick={() =>
              setHistoryModalOpen(true)
            }
          >
            <span>View Log</span>

            <ArrowRightIcon size={13} />
          </button>

          <button
            type="button"
            className="toast-close-btn"
            onClick={() =>
              setToastMessage("")
            }
            aria-label="Close notification"
          >
            <CloseIcon size={14} />
          </button>
        </aside>
      )}

      <main className="startup-validator nexus-shell-container page-shell-transition">

        {/* =================================================
            HISTORY BANNER
            ================================================= */}

        {loadedFromHistoryMeta && (
          <div className="active-history-banner">
            <div className="banner-left">
              <span className="banner-pulse" />

              <div className="banner-text">
                <span>
                  Loaded from Activity Log:
                </span>

                <strong>
                  {loadedFromHistoryMeta.domain ||
                    "Startup Analysis"}
                </strong>

                {loadedFromHistoryMeta.overallScore !==
                  undefined &&
                  loadedFromHistoryMeta.overallScore !==
                    null && (
                    <span className="banner-score-tag">
                      Score:{" "}
                      {
                        loadedFromHistoryMeta.overallScore
                      }
                      /100
                    </span>
                  )}
              </div>
            </div>

            <div className="banner-right">
              <button
                type="button"
                className="banner-new-btn"
                onClick={handleClear}
              >
                New Analysis
              </button>
            </div>
          </div>
        )}

        {/* =================================================
            NORMAL INPUT PAGE
            HIDDEN DURING VALIDATION
            ================================================= */}

        {!loading && (
          <>
            {/* PAGE HEADER */}

            <header className="studio-header">

              <div className="studio-eyebrow">
                <span
                  className="studio-live-dot"
                  aria-hidden="true"
                />

                <span>
                  FOUNDER ANALYTICS
                </span>
              </div>

              <h1 className="studio-title">
                Market & Competitor Analysis
                for Founders
              </h1>

              <p className="studio-subcopy">
                Validate startup concepts against
                live incumbent moats, customer
                segments, and feasibility signals
                in seconds.
              </p>

              {/* TEMPLATES */}

              <div className="studio-templates-section">
                <span className="studio-templates-label">
                  Templates:
                </span>

                <div className="studio-templates-grid">
                  {INSPIRATION_IDEAS.map(
                    (item, idx) => (
                      <button
                        key={item.id}
                        type="button"
                        className={`studio-template-chip ${
                          activeTemplateIdx === idx
                            ? "active"
                            : ""
                        }`}
                        onClick={() =>
                          handleSelectInspiration(
                            item,
                            idx
                          )
                        }
                        aria-label={`Load template: ${item.title}`}
                      >
                        <span className="studio-template-chip-title">
                          {item.title}
                        </span>

                        <span
                          className={`studio-industry-badge ${item.badgeClass}`}
                        >
                          {item.badge}
                        </span>
                      </button>
                    )
                  )}
                </div>
              </div>
            </header>

            {/* =================================================
                FORM CARD
                ================================================= */}

            <section className="studio-form-card">
              <form
                id="validator-form"
                onSubmit={handleSubmit}
                noValidate
              >
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "24px",
                  }}
                >

                  {/* STARTUP CONCEPT */}

                  <div className="studio-field-group">
                    <div className="studio-field-label-row">

                      <label
                        htmlFor="startup-idea"
                        className="studio-field-label"
                      >
                        Startup Concept /
                        Problem Statement
                      </label>

                      <div className="studio-counter-row">

                        <span className="studio-char-count">
                          {idea.length} characters
                        </span>

                        <span className="studio-optional-tag">
                          •
                        </span>

                        <span
                          className={`studio-min-hint ${
                            idea.trim().length >= 40
                              ? "ready"
                              : "pending"
                          }`}
                        >
                          {idea.trim().length >=
                          40
                            ? "✓ Ready"
                            : `${
                                40 -
                                idea.trim()
                                  .length
                              } more chars needed`}
                        </span>

                      </div>
                    </div>

                    <textarea
                      id="startup-idea"
                      value={idea}
                      onChange={
                        handleIdeaChange
                      }
                      placeholder="Describe the problem, target audience, and business model for live market benchmarking (e.g. Autonomous AI site reliability engineer for Kubernetes clusters that predicts outages...)"
                      rows={4}
                      disabled={loading}
                      aria-required="true"
                      aria-invalid={Boolean(
                        error
                      )}
                      className={`studio-textarea ${
                        animatingField ===
                        "idea"
                          ? "field-stagger-pop"
                          : ""
                      } ${
                        error
                          ? "invalid"
                          : ""
                      }`}
                    />

                    {error && (
                      <div
                        className="studio-inline-error"
                        role="alert"
                      >
                        <span
                          className="studio-error-dot"
                          aria-hidden="true"
                        />

                        <span>
                          {error}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* INDUSTRY + CUSTOMER */}

                  <div className="studio-two-col">

                    <div className="studio-field-group">

                      <div className="studio-field-label-row">

                        <label
                          htmlFor="startup-domain"
                          className="studio-field-label"
                        >
                          Industry / Domain
                        </label>

                        <span className="studio-optional-tag">
                          Optional
                        </span>

                      </div>

                      <input
                        id="startup-domain"
                        type="text"
                        value={domain}
                        onChange={(e) =>
                          setDomain(
                            e.target.value
                          )
                        }
                        placeholder="e.g. DevOps, HealthTech, FinTech"
                        disabled={loading}
                        className={`studio-input ${
                          animatingField ===
                          "domain"
                            ? "field-stagger-pop"
                            : ""
                        }`}
                      />

                    </div>

                    <div className="studio-field-group">

                      <div className="studio-field-label-row">

                        <label
                          htmlFor="target-customers"
                          className="studio-field-label"
                        >
                          Target Customer /
                          ICP
                        </label>

                        <span className="studio-optional-tag">
                          Optional
                        </span>

                      </div>

                      <input
                        id="target-customers"
                        type="text"
                        value={
                          targetCustomers
                        }
                        onChange={
                          handleCustomerChange
                        }
                        placeholder="e.g. Enterprise Platform Engineers, SMB Clinics"
                        disabled={loading}
                        className={`studio-input ${
                          animatingField ===
                          "target"
                            ? "field-stagger-pop"
                            : ""
                        }`}
                      />

                    </div>

                  </div>

                  {/* ANALYSIS SCOPE */}

                  <div className="studio-scope-section">

                    <div className="studio-field-label-row">
                      <label className="studio-field-label">
                        Analysis Scope
                      </label>
                    </div>

                    <div
                      className="studio-scope-grid"
                      role="radiogroup"
                      aria-label="Analysis Scope"
                    >
                      {validationOptions.map(
                        (option) => {
                          const isSelected =
                            selectedOption ===
                            option.id;

                          return (
                            <button
                              key={option.id}
                              type="button"
                              role="radio"
                              aria-checked={
                                isSelected
                              }
                              disabled={
                                loading
                              }
                              className={`studio-scope-btn ${
                                isSelected
                                  ? "active"
                                  : ""
                              }`}
                              onClick={() =>
                                setSelectedOption(
                                  option.id
                                )
                              }
                            >
                              <span
                                className="studio-scope-dot"
                                style={{
                                  backgroundColor:
                                    option.dotColor,
                                }}
                                aria-hidden="true"
                              />

                              <span className="studio-scope-title">
                                {
                                  option.title
                                }
                              </span>
                            </button>
                          );
                        }
                      )}
                    </div>

                    <div className="studio-scope-desc-box">

                      <span
                        className="studio-scope-dot"
                        style={{
                          backgroundColor:
                            selectedValidation.dotColor,
                        }}
                        aria-hidden="true"
                      />

                      <span>
                        <strong className="studio-scope-desc-strong">
                          {
                            selectedValidation.title
                          }
                          :
                        </strong>{" "}
                        {
                          selectedValidation.description
                        }
                      </span>

                    </div>
                  </div>

                  {/* CTA */}

                  <div className="studio-cta-bar">

                    <button
                      type="submit"
                      disabled={
                        loading ||
                        !isIdeaValid
                      }
                      className="studio-primary-cta"
                      aria-label="Run Market and Competitor Analysis"
                    >
                      <span>
                        Run Analysis
                      </span>

                      <ArrowRightIcon
                        size={14}
                      />

                      <kbd className="studio-cta-shortcut-badge">
                        {typeof navigator !==
                          "undefined" &&
                        navigator.platform
                          ?.toUpperCase()
                          .indexOf(
                            "MAC"
                          ) >= 0
                          ? "⌘↵"
                          : "Ctrl+↵"}
                      </kbd>
                    </button>

                    <span className="studio-cta-caption">
                      Queries live web data
                      via Tavily API,
                      benchmarks
                      competitors, and
                      calculates market
                      sizing.
                    </span>

                  </div>

                </div>
              </form>
            </section>

            {/* =================================================
                SYSTEM ENGINES
                ================================================= */}

            {/* Keep this here if you want the four analysis
                modules visible before starting validation. */}

            {/* 
            <SystemEnginesShowcase
              onScrollToInput={
                handleScrollToInput
              }
            />
            */}

          </>
        )}

        {/* =================================================
            NEW LOADING WORKSPACE
            ================================================= */}

        {loading && (
          <section className="validation-loading-workspace">

            {/* HEADER */}

            <div className="loading-workspace-header">

              <div>
                <span className="dashboard-eyebrow">
                  FOUNDER ANALYTICS
                </span>

                <h2>
                  Validating your startup idea
                </h2>

                <p>
                  Live intelligence is being
                  gathered and synthesized into
                  your validation report.
                </p>
              </div>

              <div className="loading-live-badge">
                <span className="loading-live-dot" />

                LIVE ANALYSIS
              </div>

            </div>

            {/* MAIN TWO COLUMN WORKSPACE */}

            <div className="loading-workspace-grid">

              {/* =========================================
                  LEFT — STARTUP CONTEXT
                  ========================================= */}

              <div className="loading-context-card">

                <span className="loading-card-label">
                  YOUR STARTUP
                </span>

                <div className="loading-context-section">

                  <span>
                    Problem statement
                  </span>

                  <strong>
                    {submittedIdea ||
                      idea ||
                      "Your startup idea"}
                  </strong>

                </div>

                <div className="loading-context-row">

                  <div>
                    <span>
                      Industry
                    </span>

                    <strong>
                      {submittedDomain ||
                        domain ||
                        "Not specified"}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Target customer
                    </span>

                    <strong>
                      {submittedCustomers ||
                        targetCustomers ||
                        "Not specified"}
                    </strong>
                  </div>

                </div>

                <div className="loading-scope">

                  <span>
                    ANALYSIS SCOPE
                  </span>

                  <strong>
                    {
                      (
                        validationOptions.find(
                          (option) =>
                            option.id ===
                            submittedValidation
                        ) ||
                        selectedValidation
                      ).title
                    }
                  </strong>

                </div>

                <div className="loading-context-footer">

                  <span className="loading-pulse" />

                  NEXUS intelligence engine
                  is working

                </div>

              </div>

              {/* =========================================
                  RIGHT — LIVE INTELLIGENCE
                  ========================================= */}

              <div className="loading-stream-card">

                <div className="loading-stream-header">

                  <div>

                    <span className="loading-card-label">
                      LIVE INTELLIGENCE STREAM
                    </span>

                    <h3>
                      Building your
                      validation report
                    </h3>

                  </div>

                  <SparklesIcon
                    size={18}
                  />

                </div>

                {/* PIPELINE */}

                <div className="loading-pipeline">

                  {/* STEP 1 */}

                  <div className="loading-pipeline-item active">

                    <div className="pipeline-icon">
                      01
                    </div>

                    <div>
                      <strong>
                        Searching live web
                        sources
                      </strong>

                      <p>
                        Gathering current
                        market and customer
                        intelligence...
                      </p>
                    </div>

                    <span className="pipeline-status">
                      LIVE
                    </span>

                  </div>

                  <div className="loading-pipeline-line" />

                  {/* STEP 2 */}

                  <div className="loading-pipeline-item active">

                    <div className="pipeline-icon">
                      02
                    </div>

                    <div>
                      <strong>
                        Benchmarking
                        competitors
                      </strong>

                      <p>
                        Comparing competitors
                        and incumbent feature
                        moats...
                      </p>
                    </div>

                    <span className="pipeline-status">
                      RUNNING
                    </span>

                  </div>

                  <div className="loading-pipeline-line" />

                  {/* STEP 3 */}

                  <div className="loading-pipeline-item">

                    <div className="pipeline-icon">
                      03
                    </div>

                    <div>
                      <strong>
                        Calculating market
                        sizing
                      </strong>

                      <p>
                        Modeling TAM, SAM
                        and SOM market
                        opportunity...
                      </p>
                    </div>

                  </div>

                  <div className="loading-pipeline-line" />

                  {/* STEP 4 */}

                  <div className="loading-pipeline-item">

                    <div className="pipeline-icon">
                      04
                    </div>

                    <div>
                      <strong>
                        Generating strategic
                        roadmap
                      </strong>

                      <p>
                        Synthesizing MVP
                        specifications and
                        launch strategy...
                      </p>
                    </div>

                  </div>

                </div>

                {/* ANIMATED PROGRESS */}

                <div className="loading-progress-track">
                  <div className="loading-progress-bar" />
                </div>

                <div className="loading-progress-footer">

                  <span>
                    Analyzing multiple
                    intelligence vectors
                  </span>

                  <span>
                    Please wait...
                  </span>

                </div>

              </div>

            </div>

          </section>
        )}

        {/* =================================================
            GENERAL ERROR
            ================================================= */}

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
                    onClick={
                      handleRetry
                    }
                  >
                    ↻ Retry Validation
                  </button>

                </div>

              </div>

            </div>

          </section>
        )}

        {/* =================================================
            VALIDATION ERROR
            ================================================= */}

        {validationError &&
          !loading && (
            <section className="error-section">

              <div className="error-card">

                <div className="error-icon">
                  !
                </div>

                <div className="error-content">

                  <span className="mini-label">
                    ANALYSIS ERROR
                  </span>

                  <h3>
                    Analysis could not
                    be completed
                  </h3>

                  <p>
                    {validationError}
                  </p>

                  <div className="error-actions">

                    <button
                      type="button"
                      className="retry-button"
                      onClick={
                        handleRetry
                      }
                    >
                      ↻ Retry Validation
                    </button>

                  </div>

                </div>

              </div>

            </section>
          )}

        {/* =================================================
            VALIDATION RESULTS DASHBOARD
            ================================================= */}

        {(validationResult ||
          searchCompleted) &&
          !loading &&
          !error &&
          !validationError && (
            <section
              id="results-dashboard"
              style={{
                width: "100%",
                margin: "0 auto",
              }}
            >

              <ResultsDashboard
                validationResult={
                  validationResult
                }
                searchResults={
                  results
                }
                submittedIdea={
                  submittedIdea ||
                  idea
                }
                submittedDomain={
                  submittedDomain ||
                  domain
                }
                submittedCustomers={
                  submittedCustomers ||
                  targetCustomers
                }
                onExport={
                  handleExportActiveDossier
                }
                onOpenHistory={() =>
                  setHistoryModalOpen(
                    true
                  )
                }
                onNewAnalysis={
                  handleClear
                }
              />

              {/* STARTUP ADVISOR */}

              {validationResult && (
                <StartupAdvisor
                  validationContext={{
                    ...validationResult,

                    idea:
                      validationResult.idea ||
                      submittedIdea ||
                      idea,

                    domain:
                      submittedDomain ||
                      domain ||
                      validationResult
                        ?.market_analysis
                        ?.industry,

                    target_customer:
                      submittedCustomers ||
                      targetCustomers ||
                      validationResult?.target_customer,
                  }}
                />
              )}

            </section>
          )}

        {/* =================================================
            EMPTY RESULTS
            ================================================= */}

        {!loading &&
          !error &&
          !validationError &&
          searchCompleted &&
          !validationResult &&
          (!results ||
            results.length === 0) && (
            <section className="empty-results">

              <div className="empty-icon">
                🔍
              </div>

              <h2>
                No Relevant Information
                Found
              </h2>

              <p>
                We couldn't find enough
                relevant information for
                this startup idea. Try
                adding more details.
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

      {/* =================================================
          AUTH MODAL
          ================================================= */}

      <AuthModal
        isOpen={authModalOpen}
        onClose={() =>
          setAuthModalOpen(false)
        }
      />

      {/* =================================================
          SUPABASE MODAL
          ================================================= */}

      <SupabaseConfigModal
        isOpen={supabaseModalOpen}
        onClose={() =>
          setSupabaseModalOpen(false)
        }
      />

      {/* =================================================
          ACTIVITY LOG
          ================================================= */}

      <ActivityLogModal
        isOpen={historyModalOpen}
        onClose={() =>
          setHistoryModalOpen(false)
        }
        onLoadIdeaIntoCanvas={
          handleLoadIdeaFromHistory
        }
        onDuplicateIdea={
          handleDuplicateIdea
        }
      />

      {/* =================================================
          ADVISORY COPILOT
          ================================================= */}

      <button
        type="button"
        className="advisory-float-trigger"
        onClick={() =>
          setIsAdvisoryOpen(true)
        }
        aria-label="Open Advisory Assistant"
      >
        <SparklesIcon size={15} />

        <span>
          Advisory Copilot
        </span>

        <kbd className="advisory-shortcut-badge">
          {typeof navigator !==
            "undefined" &&
          navigator.platform
            ?.toUpperCase()
            .indexOf("MAC") >= 0
            ? "⌘J"
            : "Ctrl+J"}
        </kbd>
      </button>

      {/* =================================================
          ADVISORY SLIDE OVER
          ================================================= */}

      <AdvisorySlideOver
        isOpen={isAdvisoryOpen}
        onClose={() =>
          setIsAdvisoryOpen(false)
        }
        currentIdea={
          submittedIdea || idea
        }
        validationResult={
          validationResult
        }
      />

    </div>
  );
}

export default StartupValidator;