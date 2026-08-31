# NEXUS-ISB7 — System Architecture

## 1. Overview

NEXUS-ISB7 is an **AI Startup Idea Validator**. A user submits a startup idea in the
web UI, the backend routes that idea to a Web Search Agent, the agent gathers real
web data about the market/competitors/trends, and the results are shown back to the
user.

**Current scope:** one complete, working, end-to-end flow —

```
Startup Idea → React UI → FastAPI → Web Search Agent → Tavily/DuckDuckGo → Web Results → React UI
```

Everything beyond that (multi-agent analysis, scoring, reports) is documented here as
the target architecture the system is designed to grow into.

## 2. Current architecture (built)

```
 USER
   │
   ▼
 React + Vite UI                   idea input, submit button, loading state, results display
   │  POST /api/search
   ▼
 FastAPI backend                   request validation, routing, response formatting
   │
   ▼
 Web Search Agent                 builds search queries from the idea, calls the search API
   │
   ▼
 Tavily API                       primary search provider
   │  (fallback if unavailable/rate-limited)
   ▼
 DuckDuckGo                      fallback search provider
   │ 
   ▼
 Search results → FastAPI response → React UI → displayed to user
```

Only one search provider path is used per request (Tavily first, DuckDuckGo as a
fallback) — the two are not run in parallel, to keep the current implementation
simple.

## 3. Agent roles

| Agent | Responsibility | Status |
|---|---|---|
| Web Search Agent | Turns a startup idea into search queries, calls Tavily/DuckDuckGo, returns structured results | Built |
| Market Analysis Agent | Estimates market size, growth, demand | Planned |
| Competitor Analysis Agent | Identifies and summarizes competitors | Planned |
| SWOT / Risk Agent | Surfaces risks and strengths/weaknesses | Planned |
| MVP Recommendation Agent | Suggests a minimum viable product angle | Planned |
| Report Generation Agent | Compiles all agent outputs into a single validation report | Planned |

## 4. Data flow

**Request**

1. User types a startup idea in the React UI and clicks **Validate Idea**.
2. React sends `POST /api/search` to FastAPI with the idea text.
3. FastAPI validates the request (non-empty, minimum length) and calls the Web
   Search Agent.
4. The Web Search Agent generates relevant queries from the idea and calls Tavily
   (falling back to DuckDuckGo if needed).
5. The search provider returns raw web results.

**Response**

6. The Web Search Agent normalizes results into a fixed structure.
7. FastAPI wraps this in a JSON response and returns it to the React UI.
8. React renders the results (title, URL, content snippet per result).

### API request/response structure

**Request** — `POST /api/search`
```json
{
  "idea": "AI based platform for personalized fitness plans"
}
```

**Response**
```json
{
  "results": [
    {
      "title": "Example",
      "url": "https://example.com",
      "content": "Relevant information..."
    }
  ]
}
```

This structure is the contract between the Web Search Agent and the FastAPI layer —
both members responsible for those pieces must keep it in sync.

## 5. Frontend ↔ backend communication

- The frontend never talks to Tavily/DuckDuckGo directly — it only knows about
  `POST /api/search` on the FastAPI backend.
- CORS is configured on the FastAPI backend to allow the Vite dev server origin.
- Errors (empty input, search failure, no results, invalid API key) are returned as
  JSON error responses and rendered as an error message in the UI, not a crash.

## 6. Future architecture (target design, not yet implemented)

```
 Startup Idea
   │
   ▼
 Idea Submission
   │
   ▼
 Orchestrator
   │
   ├──────────────┬──────────────┬──────────────┬──────────────┐
   ▼              ▼              ▼              ▼              ▼
 Web Search    Market         Competitor     SWOT / Risk    MVP
 Agent         Analysis       Analysis                      Recommendation
   │              │              │              │              │
   └──────────────┴──────────────┴──────────────┴──────────────┘
                              │
                              ▼
                     Report Generation
```

The Orchestrator will dispatch the idea to multiple specialized agents in parallel
(starting with the Web Search Agent already built), then hand their combined output
to a Report Generation Agent that produces the final validation summary — market
research, competitors, target market, business model, industry trends, risks, and a
key recommendation.

## 7. Repository structure

```
NEXUS-ISB7/
├── client/                           React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   ├── package.json
│   └── vite.config.js
│
├── server/                             FastAPI backend
│   ├── agents/
│   │   └── web_search_agent.py
│   ├── routes/
│   │   └── search.py
│   ├── models/
│   │   └── search.py
│   ├── main.py
│   └── requirements.txt
│
├── docs/
│   └── architecture.md           
│
├── tests/
│   ├── test_search_agent.py
│   └── test_search_api.py
│
├── .env.example
└── README.md
```

## 8. GitHub workflow

- No direct commits to `main` or `staging`.
- Each member works on a feature branch: `feature/architecture`,
  `feature/web-search-agent`, `feature/startup-idea-ui`, `feature/fastapi-search-api`.
- Flow: `feature/*` → Pull Request → `staging` → testing → `main`.

## 9. End-to-end flow checklist

1. Open the React application.
2. Enter a startup idea.
3. Click **Validate Idea**.
4. React sends the request to FastAPI.
5. FastAPI calls the Web Search Agent.
6. The Web Search Agent calls Tavily.
7. Real web results are retrieved.
8. Results are returned as JSON.
9. React displays the results.

## 10. Deliverables

- [ ] System architecture document (this file)
- [ ] React startup idea interface
- [ ] FastAPI backend endpoint
- [ ] Python Web Search Agent
- [ ] Tavily integration
- [ ] DuckDuckGo fallback (if required)
- [ ] Search results displayed on frontend
- [ ] Basic error handling
- [ ] Basic testing
- [ ] GitHub branches + PRs
- [ ] Working end-to-end demo
