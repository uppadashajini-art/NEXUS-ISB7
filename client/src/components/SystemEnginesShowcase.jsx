import React, { useState } from "react";
import {
  Globe,
  Cpu,
  Database,
  Compass,
  Sparkles,
  ShieldCheck,
  ArrowRight,
} from "lucide-react";

export default function SystemEnginesShowcase({ onScrollToInput }) {
  const [activeModuleTab, setActiveModuleTab] = useState("all");

  const FILTER_TABS = [
    { id: "all", label: "All" },
    { id: "mod-feasibility", label: "Idea" },
    { id: "mod-market", label: "Market" },
    { id: "mod-customer", label: "Customer" },
    { id: "mod-competitor", label: "Competitor" },
  ];

  const CORE_MODULES = [
    {
      id: "mod-feasibility",
      code: "01",
      accentClass: "module-accent-idea",
      accentColor: "var(--accent-idea)",
      accentRgb: "255, 199, 44",
      title: "Idea & Feasibility Analysis",
      subtitle: "Technical & Regulatory Feasibility Scoring",
      description:
        "Evaluates technical feasibility, architectural constraints, and relevant regulatory requirements before development begins.",
      metrics: [
        { label: "Scoring Model", val: "0–100 Scale" },
        { label: "Risk Factors", val: "Tech / Compliance" },
        { label: "Execution Time", val: "~15 Seconds" },
      ],
      tags: ["Technical Feasibility", "Compliance Check", "Architecture"],
    },
    {
      id: "mod-market",
      code: "02",
      accentClass: "module-accent-market",
      accentColor: "var(--accent-market)",
      accentRgb: "255, 138, 31",
      title: "Market Sizing & Growth",
      subtitle: "TAM, SAM, SOM & Growth Dynamics",
      description:
        "Calculates market sizing, industry compound annual growth rate (CAGR), and macroeconomic factors using verified market data.",
      metrics: [
        { label: "Sizing Framework", val: "TAM / SAM / SOM" },
        { label: "Growth Vector", val: "Industry CAGR" },
        { label: "Timing Factor", val: "Market Readiness" },
      ],
      tags: ["Market Sizing", "Growth Rate", "Industry Benchmarks"],
    },
    {
      id: "mod-customer",
      code: "03",
      accentClass: "module-accent-customer",
      accentColor: "var(--accent-customer)",
      accentRgb: "255, 90, 78",
      title: "Customer & ICP Profiling",
      subtitle: "Target Personas & Problem-Solution Fit",
      description:
        "Identifies ideal customer profiles (ICPs), categorizes user pain points by severity, and recommends customer acquisition channels.",
      metrics: [
        { label: "Segments", val: "B2B / B2C / Enterprise" },
        { label: "Pain Severity", val: "Critical vs Secondary" },
        { label: "Distribution", val: "Acquisition Channels" },
      ],
      tags: ["User Personas", "Pain Point Index", "Channel Strategy"],
    },
    {
      id: "mod-competitor",
      code: "04",
      accentClass: "module-accent-competitor",
      accentColor: "var(--accent-competitor)",
      accentRgb: "242, 61, 92",
      title: "Competitor Features & Market Gaps",
      subtitle: "Feature Matrix & Differentiation",
      description:
        "Analyzes direct and indirect competitors, compares key features, and highlights unaddressed requirements in the market.",
      metrics: [
        { label: "Competitor Radar", val: "Direct & Indirect" },
        { label: "Coverage", val: "Feature Comparison" },
        { label: "Opportunities", val: "Market Gaps" },
      ],
      tags: ["Competitor Matrix", "Feature Gaps", "Pricing Models"],
    },
  ];

  const INTEGRATIONS = [
    {
      id: "tavily",
      name: "Live Web Scraping & Search",
      provider: "Tavily API",
      desc: "Fetches live market reports, competitor product documentation, and industry benchmarks.",
      icon: Globe,
      accent: "var(--accent-feasibility)",
      accentRgb: "45, 212, 191",
    },
    {
      id: "heuristics",
      name: "Automated Feature Prioritization",
      provider: "Core Heuristics",
      desc: "Sorts product scope into Core MVP, secondary features, and out-of-scope items.",
      icon: Cpu,
      accent: "var(--accent-idea)",
      accentRgb: "255, 199, 44",
    },
    {
      id: "supabase",
      name: "Database Storage",
      provider: "Supabase Postgres",
      desc: "Persists research reports, audit history, and configuration with row-level security.",
      icon: Database,
      accent: "var(--accent-market)",
      accentRgb: "255, 138, 31",
    },
    {
      id: "planner",
      name: "Go-To-Market Roadmap",
      provider: "Execution Planner",
      desc: "Generates structured 30, 60, and 90-day launch milestones and distribution loops.",
      icon: Compass,
      accent: "var(--accent-advisory)",
      accentRgb: "139, 124, 246",
    },
    {
      id: "engine",
      name: "Interactive Advisory Assistant",
      provider: "Analysis Engine",
      desc: "Context-aware conversational interface for stress-testing pricing and assumptions.",
      icon: Sparkles,
      accent: "var(--accent-customer)",
      accentRgb: "255, 90, 78",
    },
    {
      id: "standards",
      name: "Regulatory & Compliance Screen",
      provider: "Standards Checker",
      desc: "Surfaces potential requirements across GDPR, HIPAA, financial regulations, and AI governance.",
      icon: ShieldCheck,
      accent: "var(--accent-competitor)",
      accentRgb: "242, 61, 92",
    },
  ];

  const displayedModules =
    activeModuleTab === "all"
      ? CORE_MODULES
      : CORE_MODULES.filter((m) => m.id === activeModuleTab);

  return (
    <section className="suite-section" aria-label="Analysis Suite">
      {/* Section Header with Eyebrow and Filter Tabs */}
      <header className="suite-header">
        <div className="suite-eyebrow">
          <span>ANALYSIS SUITE</span>
        </div>

        <div className="suite-headline-row">
          <div>
            <h2 className="suite-title">4 Core Analysis Modules</h2>
            <p className="suite-subtitle">
              Automated research pipelines that evaluate feasibility, market demand, customer segments, and competitor features.
            </p>
          </div>

          {/* Filter Tabs Row (All, Idea, Market, Customer, Competitor) */}
          <nav className="suite-filter-tabs" role="tablist" aria-label="Filter analysis modules">
            {FILTER_TABS.map((tab) => {
              const isActive = activeModuleTab === tab.id;
              return (
                <button
                  key={tab.id}
                  type="button"
                  role="tab"
                  aria-selected={isActive}
                  className={`suite-tab-btn ${isActive ? "active" : ""}`}
                  onClick={() => setActiveModuleTab(tab.id)}
                >
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </header>

      {/* 4 Core Module Cards in a 2x2 Grid */}
      <div className="suite-modules-grid">
        {displayedModules.map((mod) => (
          <article
            key={mod.id}
            className={`suite-module-card ${mod.accentClass}`}
            style={{
              "--module-accent": mod.accentColor,
              "--module-accent-rgb": mod.accentRgb,
            }}
          >
            <div className="suite-module-card-header">
              <div className="suite-module-title-wrap">
                <span className="suite-index-badge">{mod.code}</span>
                <h3 className="suite-module-card-title">{mod.title}</h3>
              </div>
            </div>

            <div className="suite-module-card-subtitle">{mod.subtitle}</div>
            <p className="suite-module-card-desc">{mod.description}</p>

            {/* 3 Stat Tiles */}
            <div className="suite-stat-tiles-row">
              {mod.metrics.map((m, idx) => (
                <div key={idx} className="suite-stat-tile">
                  <span className="suite-stat-label">{m.label}</span>
                  <span className="suite-stat-val">{m.val}</span>
                </div>
              ))}
            </div>

            {/* 3 Tag Chips (Tinted: accent at 10% bg, 30% border) */}
            <div className="suite-tag-chips-row">
              {mod.tags.map((tag, idx) => (
                <span key={idx} className="suite-tag-chip">
                  {tag}
                </span>
              ))}
            </div>
          </article>
        ))}
      </div>

      {/* Integrations & Data Sources (3x2 Grid) */}
      <div className="suite-integrations-card">
        <div className="suite-integrations-header">
          <div>
            <div className="suite-eyebrow" style={{ marginBottom: "6px" }}>
              <span>TECHNICAL STACK</span>
            </div>
            <h3 className="suite-integrations-title">Integrations & Data Sources</h3>
            <p className="suite-integrations-subtitle">
              Underlying APIs and data persistence infrastructure powering each report.
            </p>
          </div>

          {onScrollToInput && (
            <button
              type="button"
              className="suite-scroll-btn"
              onClick={onScrollToInput}
              aria-label="Scroll to idea analysis form"
            >
              <span>Analyze an Idea</span>
              <ArrowRight size={14} strokeWidth={1.5} />
            </button>
          )}
        </div>

        {/* 3x2 Grid of Compact Cards with Small Colored Icon Tiles */}
        <div className="suite-integrations-grid">
          {INTEGRATIONS.map((item) => {
            const IconComponent = item.icon;
            return (
              <div
                key={item.id}
                className="suite-integration-item"
                style={{
                  "--tile-accent": item.accent,
                  "--tile-accent-rgb": item.accentRgb,
                }}
              >
                {/* Small colored icon tile (lucide-react, 1.5 stroke) */}
                <div className="suite-icon-tile" aria-hidden="true">
                  <IconComponent size={18} strokeWidth={1.5} />
                </div>

                <div className="suite-integration-body">
                  <span className="suite-integration-provider">{item.provider}</span>
                  <span className="suite-integration-name">{item.name}</span>
                  <p className="suite-integration-desc">{item.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
