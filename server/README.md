# NEXUS Backend Intelligence Engine & Multi-Agent Architecture

The backend layer of NEXUS provides a high-performance, asynchronous REST API powered by FastAPI, Pydantic v2, and a coordinated fleet of autonomous AI agents utilizing Google Gemini and real-time web retrieval.

---

## Architecture Overview

The backend is organized into three primary layers:

1. API Route Layer (`server/routes/`): FastAPI routers handling request validation, error boundaries, rate limiting, and serialization.
2. Agent Intelligence Layer (`server/agents/`): Autonomous analytical engines executing domain-specific market analysis, competitor benchmarking, SWOT assessment, risk modeling, MVP planning, and advisory tasks.
3. Integration & Utility Layer (`server/utils/`, `server/models/`): Pydantic data schemas, Google Gemini client abstractions, and external search connectors.

---

## Agent Taxonomy & Responsibilities

| Agent Module | Primary Responsibility | Data Output |
| :--- | :--- | :--- |
| `orchestrator.py` | Central coordination, parallel task dispatching, and response synthesis | Unified validation payload |
| `web_search_agent.py` | Real-time web retrieval across Tavily and DuckDuckGo search engines | Factual web intelligence snippets |
| `market_analysis_agent.py` | Market dynamics, customer segmentation, and quantitative TAM/SAM/SOM calculations | Market sizing and trend matrices |
| `competitor_analysis_agent.py` | Incumbent identification, feature matrix benchmarking, and moat evaluation | Competitor landscape and defensibility analysis |
| `swot_risk_agent.py` | 4-quadrant strategic matrix generation and multi-vector risk assessment | SWOT matrix and categorized risk mitigations |
| `mvp_recommendation_agent.py` | Technical scope definition and Phase 1 vs. Phase 2 specification roadmaps | MVP feature prioritization |
| `gtm_agent.py` | Customer acquisition channel evaluation, launch sequencing, and pricing models | Go-to-market strategy |
| `report_generation_agent.py` | Cross-module reconciliation, executive verdict generation, and summary synthesis | Comprehensive validation dossier |
| `startup_advisor_agent.py` | Conversational strategy copilot for founder inquiries and pivot evaluations | Advisory recommendations |

---

## Orchestrator Execution Sequence

```text
1. Client POST /api/validate
   │
   ▼
2. Validate Request Schema (ValidationRequest)
   │
   ▼
3. Multi-Agent Orchestrator (run_orchestrator)
   │
   ├── Phase 1: Real-Time Web Intelligence
   │   └── WebSearchAgent executes parallelized search queries
   │
   ├── Phase 2: Parallel Analytical Synthesis
   │   ├── MarketAnalysisAgent (TAM, SAM, SOM, Trends)
   │   └── CompetitorAnalysisAgent (Incumbents, Moats, Gaps)
   │
   ├── Phase 3: Strategic Risk & Execution Planning
   │   ├── SwotRiskAgent (SWOT Matrix, Risk Assessment)
   │   ├── MvpRecommendationAgent (Must-Have vs Nice-to-Have Features)
   │   └── GtmAgent (Acquisition Channels, Pricing Architecture)
   │
   └── Phase 4: Executive Report Generation
       └── ReportGenerationAgent synthesizes final dossier and score
   │
   ▼
4. Serialize and return ValidationResponse (200 OK)
```

---

## API Endpoints

### Core Validation Pipeline

- `POST /api/validate`
  - Accepts startup concept description, industry domain, and target customer profile.
  - Returns complete multi-agent validation dossier with numerical score and qualitative models.

- `POST /api/schedule-report-email`
  - Schedules background transmission of generated report to founder's email address upon synthesis completion.

- `POST /api/search`
  - Standalone search endpoint querying market references for rapid concept discovery.

- `POST /api/advisor/chat`
  - Interactive multi-turn conversational endpoint providing strategic guidance on market positioning, pricing, and defensibility.

- `GET /api/health`
  - Health probe verifying backend process uptime and operational environment.

---

## Environment Configuration

Create a `.env` file inside the `server/` directory:

```env
# Required for Gemini LLM agents
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Enhanced search endpoint (falls back to DuckDuckGo if omitted)
TAVILY_API_KEY=your_tavily_api_key_here

# Operational environment: development, staging, or production
NODE_ENV=development
```

---

## Local Setup & Development

### 1. Initialize Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Development Server
```bash
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive OpenAPI documentation is available at `http://127.0.0.1:8000/docs`.

---

## Testing & Quality Assurance

All agents and route handlers are accompanied by automated tests using Pytest and Pytest-Asyncio.

```bash
# Run the complete test suite
pytest tests/

# Run specific agent verification tests
pytest tests/test_market_analysis.py
pytest tests/test_competitor_analysis.py
pytest tests/test_swot_risk.py
pytest tests/test_mvp_recommendation.py
pytest tests/test_gtm_agent.py
pytest tests/test_advisor_api.py

# Run with test coverage reporting
pytest --cov=server tests/
```

---

## Error Handling & Resiliency

- Graceful Degradation: If external search APIs experience upstream failures, the pipeline degrades to structured deterministic heuristic models without terminating user execution.
- Schema Validation: Pydantic v2 ensures strict data typing and catches missing or corrupted agent outputs before sending responses to the client.
- Timeout Boundaries: Agent calls enforce isolated timeouts preventing stalled network requests from blocking the orchestration lifecycle.
