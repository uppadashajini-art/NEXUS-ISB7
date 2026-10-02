# NEXUS-ISB7 — System Architecture & Multi-Agent Orchestration

## 1. Overview

**NEXUS-ISB7** is an AI-powered Startup Intelligence & Idea Validation Platform. A user enters their startup idea into the React web interface, and the system executes a coordinated multi-agent pipeline:
1. Gathers live web intelligence (market trends, existing products, competitors).
2. Performs deep market analysis, industry classification, and customer segmentation.
3. Conducts direct and indirect competitor benchmarking and gap analysis.
4. Delivers an interactive, structured validation report directly to the founder.

### Milestones Overview
* **Milestone 1 (Complete)**: Baseline Search Validation Flow  
  `Startup Idea → React UI → FastAPI (/api/search) → Web Search Agent → Search Results → React UI`
* **Milestone 2 (Current)**: Multi-Agent Market & Competitor Analysis with Orchestration  
  `Startup Idea → React UI → FastAPI (/api/validate) → Orchestrator → Web Search Agent → [Market Analysis + Competitor Analysis] → Combined Synthesis → React UI`
* **Milestone 3+ (Future)**: Autonomous Strategic Intelligence  
  `SWOT/Risk Analysis, MVP Blueprinting, GTM Strategy, Conversational Advisory & PDF Report Generation`

---

## 2. Milestone 2 Architecture (Built)

```
                            ┌──────────────┐
                            │     USER     │
                            └──────┬───────┘
                                   │
                                   ▼
                      ┌───────────────────────────┐
                      │     React + Vite UI       │
                      │  (StartupValidator Page)  │
                      └────────────┬──────────────┘
                                   │ POST /api/validate
                                   ▼
                      ┌───────────────────────────┐
                      │      FastAPI Backend      │
                      │   (routes/validation.py)  │
                      └────────────┬──────────────┘
                                   │
                                   ▼
            ┌───────────────────────────────────────────────┐
            │       MEMBER 1: MULTI-AGENT ORCHESTRATOR      │
            │          (server/agents/orchestrator.py)       │
            └──────────────┬─────────────────┬──────────────┘
                           │                 │
             1. Execute Search               │ 2. Distribute Context
                           ▼                 │
            ┌─────────────────────────────┐  │
            │      Web Search Agent       │  │
            │ (web_search_agent.py)       │  │
            └──────────────┬──────────────┘  │
                           │                 │
                           ▼                 │
                  Search Results Context     │
                           └────────┬────────┘
                                    │
            ┌───────────────────────┴───────────────────────┐
            ▼                                               ▼
┌───────────────────────────────┐       ┌───────────────────────────────┐
│           MEMBER 2            │       │           MEMBER 3            │
│     Market Analysis Agent     │       │   Competitor Analysis Agent   │
│  (market_analysis_agent.py)   │       │(competitor_analysis_agent.py) │
├───────────────────────────────┤       ├───────────────────────────────┤
│ • Industry Identification     │       │ • Direct Competitors          │
│ • Market Opportunity Sizing   │       │ • Indirect Competitors        │
│ • Emerging Market Trends      │       │ • Feature Comparison Matrix   │
│ • Target Customer Segments    │       │ • Competitor Strengths/Flaws  │
│ • Pain Points & Growth Drivers│       │ • Market Gaps & White Spaces  │
└──────────────┬────────────────┘       └───────────────┬───────────────┘
               │                                        │
               └────────────────────┬───────────────────┘
                                    │
                                    ▼ 3. Synthesize & Validate
            ┌───────────────────────────────────────────────┐
            │          Unified ValidationResponse           │
            │          (models/validation.py)               │
            └───────────────────────┬───────────────────────┘
                                    │
                                    ▼
                      ┌───────────────────────────┐
                      │   React Dashboard Display │
                      │  • MarketAnalysis         │
                      │  • CustomerSegments       │
                      │  • CompetitorAnalysis     │
                      │  • MarketGaps             │
                      └───────────────────────────┘
```

---

## 3. Agent Roles & Team Breakdown

| Role | Primary Responsibility | Key Files |
|---|---|---|
| **Member 1: Agent Orchestrator & System Integration** | Core multi-agent pipeline execution, context passing, inter-agent resilience, system architecture docs, and integration tests. | `server/agents/orchestrator.py`<br>`server/tests/test_orchestrator.py`<br>`docs/architecture.md` |
| **Member 2: Market Opportunity & Customer Segmentation** | Analyzes industry classification, total market opportunity, market trends, customer personas, needs, pain points, and growth drivers. | `server/agents/market_analysis_agent.py`<br>`server/tests/test_market_analysis.py` |
| **Member 3: Competitor Discovery & Comparison** | Discovers direct/indirect competitors from web data, extracts pricing and features, constructs comparison matrix, and uncovers market gaps. | `server/agents/competitor_analysis_agent.py`<br>`server/tests/test_competitor_analysis.py` |
| **Member 4: FastAPI Validation API, React UI & Testing** | Implements `POST /api/validate`, Pydantic data models, frontend state management, and modular UI components. | `server/routes/validation.py`<br>`server/models/validation.py`<br>`client/src/components/*`<br>`server/tests/test_validation_api.py` |

---

## 4. Inter-Agent Data Flow & Context Passing

1. **User Submission**: The founder enters a startup idea (minimum 10 characters) into the React interface.
2. **FastAPI Validation**: `POST /api/validate` validates the request payload via `ValidationRequest`.
3. **Orchestration Execution**:
   - `run_orchestrator(idea, domain=None)` initiates the pipeline.
   - **Step 1 (Web Retrieval)**: Calls `run_web_search_agent(idea)` which utilizes 4-vector query decomposition (domain, audience, problem, solution) and queries Tavily / DuckDuckGo.
   - **Step 2 (Context Distribution)**: Raw and deduplicated search results are passed as rich context into both the Market Analysis and Competitor Analysis execution streams.
   - **Step 3 (Concurrent Analysis)**: `_dispatch_market_analysis` and `_dispatch_competitor_analysis` run concurrently via `asyncio.gather`, utilizing specialized agent implementations or resilient built-in fallback engines.
   - **Step 4 (Validation & Normalization)**: The combined payload is validated against `ValidationResponse`.
4. **UI Presentation**: The frontend renders the complete structured report with dedicated cards for Market Opportunity, Customer Segments, Competitor Comparisons, and Market Gaps.

---

## 5. Request & Response Schemas

### API Request: `POST /api/validate`
```json
{
  "idea": "AI based platform for personalized fitness plans"
}
```

### API Response: `200 OK`
```json
{
  "idea": "AI based platform for personalized fitness plans",
  "market_analysis": {
    "industry": "HealthTech & Fitness Technology",
    "market_opportunity": "Significant commercial opportunity in HealthTech driven by demand for personalized digital fitness...",
    "market_trends": [
      "Rapid acceleration of AI-powered personalization in HealthTech",
      "Increasing user preference for mobile-first self-service platforms",
      "Integration of wearable health analytics"
    ],
    "customer_segments": [
      {
        "segment": "Working Professionals & Early Adopters",
        "needs": ["Automated fitness workflows", "Personalized routines"],
        "pain_points": ["Lack of time", "Generic advice", "High personal trainer costs"]
      }
    ],
    "growth_drivers": ["Expanding wellness market", "High willingness-to-pay"],
    "market_challenges": ["High customer acquisition cost", "User retention past 30 days"]
  },
  "competitor_analysis": {
    "direct_competitors": [
      {
        "name": "FitTech AI",
        "url": "https://example.com/fittech",
        "product_service": "AI Workout Generator",
        "target_customers": "Gymgoers & athletes",
        "key_features": ["Dynamic workout adjustment", "Form feedback"],
        "pricing": "$19.99/mo",
        "strengths": ["Strong app store presence"],
        "weaknesses": ["Limited meal planning integration"]
      }
    ],
    "indirect_competitors": [
      {
        "name": "Manual Spreadsheets & PDFs",
        "product_service": "Custom Excel workout templates",
        "target_customers": "Budget users",
        "key_features": ["Zero software cost"],
        "pricing": "Free",
        "strengths": ["Customizable"],
        "weaknesses": ["High manual effort, no real-time adjustments"]
      }
    ],
    "comparison": [
      {
        "competitor": "FitTech AI",
        "target_customers": "Athletes",
        "key_features": "Dynamic plans",
        "strengths": "Mobile app visibility",
        "weaknesses": "Lacks meal automation"
      }
    ],
    "market_gaps": [
      "Unified fitness and nutrition automation in a single subscription",
      "Zero-overhead onboarding with intelligent schedule adaptation",
      "Evidence-backed plan modifications"
    ]
  }
}
```

---

## 6. Repository Layout (Milestone 2)

```
NEXUS-ISB7/
├── client/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CompetitorAnalysis.jsx
│   │   │   ├── CustomerSegments.jsx
│   │   │   ├── IdeaInput.jsx
│   │   │   ├── MarketAnalysis.jsx
│   │   │   ├── MarketGaps.jsx
│   │   │   └── SearchResultCard.jsx
│   │   ├── pages/
│   │   │   └── StartupValidator.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── validationService.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── server/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── web_search_agent.py          (Milestone 1)
│   │   ├── orchestrator.py              (Milestone 2 — Member 1)
│   │   ├── market_analysis_agent.py     (Milestone 2 — Member 2)
│   │   └── competitor_analysis_agent.py (Milestone 2 — Member 3)
│   ├── routes/
│   │   ├── search.py                    (Milestone 1 API)
│   │   └── validation.py                (Milestone 2 API — Member 4)
│   ├── models/
│   │   ├── search.py                    (Milestone 1 Models)
│   │   └── validation.py                (Milestone 2 Models — Member 4)
│   ├── tests/
│   │   ├── test_search_api.py           (Milestone 1 Tests)
│   │   ├── test_validation_api.py       (Milestone 2 Validation Route Tests)
│   │   └── test_orchestrator.py         (Milestone 2 Orchestrator Tests)
│   ├── main.py
│   └── requirements.txt
│
├── docs/
│   ├── architecture.md
│   └── sequence-diagram.md
├── .env.example
└── README.md
```

---

## 7. Future Multi-Agent Architecture (Milestone 3+)

```
                          Startup Idea
                               │
                               ▼
                         Orchestrator
                               │
      ┌──────────────┬─────────┴───────┬──────────────┬──────────────┐
      ▼              ▼                 ▼              ▼              ▼
  Web Search       Market          Competitor     SWOT & Risk       MVP
    Agent         Analysis          Analysis        Analysis     Recommender
      │              │                 │              │              │
      └──────────────┴─────────┬───────┴──────────────┴──────────────┘
                               │
                               ▼
                 Go-To-Market & Financial Agent
                               │
                               ▼
                    Report Generation Agent
                               │
                               ▼
               Interactive Dashboard & PDF Export
```

* **SWOT & Risk Agent**: Generates comprehensive internal strengths/weaknesses and external opportunities/threats, evaluating regulatory, technical, and market risks.
* **MVP Recommendation Agent**: Outlines core feature priorities, scope constraints, and suggested rapid prototyping tech stacks.
* **Go-To-Market Agent**: Formulates initial acquisition channels, pricing models, unit economics benchmarks, and launch timeline.
* **Report Generation Agent**: Formulates a complete executive briefing document ready for investor or incubator submission.
