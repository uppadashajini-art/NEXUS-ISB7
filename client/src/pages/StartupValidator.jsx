import { useState, useEffect } from "react";
import confetti from "canvas-confetti";

import StartupAdvisor from "../components/StartupAdvisor";
import ResultsDashboard from "../components/ResultsDashboard";
import StreamingProgressLoader from "../components/StreamingProgressLoader";

import Navbar from "../components/Navbar";
import AuthModal from "../components/AuthModal";
import SupabaseConfigModal from "../components/SupabaseConfigModal";
import ActivityLogModal from "../components/ActivityLogModal";
import AdvisorySlideOver from "../components/AdvisorySlideOver";

import { useAuth } from "../context/AuthContext";
import { saveValidationActivity } from "../services/supabaseClient";
import { validateIdea } from "../services/validationService";
import Footer from "../components/Footer";

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

function StartupValidator({
  onNavigateToStyleguide,
  theme,
  onToggleTheme,
}) {
  const {
    user,
    updateActivityCount,
    activityCount,
  } = useAuth();

  // =========================================
  // MODALS / NAVIGATION STATE
  // =========================================

  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [supabaseModalOpen, setSupabaseModalOpen] =
    useState(false);
  const [historyModalOpen, setHistoryModalOpen] =
    useState(false);

  const [activeTab, setActiveTab] =
    useState("validator");

  const [toastMessage, setToastMessage] =
    useState("");

  const [loadedFromHistoryMeta, setLoadedFromHistoryMeta] =
    useState(null);

  // =========================================
  // FORM STATE
  // =========================================

  const [idea, setIdea] = useState("");
  const [domain, setDomain] = useState("");
  const [targetCustomers, setTargetCustomers] =
    useState("");

  const [animatingField, setAnimatingField] =
    useState(null);

  const [activeTemplateIdx, setActiveTemplateIdx] =
    useState(null);

  const [isAdvisoryOpen, setIsAdvisoryOpen] =
    useState(false);

  // =========================================
  // KEYBOARD SHORTCUTS
  // =========================================

  // CMD / CTRL + J
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
      window.removeEventListener(
        "keydown",
        handleKeyDown
      );
    };
  }, []);

  // CTRL / CMD + ENTER
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
      window.removeEventListener(
        "keydown",
        handleKeyDown
      );
    };
  }, []);

  // =========================================
  // SEARCH / LOADING STATE
  // =========================================

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // =========================================
  // SUBMITTED VALUES
  // =========================================

  const [submittedIdea, setSubmittedIdea] =
    useState("");

  const [submittedDomain, setSubmittedDomain] =
    useState("");

  const [submittedCustomers, setSubmittedCustomers] =
    useState("");

  const [submittedValidation, setSubmittedValidation] =
    useState("all");

  // =========================================
  // VALIDATION STATE
  // =========================================

  const [searchCompleted, setSearchCompleted] =
    useState(false);

  const [selectedOption, setSelectedOption] =
    useState("all");

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

  const isIdeaValid =
    idea.trim().length >= 40;

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
      document
        .getElementById("startup-idea")
        ?.focus();
    }, 450);
  };

  // =========================================
  // SCROLL TO INPUT
  // =========================================

  const handleScrollToInput = () => {
    const el =
      document.getElementById("startup-idea");

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
        validationResult.market_analysis
          .market_trends
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

    // -----------------------------------------
    // VALIDATION
    // -----------------------------------------

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

    // -----------------------------------------
    // START LOADING
    // -----------------------------------------

    setLoading(true);
    setValidationLoading(true);

    setError("");
    setValidationError("");

    setResults([]);
    setSearchCompleted(false);
    setValidationResult(null);

    setLoadedFromHistoryMeta(null);

    // -----------------------------------------
    // SAVE SUBMITTED VALUES
    // -----------------------------------------

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
      const analysisData =
        await validateIdea(
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

      // Smoothly navigate founder to the top of the validation results dashboard
      setTimeout(() => {
        const dashboardEl = document.getElementById("results-dashboard");
        if (dashboardEl) {
          dashboardEl.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
        }
      }, 100);

      // -----------------------------------------
      // AUTO SAVE TO SUPABASE
      // -----------------------------------------

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

        // -----------------------------------------
        // CONFETTI
        // -----------------------------------------

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
        setValidationError(errorMessage);
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
  // INPUT HANDLERS
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

      {/* =====================================
          NAVBAR
      ===================================== */}

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
        theme={theme}
        onToggleTheme={onToggleTheme}
      />

      {/* =====================================
          FLOATING SYSTEM TOAST
      ===================================== */}

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

      {/* =====================================
          MAIN CONTENT
      ===================================== */}

      <main className="startup-validator nexus-shell-container page-shell-transition">

        {/* ===================================
            HISTORY BANNER
        =================================== */}

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

        {/* ===================================
            HOME / FOUNDER HEADER
        =================================== */}

        {!validationResult && (
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
              Validate Your Startup Idea
            </h1>

            <p className="studio-subcopy">
              Turn an early-stage idea into
              a data-backed validation report
              using live market, customer,
              competitor, and execution
              intelligence.
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
        )}

        {/* ===================================
            FORM CARD
        =================================== */}

        {!validationResult && (
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

                {/* STARTUP IDEA */}

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
                    onChange={handleIdeaChange}
                    placeholder="Describe the problem, target audience, and business model for live market benchmarking..."
                    rows={4}
                    disabled={loading}
                    aria-required="true"
                    aria-invalid={Boolean(error)}
                    className={`studio-textarea ${
                      animatingField === "idea"
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

                {/* DOMAIN + CUSTOMER */}

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
                        animatingField === "domain"
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
                      value={targetCustomers}
                      onChange={
                        handleCustomerChange
                      }
                      placeholder="e.g. Enterprise Platform Engineers, SMB Clinics"
                      disabled={loading}
                      className={`studio-input ${
                        animatingField === "target"
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
                            disabled={loading}
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
                              {option.title}
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
                        }:
                      </strong>{" "}

                      {
                        selectedValidation.description
                      }

                    </span>

                  </div>

                </div>

                {/* RUN ANALYSIS */}

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

                    {loading ? (
                      <>
                        <span
                          className="clean-spinner"
                          style={{
                            width: "16px",
                            height: "16px",
                            borderWidth: "2px",
                          }}
                        />

                        <span>
                          Synthesizing
                          Market
                          Intelligence...
                        </span>
                      </>
                    ) : (
                      <>
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
                            .indexOf("MAC") >= 0
                            ? "⌘↵"
                            : "Ctrl+↵"}
                        </kbd>
                      </>
                    )}

                  </button>

                  <span className="studio-cta-caption">
                    Queries live web
                    data via Tavily
                    API, benchmarks
                    competitors, and
                    calculates market
                    sizing.
                  </span>

                </div>

              </div>

            </form>

          </section>
        )}

        {/* ===================================
            FOUNDER DASHBOARD
            ONLY BEFORE VALIDATION
        =================================== */}

        {!validationResult &&
          !loading && (
            <section className="founder-dashboard">

              <div className="founder-dashboard-header">

                <div>

                  <span className="dashboard-eyebrow">
                    NEXUS INTELLIGENCE
                  </span>

                  <h2>
                    Your Founder Dashboard
                  </h2>

                  <p>
                    Everything you need to
                    turn an early-stage idea
                    into a structured,
                    data-backed validation
                    report.
                  </p>

                </div>

                <button
                  type="button"
                  className="dashboard-start-btn"
                  onClick={
                    handleScrollToInput
                  }
                >
                  Start Validation

                  <ArrowRightIcon
                    size={15}
                  />
                </button>

              </div>

              <div className="dashboard-analysis-grid">

                <article className="dashboard-analysis-card">

                  <div className="dashboard-card-number">
                    01
                  </div>

                  <h3>
                    Market Intelligence
                  </h3>

                  <p>
                    Market demand,
                    trends, sizing and
                    growth signals from
                    live web research.
                  </p>

                </article>

                <article className="dashboard-analysis-card">

                  <div className="dashboard-card-number">
                    02
                  </div>

                  <h3>
                    Customer Intelligence
                  </h3>

                  <p>
                    Understand your
                    ideal customers,
                    pain points and
                    buying signals.
                  </p>

                </article>

                <article className="dashboard-analysis-card">

                  <div className="dashboard-card-number">
                    03
                  </div>

                  <h3>
                    Competitor Intelligence
                  </h3>

                  <p>
                    Compare direct and
                    indirect competitors,
                    features and
                    market gaps.
                  </p>

                </article>

                <article className="dashboard-analysis-card">

                  <div className="dashboard-card-number">
                    04
                  </div>

                  <h3>
                    Execution Strategy
                  </h3>

                  <p>
                    Identify risks,
                    MVP priorities and
                    go-to-market
                    opportunities.
                  </p>

                </article>

              </div>

              <div className="dashboard-bottom-grid">

                <div className="dashboard-info-card">

                  <span className="dashboard-small-label">
                    HOW IT WORKS
                  </span>

                  <h3>
                    From idea to validation
                  </h3>

                  <div className="dashboard-steps">

                    <div className="dashboard-step">

                      <span>1</span>

                      <div>

                        <strong>
                          Describe your idea
                        </strong>

                        <p>
                          Give NEXUS the
                          problem, product
                          and target
                          audience.
                        </p>

                      </div>

                    </div>

                    <div className="dashboard-step">

                      <span>2</span>

                      <div>

                        <strong>
                          Run live research
                        </strong>

                        <p>
                          NEXUS researches
                          markets,
                          customers and
                          competitors.
                        </p>

                      </div>

                    </div>

                    <div className="dashboard-step">

                      <span>3</span>

                      <div>

                        <strong>
                          Get your validation
                          dossier
                        </strong>

                        <p>
                          Review market
                          opportunities,
                          risks, MVP and
                          launch strategy.
                        </p>

                      </div>

                    </div>

                  </div>

                </div>

                <div className="dashboard-activity-card">

                  <span className="dashboard-small-label">
                    ACTIVITY
                  </span>

                  <div className="dashboard-activity-number">
                    {activityCount || 0}
                  </div>

                  <h3>
                    Validations completed
                  </h3>

                  <p>
                    Your previous startup
                    analyses are stored
                    in the Activity Log.
                  </p>

                  <button
                    type="button"
                    className="dashboard-history-btn"
                    onClick={() =>
                      setHistoryModalOpen(true)
                    }
                  >
                    <HistoryIcon size={15} />

                    View History
                  </button>

                </div>

              </div>

            </section>
          )}

        {/* ===================================
            LOADING
        =================================== */}

        {loading && (
          <StreamingProgressLoader
            conceptTitle={
              submittedIdea ||
              idea
            }
          />
        )}

        {/* ===================================
            VALIDATION ERROR
        =================================== */}

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

        {/* ===================================
            GENERAL ERROR
        =================================== */}

        {error &&
          !loading &&
          !validationError && (
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

        {/* ===================================
            RESULTS DASHBOARD
            ONLY AFTER VALIDATION
        =================================== */}

        {validationResult &&
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
                  setHistoryModalOpen(true)
                }

                onNewAnalysis={
                  handleClear
                }
              />

              {/* STARTUP ADVISOR */}

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
                    validationResult
                      ?.target_customer,
                }}
              />

            </section>
          )}

        {/* ===================================
            EMPTY RESULTS
        =================================== */}

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
                No Relevant Information Found
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
        <Footer />

      </main>

      {/* =====================================
          AUTH MODAL
      ===================================== */}

      <AuthModal
        isOpen={authModalOpen}
        onClose={() =>
          setAuthModalOpen(false)
        }
      />

      {/* =====================================
          SUPABASE MODAL
      ===================================== */}

      <SupabaseConfigModal
        isOpen={supabaseModalOpen}
        onClose={() =>
          setSupabaseModalOpen(false)
        }
      />

      {/* =====================================
          ACTIVITY LOG
      ===================================== */}

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

      {/* =====================================
          ADVISORY COPILOT BUTTON
      ===================================== */}

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

      {/* =====================================
          ADVISORY SLIDE OVER
      ===================================== */}

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