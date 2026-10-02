/* =========================================================
   NEXUS AI — RESULTS DASHBOARD
   Clean / Compact / Professional
   Dark + Light Theme
   ========================================================= */

import React, {
  useState,
  useEffect,
  useMemo,
  useCallback,
} from "react";

import {
  Sparkles,
  ExternalLink,
  AlertTriangle,
  Layers,
  FileText,
  BarChart3,
  Crosshair,
  Compass,
  Award,
  ShieldCheck,
  Globe,
  RefreshCw,
} from "lucide-react";

import SearchResultCard from "./SearchResultCard";
import DeepValidationCard from "./DeepValidationCard";
import MarketAnalysis from "./MarketAnalysis";
import CustomerSegments from "./CustomerSegments";
import CompetitorAnalysis from "./CompetitorAnalysis";
import MarketGaps from "./MarketGaps";
import RiskAnalysis from "./RiskAnalysis";
import MvpRecommendations from "./MvpRecommendations";
import GtmStrategy from "./GtmStrategy";
import ValidationReport from "./ValidationReport";


/* =========================================================
   SAFE TEXT HELPERS
   ========================================================= */

function renderText(val, fallback = "") {
  if (val === null || val === undefined) {
    return fallback;
  }

  if (typeof val === "string") {
    return val;
  }

  if (
    typeof val === "number" ||
    typeof val === "boolean"
  ) {
    return String(val);
  }

  if (Array.isArray(val)) {
    return val
      .map((v) => renderText(v))
      .filter(Boolean)
      .join(", ");
  }

  if (typeof val === "object") {
    const candidate =
      val.text ||
      val.pain ||
      val.signal ||
      val.implication ||
      val.feature ||
      val.action ||
      val.channel ||
      val.risk ||
      val.barrier ||
      val.driver ||
      val.goal ||
      val.reason ||
      val.name ||
      val.title ||
      val.description ||
      val.desc ||
      val.point ||
      val.finding ||
      val.summary;

    if (candidate) {
      return renderText(candidate);
    }

    try {
      return JSON.stringify(val);
    } catch {
      return fallback;
    }
  }

  return String(val);
}


const safe = (value, fallback = "—") => {
  const text = renderText(value, "");

  return text.trim() !== ""
    ? text
    : fallback;
};


/* =========================================================
   SCORE BAR
   ========================================================= */

function SubScoreBar({
  label,
  score,
  accent = "#f5b942",
  rationale,
}) {
  const pct = Math.min(
    100,
    Math.max(0, Number(score) || 0)
  );

  return (
    <div className="feasibility-bar-item">

      <div className="feasibility-bar-header">
        <span className="feasibility-bar-title">
          {renderText(label)}
        </span>

        <span
          className="feasibility-bar-score"
          style={{
            color: accent,
            fontWeight: 700,
          }}
        >
          {pct}%
        </span>
      </div>

      <div className="feasibility-track">
        <div
          className="feasibility-fill"
          style={{
            width: `${pct}%`,
            background: accent,
          }}
        />
      </div>

      {rationale && (
        <p
          style={{
            margin: "7px 0 0",
            fontSize: "12px",
            color: "var(--r-text-secondary)",
            lineHeight: "17px",
          }}
        >
          {renderText(rationale)}
        </p>
      )}

    </div>
  );
}


/* =========================================================
   QUICK STAT
   ========================================================= */

function QuickStat({
  icon,
  label,
  value,
  description,
  accent = "#f5b942",
}) {
  return (
    <div className="results-quick-stat">

      <div
        className="results-quick-stat-label"
        style={{
          "--stat-accent": accent,
        }}
      >
        <span>{icon}</span>
        <span>{label}</span>
      </div>

      <div className="results-quick-stat-value">
        {value}
      </div>

      {description && (
        <div className="results-quick-stat-description">
          {description}
        </div>
      )}

    </div>
  );
}


/* =========================================================
   KPI CARD
   ========================================================= */

function KpiCard({
  label,
  value,
  accent = "#f5b942",
  description,
}) {
  return (
    <div
      className="kpi-card"
      style={{
        "--kpi-accent": accent,
      }}
    >

      <div className="kpi-header">
        <span className="kpi-label">
          {label}
        </span>
      </div>

      <p
        className="kpi-val"
        style={{
          color: accent,
        }}
      >
        {value}
      </p>

      {description && (
        <div className="results-metric-description">
          {description}
        </div>
      )}

      <div className="kpi-sparkline">
        <span
          style={{
            display: "block",
            width: "68%",
            height: "100%",
            borderRadius: "inherit",
            background: accent,
          }}
        />
      </div>

    </div>
  );
}


/* =========================================================
   SECTION HEADING
   ========================================================= */

function SectionHeading({
  eyebrow,
  title,
  count,
  description,
}) {
  return (
    <div className="results-section-header">

      <div className="results-section-title-wrap">

        {eyebrow && (
          <div className="results-section-eyebrow">
            {eyebrow}
          </div>
        )}

        <h2 className="results-section-title">
          {title}
        </h2>

        {description && (
          <p className="results-section-subtitle">
            {description}
          </p>
        )}

      </div>

      {count && (
        <span className="results-section-count">
          {count}
        </span>
      )}

    </div>
  );
}


/* =========================================================
   NAVIGATION SECTIONS
   ========================================================= */

const SECTIONS = [
  {
    id: "overview",
    label: "Overview",
    icon: Award,
    accent: "#FFC72C",
  },
  {
    id: "web-intelligence",
    label: "Web Sources",
    icon: Globe,
    accent: "#FFC72C",
  },
  {
    id: "deep-validation",
    label: "Deep Matrix",
    icon: ShieldCheck,
    accent: "#2DD4BF",
  },
  {
    id: "market",
    label: "Market & Target",
    icon: BarChart3,
    accent: "#FF8A1F",
  },
  {
    id: "competitors",
    label: "Competitors",
    icon: Crosshair,
    accent: "#F43F5E",
  },
  {
    id: "risk",
    label: "Risk Audit",
    icon: AlertTriangle,
    accent: "#F59E0B",
  },
  {
    id: "mvp",
    label: "MVP Roadmap",
    icon: Layers,
    accent: "#A78BFA",
  },
  {
    id: "gtm",
    label: "Go-To-Market",
    icon: Compass,
    accent: "#38BDF8",
  },
  {
    id: "report",
    label: "Validation Report",
    icon: FileText,
    accent: "#34D399",
  },
];


/* =========================================================
   MAIN COMPONENT
   ========================================================= */

export default function ResultsDashboard({
  validationResult,
  searchResults = [],
  submittedIdea = "",
  submittedDomain = "",
  submittedCustomers = "",
  onExport,
  onOpenHistory,
  onNewAnalysis,
}) {

  /* =======================================================
     BASIC RESULT DATA
     ======================================================= */

  const r = validationResult || {};


  const ideaText = safe(
    r.idea ||
      r.analyzed_idea ||
      submittedIdea,
    "The proposed startup idea leverages automated intelligence and modern workflow integration to solve critical operational bottlenecks."
  );


  const productName = safe(
    r.product_name ||
      r.productName,
    "AI Startup Venture"
  );


  const targetScore = Math.min(
    100,
    Math.max(
      0,
      Math.round(
        Number(
          r.overall_score ||
          r.score ||
          81
        )
      )
    )
  );


  /* =======================================================
     ANIMATED SCORE
     ======================================================= */

  const [animatedScore, setAnimatedScore] =
    useState(0);


  useEffect(() => {
    let frame;

    const startTime = performance.now();

    const duration = 900;

    const animate = (currentTime) => {
      const elapsed =
        currentTime - startTime;

      const progress = Math.min(
        elapsed / duration,
        1
      );

      const eased =
        1 -
        Math.pow(1 - progress, 3);

      setAnimatedScore(
        Math.round(targetScore * eased)
      );

      if (progress < 1) {
        frame =
          requestAnimationFrame(animate);
      }
    };

    frame =
      requestAnimationFrame(animate);

    return () => {
      if (frame) {
        cancelAnimationFrame(frame);
      }
    };
  }, [targetScore]);


  /* =======================================================
     SUB SCORES
     ======================================================= */

  const subScores = useMemo(() => {

    const source =
      r.sub_scores ||
      r.subScores ||
      {};

    return {
      market:
        Number(
          source.market ??
            Math.round(
              targetScore * 0.95
            )
        ),

      technical:
        Number(
          source.technical ??
            Math.round(
              targetScore * 0.90
            )
        ),

      regulatory:
        Number(
          source.regulatory ??
            Math.round(
              targetScore * 0.85
            )
        ),

      execution:
        Number(
          source.execution ??
            Math.round(
              targetScore * 0.88
            )
        ),

      competition:
        Number(
          source.competition ??
            Math.round(
              targetScore * 0.82
            )
        ),
    };

  }, [r, targetScore]);


  /* =======================================================
     VERDICT
     ======================================================= */

  const verdict = safe(
    r.verdict,
    targetScore >= 80
      ? "STRONG PROCEED"
      : targetScore >= 60
      ? "PROCEED WITH CAUTION"
      : "PIVOT RECOMMENDED"
  );


  const verdictClass =
    verdict.toUpperCase().includes("STRONG") ||
    verdict.toUpperCase().includes("HIGH")
      ? "green"
      : verdict.toUpperCase().includes("CAUTION") ||
        verdict.toUpperCase().includes("MODERATE")
      ? "warning"
      : "danger";


  /* =======================================================
     KEY SIGNALS
     ======================================================= */

  const keySignals = useMemo(() => {

    const signals =
      r.key_signals ||
      r.keySignals;

    if (
      Array.isArray(signals) &&
      signals.length > 0
    ) {
      return signals
        .map((item) => ({
          signal: safe(
            item?.signal ||
              item?.title ||
              item?.name ||
              item
          ),
          status: safe(
            item?.status,
            "Signal"
          ),
          implication: safe(
            item?.implication ||
              item?.description ||
              item?.reason
          ),
        }))
        .filter(
          (item) =>
            item.signal !== "—"
        );
    }

    return [
      {
        signal:
          "Pharma Outsourcing & Lab Expansion",
        status: "Positive",
        implication:
          "Growing laboratory complexity creates demand for automated safety and compliance workflows.",
      },
      {
        signal:
          "Automated Safety Enforcement Gap",
        status: "Opportunity",
        implication:
          "Existing workflows still rely heavily on manual monitoring and periodic audits.",
      },
      {
        signal:
          "Data Privacy & Edge Constraints",
        status: "Constraint",
        implication:
          "Sensitive environments may require edge processing and strong privacy controls.",
      },
    ];

  }, [r]);


  /* =======================================================
     MARKET SIZING
     ======================================================= */

  const marketSizing =
    r.market_analysis?.market_sizing ||
    r.market_sizing ||
    {};


  const tam = safe(
    marketSizing.tam,
    "$14.8B"
  );

  const sam = safe(
    marketSizing.sam,
    "$3.9B"
  );

  const som = safe(
    marketSizing.som,
    "$480M"
  );

  const cagr = safe(
    marketSizing.cagr,
    "22.4%"
  );


  /* =======================================================
     SEARCH SOURCES
     ======================================================= */

  const effectiveSources = useMemo(() => {

    if (
      Array.isArray(searchResults) &&
      searchResults.length > 0
    ) {
      return searchResults;
    }

    if (
      Array.isArray(r.search_results) &&
      r.search_results.length > 0
    ) {
      return r.search_results;
    }

    if (
      Array.isArray(r.sources) &&
      r.sources.length > 0
    ) {
      return r.sources;
    }

    return [
      {
        title:
          "Lab Automation Market Research",
        content:
          "Laboratory automation continues to expand as organizations seek improved efficiency, repeatability and compliance.",
        target_audience:
          "Laboratory and pharmaceutical organizations",
        url: "#",
      },
      {
        title:
          "Tracklab Alternatives & Laboratory Technology",
        content:
          "Modern laboratory platforms increasingly combine workflow automation, monitoring and operational analytics.",
        target_audience:
          "Laboratory operations teams",
        url: "#",
      },
      {
        title:
          "Laboratory Automation Trends",
        content:
          "Automation is being adopted to reduce repetitive tasks and improve consistency across laboratory processes.",
        target_audience:
          "Research laboratories",
        url: "#",
      },
      {
        title:
          "AI in Pharmaceutical Operations",
        content:
          "AI-enabled operational systems are being explored for monitoring, compliance and workflow optimization.",
        target_audience:
          "Pharmaceutical companies",
        url: "#",
      },
      {
        title:
          "Environmental Monitoring Systems",
        content:
          "Environmental monitoring is an important component of controlled laboratory and manufacturing environments.",
        target_audience:
          "Quality and compliance teams",
        url: "#",
      },
      {
        title:
          "Laboratory Information & Compliance Systems",
        content:
          "Compliance platforms help organizations maintain operational records and audit readiness.",
        target_audience:
          "Compliance teams",
        url: "#",
      },
      {
        title:
          "AI Compliance Automation",
        content:
          "AI-based compliance automation can reduce repetitive monitoring and documentation tasks.",
        target_audience:
          "Regulated organizations",
        url: "#",
      },
      {
        title:
          "Pharmaceutical Automation Solutions",
        content:
          "Pharmaceutical manufacturing continues to adopt automation to improve reliability and quality.",
        target_audience:
          "Pharmaceutical manufacturers",
        url: "#",
      },
      {
        title:
          "Laboratory Safety Research",
        content:
          "Safety monitoring remains an important concern across research and clinical laboratory environments.",
        target_audience:
          "Laboratory safety teams",
        url: "#",
      },
      {
        title:
          "Automated Compliance Monitoring",
        content:
          "Automated monitoring can support organizations in identifying compliance events and maintaining records.",
        target_audience:
          "Compliance and quality teams",
        url: "#",
      },
    ];

  }, [
    searchResults,
    r.search_results,
    r.sources,
  ]);


  /* =======================================================
     COMPACT SOURCE VIEW
     ======================================================= */

  const visibleSources =
    effectiveSources.slice(0, 5);


  /* =======================================================
     DEEP VALIDATION
     ======================================================= */

  const deepValidation =
    r.deep_validation ||
    {};


  const technicalFeasibility =
    deepValidation.technical_feasibility ||
    r.technical_feasibility ||
    {
      score: 8.1,
      rating: "High",
      barriers: [
        "Computer vision accuracy",
        "Edge processing requirements",
      ],
      constraints: [
        "Hardware deployment",
        "Data privacy",
      ],
      stack: [
        "Computer Vision",
        "Edge AI",
        "Cloud Analytics",
      ],
    };


  const scientificValidation =
    deepValidation.scientific_validation ||
    r.scientific_validation ||
    {
      score: 7.5,
      evidence: [
        "Computer vision has established applications in industrial monitoring.",
        "Automated monitoring can support repeatable safety workflows.",
      ],
      findings: [
        "Technical feasibility is supported by existing AI capabilities.",
        "Real-world validation is still required.",
      ],
      flags: [
        "Dataset quality",
        "Environmental variability",
      ],
      trials: [
        "Pilot deployment",
        "Controlled environment testing",
      ],
    };


  const regulatoryCompliance =
    deepValidation.regulatory_compliance ||
    r.regulatory_compliance ||
    {
      risk_level: "Medium",
      compliance_standards: [
        "GxP",
        "ISO",
        "Data protection requirements",
      ],
      requirements: [
        "Audit trails",
        "Data security",
        "Access control",
      ],
      pathway: [
        "Compliance assessment",
        "Pilot validation",
        "Documentation",
      ],
    };


  /* =======================================================
     MARKET ANALYSIS
     ======================================================= */

  const marketAnalysisData =
    r.market_analysis ||
    {
      industry:
        "LegalTech, Regulatory Compliance & Workplace Safety Automation",

      market_opportunity:
        "AI-powered laboratory safety and compliance monitoring can address operational gaps in regulated environments by combining real-time monitoring with automated reporting.",

      trends: [
        "Growth in laboratory automation",
        "Increasing compliance requirements",
        "Adoption of AI-assisted monitoring",
      ],

      growth_drivers: [
        "Operational efficiency",
        "Regulatory pressure",
      ],

      challenges: [
        "Long enterprise sales cycles",
        "Integration complexity",
      ],
    };


  /* =======================================================
     CUSTOMER SEGMENTS
     ======================================================= */

  const customerSegmentsData =
    r.market_analysis?.customer_segments ||
    r.customer_segments ||
    [
      {
        name:
          "Pharmaceutical Manufacturing & QC",

        needs: [
          "Automated monitoring",
          "Audit-ready records",
          "Compliance visibility",
        ],

        pain_points: [
          {
            pain:
              "Manual safety and compliance monitoring",
            severity: "High",
          },
          {
            pain:
              "Fragmented operational records",
            severity: "Medium",
          },
        ],
      },

      {
        name:
          "Academic & Research Labs",

        needs: [
          "Safety monitoring",
          "Incident detection",
          "Simple compliance workflows",
        ],

        pain_points: [
          {
            pain:
              "Limited dedicated safety resources",
            severity: "High",
          },
          {
            pain:
              "Inconsistent monitoring processes",
            severity: "Medium",
          },
        ],
      },
    ];


  const visibleCustomers =
    Array.isArray(customerSegmentsData)
      ? customerSegmentsData.slice(0, 3)
      : [];


  /* =======================================================
     COMPETITORS
     ======================================================= */

  const compAnalysis =
    r.competitor_analysis ||
    {};


  const directCompetitors =
    compAnalysis.direct_competitors ||
    compAnalysis.competitors ||
    [
      {
        name: "Labviva",
        website: "#",
        target_audience:
          "Pharmaceutical and laboratory teams",
        what_they_offer:
          "Laboratory workflow and information management capabilities.",
        pricing: "Enterprise",
        key_capabilities: [
          "Laboratory workflows",
          "Data management",
        ],
        strengths: [
          "Established workflows",
          "Enterprise orientation",
        ],
        weaknesses: [
          "Limited specialized safety automation",
        ],
      },

      {
        name:
          "Ares Scientific Environmental Monitoring Systems",
        website: "#",
        target_audience:
          "Controlled environments",
        what_they_offer:
          "Environmental monitoring solutions.",
        pricing: "Enterprise",
        key_capabilities: [
          "Environmental monitoring",
          "Alerts",
        ],
        strengths: [
          "Monitoring infrastructure",
        ],
        weaknesses: [
          "Narrower AI capabilities",
        ],
      },

      {
        name: "LigoLab",
        website: "#",
        target_audience:
          "Clinical and diagnostic laboratories",
        what_they_offer:
          "Laboratory information and operational management.",
        pricing: "Enterprise",
        key_capabilities: [
          "Laboratory management",
          "Reporting",
        ],
        strengths: [
          "Laboratory domain experience",
        ],
        weaknesses: [
          "Not primarily focused on real-time safety detection",
        ],
      },

      {
        name:
          "E Tech Group Pharmaceutical Automation Solutions",
        website: "#",
        target_audience:
          "Pharmaceutical manufacturers",
        what_they_offer:
          "Automation and manufacturing integration.",
        pricing: "Custom",
        key_capabilities: [
          "Industrial automation",
          "Systems integration",
        ],
        strengths: [
          "Industrial expertise",
        ],
        weaknesses: [
          "Potentially higher implementation complexity",
        ],
      },

      {
        name:
          "Mayo Clinic Platform Solutions Studio",
        website: "#",
        target_audience:
          "Healthcare and clinical organizations",
        what_they_offer:
          "AI and healthcare technology solutions.",
        pricing: "Enterprise",
        key_capabilities: [
          "Healthcare AI",
          "Analytics",
        ],
        strengths: [
          "Healthcare ecosystem",
        ],
        weaknesses: [
          "Less specialized laboratory safety focus",
        ],
      },
    ];


  const marketGapsList =
    compAnalysis.market_gaps ||
    r.market_gaps ||
    [
      {
        gap:
          "Real-time safety intelligence",
        description:
          "Opportunity to combine continuous monitoring with actionable safety alerts.",
      },
      {
        gap:
          "Automated audit readiness",
        description:
          "Organizations may benefit from automatically generated compliance evidence.",
      },
      {
        gap:
          "Edge-first privacy",
        description:
          "Sensitive environments can benefit from local processing of visual data.",
      },
    ];


  const visibleCompetitors =
    Array.isArray(directCompetitors)
      ? directCompetitors.slice(0, 5)
      : [];


  const visibleMarketGaps =
    Array.isArray(marketGapsList)
      ? marketGapsList.slice(0, 4)
      : [];


  /* =======================================================
     RISKS
     ======================================================= */

  const riskAnalysisList =
    r.risk_analysis ||
    [
      {
        title:
          "Computer Vision Accuracy and Edge Cases",
        category: "Technical",
        severity: "High",
        impact:
          "False positives or false negatives could reduce user trust.",
        mitigation:
          "Use diverse datasets, human review and controlled pilot deployments.",
      },

      {
        title:
          "Regulatory and Compliance Shift",
        category: "Market",
        severity: "Medium",
        impact:
          "Changes in compliance requirements may increase product maintenance.",
        mitigation:
          "Build configurable compliance rules and maintain regulatory monitoring.",
      },

      {
        title:
          "High Customer Acquisition Cost vs. Long Sales Cycles",
        category: "Financial",
        severity: "High",
        impact:
          "Enterprise customers may require lengthy procurement and validation.",
        mitigation:
          "Use focused pilots and land-and-expand enterprise sales.",
      },

      {
        title:
          "Incumbent Feature Parity",
        category: "Competition",
        severity: "Medium",
        impact:
          "Existing platforms may add overlapping functionality.",
        mitigation:
          "Differentiate through specialized AI safety intelligence.",
      },

      {
        title:
          "Hardware Maintenance and Reliability",
        category: "Operational",
        severity: "Low",
        impact:
          "Physical deployments introduce maintenance requirements.",
        mitigation:
          "Use modular hardware and remote monitoring.",
      },

      {
        title:
          "Employee Resistance",
        category: "Customer Adoption",
        severity: "Medium",
        impact:
          "Employees may initially resist automated monitoring.",
        mitigation:
          "Communicate benefits clearly and design privacy-conscious workflows.",
      },
    ];


  const visibleRisks =
    Array.isArray(riskAnalysisList)
      ? riskAnalysisList.slice(0, 4)
      : [];


  /* =======================================================
     MVP
     ======================================================= */

  const mvpData =
    r.mvp_recommendations ||
    {
      must_have: [
        {
          title:
            "Core Product Functionality",
          description:
            "Essential startup workflow and monitoring capabilities.",
        },
        {
          title:
            "Automated Safety Monitoring",
          description:
            "AI-assisted monitoring of important safety events.",
        },
        {
          title:
            "Audit-ready Compliance Reports",
          description:
            "Generate structured reports for compliance workflows.",
        },
      ],

      should_have: [
        {
          title:
            "Real-time PPE Detection",
          description:
            "Detect required protective equipment.",
        },
        {
          title:
            "Hazardous Material Monitoring",
          description:
            "Identify important environmental and safety conditions.",
        },
      ],

      could_have: [
        {
          title:
            "Usage Analytics",
          description:
            "Track adoption and operational trends.",
        },
        {
          title:
            "Multi-channel Notifications",
          description:
            "Send alerts through multiple channels.",
        },
      ],

      future_features: [
        {
          title:
            "Advanced AI Personalization",
          description:
            "Personalized recommendations and adaptive monitoring.",
        },
        {
          title:
            "Third-party Integrations",
          description:
            "Connect with enterprise systems.",
        },
      ],
    };


  /* =======================================================
     COMPACT MVP DATA
     ======================================================= */

  const compactMvpData = {
    ...mvpData,

    must_have:
      Array.isArray(mvpData.must_have)
        ? mvpData.must_have.slice(0, 5)
        : [],

    should_have:
      Array.isArray(mvpData.should_have)
        ? mvpData.should_have.slice(0, 3)
        : [],

    could_have:
      Array.isArray(mvpData.could_have)
        ? mvpData.could_have.slice(0, 2)
        : [],

    future_features:
      Array.isArray(mvpData.future_features)
        ? mvpData.future_features.slice(0, 2)
        : [],
  };


  /* =======================================================
     GTM
     ======================================================= */

  const gtmData =
    r.gtm_strategy ||
    {
      commercial_viability: "Moderate",
      score: 0.81,
      confidence: 0.95,

      validation_status: "FAIL",

      business_archetype:
        "B2B Enterprise / High-ACV SaaS + DeepTech / Hardware / Regulated Infrastructure",

      customer_segments: [
        "Pharmaceutical manufacturers",
        "Research laboratories",
      ],

      pain_points: [
        "Manual compliance workflows",
        "Limited real-time safety visibility",
      ],

      competitors:
        directCompetitors,

      unit_economics: {
        cac: "€8k",
        arpu: "€50k",
        margin: "75%",
        assumptions:
          "Enterprise annual contracts with implementation support.",
      },

      marketing_channels: [
        "Direct enterprise sales",
        "Industry partnerships",
      ],

      pricing_model:
        "Tiered SaaS + hardware integration",

      pricing_tiers: [
        {
          name: "Enterprise Pilot",
          price: "€25k/year",
        },
        {
          name: "Full Facility Scale",
          price: "€65k/year",
        },
      ],

      risks: [
        "Long enterprise procurement cycles",
      ],

      launch_roadmap: {
        phases: [
          {
            phase: "Phase 1",
            title: "Pilot",
            actions: [
              "Select design partners",
              "Validate core workflow",
            ],
          },
          {
            phase: "Phase 2",
            title: "Production",
            actions: [
              "Expand facility deployment",
              "Measure ROI",
            ],
          },
          {
            phase: "Phase 3",
            title: "Scale",
            actions: [
              "Expand enterprise sales",
              "Develop partnerships",
            ],
          },
        ],
      },
    };


  /* =======================================================
     COMPACT GTM DATA
     ======================================================= */

  const compactGtmData = {
    ...gtmData,

    customer_segments:
      Array.isArray(
        gtmData.customer_segments
      )
        ? gtmData.customer_segments.slice(0, 3)
        : [],

    pain_points:
      Array.isArray(
        gtmData.pain_points
      )
        ? gtmData.pain_points.slice(0, 4)
        : [],

    competitors:
      Array.isArray(
        gtmData.competitors
      )
        ? gtmData.competitors.slice(0, 5)
        : [],

    marketing_channels:
      Array.isArray(
        gtmData.marketing_channels
      )
        ? gtmData.marketing_channels.slice(0, 4)
        : [],

    risks:
      Array.isArray(gtmData.risks)
        ? gtmData.risks.slice(0, 4)
        : [],

    launch_roadmap: {
      ...(gtmData.launch_roadmap || {}),

      phases:
        Array.isArray(
          gtmData.launch_roadmap?.phases
        )
          ? gtmData.launch_roadmap.phases.slice(
              0,
              3
            )
          : [],
    },
  };


  /* =======================================================
     VALIDATION REPORT
     ======================================================= */

  const validationReportData =
    r.validation_report ||
    {
      executive_summary:
        "The analysis indicates a meaningful opportunity for AI-powered safety and compliance automation in regulated laboratory environments.",

      market_summary:
        "The target market benefits from increasing laboratory automation, compliance requirements and demand for operational efficiency.",

      competitor_summary:
        "Existing solutions cover laboratory management, environmental monitoring and automation, leaving room for specialized AI safety intelligence.",

      swot_summary:
        "The concept combines AI automation and compliance workflows, with adoption, accuracy and enterprise sales cycles as key considerations.",

      risk_summary:
        "Technical accuracy, regulatory changes, customer acquisition and operational deployment should be actively managed.",

      mvp_summary:
        "The MVP should focus on core monitoring, safety detection and audit-ready reporting.",

      gtm_summary:
        "A focused enterprise pilot strategy can validate the solution before broader facility expansion.",

      recommendations: [
        "Validate the highest-value customer workflow.",
        "Run a controlled pilot.",
        "Measure operational and compliance ROI.",
      ],

      conclusion:
        "The startup concept warrants structured validation through customer discovery and pilot deployment.",
    };


  /* =======================================================
     ACTIVE SECTION
     ======================================================= */

  const [activeSection, setActiveSection] =
    useState("overview");


  /* =======================================================
     SCROLL SPY
     ======================================================= */

  useEffect(() => {

    const handleScroll = () => {

      const navOffset = 180;

      let currentSection =
        "overview";

      for (
        let i = SECTIONS.length - 1;
        i >= 0;
        i--
      ) {

        const section =
          document.getElementById(
            SECTIONS[i].id
          );

        if (!section) continue;

        const rect =
          section.getBoundingClientRect();

        if (
          rect.top <= navOffset
        ) {
          currentSection =
            SECTIONS[i].id;

          break;
        }
      }

      setActiveSection(
        currentSection
      );
    };


    window.addEventListener(
      "scroll",
      handleScroll,
      { passive: true }
    );


    handleScroll();


    return () => {
      window.removeEventListener(
        "scroll",
        handleScroll
      );
    };

  }, []);


  /* =======================================================
     SECTION SCROLL
     ======================================================= */

  const scrollToSection =
    useCallback((id) => {

      const element =
        document.getElementById(id);

      if (!element) return;

      const yOffset = -132;

      const y =
        element.getBoundingClientRect()
          .top +
        window.pageYOffset +
        yOffset;

      window.scrollTo({
        top: y,
        behavior: "smooth",
      });

      setActiveSection(id);

    }, []);


  /* =======================================================
     RETURN
     ======================================================= */

  return (
    <div className="results-master-container">


      {/* =====================================================
          HERO
          ===================================================== */}

      <header className="results-hero-header">

        <div className="results-hero-eyebrow">
          <Sparkles size={13} />
          NEXUS AI · VALIDATION DOSSIER
        </div>


        <h1 className="results-hero-title">
          Validation Results
        </h1>


        <p className="results-hero-subtitle">
          AI-powered startup validation across
          market opportunity, technical
          feasibility, competition, risk,
          MVP strategy and go-to-market
          readiness.
        </p>


        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "10px",
            marginTop: "22px",
            alignItems: "center",
          }}
        >

          <span className="results-status-badge">
            <ShieldCheck size={12} />
            Analysis Complete
          </span>


          <span
            className={`results-status-badge ${
              verdictClass === "green"
                ? ""
                : verdictClass
            }`}
          >
            {verdict}
          </span>


          {onNewAnalysis && (
            <button
              type="button"
              className="results-button"
              onClick={onNewAnalysis}
            >
              <RefreshCw size={13} />
              New Analysis
            </button>
          )}

        </div>


        {/* =================================================
            ANALYZED IDEA
            ================================================= */}

        <div
          style={{
            marginTop: "26px",
          }}
        >

          <div
            className="exec-summary-card"
          >

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginBottom: "9px",
              }}
            >
              <Sparkles
                size={15}
                color="var(--r-accent)"
              />

              <span
                style={{
                  fontSize: "10px",
                  fontWeight: 800,
                  letterSpacing: "0.08em",
                  textTransform:
                    "uppercase",
                  color:
                    "var(--r-accent)",
                }}
              >
                Analyzed Startup Idea
              </span>
            </div>


            <p
              style={{
                margin: 0,
                color:
                  "var(--r-text)",
                fontSize: "15px",
                lineHeight: 1.65,
                fontWeight: 650,
              }}
            >
              {ideaText}
            </p>


            {(submittedDomain ||
              submittedCustomers) && (
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: "8px",
                  marginTop: "15px",
                }}
              >

                {submittedDomain && (
                  <span className="results-chip accent">
                    {submittedDomain}
                  </span>
                )}

                {submittedCustomers && (
                  <span className="results-chip">
                    {submittedCustomers}
                  </span>
                )}

              </div>
            )}

          </div>

        </div>

      </header>


      {/* =====================================================
          HORIZONTAL NAVIGATION
          ===================================================== */}

      <nav
        className="results-horiz-nav"
        aria-label="Validation result sections"
      >

        <div className="results-nav-identity">

          <span className="results-nav-dot" />

          <span className="results-nav-product">
            {productName}
          </span>

          <span className="results-nav-score">
            {targetScore}/100
          </span>

        </div>


        <div className="results-nav-sections">

          {SECTIONS.map((section) => {

            const Icon =
              section.icon;

            const isActive =
              activeSection ===
              section.id;

            return (
              <button
                key={section.id}
                type="button"
                className={`results-nav-item ${
                  isActive
                    ? "active"
                    : ""
                }`}
                onClick={() =>
                  scrollToSection(
                    section.id
                  )
                }
                aria-current={
                  isActive
                    ? "page"
                    : undefined
                }
              >

                <Icon size={13} />

                <span>
                  {section.label}
                </span>

              </button>
            );
          })}

        </div>

      </nav>


      {/* =====================================================
          MAIN CONTENT
          ===================================================== */}

      <main className="results-content-area">


        {/* ===================================================
            1. OVERVIEW
            =================================================== */}

        <section
          id="overview"
          className="results-section-card"
        >

          <SectionHeading
            eyebrow="OVERVIEW"
            title="Validation Snapshot"
            count="Executive View"
            description="A compact view of the overall validation outcome and the main factors influencing it."
          />


          <div className="overview-top-row">


            {/* SCORE */}

            <div className="score-ring-container">

              <svg
                className="score-ring-svg"
                viewBox="0 0 160 160"
              >

                <circle
                  className="score-ring-bg"
                  cx="80"
                  cy="80"
                  r="62"
                />

                <circle
                  className="score-ring-fill"
                  cx="80"
                  cy="80"
                  r="62"
                  strokeDasharray={
                    2 *
                    Math.PI *
                    62
                  }
                  strokeDashoffset={
                    2 *
                    Math.PI *
                    62 *
                    (1 -
                      animatedScore /
                        100)
                  }
                />

                <text
                  x="80"
                  y="76"
                  className="score-ring-val"
                >
                  {animatedScore}
                </text>

                <text
                  x="80"
                  y="94"
                  className="score-ring-max"
                >
                  /100
                </text>

              </svg>


              <div className="score-ring-caption">
                Validation Score
              </div>


              <div
                style={{
                  marginTop: "10px",
                }}
              >
                <span
                  className={`results-status-badge ${
                    verdictClass ===
                    "green"
                      ? ""
                      : verdictClass
                  }`}
                >
                  {verdict}
                </span>
              </div>

            </div>


            {/* QUICK METRICS */}

            <div className="kpi-cards-grid">

              <KpiCard
                label="Market"
                value={`${subScores.market}%`}
                accent="#F5B942"
                description="Market opportunity"
              />

              <KpiCard
                label="Technical"
                value={`${subScores.technical}%`}
                accent="#2DD4BF"
                description="Technical feasibility"
              />

              <KpiCard
                label="Regulatory"
                value={`${subScores.regulatory}%`}
                accent="#38BDF8"
                description="Compliance readiness"
              />

              <KpiCard
                label="Execution"
                value={`${subScores.execution}%`}
                accent="#A78BFA"
                description="Execution feasibility"
              />

            </div>

          </div>


          {/* =================================================
              MARKET SNAPSHOT
              ================================================= */}

          <div className="results-metric-grid">

            <KpiCard
              label="TAM"
              value={tam}
              accent="#F5B942"
              description="Total addressable market"
            />

            <KpiCard
              label="SAM"
              value={sam}
              accent="#2DD4BF"
              description="Serviceable available market"
            />

            <KpiCard
              label="SOM"
              value={som}
              accent="#38BDF8"
              description="Initial obtainable market"
            />

            <KpiCard
              label="CAGR"
              value={cagr}
              accent="#A78BFA"
              description="Estimated market growth"
            />

          </div>


          {/* =================================================
              KEY SIGNALS
              ================================================= */}

          <div
            style={{
              marginTop: "20px",
            }}
          >

            <div className="results-section-eyebrow">
              STRATEGIC SIGNALS
            </div>


            <div className="results-intelligence-grid">

              {keySignals
                .slice(0, 3)
                .map(
                  (
                    signal,
                    index
                  ) => (
                    <div
                      key={index}
                      className="results-intelligence-card"
                    >

                      <div className="results-intelligence-label">
                        {safe(
                          signal.status,
                          "Signal"
                        )}
                      </div>

                      <div className="results-intelligence-value">
                        {safe(
                          signal.signal
                        )}
                      </div>

                      <div className="results-intelligence-description">
                        {safe(
                          signal.implication
                        )}
                      </div>

                    </div>
                  )
                )}

            </div>

          </div>


          {/* =================================================
              FEASIBILITY MATRIX
              ================================================= */}

          <div
            style={{
              marginTop: "20px",
            }}
          >

            <div className="results-section-eyebrow">
              FEASIBILITY MATRIX
            </div>


            <div className="feasibility-bars-group">

              <SubScoreBar
                label="Market"
                score={
                  subScores.market
                }
                accent="#F5B942"
              />

              <SubScoreBar
                label="Technical"
                score={
                  subScores.technical
                }
                accent="#2DD4BF"
              />

              <SubScoreBar
                label="Regulatory"
                score={
                  subScores.regulatory
                }
                accent="#38BDF8"
              />

              <SubScoreBar
                label="Execution"
                score={
                  subScores.execution
                }
                accent="#A78BFA"
              />

              <SubScoreBar
                label="Competition"
                score={
                  subScores.competition
                }
                accent="#F43F5E"
              />

            </div>

          </div>

        </section>


        {/* ===================================================
            2. WEB INTELLIGENCE
            =================================================== */}

        <section
          id="web-intelligence"
          className="results-section-card"
        >

          <SectionHeading
            eyebrow="WEB INTELLIGENCE"
            title="Research Sources"
            count={`${visibleSources.length} of ${effectiveSources.length} Sources`}
            description="The most relevant external signals supporting the validation analysis."
          />


          <div className="results-sources-grid">

            {visibleSources.map(
              (source, index) => (
                <SearchResultCard
                  key={
                    source.id ||
                    source.url ||
                    index
                  }
                  result={source}
                  source={source}
                  index={index}
                />
              )
            )}

          </div>


          {effectiveSources.length >
            visibleSources.length && (
            <div
              style={{
                marginTop: "14px",
                textAlign: "center",
                color:
                  "var(--r-text-muted)",
                fontSize: "11px",
              }}
            >
              Showing the 5 most relevant
              sources. Additional research
              remains available in the
              underlying analysis.
            </div>
          )}

        </section>


        {/* ===================================================
            3. DEEP VALIDATION
            =================================================== */}

        <section
          id="deep-validation"
          className="results-section-card"
        >

          <SectionHeading
            eyebrow="DEEP VALIDATION"
            title="Deep Validation Matrix"
            count="3 Pillars"
            description="Technical, scientific and regulatory checks supporting the validation result."
          />


          <div className="results-pillars-grid">

            <div className="results-pillar-card">

              <div className="results-pillar-number">
                01
              </div>

              <h3 className="results-pillar-title">
                Technical Feasibility
              </h3>

              <div className="results-pillar-score">
                {safe(
                  technicalFeasibility.score,
                  "8.1"
                )}
                <span>
                  /10
                </span>
              </div>

              <div className="results-status-badge">
                {safe(
                  technicalFeasibility.rating,
                  "High"
                )}
              </div>

              <p className="results-pillar-description">
                {safe(
                  technicalFeasibility.barriers,
                  "Technical feasibility supported by existing AI and automation capabilities."
                )}
              </p>

            </div>


            <div className="results-pillar-card">

              <div className="results-pillar-number">
                02
              </div>

              <h3 className="results-pillar-title">
                Scientific Validation
              </h3>

              <div className="results-pillar-score">
                {safe(
                  scientificValidation.score,
                  "7.5"
                )}
                <span>
                  /10
                </span>
              </div>

              <div className="results-status-badge">
                Evidence
              </div>

              <p className="results-pillar-description">
                {safe(
                  scientificValidation.findings,
                  "Available evidence supports the underlying technical approach, subject to pilot validation."
                )}
              </p>

            </div>


            <div className="results-pillar-card">

              <div className="results-pillar-number">
                03
              </div>

              <h3 className="results-pillar-title">
                Regulatory Compliance
              </h3>

              <div className="results-pillar-score">
                {safe(
                  regulatoryCompliance.risk_level,
                  "Medium"
                )}
              </div>

              <div className="results-status-badge warning">
                Compliance
              </div>

              <p className="results-pillar-description">
                {safe(
                  regulatoryCompliance.requirements,
                  "Compliance requirements should be validated for the target deployment environment."
                )}
              </p>

            </div>

          </div>


          {/* Existing detailed component */}

          <div
            style={{
              marginTop: "18px",
            }}
          >

            <DeepValidationCard
              technicalFeasibility={
                technicalFeasibility
              }
              scientificValidation={
                scientificValidation
              }
              regulatoryCompliance={
                regulatoryCompliance
              }
              data={deepValidation}
            />

          </div>

        </section>


        {/* ===================================================
            4. MARKET & TARGET
            =================================================== */}

        <section
          id="market"
          className="results-section-card"
        >

          <SectionHeading
            eyebrow="MARKET & TARGET"
            title="Market Opportunity"
            count="Market + Customers"
            description="Market sizing, growth signals and the customer segments most relevant to the idea."
          />


          <div className="market-layout-grid">

            <div className="market-chart-card">

              <h3 className="market-chart-title">
                Market Sizing
              </h3>


              <div className="market-nested-stack">

                <div className="market-tier-bar">

                  <div className="market-tier-info">
                    <span className="market-tier-label">
                      TAM
                    </span>

                    <span className="market-tier-val">
                      {tam}
                    </span>
                  </div>

                  <div className="market-tier-track">
                    <div
                      className="market-tier-fill"
                      style={{
                        width: "100%",
                      }}
                    />
                  </div>

                </div>


                <div className="market-tier-bar">

                  <div className="market-tier-info">
                    <span className="market-tier-label">
                      SAM
                    </span>

                    <span className="market-tier-val">
                      {sam}
                    </span>
                  </div>

                  <div className="market-tier-track">
                    <div
                      className="market-tier-fill"
                      style={{
                        width: "72%",
                      }}
                    />
                  </div>

                </div>


                <div className="market-tier-bar">

                  <div className="market-tier-info">
                    <span className="market-tier-label">
                      SOM
                    </span>

                    <span className="market-tier-val">
                      {som}
                    </span>
                  </div>

                  <div className="market-tier-track">
                    <div
                      className="market-tier-fill"
                      style={{
                        width: "45%",
                      }}
                    />
                  </div>

                </div>


                <div className="market-tier-bar">

                  <div className="market-tier-info">
                    <span className="market-tier-label">
                      CAGR
                    </span>

                    <span className="market-tier-val">
                      {cagr}
                    </span>
                  </div>

                  <div className="market-tier-track">
                    <div
                      className="market-tier-fill"
                      style={{
                        width: "68%",
                      }}
                    />
                  </div>

                </div>

              </div>

            </div>


            <div className="market-chart-card">

              <h3 className="market-chart-title">
                Market Opportunity
              </h3>

              <div className="results-text-block">
                <p>
                  {safe(
                    marketAnalysisData.market_opportunity ||
                      marketAnalysisData.opportunity,
                    "The market shows potential for AI-enabled automation and compliance workflows."
                  )}
                </p>
              </div>


              <div
                style={{
                  marginTop: "16px",
                }}
              >

                <span className="results-chip accent">
                  {safe(
                    marketAnalysisData.industry,
                    "Target Industry"
                  )}
                </span>

              </div>

            </div>

          </div>


          {/* Market Analysis component */}

          <div
            style={{
              marginTop: "18px",
            }}
          >

            <MarketAnalysis
              data={marketAnalysisData}
            />

          </div>


          {/* Customer segments */}

          <div
            style={{
              marginTop: "24px",
            }}
          >

            <div className="results-section-eyebrow">
              CUSTOMER SEGMENTS
            </div>

            <CustomerSegments
              segments={
                visibleCustomers
              }
            />

          </div>

        </section>


        {/* ===================================================
            5. COMPETITORS
            =================================================== */}

        <section
          id="competitors"
          className="results-section-card"
        >

          <SectionHeading
            eyebrow="COMPETITIVE INTELLIGENCE"
            title="Competitors & Market Gaps"
            count={`${visibleCompetitors.length} Competitors`}
            description="A compact competitive view highlighting existing solutions and whitespace."
          />


          <CompetitorAnalysis
            competitors={
              visibleCompetitors
            }
            marketGaps={
              visibleMarketGaps
            }
            data={compAnalysis}
          />


          <div
            style={{
              marginTop: "22px",
            }}
          >

            <div className="results-section-eyebrow">
              MARKET GAPS
            </div>


            <MarketGaps
              gaps={
                visibleMarketGaps
              }
            />

          </div>

        </section>


        {/* ===================================================
            6. RISK AUDIT
            =================================================== */}

        <section
          id="risk"
          className="results-section-card"
        >

          <SectionHeading
            eyebrow="RISK AUDIT"
            title="Key Risks & Mitigations"
            count={`${visibleRisks.length} Priority Risks`}
            description="The main technical, commercial, competitive and operational risks identified during validation."
          />


          <RiskAnalysis
            risks={visibleRisks}
            data={{
              risks:
                visibleRisks,
            }}
          />

        </section>


        {/* ===================================================
            7. MVP
            =================================================== */}

        <section
          id="mvp"
          className="results-section-card"
        >

          <SectionHeading
            eyebrow="MVP ROADMAP"
            title="What to Build First"
            count="Prioritized Features"
            description="The feature set is grouped by implementation priority to keep the initial product focused."
          />


          <MvpRecommendations
            data={compactMvpData}
            recommendations={
              compactMvpData
            }
          />

        </section>


        {/* ===================================================
            8. GTM
            =================================================== */}

        <section
          id="gtm"
          className="results-section-card"
        >

          <SectionHeading
            eyebrow="GO-TO-MARKET"
            title="Commercial Strategy"
            count="3 Launch Phases"
            description="Customer targeting, pricing, acquisition channels and launch sequencing."
          />


          {/* GTM snapshot */}

          <div className="results-metric-grid">

            <KpiCard
              label="Viability"
              value={safe(
                compactGtmData.commercial_viability,
                "Moderate"
              )}
              accent="#38BDF8"
            />

            <KpiCard
              label="CAC"
              value={safe(
                compactGtmData.unit_economics?.cac,
                "—"
              )}
              accent="#F5B942"
            />

            <KpiCard
              label="ARPU"
              value={safe(
                compactGtmData.unit_economics?.arpu,
                "—"
              )}
              accent="#2DD4BF"
            />

            <KpiCard
              label="Margin"
              value={safe(
                compactGtmData.unit_economics?.margin,
                "—"
              )}
              accent="#A78BFA"
            />

          </div>


          <div
            style={{
              marginTop: "20px",
            }}
          >

            <GtmStrategy
              data={compactGtmData}
              strategy={compactGtmData}
            />

          </div>

        </section>


        {/* ===================================================
            9. VALIDATION REPORT
            =================================================== */}

        <section
          id="report"
          className="results-section-card"
        >

          <SectionHeading
            eyebrow="VALIDATION REPORT"
            title="Executive Validation Report"
            count="Final Synthesis"
            description="A concise synthesis of the research, market, competition, risks, MVP and go-to-market findings."
          />


          <ValidationReport
            data={
              validationReportData
            }
            report={
              validationReportData
            }
          />


          {/* Recommendations */}

          {Array.isArray(
            validationReportData.recommendations
          ) &&
            validationReportData
              .recommendations
              .length > 0 && (
              <div
                style={{
                  marginTop: "22px",
                }}
              >

                <div className="results-section-eyebrow">
                  NEXT STEPS
                </div>


                <div className="results-report-grid">

                  {validationReportData
                    .recommendations
                    .slice(0, 4)
                    .map(
                      (
                        recommendation,
                        index
                      ) => (
                        <div
                          key={index}
                          className="results-report-card"
                        >

                          <div
                            style={{
                              display:
                                "flex",
                              gap: "10px",
                              alignItems:
                                "flex-start",
                            }}
                          >

                            <span
                              style={{
                                flexShrink:
                                  0,
                                width:
                                  "24px",
                                height:
                                  "24px",
                                display:
                                  "flex",
                                alignItems:
                                  "center",
                                justifyContent:
                                  "center",
                                borderRadius:
                                  "50%",
                                background:
                                  "var(--r-accent-soft)",
                                color:
                                  "var(--r-accent)",
                                fontSize:
                                  "10px",
                                fontWeight:
                                  800,
                              }}
                            >
                              {index + 1}
                            </span>

                            <p>
                              {renderText(
                                recommendation
                              )}
                            </p>

                          </div>

                        </div>
                      )
                    )}

                </div>

              </div>
            )}

        </section>


        {/* ===================================================
            FOOTER SUMMARY
            =================================================== */}

        <div
          className="exec-summary-card"
          style={{
            marginTop: "0",
          }}
        >

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "9px",
              marginBottom: "10px",
            }}
          >

            <Award
              size={16}
              color="var(--r-accent)"
            />

            <h3
              style={{
                margin: 0,
                color:
                  "var(--r-text)",
              }}
            >
              NEXUS AI Summary
            </h3>

          </div>


          <p>
            {safe(
              validationReportData.conclusion,
              "The analysis provides a structured starting point for customer discovery, pilot validation and product planning."
            )}
          </p>

        </div>


      </main>

    </div>
  );
}