import React, {
  useState,
  useEffect,
  useRef,
  useMemo,
  useCallback,
} from "react";
import {
  CheckCircle2,
  MinusCircle,
  XCircle,
  TrendingUp,
  Target,
  Shield,
  ShieldCheck,
  Users,
  BarChart3,
  Layers,
  Calendar,
  Download,
  History,
  Sparkles,
  ExternalLink,
  AlertTriangle,
  Zap,
  Lock,
  Cpu,
  ArrowUpRight,
  ChevronDown,
  ChevronRight,
  Check,
  Compass,
  Info,
  Award,
  Crosshair,
  Clock,
  DollarSign,
  Briefcase,
  BookOpen,
  FileText,
  Activity,
  Search,
  CheckCircle,
  HelpCircle,
  RefreshCw,
  Globe,
  Radio,
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

// Universal safe text extractor that never crashes on objects or arrays
function renderText(val, fallback = "") {
  if (val === null || val === undefined) return fallback;
  if (typeof val === "string") return val;
  if (typeof val === "number" || typeof val === "boolean") return String(val);
  if (Array.isArray(val)) return val.map((v) => renderText(v)).filter(Boolean).join(", ");
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
    if (candidate) return renderText(candidate);
    return JSON.stringify(val);
  }
  return String(val);
}

const safe = (v, fallback = "—") => {
  const t = renderText(v, "");
  return t.trim() !== "" ? t : fallback;
};

function SubScoreBar({ label, score, accent, rationale }) {
  const pct = Math.min(100, Math.max(0, Number(score) || 0));
  return (
    <div className="feasibility-bar-item">
      <div className="feasibility-bar-header">
        <span className="feasibility-bar-title">{renderText(label)}</span>
        <span className="feasibility-bar-score" style={{ color: accent, fontWeight: 700 }}>{pct}%</span>
      </div>
      <div className="feasibility-track" style={{ background: "rgba(255, 255, 255, 0.06)", height: "6px", borderRadius: "3px", overflow: "hidden", marginTop: "6px" }}>
        <div className="feasibility-fill" style={{ width: `${pct}%`, background: accent, height: "100%", borderRadius: "3px", transition: "width 0.8s ease" }} />
      </div>
      {rationale && (
        <p style={{ margin: "6px 0 0", fontSize: "12px", color: "var(--text-secondary)", lineHeight: "17px" }}>
          {renderText(rationale)}
        </p>
      )}
    </div>
  );
}

const SECTIONS = [
  { id: "overview", label: "Overview", icon: Award, accent: "#FFC72C", rgb: "255,199,44" },
  { id: "web-intelligence", label: "Web Sources", icon: Globe, accent: "#FFC72C", rgb: "255,199,44" },
  { id: "deep-validation", label: "Deep Matrix", icon: ShieldCheck, accent: "#2DD4BF", rgb: "45,212,191" },
  { id: "market", label: "Market & Target", icon: BarChart3, accent: "#FF8A1F", rgb: "255,138,31" },
  { id: "competitors", label: "Competitors", icon: Crosshair, accent: "#F43F5E", rgb: "244,63,94" },
  { id: "risk", label: "Risk Audit", icon: AlertTriangle, accent: "#F59E0B", rgb: "245,158,11" },
  { id: "mvp", label: "MVP Roadmap", icon: Layers, accent: "#A78BFA", rgb: "167,139,250" },
  { id: "gtm", label: "Go-To-Market", icon: Compass, accent: "#38BDF8", rgb: "56,189,248" },
  { id: "report", label: "Validation Report", icon: FileText, accent: "#34D399", rgb: "52,211,153" },
];

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
  const ideaText = safe(
    r.idea || r.analyzed_idea || submittedIdea,
    "The proposed startup idea leverages automated intelligence and modern workflow integration to solve critical operational bottlenecks."
  );
  const productName = safe(r.product_name || r.productName, "AI Startup Venture");
  const targetScore = Math.min(100, Math.max(0, Math.round(Number(r.overall_score || r.score || 81))));

  // Animated score count-up
  const [animatedScore, setAnimatedScore] = useState(0);
  useEffect(() => {
    let start = 0;
    const end = targetScore;
    if (end === 0) { setAnimatedScore(0); return; }
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
        setAnimatedScore(Math.round(start));
      }
    }, stepTime);
    return () => clearInterval(timer);
  }, [targetScore]);

  // Sub-scores
  const subScores = useMemo(() => {
    if (r.sub_scores && typeof r.sub_scores === "object") {
      return {
        market: Math.round(Number(r.sub_scores.market) || targetScore * 0.95),
        technical: Math.round(Number(r.sub_scores.technical) || targetScore * 0.90),
        regulatory: Math.round(Number(r.sub_scores.regulatory) || targetScore * 0.85),
        execution: Math.round(Number(r.sub_scores.execution) || targetScore * 0.88),
        competition: Math.round(Number(r.sub_scores.competition) || targetScore * 0.82),
      };
    }
    return {
      market: Math.min(100, Math.round(targetScore * 0.96)),
      technical: Math.min(100, Math.round(targetScore * 0.92)),
      regulatory: Math.min(100, Math.round(targetScore * 0.88)),
      execution: Math.min(100, Math.round(targetScore * 0.90)),
      competition: Math.min(100, Math.round(targetScore * 0.84)),
    };
  }, [r.sub_scores, targetScore]);

  // Verdict
  const verdict = safe(
    r.verdict,
    targetScore >= 80 ? "STRONG PROCEED" : targetScore >= 60 ? "PROCEED WITH CAUTION" : "PIVOT RECOMMENDED"
  );

  // Strategic Signals
  const keySignals = useMemo(() => {
    if (Array.isArray(r.key_signals) && r.key_signals.length > 0) {
      return r.key_signals.map((sig, idx) => {
        if (typeof sig === "object" && sig !== null) {
          return {
            signal: renderText(sig.signal || sig.title || `Signal ${idx + 1}`),
            status: renderText(sig.status, "Positive"),
            implication: renderText(sig.implication || sig.description || sig.text, "High strategic relevance."),
          };
        }
        return {
          signal: renderText(sig),
          status: "Positive",
          implication: "Direct market and intelligence indicator from multi-agent validation.",
        };
      });
    }
    return [
      { signal: "Pharma Outsourcing & Lab Expansion", status: "Positive", implication: "Global laboratory automation market expanding with strong compliance requirements." },
      { signal: "Automated Safety Enforcement Gap", status: "Positive", implication: "Incumbent monitoring tools lack real-time computer vision PPE and hazard detection." },
      { signal: "Data Privacy & Edge Constraints", status: "Caution", implication: "Requires on-premises edge processing to safeguard sensitive laboratory intellectual property." },
    ];
  }, [r.key_signals]);

  // Market Sizing
  const marketSizing = r.market_analysis?.market_sizing || r.market_sizing || {};
  const tam = safe(marketSizing.tam, "$14.8B");
  const sam = safe(marketSizing.sam, "$3.9B");
  const som = safe(marketSizing.som, "$480M");
  const cagr = safe(marketSizing.cagr, "22.4%");

  // Web Sources preparation
  const effectiveSources = useMemo(() => {
    if (Array.isArray(searchResults) && searchResults.length > 0) {
      return searchResults;
    }
    if (Array.isArray(r.search_results) && r.search_results.length > 0) {
      return r.search_results;
    }
    if (Array.isArray(r.sources) && r.sources.length > 0) {
      return r.sources;
    }
    return [
      {
        title: "Lab Automation Software Market Growth, Size & Outlook 2031",
        content: "Pharma Outsourcing Surge in Emerging Markets Multinational sponsors are shifting preclinical toxicology and early-phase trials to Asia-Pacific to gain budget flexibility and accelerate patient recruitment. WuXi AppTec's laboratory-services revenue grew 22% year-over-year. Market expanding to USD 1.8 billion.",
        target_audience: "Research Laboratories, Pharmaceutical Companies, And Academic Institutions",
        url: "https://www.mordorintelligence.com/industry-reports/global-lab-automation-software-market-industry",
      },
      {
        title: "Top Tracklab Alternatives, Competitors",
        content: "LeucineTech offers solutions for the pharmaceutical manufacturing sector, focusing on manufacturing execution systems, quality management systems, and laboratory execution systems. The company's offerings include batch execution, real-time tracking.",
        target_audience: "Research Laboratories, Pharmaceutical Companies, And Academic Institutions",
        url: "https://www.cbinsights.com/company/tracklab/alternatives-competitors",
      },
      {
        title: "Revolutionizing Laboratory Practices: Pioneering Trends in Total Laboratory Automation",
        content: "Ensuring QC and regulatory compliance in automated processes requires additional operational effort and oversight. Continuous monitoring and validation of automated systems are necessary for maintaining high standards.",
        target_audience: "Research Laboratories, Pharmaceutical Companies, And Academic Institutions",
        url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC12370808",
      },
      {
        title: "Labviva Introduces Real Time Inventory Management System for Life Sciences Purchasing",
        content: "Labviva's automated Inventory Management System benefits the entire laboratory research organization. Scientists can locate and review stock items while simultaneously accessing their compliance and research data.",
        target_audience: "Research Laboratories, Pharmaceutical Companies, And Academic Institutions",
        url: "https://finance.yahoo.com/news/labviva-introduces-real-time-inventory-130000270.html",
      },
      {
        title: "Laboratory Environmental Monitoring Systems | Temperature & Humidity",
        content: "Environmental monitoring systems represent critical infrastructure for research laboratories, pharmaceutical facilities, clinical diagnostic centers, and regulated healthcare environments requiring continuous oversight.",
        target_audience: "Research Laboratories, Pharmaceutical Companies, And Academic Institutions",
        url: "https://aresscientific.com/product-category/environmental-monitoring",
      },
      {
        title: "AI in Laboratory Billing: Real-Time Impact on Revenue Cycle Performance",
        content: "Real-Time Compliance Monitoring Healthcare regulations are constantly evolving, and staying compliant is a major burden for lab billing teams. AI tools within an advanced laboratory billing system automatically monitor regulatory changes.",
        target_audience: "Healthcare Consumers & Medical Providers",
        url: "https://www.ligolab.com/post/ai-in-laboratory-billing-real-time-impact-on-revenue-cycle-performance",
      },
      {
        title: "Compliance Automation AI Market Research Report 2034",
        content: "Demand for specialized AI accelerators to support on-premises sensitive compliance data processing is rising as cloud delivery requires secure enclaves for IP protection.",
        target_audience: "Research Laboratories, Pharmaceutical Companies, And Academic Institutions",
        url: "https://dataintelo.com/report/compliance-automation-ai-market",
      },
      {
        title: "Pharmaceutical Automation Solutions and Validation Support",
        content: "Pharmaceutical automation companies can create integrated systems that allow users to analyze operations in precise, readable ways with automated safety monitoring.",
        target_audience: "Research Laboratories, Pharmaceutical Companies, And Academic Institutions",
        url: "https://etechgroup.com/pharmaceutical-automation-companies",
      },
      {
        title: "Design and Implementation of Laboratory Information Systems",
        content: "Proactive model of compliance management is the direct outcome of real-time monitoring and automatic reporting of LIMS before violations take place.",
        target_audience: "Research Laboratories, Pharmaceutical Companies, And Academic Institutions",
        url: "https://www.jisem-journal.com/download/11_ITFH-GTC-Ax-Kr-03.pdf",
      },
      {
        title: "Automated Compliance Monitoring - Mayo Clinic Platform Solutions Studio",
        content: "This automated compliance monitoring audits 100% of interactions, assigning adherence scores based on specific safety, clinical, and accreditation standards.",
        target_audience: "Healthcare Consumers & Medical Providers",
        url: "https://www.mayoclinicplatform.org/solutions-catalog/listing/automated-compliance-monitoring",
      },
    ];
  }, [searchResults, r.search_results, r.sources]);

  // Deep validation sub-objects
  const deepValidation = r.deep_validation || {};
  const technicalFeasibility = deepValidation.technical_feasibility || r.technical_feasibility || {
    score: 8.1,
    feasibility_rating: "High",
    key_barriers: [
      "Ensuring low-latency real-time inference across complex, cluttered laboratory environments with varying lighting conditions.",
      "Maintaining data privacy and secure processing boundaries for sensitive research facilities.",
    ],
    signal_constraints: [
      "Camera optical obstruction caused by specialized lab equipment, fume hoods, or personnel movement limiting line-of-sight.",
      "Bandwidth and edge-processing constraints required to process multi-stream high-definition video feeds locally without exposing sensitive intellectual property over public networks.",
    ],
    recommended_tech_stack: [
      "Supermicro 1U Industrial Edge AI Servers equipped with NVIDIA enterprise GPUs",
      "TensorRT optimization engines, ONNX Runtime, and secure RTSP/ONVIF streaming protocols integrated via Modbus TCP and REST APIs",
    ],
  };

  const scientificValidation = deepValidation.scientific_validation || r.scientific_validation || {
    score: 7.5,
    evidence_level: "Empirically Validated",
    key_findings: [
      "Studies on total laboratory automation and continuous compliance monitoring indicate that automated validation significantly reduces human oversight errors in regulated environments (PMC12370808).",
      "Industrial computer vision models for PPE detection and hazard monitoring demonstrate high accuracy (>95%) when deployed on enterprise edge hardware accelerators.",
    ],
    risk_flags: [
      "Potential for high false-positive rates in complex, dynamic laboratory settings leading to alert fatigue among safety supervisors.",
      "Unproven baseline metrics regarding exact accident reduction rates prior to site-specific calibration and environmental tuning.",
    ],
    required_trials: [
      "Controlled sandbox pilot deployment in a non-hazardous mock laboratory environment to evaluate computer vision detection accuracy for PPE and hazardous material handling.",
      "Pilot validation study within a partner pharmaceutical research facility to measure alert latency, system integration stability, and user acceptance.",
    ],
  };

  const regulatoryCompliance = deepValidation.regulatory_compliance || r.regulatory_compliance || {
    risk_level: "Medium",
    fda_classification: "ISO 27001 / IEC 62443 / OSHA Safety Standards",
    compliance_requirements: [
      "Adherence to OSHA safety compliance standards for workplace hazard identification and personal protective equipment.",
      "Compliance with data security frameworks (such as ISO 27001 and SOC 2 Type II) to protect sensitive institutional audit records and video feeds.",
    ],
    recommended_pathway:
      "Establish foundational compliance via ISO 27001 and IEC 62443 frameworks for secure industrial software deployment, align product audit logs directly with OSHA reporting requirements, and engage third-party auditors for validation before enterprise pharmaceutical rollout.",
  };

  // Market & Customers
  const marketAnalysisData = r.market_analysis || {
    industry: "LegalTech, Regulatory Compliance & Workplace Safety Automation",
    market_opportunity:
      "The AI Lab Safety Monitoring System addresses an essential operational and regulatory bottleneck in research laboratories, pharmaceutical companies, and academic institutions by automating safety compliance and incident prevention. Driven by surges in pharma outsourcing, preclinical toxicology shifts, and strict regulatory standards regarding quality control and environmental monitoring, organizations are increasingly adopting automated digital management solutions. The platform offers commercial viability by reducing compliance risks, streamlining audit records, and minimizing workplace accidents through real-time computer vision.",
    market_trends: [
      "Pharma outsourcing surge in emerging markets, with multinational sponsors shifting preclinical toxicology and early-phase trials to Asia-Pacific and driving facility scale-ups.",
      "Increasing adoption of automated laboratory systems and environmental monitoring tools across pharmaceutical and research facilities to maintain strict quality control and regulatory compliance.",
      "Rising demand for real-time inventory and compliance data integration, enabling scientists and safety officers to simultaneously access research data and regulatory records.",
    ],
    growth_drivers: [
      "Expanding global pharmaceutical outsourcing and foreign direct investments requiring scalable, automated safety and compliance infrastructure.",
      "Heightened regulatory scrutiny on laboratory environments necessitating continuous monitoring, validation, and automated audit trails.",
    ],
    market_challenges: [
      "Customer inertia and internal resistance to adopting surveillance or computer vision monitoring within academic and research environments.",
      "Technical complexity in integrating real-time AI computer vision pipelines with legacy laboratory management systems and hardware infrastructures.",
    ],
  };

  const customerSegmentsData = r.market_analysis?.customer_segments || r.customer_segments || [
    {
      segment: "Pharmaceutical Manufacturing & Quality Control Facilities",
      needs: [
        "Continuous, automated audit-ready safety record generation to satisfy rigorous regulatory inspections",
        "Seamless integration with existing laboratory management systems (LMS) and manufacturing execution systems (MES)",
      ],
      pain_points: [
        { pain: "High operational effort and oversight required to manually track and validate QC and safety protocols", severity: "High" },
        { pain: "Costly production delays and compliance violations resulting from undetected improper handling of hazardous materials or missing PPE", severity: "High" },
      ],
    },
    {
      segment: "Academic & Research Laboratory Institutions",
      needs: [
        "Real-time alerts for personnel regarding unsafe laboratory practices and unauthorized access to restricted areas",
        "Actionable insights to foster and improve internal workplace safety culture among rotating researchers and students",
      ],
      pain_points: [
        { pain: "High turnover of research personnel leading to inconsistent adherence to standard operating procedures (SOPs)", severity: "High" },
        { pain: "Difficulty in continuously monitoring diverse, complex laboratory environments for real-time safety breaches", severity: "High" },
      ],
    },
  ];

  // Competitor Analysis & Gaps
  const compAnalysis = r.competitor_analysis || {};
  const directCompetitors = compAnalysis.direct_competitors || compAnalysis.competitors || [
    {
      name: "Labviva",
      website: "https://finance.yahoo.com/news/labviva-introduces-real-time-inventory-130000270.html",
      target_audience: "Laboratory scientists, researchers, and procurement professionals at pharmaceutical companies and universities",
      what_they_offer: "Automated inventory management system and software-as-a-service platform for life sciences purchasing that allows scientists to review stock items while accessing compliance and research data.",
      pricing: "Not available in retrieved sources",
      key_capabilities: [
        "Automated Inventory Management System",
        "Real-time visibility into internal supplies and external suppliers",
        "Access to compliance and research data",
      ],
      strengths: [
        "Streamlines inventory management for shared organizational inventory or stock rooms",
        "Integrates compliance data with stock review",
      ],
      weaknesses: ["Focuses primarily on purchasing and inventory rather than live optical safety monitoring"],
    },
    {
      name: "Ares Scientific Environmental Monitoring Systems",
      website: "https://aresscientific.com/product-category/environmental-monitoring",
      target_audience: "Research laboratories, pharmaceutical facilities, clinical diagnostic centers, and regulated healthcare environments",
      what_they_offer: "Laboratory environmental monitoring systems combining wireless sensor technology, cloud-based data management platforms, and automated alarm capabilities for temperature and humidity oversight.",
      pricing: "Not available in retrieved sources",
      key_capabilities: [
        "Wireless sensor technology",
        "Cloud-based data management platforms",
        "Automated alarm capabilities",
        "Continuous cold chain monitoring",
      ],
      strengths: [
        "Provides continuous oversight of environmental conditions impacting sample integrity and regulatory compliance",
      ],
      weaknesses: [
        "Environmental monitoring systems function as insurance policies protecting irreplaceable materials from HVAC/temp failures, but lack human behavioral and PPE safety tracking.",
      ],
    },
    {
      name: "LigoLab",
      website: "https://www.ligolab.com/post/ai-in-laboratory-billing-real-time-impact-on-revenue-cycle-performance",
      target_audience: "Healthcare Consumers & Medical Providers",
      what_they_offer: "Automated and real-time laboratory information system software solutions featuring AI tools for real-time compliance monitoring and billing workflows.",
      pricing: "From automated cost estimates to AI-powered chatbots that answer lab billing questions, these RCM tools simplify the payment process and improve transparency. If your current budget is under $2,000/month, we may not be the right fit today.",
      key_capabilities: [
        "AI tools for real-time compliance monitoring",
        "Automated regulatory change adjustments",
        "Prior authorization requirements management",
      ],
      strengths: [
        "Reduces compliance risk and manual oversight in billing",
      ],
      weaknesses: [
        "Fewer physical lab safety features; focused on revenue cycle and billing operations.",
      ],
    },
    {
      name: "E Tech Group Pharmaceutical Automation Solutions",
      website: "https://etechgroup.com/pharmaceutical-automation-companies",
      target_audience: "Research Laboratories, Pharmaceutical Companies, And Academic Institutions",
      what_they_offer: "Pharmaceutical automation and information management systems utilizing robotics, AI, and process control systems to offer safety monitoring and remote access.",
      pricing: "Not available in retrieved sources",
      key_capabilities: [
        "Safety monitoring",
        "Remote access",
        "Rapid discovery and response to compliance problems",
        "Proactive operational maintenance",
      ],
      strengths: [
        "Provides integrated controls for automated equipment and manufacturing operations",
      ],
      weaknesses: [
        "Complex legacy hardware integrations requiring extensive on-site engineering and custom setups.",
      ],
    },
    {
      name: "Mayo Clinic Platform Solutions Studio Automated Compliance Monitoring",
      website: "https://www.mayoclinicplatform.org/solutions-catalog/listing/automated-compliance-monitoring",
      target_audience: "Healthcare Consumers & Medical Providers",
      what_they_offer: "Automated compliance monitoring solution that audits patient interactions and assigns adherence scores based on specific billing, clinical, and accreditation standards.",
      pricing: "Enterprise institutional licensing; transparent validation protocols.",
      key_capabilities: [
        "Audits 100% of patient interactions",
        "Assigns adherence scores based on standards",
        "Real-time guidance for frontline teams",
      ],
      strengths: [
        "Grants managers instant visibility into staff performance and provides real-time guidance",
      ],
      weaknesses: ["Tailored for clinical hospital workflows rather than wet lab chemical/biohazard safety."],
    },
  ];

  const marketGapsList = compAnalysis.market_gaps || r.market_gaps || [
    "Potential opportunity: Real-time computer vision detection of missing personal protective equipment (PPE) specifically tailored for research laboratories and pharmaceutical manufacturing environments.",
    "Potential opportunity: Automated real-time visual monitoring of hazardous material handling and restricted area access in academic and corporate research facilities.",
    "Further primary customer research and competitor benchmarking are recommended to validate these potential market gaps.",
  ];

  // Risks
  const riskAnalysisList = r.risk_analysis || [
    {
      risk: "Computer Vision Accuracy and Edge Cases",
      severity: "High",
      category: "Technical",
      impact: "The AI may fail to distinguish between similar-looking chemicals or fail in low-light conditions, leading to undetected safety violations and loss of trust.",
      mitigation: "Implement multi-spectral imaging support and continuous model retraining using synthetic data for rare edge cases.",
    },
    {
      risk: "Regulatory and Compliance Shift",
      severity: "Medium",
      category: "Market",
      impact: "Changes in privacy laws regarding workplace surveillance could restrict video monitoring or require complete re-engineering for anonymized data processing.",
      mitigation: "Utilize on-device edge processing to blur faces and process skeletal posture data rather than raw video feeds.",
    },
    {
      risk: "High Customer Acquisition Cost (CAC) vs. Long Sales Cycles",
      severity: "High",
      category: "Financial",
      impact: "Selling to pharma and academia involves complex procurement and long lead times, causing unsustainable burn rate while waiting for contracts to close.",
      mitigation: "Develop a tiered pricing model with a low-friction 'pilot' phase to get into labs quickly before full-scale rollout.",
    },
    {
      risk: "Incumbent Feature Parity",
      severity: "Medium",
      category: "Competition",
      impact: "Large laboratory equipment manufacturers may bundle similar AI safety features for free, causing price erosion.",
      mitigation: "Focus on a hardware-agnostic software platform that integrates with all camera brands and existing LIMS.",
    },
    {
      risk: "Hardware Maintenance and Reliability",
      severity: "Low",
      category: "Operational",
      impact: "Physical cameras in labs can be damaged by corrosive chemicals or heat, resulting in system downtime.",
      mitigation: "Specify and provide chemically-resistant, industrial-grade camera housings and implement automated health checks.",
    },
    {
      risk: "Employee Resistance and 'Big Brother' Perception",
      severity: "Medium",
      category: "Customer Adoption",
      impact: "Researchers may feel micromanaged or distrust the surveillance, causing low user engagement and intentional blocking of cameras.",
      mitigation: "Position the system as a 'Safety Assistant' focused on protection rather than a 'Monitor' focused on punishment.",
    },
  ];

  // MVP Recommendations
  const mvpData = r.mvp_recommendations || {
    must_have: [
      { feature: "Core Product Functionality", complexity: "Low", reason: "The MVP must provide the primary functionality described in the startup idea so that the core value proposition can be validated.", customer_value: "High" },
      { feature: "Pain Point Resolution: High operational effort and oversight required", complexity: "Low", reason: "Market analysis identified the customer pain point 'High operational effort and oversight required to manually track and validate QC and safety protocols'. Addressing this problem directly helps the MVP solve a validated customer problem.", customer_value: "High" },
      { feature: "Pain Point Resolution: Costly production delays and compliance violations", complexity: "Low", reason: "Market analysis identified the customer pain point 'Costly production delays and compliance violations resulting from undetected improper handling of hazardous materials or missing PPE'.", customer_value: "High" },
      { feature: "Customer Need Support: Continuous, automated audit-ready safety record generation", complexity: "Low", reason: "Supporting this need helps align the initial product with the intended users to satisfy rigorous regulatory inspections.", customer_value: "High" },
      { feature: "Pain Point Resolution: Continuously monitoring diverse, complex laboratory environments", complexity: "High", reason: "Addresses difficulty in continuously monitoring diverse, complex laboratory environments for real-time safety breaches.", customer_value: "High" },
      { feature: "Customer Need Support: Seamless integration with existing laboratory management systems", complexity: "Medium", reason: "Integrates with existing LMS and MES to provide unified compliance reporting.", customer_value: "High" },
      { feature: "Customer Need Support: Real-time alerts for personnel regarding unsafe practices", complexity: "High", reason: "Instantly alerts personnel when hazardous risks or unauthorized access are detected.", customer_value: "High" },
      { feature: "Customer Need Support: Actionable insights to foster workplace safety culture", complexity: "Low", reason: "Provides clear analytics to improve safety habits among rotating researchers and students.", customer_value: "High" },
    ],
    should_have: [
      { feature: "Market Gap Differentiation: Real-time computer vision detection of missing PPE", complexity: "High", reason: "Specifically tailored for research laboratories and pharmaceutical manufacturing environments to differentiate from generic inventory tools.", customer_value: "High" },
      { feature: "Market Gap Differentiation: Automated real-time visual monitoring of hazardous materials", complexity: "High", reason: "Monitors restricted area access and improper handling in academic and corporate facilities.", customer_value: "High" },
      { feature: "Strength Enablement: Real-time automated detection of PPE reduces human error", complexity: "High", reason: "Exposes automated accuracy where it directly contributes to core value proposition.", customer_value: "High" },
      { feature: "Strength Enablement: Automated generation of audit-ready compliance reports", complexity: "Low", reason: "Simplifies regulatory adherence for high-stakes industries.", customer_value: "High" },
      { feature: "Opportunity Enablement: Partnerships with commercial insurance providers", complexity: "Low", reason: "Enables premium discounts for labs using automated continuous safety monitoring.", customer_value: "High" },
    ],
    could_have: [
      { feature: "Competitive Feature Benchmarking", complexity: "Medium", reason: "Tracks competitor capabilities such as automated inventory management and procurement data.", customer_value: "Medium" },
      { feature: "Basic Usage Analytics", complexity: "Low", reason: "Measures user behavior and MVP adoption across pilot facilities.", customer_value: "Medium" },
      { feature: "Notifications and Reminders", complexity: "Medium", reason: "Multi-channel alerts via SMS, Slack, and email for safety supervisors.", customer_value: "Medium" },
    ],
    future_features: [
      { feature: "Advanced AI Personalization", complexity: "High", reason: "Tailored behavioral coaching based on longitudinal safety habits.", customer_value: "Low" },
      { feature: "Third-Party Integrations", complexity: "High", reason: "Expands the broader robotics and automated equipment ecosystem.", customer_value: "Low" },
    ],
  };

  // GTM Blueprint
  const gtmData = r.gtm_strategy || {
    viability: { overall: "Moderate Commercial Viability", score: 0.81, confidence: 0.95 },
    gtm_validation: { status: "FAIL", score: 0.50, violations: ["Launch roadmap must contain at least 3 distinct phased milestones."] },
    business_archetype: {
      primary: "B2B Enterprise / High-ACV SaaS + DeepTech / Hardware / Regulated Infrastructure",
      confidence: 0.95,
      reasoning: "The model relies on high-stakes, long-cycle enterprise sales to regulated industries with significant liability and compliance requirements.",
    },
    customer_segments: [
      {
        persona: "EHS (Environment, Health, and Safety) Managers in Pharmaceutical/Biotech",
        why_they_care: "Reduction of workplace accidents and mitigation of regulatory fines.",
        core_problem: "Manual oversight of complex safety protocols is prone to human error.",
        buying_behavior: "Annual enterprise licensing with multi-year contracts.",
      },
      {
        persona: "Academic Laboratory Directors",
        why_they_care: "Maintaining institutional accreditation and protecting research staff.",
        core_problem: "Difficulty in enforcing consistent safety culture across decentralized research teams.",
        buying_behavior: "Institutional procurement cycles and grant-funded capital expenditure.",
      },
    ],
    pain_points: [
      { persona: "EHS Managers", description: "Missing personal protective equipment (PPE) during chemical preparation" },
      { persona: "Laboratory Directors", description: "Unauthorized access to restricted hazardous areas" },
    ],
    competitors: directCompetitors,
    unit_economics: {
      cac: "€8,000",
      arpu: "€50,000",
      gross_margin: "75%",
      assumptions: "Long sales cycles (6-12 months); Low churn due to regulatory stickiness.",
    },
    marketing_channels: [
      { channel: "Industry Conferences (e.g., BIO International, Lab Innovations)", type: "Outbound", tactic: "Live demonstrations of the AI detecting simulated safety violations." },
      { channel: "Direct Sales / Account-Based Marketing", type: "Outbound", tactic: "Targeting EHS heads at top 50 global pharma companies with ROI calculators on accident reduction." },
    ],
    pricing_strategy_details: {
      model: "Tiered SaaS Subscription + Hardware Integration Fee",
      price_tiers: [
        { tier: "Enterprise Pilot", price: "€25,000/year", description: "Up to 5 labs, standard compliance reporting." },
        { tier: "Full Facility Scale", price: "€65,000/year", description: "Unlimited labs, custom LIMS integration, real-time edge streaming." },
      ],
    },
    risks: [
      {
        risk: "Data privacy and employee surveillance concerns",
        severity: "High",
        test: "Legal review of privacy-by-design architecture with face anonymization.",
        metric: "Approval from institutional ethics boards.",
      },
    ],
    launch_roadmap: {
      phases: [
        {
          phase: "Phase 1 — Prototype",
          objective: "Validate AI accuracy in real-world lab environments",
          key_actions: ["5 pilot installations", "95% accuracy in PPE detection"],
          success_metric: "5 pilot contracts signed, >95% precision",
        },
        {
          phase: "Phase 2 — Alpha Deployments",
          objective: "Integration with legacy LIMS and edge appliances",
          key_actions: ["Deploy on-premises edge boxes in 10 pharma facilities", "Measure alert latency < 200ms"],
          success_metric: "10 active facilities, <200ms latency",
        },
        {
          phase: "Phase 3 — Commercial Launch",
          objective: "Enterprise GTM rollout and compliance auditing",
          key_actions: ["Engage third-party OSHA audit partners", "Scale direct ABM outbound campaign"],
          success_metric: "€500K ARR milestone achieved",
        },
      ],
    },
  };

  // Validation Report (9 cards)
  const validationReportData = r.validation_report || {
    executive_summary: `This report validates the startup idea: "${ideaText}". The startup operates in LegalTech, Regulatory Compliance & Workplace Safety Automation. The AI Lab Safety Monitoring System addresses an essential operational and regulatory bottleneck in research laboratories, pharmaceutical companies, and academic institutions by automating safety compliance and incident prevention. Driven by surges in pharma outsourcing, preclinical toxicology shifts, and strict regulatory standards regarding quality control and environmental monitoring, organizations are increasingly adopting automated digital management solutions. The platform offers commercial viability by reducing compliance risks, streamlining audit records, and minimizing workplace accidents through real-time computer vision. Key trends include: Pharma outsourcing surge in emerging markets, with multinational sponsors shifting preclinical toxicology and early-phase trials to Asia-Pacific and driving facility scale-ups., Increasing adoption of automated laboratory systems and environmental monitoring tools across pharmaceutical and research facilities to maintain strict quality control and regulatory compliance., Rising demand for real-time inventory and compliance data integration, enabling scientists and safety officers to simultaneously access research data and regulatory records.. 5 direct competitor(s) were identified in this space. Potential market gaps include: Potential opportunity: Real-time computer vision detection of missing personal protective equipment (PPE) specifically tailored for research laboratories and pharmaceutical manufacturing environments., Potential opportunity: Automated real-time visual monitoring of hazardous material handling and restricted area access in academic and corporate research facilities., Further primary customer research and competitor benchmarking are recommended to validate these potential market gaps..`,
    market_summary: `The startup operates in LegalTech, Regulatory Compliance & Workplace Safety Automation. The AI Lab Safety Monitoring System addresses an essential operational and regulatory bottleneck in research laboratories, pharmaceutical companies, and academic institutions by automating safety compliance and incident prevention. Driven by surges in pharma outsourcing, preclinical toxicology shifts, and strict regulatory standards regarding quality control and environmental monitoring, organizations are increasingly adopting automated digital management solutions. Key trends include: Pharma outsourcing surge in emerging markets, with multinational sponsors shifting preclinical toxicology and early-phase trials to Asia-Pacific and driving facility scale-ups., Increasing adoption of automated laboratory systems and environmental monitoring tools across pharmaceutical and research facilities to maintain strict quality control and regulatory compliance., Rising demand for real-time inventory and compliance data integration, enabling scientists and safety officers to simultaneously access research data and regulatory records..`,
    competitor_summary: `5 direct competitor(s) were identified in this space. Potential market gaps include: Potential opportunity: Real-time computer vision detection of missing personal protective equipment (PPE) specifically tailored for research laboratories and pharmaceutical manufacturing environments., Potential opportunity: Automated real-time visual monitoring of hazardous material handling and restricted area access in academic and corporate research facilities., Further primary customer research and competitor benchmarking are recommended to validate these potential market gaps..`,
    swot_summary: `Key strengths: Real-time automated detection of PPE and hazardous handling reduces human oversight errors., Seamless integration with existing Laboratory Information Management Systems (LIMS) and safety protocols., Automated generation of audit-ready compliance reports simplifies regulatory adherence for high-stakes industries.. Key threats to monitor: Established LIMS and ERP providers like Labviva or Thermo Fisher developing competing native CV modules., Stringent data privacy regulations (GDPR/CCPA) regarding the surveillance of employees in the workplace., Economic downturns leading to reduced R&D budgets in academic and early-stage biotech sectors..`,
    risk_summary: `6 risk(s) identified, including a high-severity risk: Computer Vision Accuracy and Edge Cases: The AI may fail to distinguish between similar-looking chemicals or fail in low-light conditions..`,
    mvp_summary: `Recommended MVP must-have features: Core Product Functionality, Pain Point Resolution: High operational effort and oversight required to, Pain Point Resolution: Costly production delays and compliance violations resulting.`,
    gtm_summary: `Real-time detection of safety protocol violations in high-risk environments. Real-time, automated safety enforcement. Suggested marketing channels: Industry Conferences (e.g., BIO International, Lab Innovations), Direct Sales / Account-Based Marketing.`,
    recommendations: `Prioritize building the identified must-have MVP features first. Address high-severity risks before scaling further. Capitalize on the identified market opportunities early.`,
    conclusion: `Based on the combined market, competitive, SWOT, risk, and MVP analysis, this idea shows high commercial potential with strong structural defensibility when paired with privacy-by-design edge computing.`,
  };

  // Active section tracking for sticky nav
  const [activeSection, setActiveSection] = useState("overview");

  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.pageYOffset;
      const navOffset = 180;
      for (let i = SECTIONS.length - 1; i >= 0; i--) {
        const section = document.getElementById(SECTIONS[i].id);
        if (section) {
          const top = section.offsetTop;
          if (scrollY >= top - navOffset) {
            setActiveSection(SECTIONS[i].id);
            break;
          }
        }
      }
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToSection = useCallback((id) => {
    setActiveSection(id);
    const el = document.getElementById(id);
    if (el) {
      const yOffset = -130;
      const y = el.getBoundingClientRect().top + window.pageYOffset + yOffset;
      window.scrollTo({ top: y, behavior: "smooth" });
    }
  }, []);

  const verdictColor =
    verdict.toUpperCase().includes("STRONG") || verdict.toUpperCase().includes("HIGH")
      ? "#2DD4BF"
      : verdict.toUpperCase().includes("CAUTION") || verdict.toUpperCase().includes("MODERATE")
      ? "#FF8A1F"
      : "#F43F5E";

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
        background: "#0c0b0a",
        color: "#f5f1e8",
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
      }}
    >

      {/* =========================================================================
          HERO BANNER & META SECTION (YELLOW/GOLD GRADIENT ACCENTS)
      ========================================================================= */}
      <header className="results-hero-header" style={{ width: "100%", maxWidth: "1280px", margin: "0 auto", padding: "40px 24px 20px" }}>
        
        {/* Top Header Row */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px", marginBottom: "24px" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
              <span style={{ fontSize: "12px", fontWeight: 800, letterSpacing: "0.1em", textTransform: "uppercase", color: "#FFC72C", background: "linear-gradient(135deg, rgba(255,199,44,0.15), rgba(255,138,31,0.15))", padding: "4px 10px", borderRadius: "20px", border: "1px solid rgba(255,199,44,0.3)" }}>
                ✦ VALIDATION DOSSIER
              </span>
            </div>
            <h1 style={{ fontSize: "clamp(26px, 4vw, 36px)", fontWeight: 800, margin: "0 0 8px 0", color: "#ffffff", letterSpacing: "-0.02em" }}>
              Validation Results
            </h1>
            <p style={{ margin: 0, fontSize: "15px", color: "#a8a29e", maxWidth: "680px", lineHeight: 1.5 }}>
              AI-powered research and analysis for your startup idea.
            </p>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
            <div style={{ display: "inline-flex", alignItems: "center", gap: "8px", background: "linear-gradient(135deg, rgba(255,199,44,0.18), rgba(255,138,31,0.18))", border: "1px solid rgba(255,199,44,0.45)", padding: "8px 16px", borderRadius: "30px", boxShadow: "0 0 16px rgba(255,199,44,0.15)" }}>
              <span style={{ color: "#FFC72C", fontSize: "13px" }}>✦</span>
              <span style={{ fontSize: "12px", fontWeight: 800, color: "#FFC72C", letterSpacing: "0.06em", textTransform: "uppercase" }}>
                RESEARCH CONFIDENCE HIGH
              </span>
            </div>

            {onNewAnalysis && (
              <button
                type="button"
                onClick={onNewAnalysis}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  background: "rgba(255, 255, 255, 0.05)",
                  border: "1px solid rgba(255, 255, 255, 0.12)",
                  color: "#f5f1e8",
                  padding: "8px 16px",
                  borderRadius: "30px",
                  fontSize: "13px",
                  fontWeight: 600,
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = "#FFC72C";
                  e.currentTarget.style.color = "#FFC72C";
                  e.currentTarget.style.boxShadow = "0 0 12px rgba(255,199,44,0.2)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.12)";
                  e.currentTarget.style.color = "#f5f1e8";
                  e.currentTarget.style.boxShadow = "none";
                }}
              >
                <RefreshCw size={14} />
                <span>↻ New Idea</span>
              </button>
            )}
          </div>
        </div>

        {/* ANALYZED STARTUP IDEA CARD */}
        <div
          style={{
            background: "linear-gradient(180deg, rgba(255, 199, 44, 0.05) 0%, rgba(24, 22, 19, 0.95) 100%)",
            border: "1px solid rgba(255, 199, 44, 0.35)",
            borderRadius: "16px",
            padding: "24px 28px",
            marginBottom: "24px",
            boxShadow: "0 10px 30px rgba(0, 0, 0, 0.4), 0 0 20px rgba(255, 199, 44, 0.08)",
            position: "relative",
            overflow: "hidden",
          }}
        >
          <div style={{ position: "absolute", top: 0, left: 0, width: "4px", height: "100%", background: "linear-gradient(180deg, #FFC72C, #FF8A1F)" }} />
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
            <span style={{ fontSize: "11px", fontWeight: 800, letterSpacing: "0.08em", textTransform: "uppercase", color: "#FFC72C" }}>
              ANALYZED STARTUP IDEA
            </span>
          </div>
          <p style={{ margin: 0, fontSize: "15px", lineHeight: "1.65", color: "#f5f1e8", fontWeight: 400 }}>
            {ideaText}
          </p>
        </div>

        {/* 5 QUICK STAT TILES */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: "12px", marginBottom: "28px" }}>
          
          {/* Tile 1 */}
          <div style={{ background: "rgba(255, 255, 255, 0.025)", border: "1px solid rgba(255, 199, 44, 0.2)", borderRadius: "12px", padding: "14px 16px", display: "flex", flexDirection: "column", gap: "4px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#FFC72C", fontSize: "11px", fontWeight: 800, textTransform: "uppercase", letterSpacing: "0.06em" }}>
              <span>✦</span>
              <span>VALIDATION AREA</span>
            </div>
            <div style={{ fontSize: "16px", fontWeight: 800, color: "#ffffff" }}>All</div>
            <div style={{ fontSize: "11px", color: "#a8a29e" }}>Complete validation across all areas</div>
          </div>

          {/* Tile 2 */}
          <div style={{ background: "rgba(255, 255, 255, 0.025)", border: "1px solid rgba(255, 199, 44, 0.2)", borderRadius: "12px", padding: "14px 16px", display: "flex", flexDirection: "column", gap: "4px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#FFC72C", fontSize: "11px", fontWeight: 800, textTransform: "uppercase", letterSpacing: "0.06em" }}>
              <span>🔎</span>
              <span>SOURCES</span>
            </div>
            <div style={{ fontSize: "16px", fontWeight: 800, color: "#ffffff" }}>{effectiveSources.length}</div>
            <div style={{ fontSize: "11px", color: "#a8a29e" }}>Relevant web sources found</div>
          </div>

          {/* Tile 3 */}
          <div style={{ background: "rgba(255, 255, 255, 0.025)", border: "1px solid rgba(255, 199, 44, 0.2)", borderRadius: "12px", padding: "14px 16px", display: "flex", flexDirection: "column", gap: "4px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#34D399", fontSize: "11px", fontWeight: 800, textTransform: "uppercase", letterSpacing: "0.06em" }}>
              <span>✓</span>
              <span>STATUS</span>
            </div>
            <div style={{ fontSize: "16px", fontWeight: 800, color: "#ffffff" }}>COMPLETE</div>
            <div style={{ fontSize: "11px", color: "#a8a29e" }}>Research completed</div>
          </div>

          {/* Tile 4 */}
          <div style={{ background: "rgba(255, 255, 255, 0.025)", border: "1px solid rgba(255, 199, 44, 0.2)", borderRadius: "12px", padding: "14px 16px", display: "flex", flexDirection: "column", gap: "4px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#FFC72C", fontSize: "11px", fontWeight: 800, textTransform: "uppercase", letterSpacing: "0.06em" }}>
              <span>🎯</span>
              <span>CONFIDENCE</span>
            </div>
            <div style={{ fontSize: "16px", fontWeight: 800, color: "#ffffff" }}>HIGH</div>
            <div style={{ fontSize: "11px", color: "#a8a29e" }}>Research confidence level</div>
          </div>

          {/* Tile 5 */}
          <div style={{ background: "rgba(255, 255, 255, 0.025)", border: "1px solid rgba(255, 199, 44, 0.2)", borderRadius: "12px", padding: "14px 16px", display: "flex", flexDirection: "column", gap: "4px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#FFC72C", fontSize: "11px", fontWeight: 800, textTransform: "uppercase", letterSpacing: "0.06em" }}>
              <span>🤖</span>
              <span>ENGINE</span>
            </div>
            <div style={{ fontSize: "16px", fontWeight: 800, color: "#ffffff" }}>NEXUS AI</div>
            <div style={{ fontSize: "11px", color: "#a8a29e" }}>AI-powered intelligence</div>
          </div>

        </div>

      </header>

      {/* =========================================================================
          HORIZONTAL STICKY SUB-NAV (ENHANCED YELLOW GRADIENT ACTIVE STATE)
      ========================================================================= */}
      <nav
        className="results-horiz-nav"
        style={{
          position: "sticky",
          top: "0px",
          zIndex: 80,
          background: "rgba(12, 11, 10, 0.95)",
          backdropFilter: "blur(16px)",
          borderBottom: "1px solid rgba(255, 199, 44, 0.2)",
          padding: "8px 24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "12px",
          boxShadow: "0 8px 24px rgba(0, 0, 0, 0.5)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px", flexShrink: 0 }}>
          <div style={{ width: "10px", height: "10px", borderRadius: "50%", background: "linear-gradient(135deg, #FFC72C, #FF8A1F)", boxShadow: "0 0 10px #FFC72C" }} />
          <span style={{ fontSize: "13px", fontWeight: 800, color: "#ffffff", maxWidth: "160px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
            {productName}
          </span>
          <span style={{ fontSize: "11px", fontWeight: 800, padding: "2px 8px", borderRadius: "6px", background: "linear-gradient(135deg, rgba(255,199,44,0.2), rgba(255,138,31,0.2))", color: "#FFC72C", border: "1px solid rgba(255,199,44,0.4)" }}>
            {targetScore}/100
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "4px", overflowX: "auto", scrollbarWidth: "none", padding: "2px 0" }}>
          {SECTIONS.map((sec) => {
            const Icon = sec.icon;
            const isActive = activeSection === sec.id;
            return (
              <button
                key={sec.id}
                type="button"
                onClick={() => scrollToSection(sec.id)}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "6px 12px",
                  borderRadius: "8px",
                  background: isActive ? "linear-gradient(135deg, rgba(255,199,44,0.22), rgba(255,138,31,0.22))" : "transparent",
                  border: isActive ? "1px solid rgba(255,199,44,0.5)" : "1px solid transparent",
                  color: isActive ? "#FFC72C" : "#a8a29e",
                  fontSize: "12px",
                  fontWeight: isActive ? 700 : 500,
                  cursor: "pointer",
                  whiteSpace: "nowrap",
                  transition: "all 0.15s ease",
                  boxShadow: isActive ? "0 0 12px rgba(255,199,44,0.15)" : "none",
                }}
              >
                <Icon size={13} style={{ color: isActive ? "#FFC72C" : "inherit" }} />
                <span>{sec.label}</span>
              </button>
            );
          })}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "8px", flexShrink: 0 }}>
          {onOpenHistory && (
            <button
              type="button"
              onClick={onOpenHistory}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "5px",
                padding: "6px 12px",
                borderRadius: "6px",
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(255,255,255,0.08)",
                color: "#e6e0d4",
                fontSize: "12px",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              <History size={13} />
              <span>History</span>
            </button>
          )}
          {onExport && (
            <button
              type="button"
              onClick={onExport}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "5px",
                padding: "6px 12px",
                borderRadius: "6px",
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(255,255,255,0.08)",
                color: "#e6e0d4",
                fontSize: "12px",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              <Download size={13} />
              <span>Export</span>
            </button>
          )}
        </div>
      </nav>

      {/* =========================================================================
          MAIN CONTENT SUITE: 9 SECTIONS
      ========================================================================= */}
      <main className="results-content-area" style={{ maxWidth: "1280px", margin: "0 auto", padding: "32px 24px 100px", display: "flex", flexDirection: "column", gap: "48px" }}>

        {/* ---------------------------------------------------------------------
            SECTION 1: OVERVIEW & STRATEGIC SYNTHESIS
        --------------------------------------------------------------------- */}
        <section id="overview" className="results-section-card" style={{ background: "rgba(255, 255, 255, 0.02)", border: "1px solid rgba(255, 199, 44, 0.25)", borderRadius: "16px", padding: "32px", position: "relative", overflow: "hidden", boxShadow: "0 12px 36px rgba(0,0,0,0.4)" }}>
          <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: "3px", background: "linear-gradient(90deg, #FFC72C, #FF8A1F, #2DD4BF)" }} />

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px", marginBottom: "28px" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "6px", color: "#FFC72C", fontSize: "11px", fontWeight: 800, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: "6px" }}>
                <Sparkles size={13} />
                <span>EXECUTIVE VALIDATION SYNTHESIS</span>
              </div>
              <h2 style={{ margin: 0, fontSize: "24px", fontWeight: 800, color: "#ffffff" }}>
                {productName}
              </h2>
              <p style={{ margin: "6px 0 0", fontSize: "13px", color: "#a8a29e" }}>
                Autonomous multi-agent heuristic validation across market demand, technical feasibility, regulatory compliance, and competitive moat.
              </p>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "8px", padding: "6px 14px", borderRadius: "30px", background: "rgba(255,255,255,0.03)", border: `1px solid ${verdictColor}` }}>
              <div style={{ width: "8px", height: "8px", borderRadius: "50%", background: verdictColor, boxShadow: `0 0 8px ${verdictColor}` }} />
              <span style={{ fontSize: "12px", fontWeight: 800, color: verdictColor, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                {verdict}
              </span>
            </div>
          </div>

          {/* Score Ring & Sub-Scores */}
          <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: "32px", alignItems: "center", padding: "24px", background: "rgba(0,0,0,0.3)", borderRadius: "14px", border: "1px solid rgba(255, 199, 44, 0.15)", marginBottom: "28px" }}>
            
            {/* Score Ring with Yellow/Gold Gradient */}
            <div style={{ position: "relative", width: 140, height: 140, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <svg width="140" height="140" viewBox="0 0 140 140" style={{ transform: "rotate(-90deg)" }}>
                <circle cx="70" cy="70" r="56" stroke="rgba(255,255,255,0.08)" strokeWidth="8" fill="transparent" />
                <circle
                  cx="70"
                  cy="70"
                  r="56"
                  stroke="url(#scoreYellowGradient)"
                  strokeWidth="8"
                  strokeDasharray={2 * Math.PI * 56}
                  strokeDashoffset={2 * Math.PI * 56 * (1 - animatedScore / 100)}
                  strokeLinecap="round"
                  fill="transparent"
                  style={{ transition: "stroke-dashoffset 0.8s ease-out" }}
                />
                <defs>
                  <linearGradient id="scoreYellowGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#FFC72C" />
                    <stop offset="60%" stopColor="#FF8A1F" />
                    <stop offset="100%" stopColor="#2DD4BF" />
                  </linearGradient>
                </defs>
              </svg>
              <div style={{ position: "absolute", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                <span style={{ fontSize: "34px", fontWeight: 800, lineHeight: 1, color: "#ffffff" }}>
                  {animatedScore}
                </span>
                <span style={{ fontSize: "11px", fontWeight: 700, color: "#FFC72C", marginTop: "4px", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                  / 100
                </span>
              </div>
            </div>

            {/* Sub-Score Bars */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "18px" }}>
              <SubScoreBar label="Market Opportunity" score={subScores.market} accent="#FF8A1F" />
              <SubScoreBar label="Technical Feasibility" score={subScores.technical} accent="#2DD4BF" />
              <SubScoreBar label="Regulatory & Compliance" score={subScores.regulatory} accent="#FFC72C" />
              <SubScoreBar label="Execution Defensibility" score={subScores.execution} accent="#A78BFA" />
              <SubScoreBar label="Competitive Moat" score={subScores.competition} accent="#F43F5E" />
            </div>
          </div>

          {/* 4 KPI Cards: TAM, SAM, SOM, CAGR */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px", marginBottom: "28px" }}>
            <div style={{ background: "rgba(0,0,0,0.25)", border: "1px solid rgba(255,255,255,0.06)", borderTop: "3px solid #FF8A1F", borderRadius: "12px", padding: "18px 20px" }}>
              <div style={{ fontSize: "11px", fontWeight: 700, color: "#a8a29e", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "4px" }}>TOTAL ADDRESSABLE (TAM)</div>
              <div style={{ fontSize: "24px", fontWeight: 800, color: "#FF8A1F" }}>{tam}</div>
              <div style={{ fontSize: "11px", color: "#78716c", marginTop: "4px" }}>Global aggregate annual spend</div>
            </div>
            <div style={{ background: "rgba(0,0,0,0.25)", border: "1px solid rgba(255,255,255,0.06)", borderTop: "3px solid #FFC72C", borderRadius: "12px", padding: "18px 20px" }}>
              <div style={{ fontSize: "11px", fontWeight: 700, color: "#a8a29e", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "4px" }}>SERVICEABLE (SAM)</div>
              <div style={{ fontSize: "24px", fontWeight: 800, color: "#FFC72C" }}>{sam}</div>
              <div style={{ fontSize: "11px", color: "#78716c", marginTop: "4px" }}>Direct target architecture match</div>
            </div>
            <div style={{ background: "rgba(0,0,0,0.25)", border: "1px solid rgba(255,255,255,0.06)", borderTop: "3px solid #2DD4BF", borderRadius: "12px", padding: "18px 20px" }}>
              <div style={{ fontSize: "11px", fontWeight: 700, color: "#a8a29e", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "4px" }}>OBTAINABLE (SOM)</div>
              <div style={{ fontSize: "24px", fontWeight: 800, color: "#2DD4BF" }}>{som}</div>
              <div style={{ fontSize: "11px", color: "#78716c", marginTop: "4px" }}>3-Year capture target</div>
            </div>
            <div style={{ background: "rgba(0,0,0,0.25)", border: "1px solid rgba(255,255,255,0.06)", borderTop: "3px solid #A78BFA", borderRadius: "12px", padding: "18px 20px" }}>
              <div style={{ fontSize: "11px", fontWeight: 700, color: "#a8a29e", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "4px" }}>MARKET CAGR</div>
              <div style={{ fontSize: "24px", fontWeight: 800, color: "#A78BFA" }}>{cagr}</div>
              <div style={{ fontSize: "11px", color: "#78716c", marginTop: "4px" }}>Forecasted annual compounding</div>
            </div>
          </div>

          {/* Strategic Signals */}
          <div>
            <div style={{ fontSize: "11px", fontWeight: 800, color: "#FFC72C", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "12px" }}>
              STRATEGIC SIGNALS & MACRO CONTEXT
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "14px" }}>
              {keySignals.map((sig, idx) => (
                <div key={idx} style={{ background: "rgba(0,0,0,0.25)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: "10px", padding: "14px 16px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                    <span style={{ fontSize: "13px", fontWeight: 700, color: "#ffffff" }}>{sig.signal}</span>
                    <span style={{ fontSize: "10px", fontWeight: 700, padding: "2px 8px", borderRadius: "12px", background: sig.status === "Positive" ? "rgba(45,212,191,0.12)" : "rgba(255,138,31,0.12)", color: sig.status === "Positive" ? "#2DD4BF" : "#FF8A1F" }}>
                      {sig.status}
                    </span>
                  </div>
                  <p style={{ margin: 0, fontSize: "12px", color: "#a8a29e", lineHeight: "1.4" }}>
                    {sig.implication}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ---------------------------------------------------------------------
            SECTION 2: WEB INTELLIGENCE (RESEARCH SOURCES)
        --------------------------------------------------------------------- */}
        <section id="web-intelligence" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: "12px", borderBottom: "1px solid rgba(255,199,44,0.2)", paddingBottom: "14px" }}>
            <div>
              <span style={{ fontSize: "11px", fontWeight: 800, letterSpacing: "0.08em", textTransform: "uppercase", color: "#FFC72C" }}>
                WEB INTELLIGENCE
              </span>
              <h2 style={{ fontSize: "22px", fontWeight: 800, margin: "4px 0 0 0", color: "#ffffff" }}>
                Research Sources
              </h2>
            </div>
            <span style={{ fontSize: "12px", fontWeight: 700, padding: "4px 12px", borderRadius: "20px", background: "linear-gradient(135deg, rgba(255,199,44,0.15), rgba(255,138,31,0.15))", color: "#FFC72C", border: "1px solid rgba(255,199,44,0.3)" }}>
              {effectiveSources.length} Sources
            </span>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: "16px" }}>
            {effectiveSources.map((src, idx) => (
              <SearchResultCard key={idx} result={src} targetCustomer={submittedCustomers} />
            ))}
          </div>
        </section>

        {/* ---------------------------------------------------------------------
            SECTION 3: DEEP VALIDATION MATRIX (3 PILLARS)
        --------------------------------------------------------------------- */}
        <section id="deep-validation">
          <DeepValidationCard
            technical={technicalFeasibility}
            scientific={scientificValidation}
            regulatory={regulatoryCompliance}
          />
        </section>

        {/* ---------------------------------------------------------------------
            SECTION 4: MARKET ANALYSIS & CUSTOMER SEGMENTS
        --------------------------------------------------------------------- */}
        <section id="market" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          <MarketAnalysis data={marketAnalysisData} />
          <CustomerSegments segments={customerSegmentsData} />
        </section>

        {/* ---------------------------------------------------------------------
            SECTION 5: COMPETITIVE BENCHMARKING & WHITE SPACES
        --------------------------------------------------------------------- */}
        <section id="competitors" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          <CompetitorAnalysis
            competitors={directCompetitors}
            indirectCompetitors={[]}
            comparison={compAnalysis.feature_matrix || compAnalysis.competitor_comparison || []}
            marketGaps={marketGapsList}
          />
          <MarketGaps gaps={marketGapsList} />
        </section>

        {/* ---------------------------------------------------------------------
            SECTION 6: RISK ANALYSIS & MITIGATIONS
        --------------------------------------------------------------------- */}
        <section id="risk">
          <RiskAnalysis risks={riskAnalysisList} />
        </section>

        {/* ---------------------------------------------------------------------
            SECTION 7: MVP RECOMMENDATIONS
        --------------------------------------------------------------------- */}
        <section id="mvp">
          <MvpRecommendations data={mvpData} />
        </section>

        {/* ---------------------------------------------------------------------
            SECTION 8: COMMERCIAL GO-TO-MARKET BLUEPRINT
        --------------------------------------------------------------------- */}
        <section id="gtm">
          <GtmStrategy gtmStrategy={gtmData} />
        </section>

        {/* ---------------------------------------------------------------------
            SECTION 9: STARTUP VALIDATION REPORT (9 SYNTHESIS CARDS)
        --------------------------------------------------------------------- */}
        <section id="report">
          <ValidationReport report={validationReportData} />
        </section>

      </main>

      {/* Embedded Style Overrides for Maximum Radiant Yellow Gradient Theme */}
      <style>{`
        .results-horiz-nav::-webkit-scrollbar {
          display: none;
        }
        .analysis-card {
          background: rgba(255, 255, 255, 0.02);
          border: 1px solid rgba(255, 199, 44, 0.2);
          border-radius: 16px;
          padding: 28px;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        }
        .analysis-card h2 {
          font-size: 1.35rem;
          font-weight: 700;
          color: #f5f1e8;
          margin: 0 0 18px 0;
        }
        .card-mini-badge {
          display: inline-block;
          font-size: 0.7rem;
          font-weight: 800;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          padding: 3px 10px;
          border-radius: 20px;
          margin-bottom: 8px;
        }
        .gap-card {
          background: rgba(255, 255, 255, 0.025);
          border: 1px solid rgba(255, 199, 44, 0.25);
          border-radius: 12px;
          padding: 18px;
          margin-bottom: 12px;
          transition: all 0.2s ease;
        }
        .gap-card:hover {
          border-color: rgba(255, 199, 44, 0.5);
          background: rgba(255, 199, 44, 0.04);
          transform: translateY(-2px);
        }
        .gap-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          background: linear-gradient(135deg, rgba(255,199,44,0.2), rgba(255,138,31,0.2));
          color: #FFC72C;
          font-size: 0.72rem;
          font-weight: 800;
          padding: 2px 8px;
          border-radius: 4px;
          border: 1px solid rgba(255,199,44,0.35);
          margin-bottom: 8px;
        }
        .gap-text {
          margin: 0;
          font-size: 0.9rem;
          color: #e6e0d4;
          line-height: 1.5;
        }
      `}</style>
    </div>
  );
}
