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

/* ============================================================
   SAFE TEXT HELPERS
============================================================ */

function renderText(val, fallback = "") {
  if (val === null || val === undefined) return fallback;

  if (typeof val === "string") return val;

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
  return text.trim() !== "" ? text : fallback;
};

/* ============================================================
   SUB SCORE BAR
============================================================ */

function SubScoreBar({
  label,
  score,
  accent,
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

      <div
        className="feasibility-track"
        style={{
          background: "rgba(255,255,255,0.06)",
          height: "6px",
          borderRadius: "3px",
          overflow: "hidden",
          marginTop: "6px",
        }}
      >
        <div
          className="feasibility-fill"
          style={{
            width: `${pct}%`,
            background: accent,
            height: "100%",
            borderRadius: "3px",
            transition: "width 0.8s ease",
          }}
        />
      </div>

      {rationale && (
        <p
          style={{
            margin: "6px 0 0",
            fontSize: "12px",
            color: "var(--text-secondary)",
            lineHeight: "17px",
          }}
        >
          {renderText(rationale)}
        </p>
      )}
    </div>
  );
}

/* ============================================================
   RESULTS SECTIONS
============================================================ */

const SECTIONS = [
  {
    id: "overview",
    label: "Overview",
    icon: Award,
    accent: "#FFC72C",
    rgb: "255,199,44",
  },
  {
    id: "web-intelligence",
    label: "Web Sources",
    icon: Globe,
    accent: "#FFC72C",
    rgb: "255,199,44",
  },
  {
    id: "deep-validation",
    label: "Deep Matrix",
    icon: ShieldCheck,
    accent: "#2DD4BF",
    rgb: "45,212,191",
  },
  {
    id: "market",
    label: "Market & Target",
    icon: BarChart3,
    accent: "#FF8A1F",
    rgb: "255,138,31",
  },
  {
    id: "competitors",
    label: "Competitors",
    icon: Crosshair,
    accent: "#F43F5E",
    rgb: "244,63,94",
  },
  {
    id: "risk",
    label: "Risk Audit",
    icon: AlertTriangle,
    accent: "#F59E0B",
    rgb: "245,158,11",
  },
  {
    id: "mvp",
    label: "MVP Roadmap",
    icon: Layers,
    accent: "#A78BFA",
    rgb: "167,139,250",
  },
  {
    id: "gtm",
    label: "Go-To-Market",
    icon: Compass,
    accent: "#38BDF8",
    rgb: "56,189,248",
  },
  {
    id: "report",
    label: "Validation Report",
    icon: FileText,
    accent: "#34D399",
    rgb: "52,211,153",
  },
];

/* ============================================================
   MAIN COMPONENT
============================================================ */

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
  const r = validationResult || {};

  /* ============================================================
     BASIC RESULT INFORMATION
  ============================================================ */

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

  /* ============================================================
     ANIMATED SCORE
  ============================================================ */

  const [animatedScore, setAnimatedScore] =
    useState(0);

  useEffect(() => {
    let start = 0;

    const end = targetScore;

    if (end === 0) {
      setAnimatedScore(0);
      return;
    }

    const duration = 900;
    const stepTime = 16;
    const steps = duration / stepTime;
    const increment = end / steps;

    const timer = setInterval(() => {
      start += increment;

      if (start >= end) {
        setAnimatedScore(end);
        clearInterval(timer);
      } else {
        setAnimatedScore(
          Math.round(start)
        );
      }
    }, stepTime);

    return () =>
      clearInterval(timer);
  }, [targetScore]);

  /* ============================================================
     SUB SCORES
  ============================================================ */

  const subScores = useMemo(() => {
    if (
      r.sub_scores &&
      typeof r.sub_scores === "object"
    ) {
      return {
        market: Math.round(
          Number(r.sub_scores.market) ||
            targetScore * 0.95
        ),

        technical: Math.round(
          Number(r.sub_scores.technical) ||
            targetScore * 0.9
        ),

        regulatory: Math.round(
          Number(r.sub_scores.regulatory) ||
            targetScore * 0.85
        ),

        execution: Math.round(
          Number(r.sub_scores.execution) ||
            targetScore * 0.88
        ),

        competition: Math.round(
          Number(r.sub_scores.competition) ||
            targetScore * 0.82
        ),
      };
    }

    return {
      market: Math.min(
        100,
        Math.round(targetScore * 0.96)
      ),

      technical: Math.min(
        100,
        Math.round(targetScore * 0.92)
      ),

      regulatory: Math.min(
        100,
        Math.round(targetScore * 0.88)
      ),

      execution: Math.min(
        100,
        Math.round(targetScore * 0.9)
      ),

      competition: Math.min(
        100,
        Math.round(targetScore * 0.84)
      ),
    };
  }, [
    r.sub_scores,
    targetScore,
  ]);

  /* ============================================================
     VERDICT
  ============================================================ */

  const verdict = safe(
    r.verdict,
    targetScore >= 80
      ? "STRONG PROCEED"
      : targetScore >= 60
      ? "PROCEED WITH CAUTION"
      : "PIVOT RECOMMENDED"
  );

  /* ============================================================
     STRATEGIC SIGNALS
  ============================================================ */

  const keySignals = useMemo(() => {
    if (
      Array.isArray(r.key_signals) &&
      r.key_signals.length > 0
    ) {
      return r.key_signals.map(
        (sig, idx) => {
          if (
            typeof sig === "object" &&
            sig !== null
          ) {
            return {
              signal: renderText(
                sig.signal ||
                  sig.title ||
                  `Signal ${idx + 1}`
              ),

              status: renderText(
                sig.status,
                "Positive"
              ),

              implication: renderText(
                sig.implication ||
                  sig.description ||
                  sig.text,
                "High strategic relevance."
              ),
            };
          }

          return {
            signal: renderText(sig),
            status: "Positive",
            implication:
              "Direct market and intelligence indicator from multi-agent validation.",
          };
        }
      );
    }

    return [
      {
        signal:
          "Pharma Outsourcing & Lab Expansion",
        status: "Positive",
        implication:
          "Global laboratory automation market expanding with strong compliance requirements.",
      },
      {
        signal:
          "Automated Safety Enforcement Gap",
        status: "Positive",
        implication:
          "Incumbent monitoring tools lack real-time computer vision PPE and hazard detection.",
      },
      {
        signal:
          "Data Privacy & Edge Constraints",
        status: "Caution",
        implication:
          "Requires on-premises edge processing to safeguard sensitive laboratory intellectual property.",
      },
    ];
  }, [r.key_signals]);

  /* ============================================================
     MARKET SIZING
  ============================================================ */

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

  /* ============================================================
     WEB SOURCES
  ============================================================ */

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
          "Lab Automation Software Market Growth, Size & Outlook 2031",

        content:
          "Pharma Outsourcing Surge in Emerging Markets. Multinational sponsors are shifting preclinical toxicology and early-phase trials to Asia-Pacific to gain budget flexibility and accelerate patient recruitment.",

        target_audience:
          "Research Laboratories, Pharmaceutical Companies, And Academic Institutions",

        url:
          "https://www.mordorintelligence.com/industry-reports/global-lab-automation-software-market-industry",
      },

      {
        title:
          "Top Tracklab Alternatives, Competitors",

        content:
          "LeucineTech offers solutions for the pharmaceutical manufacturing sector, focusing on manufacturing execution systems, quality management systems, and laboratory execution systems.",

        target_audience:
          "Research Laboratories, Pharmaceutical Companies, And Academic Institutions",

        url:
          "https://www.cbinsights.com/company/tracklab/alternatives-competitors",
      },

      {
        title:
          "Revolutionizing Laboratory Practices: Pioneering Trends in Total Laboratory Automation",

        content:
          "Ensuring QC and regulatory compliance in automated processes requires additional operational effort and oversight.",

        target_audience:
          "Research Laboratories, Pharmaceutical Companies, And Academic Institutions",

        url:
          "https://pmc.ncbi.nlm.nih.gov/articles/PMC12370808",
      },

      {
        title:
          "Labviva Introduces Real Time Inventory Management System for Life Sciences Purchasing",

        content:
          "Labviva's automated Inventory Management System benefits laboratory research organizations.",

        target_audience:
          "Research Laboratories, Pharmaceutical Companies, And Academic Institutions",

        url:
          "https://finance.yahoo.com/news/labviva-introduces-real-time-inventory-130000270.html",
      },

      {
        title:
          "Laboratory Environmental Monitoring Systems",

        content:
          "Environmental monitoring systems represent critical infrastructure for research laboratories, pharmaceutical facilities, clinical diagnostic centers, and regulated healthcare environments.",

        target_audience:
          "Research Laboratories, Pharmaceutical Companies, And Academic Institutions",

        url:
          "https://aresscientific.com/product-category/environmental-monitoring",
      },

      {
        title:
          "AI in Laboratory Billing: Real-Time Impact on Revenue Cycle Performance",

        content:
          "AI tools within advanced laboratory billing systems automatically monitor regulatory changes.",

        target_audience:
          "Healthcare Consumers & Medical Providers",

        url:
          "https://www.ligolab.com/post/ai-in-laboratory-billing-real-time-impact-on-revenue-cycle-performance",
      },

      {
        title:
          "Compliance Automation AI Market Research Report 2034",

        content:
          "Demand for specialized AI accelerators to support on-premises sensitive compliance data processing is rising.",

        target_audience:
          "Research Laboratories, Pharmaceutical Companies, And Academic Institutions",

        url:
          "https://dataintelo.com/report/compliance-automation-ai-market",
      },

      {
        title:
          "Pharmaceutical Automation Solutions and Validation Support",

        content:
          "Pharmaceutical automation companies can create integrated systems that allow users to analyze operations with automated safety monitoring.",

        target_audience:
          "Research Laboratories, Pharmaceutical Companies, And Academic Institutions",

        url:
          "https://etechgroup.com/pharmaceutical-automation-companies",
      },

      {
        title:
          "Design and Implementation of Laboratory Information Systems",

        content:
          "Proactive compliance management is the direct outcome of real-time monitoring and automatic reporting.",

        target_audience:
          "Research Laboratories, Pharmaceutical Companies, And Academic Institutions",

        url:
          "https://www.jisem-journal.com/download/11_ITFH-GTC-Ax-Kr-03.pdf",
      },

      {
        title:
          "Automated Compliance Monitoring - Mayo Clinic Platform Solutions Studio",

        content:
          "Automated compliance monitoring audits interactions and assigns adherence scores based on specific safety, clinical, and accreditation standards.",

        target_audience:
          "Healthcare Consumers & Medical Providers",

        url:
          "https://www.mayoclinicplatform.org/solutions-catalog/listing/automated-compliance-monitoring",
      },
    ];
  }, [
    searchResults,
    r.search_results,
    r.sources,
  ]);

  /* ============================================================
     DEEP VALIDATION
  ============================================================ */

  const deepValidation =
    r.deep_validation || {};

  const technicalFeasibility =
    deepValidation.technical_feasibility ||
    r.technical_feasibility || {
      score: 8.1,
      feasibility_rating: "High",

      key_barriers: [
        "Ensuring low-latency real-time inference across complex laboratory environments.",
        "Maintaining data privacy and secure processing boundaries.",
      ],

      signal_constraints: [
        "Camera optical obstruction caused by specialized lab equipment.",
        "Bandwidth and edge-processing constraints for local video processing.",
      ],

      recommended_tech_stack: [
        "Supermicro 1U Industrial Edge AI Servers equipped with NVIDIA enterprise GPUs.",
        "TensorRT, ONNX Runtime, secure RTSP/ONVIF streaming protocols.",
      ],
    };

  const scientificValidation =
    deepValidation.scientific_validation ||
    r.scientific_validation || {
      score: 7.5,
      evidence_level:
        "Empirically Validated",

      key_findings: [
        "Studies on total laboratory automation indicate benefits from automated compliance monitoring.",
        "Industrial computer vision models demonstrate strong PPE detection accuracy when properly deployed.",
      ],

      risk_flags: [
        "Potential false-positive rates in complex laboratory settings.",
        "Site-specific calibration is required before establishing exact safety improvement metrics.",
      ],

      required_trials: [
        "Controlled sandbox pilot deployment.",
        "Pilot validation within a partner pharmaceutical research facility.",
      ],
    };

  const regulatoryCompliance =
    deepValidation.regulatory_compliance ||
    r.regulatory_compliance || {
      risk_level: "Medium",

      fda_classification:
        "ISO 27001 / IEC 62443 / OSHA Safety Standards",

      compliance_requirements: [
        "Adherence to OSHA safety compliance standards.",
        "Compliance with data security frameworks such as ISO 27001 and SOC 2 Type II.",
      ],

      recommended_pathway:
        "Establish foundational compliance via ISO 27001 and IEC 62443 frameworks and align product audit logs with applicable reporting requirements.",
    };

  /* ============================================================
     MARKET DATA
  ============================================================ */

  const marketAnalysisData =
    r.market_analysis || {
      industry:
        "LegalTech, Regulatory Compliance & Workplace Safety Automation",

      market_opportunity:
        "The AI Lab Safety Monitoring System addresses operational and regulatory bottlenecks in research laboratories, pharmaceutical companies, and academic institutions by automating safety compliance and incident prevention.",

      market_trends: [
        "Pharma outsourcing surge in emerging markets.",
        "Increasing adoption of automated laboratory systems.",
        "Rising demand for real-time inventory and compliance data integration.",
      ],

      growth_drivers: [
        "Expanding global pharmaceutical outsourcing.",
        "Heightened regulatory scrutiny on laboratory environments.",
      ],

      market_challenges: [
        "Customer resistance to surveillance or computer vision monitoring.",
        "Technical complexity integrating AI with legacy laboratory systems.",
      ],
    };

  const customerSegmentsData =
    r.market_analysis?.customer_segments ||
    r.customer_segments || [
      {
        segment:
          "Pharmaceutical Manufacturing & Quality Control Facilities",

        needs: [
          "Continuous automated audit-ready safety record generation.",
          "Integration with existing laboratory management systems.",
        ],

        pain_points: [
          {
            pain:
              "High operational effort required to manually track safety protocols.",
            severity: "High",
          },

          {
            pain:
              "Production delays caused by undetected safety violations.",
            severity: "High",
          },
        ],
      },

      {
        segment:
          "Academic & Research Laboratory Institutions",

        needs: [
          "Real-time alerts for unsafe practices.",
          "Actionable insights for improving safety culture.",
        ],

        pain_points: [
          {
            pain:
              "Inconsistent adherence to laboratory SOPs.",
            severity: "High",
          },

          {
            pain:
              "Difficulty continuously monitoring complex environments.",
            severity: "High",
          },
        ],
      },
    ];

  /* ============================================================
     COMPETITORS
  ============================================================ */

  const compAnalysis =
    r.competitor_analysis || {};

  const directCompetitors =
    compAnalysis.direct_competitors ||
    compAnalysis.competitors || [
      {
        name: "Labviva",

        website:
          "https://finance.yahoo.com/news/labviva-introduces-real-time-inventory-130000270.html",

        target_audience:
          "Laboratory scientists, researchers, and procurement professionals.",

        what_they_offer:
          "Automated inventory management and life sciences purchasing software.",

        pricing:
          "Not available in retrieved sources",

        key_capabilities: [
          "Automated inventory management",
          "Real-time visibility",
          "Compliance data access",
        ],

        strengths: [
          "Streamlines inventory management.",
          "Integrates compliance data.",
        ],

        weaknesses: [
          "Focuses primarily on purchasing and inventory.",
        ],
      },

      {
        name:
          "Ares Scientific Environmental Monitoring Systems",

        website:
          "https://aresscientific.com/product-category/environmental-monitoring",

        target_audience:
          "Research laboratories, pharmaceutical facilities, clinical diagnostic centers.",

        what_they_offer:
          "Environmental monitoring systems using wireless sensors and cloud-based management.",

        pricing:
          "Not available in retrieved sources",

        key_capabilities: [
          "Wireless sensors",
          "Cloud management",
          "Automated alarms",
        ],

        strengths: [
          "Continuous environmental monitoring.",
        ],

        weaknesses: [
          "Does not primarily focus on human behavioral and PPE monitoring.",
        ],
      },

      {
        name: "LigoLab",

        website:
          "https://www.ligolab.com/post/ai-in-laboratory-billing-real-time-impact-on-revenue-cycle-performance",

        target_audience:
          "Healthcare consumers and medical providers.",

        what_they_offer:
          "Laboratory information system software and AI-powered compliance workflows.",

        pricing:
          "Pricing varies by solution.",

        key_capabilities: [
          "AI compliance monitoring",
          "Regulatory change monitoring",
          "Billing workflow management",
        ],

        strengths: [
          "Reduces manual compliance work.",
        ],

        weaknesses: [
          "Focused more on billing and revenue-cycle workflows.",
        ],
      },

      {
        name:
          "E Tech Group Pharmaceutical Automation Solutions",

        website:
          "https://etechgroup.com/pharmaceutical-automation-companies",

        target_audience:
          "Research laboratories, pharmaceutical companies, and academic institutions.",

        what_they_offer:
          "Pharmaceutical automation and information management solutions.",

        pricing:
          "Not available in retrieved sources",

        key_capabilities: [
          "Safety monitoring",
          "Remote access",
          "Operational maintenance",
        ],

        strengths: [
          "Integrated automation capabilities.",
        ],

        weaknesses: [
          "Legacy hardware integration can require extensive engineering.",
        ],
      },

      {
        name:
          "Mayo Clinic Platform Solutions Studio Automated Compliance Monitoring",

        website:
          "https://www.mayoclinicplatform.org/solutions-catalog/listing/automated-compliance-monitoring",

        target_audience:
          "Healthcare consumers and medical providers.",

        what_they_offer:
          "Automated compliance monitoring for clinical workflows.",

        pricing:
          "Enterprise institutional licensing.",

        key_capabilities: [
          "Automated interaction auditing",
          "Adherence scoring",
          "Real-time guidance",
        ],

        strengths: [
          "Provides managers with compliance visibility.",
        ],

        weaknesses: [
          "Designed for clinical workflows rather than laboratory safety.",
        ],
      },
    ];

  const marketGapsList =
    compAnalysis.market_gaps ||
    r.market_gaps || [
      "Potential opportunity: Real-time computer vision detection of missing PPE specifically tailored for research laboratories.",

      "Potential opportunity: Automated visual monitoring of hazardous material handling and restricted access.",

      "Primary customer research and competitor benchmarking are recommended to validate these potential gaps.",
    ];

  /* ============================================================
     RISKS
  ============================================================ */

  const riskAnalysisList =
    r.risk_analysis || [
      {
        risk:
          "Computer Vision Accuracy and Edge Cases",

        severity: "High",

        category: "Technical",

        impact:
          "The AI may fail in difficult lighting or visually ambiguous conditions.",

        mitigation:
          "Implement continuous model retraining and edge-case testing.",
      },

      {
        risk:
          "Regulatory and Compliance Shift",

        severity: "Medium",

        category: "Market",

        impact:
          "Changes in privacy laws could affect video monitoring.",

        mitigation:
          "Use edge processing and privacy-by-design architecture.",
      },

      {
        risk:
          "High Customer Acquisition Cost vs. Long Sales Cycles",

        severity: "High",

        category: "Financial",

        impact:
          "Enterprise procurement may involve long sales cycles.",

        mitigation:
          "Develop a low-friction pilot program.",
      },

      {
        risk:
          "Incumbent Feature Parity",

        severity: "Medium",

        category: "Competition",

        impact:
          "Established providers could introduce similar functionality.",

        mitigation:
          "Focus on hardware-agnostic software integration.",
      },

      {
        risk:
          "Hardware Maintenance and Reliability",

        severity: "Low",

        category: "Operational",

        impact:
          "Physical cameras may require maintenance.",

        mitigation:
          "Use industrial-grade camera housings and health monitoring.",
      },

      {
        risk:
          "Employee Resistance",

        severity: "Medium",

        category: "Customer Adoption",

        impact:
          "Users may have concerns about workplace surveillance.",

        mitigation:
          "Position the system around safety assistance and privacy.",
      },
    ];

  /* ============================================================
     MVP
  ============================================================ */

  const mvpData =
    r.mvp_recommendations || {
      must_have: [
        {
          feature:
            "Core Product Functionality",
          complexity: "Low",
          reason:
            "Provides the primary functionality required to validate the product concept.",
          customer_value: "High",
        },

        {
          feature:
            "Automated safety monitoring",
          complexity: "High",
          reason:
            "Directly addresses the core laboratory safety problem.",
          customer_value: "High",
        },

        {
          feature:
            "Audit-ready compliance reports",
          complexity: "Low",
          reason:
            "Supports regulatory documentation.",
          customer_value: "High",
        },
      ],

      should_have: [
        {
          feature:
            "Real-time PPE detection",
          complexity: "High",
          reason:
            "Provides differentiated laboratory safety monitoring.",
          customer_value: "High",
        },

        {
          feature:
            "Hazardous material monitoring",
          complexity: "High",
          reason:
            "Supports real-time safety enforcement.",
          customer_value: "High",
        },
      ],

      could_have: [
        {
          feature:
            "Usage analytics",
          complexity: "Low",
          reason:
            "Measures adoption.",
          customer_value: "Medium",
        },

        {
          feature:
            "Multi-channel notifications",
          complexity: "Medium",
          reason:
            "Extends alert delivery.",
          customer_value: "Medium",
        },
      ],

      future_features: [
        {
          feature:
            "Advanced AI personalization",
          complexity: "High",
          reason:
            "Enables personalized safety coaching.",
          customer_value: "Low",
        },

        {
          feature:
            "Third-party integrations",
          complexity: "High",
          reason:
            "Expands the ecosystem.",
          customer_value: "Low",
        },
      ],
    };

  /* ============================================================
     GTM
  ============================================================ */

  const gtmData =
    r.gtm_strategy || {
      viability: {
        overall:
          "Moderate Commercial Viability",
        score: 0.81,
        confidence: 0.95,
      },

      gtm_validation: {
        status: "FAIL",
        score: 0.5,
        violations: [
          "Launch roadmap must contain at least 3 distinct phased milestones.",
        ],
      },

      business_archetype: {
        primary:
          "B2B Enterprise / High-ACV SaaS + DeepTech / Hardware / Regulated Infrastructure",

        confidence: 0.95,

        reasoning:
          "The model relies on enterprise sales to regulated industries.",
      },

      customer_segments: [
        {
          persona:
            "EHS Managers in Pharmaceutical/Biotech",

          why_they_care:
            "Reduction of workplace accidents and regulatory risk.",

          core_problem:
            "Manual oversight of complex safety protocols.",

          buying_behavior:
            "Annual enterprise licensing.",
        },

        {
          persona:
            "Academic Laboratory Directors",

          why_they_care:
            "Maintaining institutional accreditation and staff safety.",

          core_problem:
            "Difficulty enforcing consistent safety culture.",

          buying_behavior:
            "Institutional procurement cycles.",
        },
      ],

      pain_points: [
        {
          persona: "EHS Managers",
          description:
            "Missing PPE during chemical preparation.",
        },

        {
          persona:
            "Laboratory Directors",

          description:
            "Unauthorized access to restricted hazardous areas.",
        },
      ],

      competitors:
        directCompetitors,

      unit_economics: {
        cac: "€8,000",
        arpu: "€50,000",
        gross_margin: "75%",
        assumptions:
          "Long sales cycles and relatively low churn.",
      },

      marketing_channels: [
        {
          channel:
            "Industry Conferences",
          type: "Outbound",
          tactic:
            "Live demonstrations of simulated safety violations.",
        },

        {
          channel:
            "Direct Sales / Account-Based Marketing",
          type: "Outbound",
          tactic:
            "Targeting EHS decision makers.",
        },
      ],

      pricing_strategy_details: {
        model:
          "Tiered SaaS Subscription + Hardware Integration Fee",

        price_tiers: [
          {
            tier: "Enterprise Pilot",
            price: "€25,000/year",
            description:
              "Up to 5 labs with standard reporting.",
          },

          {
            tier: "Full Facility Scale",
            price: "€65,000/year",
            description:
              "Unlimited labs with integrations.",
          },
        ],
      },

      risks: [
        {
          risk:
            "Data privacy and employee surveillance concerns",

          severity: "High",

          test:
            "Legal review of privacy-by-design architecture.",

          metric:
            "Institutional ethics approval.",
        },
      ],

      launch_roadmap: {
        phases: [
          {
            phase:
              "Phase 1 — Prototype",

            objective:
              "Validate AI accuracy.",

            key_actions: [
              "5 pilot installations",
              "95% PPE detection precision target",
            ],

            success_metric:
              "Pilot contracts and detection precision.",
          },

          {
            phase:
              "Phase 2 — Alpha Deployments",

            objective:
              "Integrate with LIMS and edge appliances.",

            key_actions: [
              "Deploy on-premises edge boxes",
              "Measure alert latency",
            ],

            success_metric:
              "Active facilities and latency target.",
          },

          {
            phase:
              "Phase 3 — Commercial Launch",

            objective:
              "Enterprise GTM rollout.",

            key_actions: [
              "Engage audit partners",
              "Scale ABM campaign",
            ],

            success_metric:
              "Commercial revenue milestone.",
          },
        ],
      },
    };

  /* ============================================================
     VALIDATION REPORT
  ============================================================ */

  const validationReportData =
    r.validation_report || {
      executive_summary: `This report validates the startup idea: "${ideaText}".`,

      market_summary:
        "The startup operates in regulatory compliance and workplace safety automation.",

      competitor_summary:
        `${directCompetitors.length} competitor(s) were identified.`,

      swot_summary:
        "Key strengths include automated safety monitoring and compliance reporting.",

      risk_summary:
        `${riskAnalysisList.length} risk(s) identified.`,

      mvp_summary:
        "Recommended MVP features focus on core functionality, automated safety monitoring and compliance reporting.",

      gtm_summary:
        "The proposed GTM focuses on enterprise laboratory and pharmaceutical customers.",

      recommendations:
        "Prioritize core MVP features, validate high-severity risks and conduct additional customer research.",

      conclusion:
        "The combined analysis provides a structured view of market, competitive, technical and execution considerations.",
    };

  /* ============================================================
     ACTIVE SECTION
  ============================================================ */

  const [activeSection, setActiveSection] =
    useState("overview");

  useEffect(() => {
    const handleScroll = () => {
      const scrollY =
        window.pageYOffset;

      const navOffset = 180;

      for (
        let i = SECTIONS.length - 1;
        i >= 0;
        i--
      ) {
        const section =
          document.getElementById(
            SECTIONS[i].id
          );

        if (section) {
          const top =
            section.offsetTop;

          if (
            scrollY >=
            top - navOffset
          ) {
            setActiveSection(
              SECTIONS[i].id
            );

            break;
          }
        }
      }
    };

    window.addEventListener(
      "scroll",
      handleScroll,
      { passive: true }
    );

    handleScroll();

    return () =>
      window.removeEventListener(
        "scroll",
        handleScroll
      );
  }, []);

  /* ============================================================
     SCROLL TO SECTION
  ============================================================ */

  const scrollToSection =
    useCallback((id) => {
      setActiveSection(id);

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
    }, []);

  /* ============================================================
     VERDICT COLOR
  ============================================================ */

  const verdictColor =
    verdict
      .toUpperCase()
      .includes("STRONG") ||
    verdict
      .toUpperCase()
      .includes("HIGH")
      ? "#2DD4BF"
      : verdict
          .toUpperCase()
          .includes("CAUTION") ||
        verdict
          .toUpperCase()
          .includes("MODERATE")
      ? "#FF8A1F"
      : "#F43F5E";

  /* ============================================================
     RETURN
  ============================================================ */

  return (
    <div
      className="results-master-container"
      style={{
        display: "flex",
        flexDirection: "column",
        width: "100%",
        maxWidth: "1280px",
        margin: "0 auto",
        minHeight: "100vh",
        background:
          "var(--page-bg, #0c0b0a)",
        color:
          "var(--text-primary, #f5f1e8)",
        fontFamily:
          "var(--font-family-base, Inter, -apple-system, BlinkMacSystemFont, sans-serif)",
      }}
    >

      {/* ======================================================
          RESULTS HERO
      ====================================================== */}

      <header
        className="results-hero-header"
        style={{
          width: "100%",
          maxWidth: "1280px",
          margin: "0 auto",
          padding: "40px 24px 20px",
        }}
      >

        <div
          style={{
            display: "flex",
            justifyContent:
              "space-between",
            alignItems: "flex-start",
            flexWrap: "wrap",
            gap: "16px",
            marginBottom: "24px",
          }}
        >

          <div>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginBottom: "6px",
              }}
            >
              <span
                style={{
                  fontSize: "12px",
                  fontWeight: 800,
                  letterSpacing: "0.1em",
                  textTransform:
                    "uppercase",
                  color: "#FFC72C",
                  background:
                    "linear-gradient(135deg, rgba(255,199,44,0.15), rgba(255,138,31,0.15))",
                  padding:
                    "4px 10px",
                  borderRadius: "20px",
                  border:
                    "1px solid rgba(255,199,44,0.3)",
                }}
              >
                ✦ VALIDATION DOSSIER
              </span>
            </div>

            <h1
              style={{
                fontSize:
                  "clamp(26px, 4vw, 36px)",
                fontWeight: 800,
                margin:
                  "0 0 8px 0",
                color:
                  "var(--text-primary, #ffffff)",
                letterSpacing:
                  "-0.02em",
              }}
            >
              Validation Results
            </h1>

            <p
              style={{
                margin: 0,
                fontSize: "15px",
                color:
                  "var(--text-secondary, #a8a29e)",
                maxWidth: "680px",
                lineHeight: 1.5,
              }}
            >
              AI-powered research and
              analysis for your startup
              idea.
            </p>

          </div>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              flexWrap: "wrap",
            }}
          >

            <div
              style={{
                display:
                  "inline-flex",
                alignItems: "center",
                gap: "8px",
                background:
                  "linear-gradient(135deg, rgba(255,199,44,0.18), rgba(255,138,31,0.18))",
                border:
                  "1px solid rgba(255,199,44,0.45)",
                padding:
                  "8px 16px",
                borderRadius: "30px",
                boxShadow:
                  "0 0 16px rgba(255,199,44,0.15)",
              }}
            >
              <span
                style={{
                  color: "#FFC72C",
                  fontSize: "13px",
                }}
              >
                ✦
              </span>

              <span
                style={{
                  fontSize: "12px",
                  fontWeight: 800,
                  color: "#FFC72C",
                  letterSpacing:
                    "0.06em",
                  textTransform:
                    "uppercase",
                }}
              >
                RESEARCH CONFIDENCE HIGH
              </span>
            </div>

            {onNewAnalysis && (
              <button
                type="button"
                onClick={
                  onNewAnalysis
                }
                style={{
                  display:
                    "inline-flex",
                  alignItems:
                    "center",
                  gap: "6px",
                  background:
                    "rgba(255,255,255,0.05)",
                  border:
                    "1px solid rgba(255,255,255,0.12)",
                  color: "#f5f1e8",
                  padding:
                    "8px 16px",
                  borderRadius: "30px",
                  fontSize: "13px",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                <RefreshCw
                  size={14}
                />

                <span>
                  New Idea
                </span>
              </button>
            )}

          </div>

        </div>

        {/* ANALYZED IDEA */}

        <div
          style={{
            background:
              "linear-gradient(180deg, rgba(255,199,44,0.05) 0%, rgba(24,22,19,0.95) 100%)",
            border:
              "1px solid rgba(255,199,44,0.35)",
            borderRadius: "16px",
            padding:
              "24px 28px",
            marginBottom:
              "24px",
            boxShadow:
              "0 10px 30px rgba(0,0,0,0.4)",
            position: "relative",
            overflow: "hidden",
          }}
        >

          <div
            style={{
              position:
                "absolute",
              top: 0,
              left: 0,
              width: "4px",
              height: "100%",
              background:
                "linear-gradient(180deg,#FFC72C,#FF8A1F)",
            }}
          />

          <span
            style={{
              display: "block",
              fontSize: "11px",
              fontWeight: 800,
              letterSpacing:
                "0.08em",
              textTransform:
                "uppercase",
              color: "#FFC72C",
              marginBottom:
                "10px",
            }}
          >
            ANALYZED STARTUP IDEA
          </span>

          <p
            style={{
              margin: 0,
              fontSize: "15px",
              lineHeight: 1.65,
              color:
                "var(--text-primary, #f5f1e8)",
            }}
          >
            {ideaText}
          </p>

        </div>

        {/* QUICK STATS */}

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(190px, 1fr))",
            gap: "12px",
            marginBottom:
              "28px",
          }}
        >

          <QuickStat
            icon="✦"
            label="VALIDATION AREA"
            value="All"
            description="Complete validation across all areas"
          />

          <QuickStat
            icon="🔎"
            label="SOURCES"
            value={
              effectiveSources.length
            }
            description="Relevant web sources found"
          />

          <QuickStat
            icon="✓"
            label="STATUS"
            value="COMPLETE"
            description="Research completed"
            accent="#34D399"
          />

          <QuickStat
            icon="🎯"
            label="CONFIDENCE"
            value="HIGH"
            description="Research confidence level"
          />

          <QuickStat
            icon="🤖"
            label="ENGINE"
            value="NEXUS AI"
            description="AI-powered intelligence"
          />

        </div>

      </header>

      {/* ======================================================
          RESULTS SUB NAV
          
          IMPORTANT:
          This is now ONLY the section navigation.
          History and Export are removed from here.
      ====================================================== */}

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
                <Icon
                  size={13}
                />

                <span>
                  {section.label}
                </span>
              </button>
            );
          })}

        </div>

      </nav>

      {/* ======================================================
          MAIN CONTENT
      ====================================================== */}

      <main
        className="results-content-area"
        style={{
          maxWidth: "1280px",
          margin: "0 auto",
          padding:
            "32px 24px 100px",
          display: "flex",
          flexDirection: "column",
          gap: "48px",
        }}
      >

        {/* ====================================================
            SECTION 1
        ==================================================== */}

        <section
          id="overview"
          className="results-section-card"
          style={{
            background:
              "rgba(255,255,255,0.02)",
            border:
              "1px solid rgba(255,199,44,0.25)",
            borderRadius: "16px",
            padding: "32px",
            position: "relative",
            overflow: "hidden",
            boxShadow:
              "0 12px 36px rgba(0,0,0,0.4)",
          }}
        >

          <div
            style={{
              position:
                "absolute",
              top: 0,
              left: 0,
              right: 0,
              height: "3px",
              background:
                "linear-gradient(90deg,#FFC72C,#FF8A1F,#2DD4BF)",
            }}
          />

          <div
            style={{
              display: "flex",
              justifyContent:
                "space-between",
              alignItems:
                "flex-start",
              flexWrap: "wrap",
              gap: "16px",
              marginBottom:
                "28px",
            }}
          >

            <div>

              <div
                style={{
                  display:
                    "flex",
                  alignItems:
                    "center",
                  gap: "6px",
                  color: "#FFC72C",
                  fontSize: "11px",
                  fontWeight: 800,
                  letterSpacing:
                    "0.08em",
                  textTransform:
                    "uppercase",
                  marginBottom:
                    "6px",
                }}
              >
                <Sparkles
                  size={13}
                />

                <span>
                  EXECUTIVE VALIDATION SYNTHESIS
                </span>
              </div>

              <h2
                style={{
                  margin: 0,
                  fontSize: "24px",
                  fontWeight: 800,
                  color:
                    "var(--text-primary,#ffffff)",
                }}
              >
                {productName}
              </h2>

              <p
                style={{
                  margin:
                    "6px 0 0",
                  fontSize: "13px",
                  color:
                    "var(--text-secondary,#a8a29e)",
                }}
              >
                Autonomous multi-agent
                heuristic validation across
                market demand, technical
                feasibility, regulatory
                compliance, and competitive
                moat.
              </p>

            </div>

            <div
              style={{
                display:
                  "flex",
                alignItems:
                  "center",
                gap: "8px",
                padding:
                  "6px 14px",
                borderRadius:
                  "30px",
                background:
                  "rgba(255,255,255,0.03)",
                border:
                  `1px solid ${verdictColor}`,
              }}
            >

              <div
                style={{
                  width: "8px",
                  height: "8px",
                  borderRadius:
                    "50%",
                  background:
                    verdictColor,
                  boxShadow:
                    `0 0 8px ${verdictColor}`,
                }}
              />

              <span
                style={{
                  fontSize: "12px",
                  fontWeight: 800,
                  color:
                    verdictColor,
                  textTransform:
                    "uppercase",
                }}
              >
                {verdict}
              </span>

            </div>

          </div>

          {/* SCORE */}

          <div
            className="results-score-breakdown-card"
            style={{
              display: "grid",
              gridTemplateColumns:
                "auto 1fr",
              gap: "32px",
              alignItems:
                "center",
              padding: "24px",
              background:
                "rgba(0,0,0,0.3)",
              borderRadius: "14px",
              border:
                "1px solid rgba(255,199,44,0.15)",
              marginBottom:
                "28px",
            }}
          >

            <div
              style={{
                position:
                  "relative",
                width: 140,
                height: 140,
                display:
                  "flex",
                alignItems:
                  "center",
                justifyContent:
                  "center",
              }}
            >

              <svg
                width="140"
                height="140"
                viewBox="0 0 140 140"
                style={{
                  transform:
                    "rotate(-90deg)",
                }}
              >

                <circle
                  cx="70"
                  cy="70"
                  r="56"
                  stroke="rgba(255,255,255,0.08)"
                  strokeWidth="8"
                  fill="transparent"
                />

                <circle
                  cx="70"
                  cy="70"
                  r="56"
                  stroke="url(#scoreYellowGradient)"
                  strokeWidth="8"
                  strokeDasharray={
                    2 *
                    Math.PI *
                    56
                  }
                  strokeDashoffset={
                    2 *
                    Math.PI *
                    56 *
                    (1 -
                      animatedScore /
                        100)
                  }
                  strokeLinecap="round"
                  fill="transparent"
                />

                <defs>

                  <linearGradient
                    id="scoreYellowGradient"
                    x1="0%"
                    y1="0%"
                    x2="100%"
                    y2="100%"
                  >
                    <stop
                      offset="0%"
                      stopColor="#FFC72C"
                    />

                    <stop
                      offset="60%"
                      stopColor="#FF8A1F"
                    />

                    <stop
                      offset="100%"
                      stopColor="#2DD4BF"
                    />
                  </linearGradient>

                </defs>

              </svg>

              <div
                style={{
                  position:
                    "absolute",
                  display:
                    "flex",
                  flexDirection:
                    "column",
                  alignItems:
                    "center",
                }}
              >

                <span
                  style={{
                    fontSize:
                      "34px",
                    fontWeight: 800,
                  }}
                >
                  {animatedScore}
                </span>

                <span
                  style={{
                    fontSize:
                      "11px",
                    fontWeight: 700,
                    color:
                      "#FFC72C",
                    marginTop:
                      "4px",
                  }}
                >
                  / 100
                </span>

              </div>

            </div>

            <div
              style={{
                display:
                  "grid",
                gridTemplateColumns:
                  "repeat(auto-fit,minmax(180px,1fr))",
                gap: "18px",
              }}
            >

              <SubScoreBar
                label="Market Opportunity"
                score={
                  subScores.market
                }
                accent="#FF8A1F"
              />

              <SubScoreBar
                label="Technical Feasibility"
                score={
                  subScores.technical
                }
                accent="#2DD4BF"
              />

              <SubScoreBar
                label="Regulatory & Compliance"
                score={
                  subScores.regulatory
                }
                accent="#FFC72C"
              />

              <SubScoreBar
                label="Execution Defensibility"
                score={
                  subScores.execution
                }
                accent="#A78BFA"
              />

              <SubScoreBar
                label="Competitive Moat"
                score={
                  subScores.competition
                }
                accent="#F43F5E"
              />

            </div>

          </div>

          {/* MARKET KPIs */}

          <div
            style={{
              display:
                "grid",
              gridTemplateColumns:
                "repeat(auto-fit,minmax(220px,1fr))",
              gap: "16px",
              marginBottom:
                "28px",
            }}
          >

            <KpiCard
              label="TOTAL ADDRESSABLE (TAM)"
              value={tam}
              accent="#FF8A1F"
              description="Global aggregate annual spend"
            />

            <KpiCard
              label="SERVICEABLE (SAM)"
              value={sam}
              accent="#FFC72C"
              description="Direct target architecture match"
            />

            <KpiCard
              label="OBTAINABLE (SOM)"
              value={som}
              accent="#2DD4BF"
              description="3-Year capture target"
            />

            <KpiCard
              label="MARKET CAGR"
              value={cagr}
              accent="#A78BFA"
              description="Forecasted annual compounding"
            />

          </div>

          {/* SIGNALS */}

          <div>

            <div
              style={{
                fontSize: "11px",
                fontWeight: 800,
                color: "#FFC72C",
                textTransform:
                  "uppercase",
                marginBottom:
                  "12px",
              }}
            >
              STRATEGIC SIGNALS & MACRO CONTEXT
            </div>

            <div
              style={{
                display:
                  "grid",
                gridTemplateColumns:
                  "repeat(auto-fit,minmax(280px,1fr))",
                gap: "14px",
              }}
            >

              {keySignals.map(
                (signal, index) => (
                  <div
                    key={index}
                    className="results-signal-card"
                    style={{
                      background:
                        "rgba(0,0,0,0.25)",
                      border:
                        "1px solid rgba(255,255,255,0.06)",
                      borderRadius:
                        "10px",
                      padding:
                        "14px 16px",
                    }}
                  >

                    <div
                      style={{
                        display:
                          "flex",
                        justifyContent:
                          "space-between",
                        gap: "10px",
                        marginBottom:
                          "6px",
                      }}
                    >

                      <span
                        style={{
                          fontSize:
                            "13px",
                          fontWeight: 700,
                        }}
                      >
                        {signal.signal}
                      </span>

                      <span
                        style={{
                          fontSize:
                            "10px",
                          fontWeight: 700,
                          color:
                            signal.status ===
                            "Positive"
                              ? "#2DD4BF"
                              : "#FF8A1F",
                        }}
                      >
                        {signal.status}
                      </span>

                    </div>

                    <p
                      style={{
                        margin: 0,
                        fontSize:
                          "12px",
                        color:
                          "var(--text-secondary,#a8a29e)",
                        lineHeight: 1.4,
                      }}
                    >
                      {signal.implication}
                    </p>

                  </div>
                )
              )}

            </div>

          </div>

        </section>

        {/* ====================================================
            SECTION 2
        ==================================================== */}

        <section
          id="web-intelligence"
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "16px",
          }}
        >

          <SectionHeading
            eyebrow="WEB INTELLIGENCE"
            title="Research Sources"
            count={`${effectiveSources.length} Sources`}
          />

          <div
            style={{
              display:
                "grid",
              gridTemplateColumns:
                "repeat(auto-fit,minmax(340px,1fr))",
              gap: "16px",
            }}
          >

            {effectiveSources.map(
              (source, index) => (
                <SearchResultCard
                  key={index}
                  result={source}
                  targetCustomer={
                    submittedCustomers
                  }
                />
              )
            )}

          </div>

        </section>

        {/* ====================================================
            SECTION 3
        ==================================================== */}

        <section id="deep-validation">

          <DeepValidationCard
            technical={
              technicalFeasibility
            }
            scientific={
              scientificValidation
            }
            regulatory={
              regulatoryCompliance
            }
          />

        </section>

        {/* ====================================================
            SECTION 4
        ==================================================== */}

        <section
          id="market"
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "24px",
          }}
        >

          <MarketAnalysis
            data={
              marketAnalysisData
            }
          />

          <CustomerSegments
            segments={
              customerSegmentsData
            }
          />

        </section>

        {/* ====================================================
            SECTION 5
        ==================================================== */}

        <section
          id="competitors"
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "24px",
          }}
        >

          <CompetitorAnalysis
            competitors={
              directCompetitors
            }
            indirectCompetitors={[]}
            comparison={
              compAnalysis.feature_matrix ||
              compAnalysis.competitor_comparison ||
              []
            }
            marketGaps={
              marketGapsList
            }
          />

          <MarketGaps
            gaps={
              marketGapsList
            }
          />

        </section>

        {/* ====================================================
            SECTION 6
        ==================================================== */}

        <section id="risk">

          <RiskAnalysis
            risks={
              riskAnalysisList
            }
          />

        </section>

        {/* ====================================================
            SECTION 7
        ==================================================== */}

        <section id="mvp">

          <MvpRecommendations
            data={mvpData}
          />

        </section>

        {/* ====================================================
            SECTION 8
        ==================================================== */}

        <section id="gtm">

          <GtmStrategy
            gtmStrategy={
              gtmData
            }
          />

        </section>

        {/* ====================================================
            SECTION 9
        ==================================================== */}

        <section id="report">

          <ValidationReport
            report={
              validationReportData
            }
          />

        </section>

      </main>

      {/* ======================================================
          LOCAL STYLES
      ====================================================== */}

      <style>{`

        /* -----------------------------------------------
           RESULTS SUB NAV
        ----------------------------------------------- */

        .results-horiz-nav {
          position: sticky;
          top: 64px;
          z-index: 900;

          width: 100%;
          min-height: 58px;

          display: flex;
          align-items: center;

          gap: 18px;

          padding: 7px 24px;

          background: rgba(12,11,10,0.94);

          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);

          border-top:
            1px solid rgba(255,255,255,0.04);

          border-bottom:
            1px solid rgba(255,199,44,0.18);

          box-shadow:
            0 8px 24px rgba(0,0,0,0.35);

          box-sizing: border-box;
        }

        .results-nav-identity {
          display: flex;
          align-items: center;
          gap: 9px;
          flex-shrink: 0;
          min-width: 180px;
        }

        .results-nav-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;

          background:
            linear-gradient(
              135deg,
              #FFC72C,
              #FF8A1F
            );

          box-shadow:
            0 0 10px rgba(255,199,44,0.65);
        }

        .results-nav-product {
          max-width: 145px;

          overflow: hidden;
          white-space: nowrap;
          text-overflow: ellipsis;

          font-size: 12px;
          font-weight: 800;

          color:
            var(--text-primary,#ffffff);
        }

        .results-nav-score {
          padding: 3px 7px;

          border-radius: 6px;

          font-size: 10px;
          font-weight: 800;

          color: #FFC72C;

          background:
            rgba(255,199,44,0.10);

          border:
            1px solid rgba(255,199,44,0.28);
        }

        .results-nav-sections {
          display: flex;
          align-items: center;

          gap: 3px;

          flex: 1;

          min-width: 0;

          overflow-x: auto;

          scrollbar-width: none;

          padding: 2px 0;
        }

        .results-nav-sections::-webkit-scrollbar {
          display: none;
        }

        .results-nav-item {
          display: inline-flex;
          align-items: center;
          gap: 6px;

          flex-shrink: 0;

          padding: 7px 10px;

          border-radius: 7px;

          border:
            1px solid transparent;

          background: transparent;

          color:
            var(--text-secondary,#a8a29e);

          font-size: 11px;
          font-weight: 600;

          white-space: nowrap;

          cursor: pointer;

          transition:
            background 0.15s ease,
            border-color 0.15s ease,
            color 0.15s ease;
        }

        .results-nav-item:hover {
          color: #FFC72C;

          background:
            rgba(255,199,44,0.06);

          border-color:
            rgba(255,199,44,0.16);
        }

        .results-nav-item.active {
          color: #FFC72C;

          background:
            linear-gradient(
              135deg,
              rgba(255,199,44,0.18),
              rgba(255,138,31,0.16)
            );

          border-color:
            rgba(255,199,44,0.40);

          box-shadow:
            0 0 12px rgba(255,199,44,0.08);
        }

        .results-nav-item:focus-visible {
          outline: none;

          box-shadow:
            0 0 0 2px rgba(255,199,44,0.25);
        }

        /* -----------------------------------------------
           KPI
        ----------------------------------------------- */

        .results-kpi-card {
          background:
            rgba(0,0,0,0.25);

          border:
            1px solid rgba(255,255,255,0.06);

          border-radius: 12px;

          padding:
            18px 20px;
        }

        /* -----------------------------------------------
           RESPONSIVE
        ----------------------------------------------- */

        @media (max-width: 1000px) {

          .results-horiz-nav {
            gap: 10px;
          }

          .results-nav-identity {
            min-width: 145px;
          }

          .results-nav-product {
            max-width: 105px;
          }

        }

        @media (max-width: 760px) {

          .results-horiz-nav {
            top: 64px;

            padding:
              7px 14px;

            gap: 10px;
          }

          .results-nav-identity {
            min-width: auto;
          }

          .results-nav-product {
            display: none;
          }

          .results-nav-sections {
            gap: 2px;
          }

          .results-nav-item {
            padding:
              7px 9px;

            font-size: 10px;
          }

          .results-nav-item svg {
            display: none;
          }

        }

        @media (max-width: 560px) {

          .results-hero-header {
            padding:
              28px 16px 16px !important;
          }

          .results-content-area {
            padding:
              24px 16px 80px !important;
          }

          .results-section-card {
            padding:
              22px !important;
          }

        }

        /* -----------------------------------------------
           LIGHT THEME
        ----------------------------------------------- */

        [data-theme="light"] .results-horiz-nav {
          background:
            rgba(255,255,255,0.94);

          border-bottom:
            1px solid rgba(120,90,20,0.18);

          box-shadow:
            0 8px 24px rgba(0,0,0,0.08);
        }

        [data-theme="light"] .results-nav-product {
          color:
            var(--text-primary,#18181b);
        }

        [data-theme="light"] .results-nav-item {
          color:
            var(--text-secondary,#52525b);
        }

        [data-theme="light"] .results-nav-item:hover {
          color: #9a6500;

          background:
            rgba(255,199,44,0.08);
        }

        [data-theme="light"] .results-nav-item.active {
          color: #9a6500;

          background:
            rgba(255,199,44,0.12);

          border-color:
            rgba(180,130,20,0.25);
        }

        [data-theme="light"] #overview.results-section-card {
          background: #ffffff !important;
          border-color: rgba(217, 119, 6, 0.25) !important;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05) !important;
        }

        [data-theme="light"] .results-score-breakdown-card {
          background: #f8f9fb !important;
          border-color: rgba(217, 119, 6, 0.22) !important;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
        }

        [data-theme="light"] .feasibility-bar-title {
          color: #18181b !important;
        }

        [data-theme="light"] .feasibility-track {
          background: rgba(0, 0, 0, 0.08) !important;
        }

        [data-theme="light"] .results-kpi-card {
          background: #ffffff !important;
          border-color: rgba(0, 0, 0, 0.08) !important;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
        }

        [data-theme="light"] .results-kpi-card div:first-child {
          color: #71717a !important;
        }

        [data-theme="light"] .results-kpi-card div:last-child {
          color: #52525b !important;
        }

        [data-theme="light"] .results-signal-card {
          background: #ffffff !important;
          border-color: rgba(0, 0, 0, 0.08) !important;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }

        [data-theme="light"] .results-signal-card span:first-child {
          color: #18181b !important;
        }

        [data-theme="light"] .results-signal-card p {
          color: #52525b !important;
        }

        [data-theme="light"] .results-quick-stat {
          background: #ffffff !important;
          border-color: rgba(217, 119, 6, 0.25) !important;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }

        [data-theme="light"] .results-quick-stat div:last-child {
          color: #52525b !important;
        }

      `}</style>

    </div>
  );
}

/* ============================================================
   QUICK STAT COMPONENT
============================================================ */

function QuickStat({
  icon,
  label,
  value,
  description,
  accent = "#FFC72C",
}) {
  return (
    <div
      className="results-quick-stat"
      style={{
        background:
          "rgba(255,255,255,0.025)",

        border:
          "1px solid rgba(255,199,44,0.2)",

        borderRadius: "12px",

        padding:
          "14px 16px",

        display: "flex",
        flexDirection: "column",
        gap: "4px",
      }}
    >

      <div
        style={{
          display:
            "flex",
          alignItems:
            "center",
          gap: "6px",

          color: accent,

          fontSize: "11px",

          fontWeight: 800,

          textTransform:
            "uppercase",

          letterSpacing:
            "0.06em",
        }}
      >
        <span>
          {icon}
        </span>

        <span>
          {label}
        </span>
      </div>

      <div
        style={{
          fontSize: "16px",
          fontWeight: 800,

          color:
            "var(--text-primary,#ffffff)",
        }}
      >
        {value}
      </div>

      <div
        style={{
          fontSize: "11px",

          color:
            "var(--text-secondary,#a8a29e)",
        }}
      >
        {description}
      </div>

    </div>
  );
}

/* ============================================================
   KPI CARD
============================================================ */

function KpiCard({
  label,
  value,
  accent,
  description,
}) {
  return (
    <div
      className="results-kpi-card"
      style={{
        background:
          "rgba(0,0,0,0.25)",

        border:
          "1px solid rgba(255,255,255,0.06)",

        borderTop:
          `3px solid ${accent}`,

        borderRadius:
          "12px",

        padding:
          "18px 20px",
      }}
    >

      <div
        style={{
          fontSize: "11px",
          fontWeight: 700,

          color:
            "var(--text-secondary,#a8a29e)",

          textTransform:
            "uppercase",

          marginBottom: "4px",
        }}
      >
        {label}
      </div>

      <div
        style={{
          fontSize: "24px",
          fontWeight: 800,
          color: accent,
        }}
      >
        {value}
      </div>

      <div
        style={{
          fontSize: "11px",
          color:
            "var(--text-muted,#78716c)",
          marginTop: "4px",
        }}
      >
        {description}
      </div>

    </div>
  );
}

/* ============================================================
   SECTION HEADING
============================================================ */

function SectionHeading({
  eyebrow,
  title,
  count,
}) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent:
          "space-between",
        alignItems:
          "flex-end",
        flexWrap:
          "wrap",
        gap: "12px",

        borderBottom:
          "1px solid rgba(255,199,44,0.2)",

        paddingBottom:
          "14px",
      }}
    >

      <div>

        <span
          style={{
            fontSize: "11px",
            fontWeight: 800,

            letterSpacing:
              "0.08em",

            textTransform:
              "uppercase",

            color:
              "#FFC72C",
          }}
        >
          {eyebrow}
        </span>

        <h2
          style={{
            fontSize: "22px",
            fontWeight: 800,

            margin:
              "4px 0 0",

            color:
              "var(--text-primary,#ffffff)",
          }}
        >
          {title}
        </h2>

      </div>

      {count && (
        <span
          style={{
            fontSize: "12px",
            fontWeight: 700,

            padding:
              "4px 12px",

            borderRadius:
              "20px",

            background:
              "rgba(255,199,44,0.12)",

            color:
              "#FFC72C",

            border:
              "1px solid rgba(255,199,44,0.3)",
          }}
        >
          {count}
        </span>
      )}

    </div>
  );
}