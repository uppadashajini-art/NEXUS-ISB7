# NEXUS-ISB7 — Sequence Diagram

This document shows the step-by-step sequence of calls for a single "Validate Idea"
request. See [architecture.md](./architecture.md) for the full system architecture and component responsibilities.

```mermaid
sequenceDiagram
    actor User
    participant UI as React + Vite UI
    participant API as FastAPI Backend
    participant Agent as Web Search Agent
    participant Tavily as Tavily API
    participant DDG as DuckDuckGo (fallback)

    User->>UI: Enter startup idea, click "Validate Idea"
    UI->>API: POST /api/search { "idea": "..." }
    API->>API: Validate request (non-empty, min length)
    API->>Agent: Forward idea for processing
    Agent->>Agent: Build search queries from idea
    Agent->>Tavily: Search query request

    alt Tavily responds successfully
        Tavily-->>Agent: Search results
    else Tavily unavailable / rate-limited
        Agent->>DDG: Search query request (fallback)
        DDG-->>Agent: Search results
    end

    Agent->>Agent: Normalize results into fixed structure
    Agent-->>API: Structured results
    API-->>UI: JSON response { "results": [...] }
    UI-->>User: Render results (title, url, content)
```

## Error path

```mermaid
sequenceDiagram
    actor User
    participant UI as React + Vite UI
    participant API as FastAPI Backend
    participant Agent as Web Search Agent

    User->>UI: Enter startup idea, click "Validate Idea"
    UI->>API: POST /api/search { "idea": "..." }
    API->>Agent: Forward idea for processing
    Agent--xAPI: Search fails (no provider available / no results)
    API-->>UI: JSON error response { "error": "..." }
    UI-->>User: Show error message, no crash
```

## Notes

- Only one search provider is used per request — Tavily first, DuckDuckGo only as a
  fallback if Tavily fails or is rate-limited. They are not called in parallel.
- The FastAPI layer is the only component the frontend talks to directly; it never
  calls Tavily/DuckDuckGo itself, and the React UI never calls them either.
- Errors at any step return a JSON error object rather than crashing, and the UI is
  responsible for rendering that as a user-facing message.
