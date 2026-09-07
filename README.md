# 🚀 NEXUS — AI Startup Idea Validator

### Development of AI-Based Startup Idea Validator with Market Analysis Assistance

NEXUS is an AI-powered platform designed to help entrepreneurs evaluate startup ideas using **real-time web data and AI-based analysis**.

The system allows a founder to submit a startup idea and retrieves relevant market and competitor information through a Web Search Agent.

---

## 🎯 Project Objective

Entrepreneurs often find it difficult and time-consuming to validate startup ideas because they need to research:

* Market demand
* Industry trends
* Existing competitors
* Customer needs
* Business opportunities

NEXUS aims to simplify this process by combining **AI agents and real-time web search** to provide data-backed startup validation.

---

# 🏗️ System Architecture

## Current Implementation

The current implementation focuses on the **Startup Idea Submission Interface and Web Search Agent**.

```text
User
  ↓
React + Vite Frontend
  ↓
Startup Idea Submission
  ↓
FastAPI + Uvicorn Backend
  ↓
Web Search Agent
  ↓
Tavily API / DuckDuckGo
  ↓
Live Web Data
  ↓
Data Retrieval & Processing
  ↓
Structured JSON Response
  ↓
React Results Interface
```

### Current Flow

**React/Vite → FastAPI → Web Search Agent → Tavily API → Web Data → Structured Results → React Interface**

---

# 🤖 Web Search Agent

The Web Search Agent is the main AI component implemented in the current milestone.

### Responsibilities

* Receive the startup idea from the backend
* Generate relevant search queries
* Search the web for startup-related information
* Retrieve market and competitor data
* Process search results
* Return structured data to the frontend

### Search Flow

```text
Startup Idea
      ↓
FastAPI Backend
      ↓
Web Search Agent
      ↓
Tavily API
      ↓
Live Web Search
      ↓
Search Results
      ↓
Data Processing
      ↓
JSON Response
      ↓
Frontend
```

---

# 🖥️ Frontend

The frontend provides an interface where the user can submit the necessary startup information.

### Frontend Responsibilities

* Startup idea input
* Submit validation request
* Communicate with FastAPI backend
* Display search results
* Display retrieved web information

### Technology

**React + Vite**

---

# ⚙️ Backend

The backend handles API requests and communicates with the Web Search Agent.

### Backend Responsibilities

* Receive startup idea
* Validate input
* Trigger Web Search Agent
* Communicate with Tavily API
* Process search results
* Return structured JSON data

### Technology

**Python + FastAPI + Uvicorn**

---

# 🔎 Web Search & Data Retrieval

The current system uses **Tavily API** for real-time web search and data retrieval.

An alternative search provider such as **DuckDuckGo** can also be used.

```text
                ┌─────────────────┐
                │  Startup Idea   │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │ Web Search Agent│
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │   Tavily API    │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │  Web Results    │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │ Data Processing │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │ React Interface │
                └─────────────────┘
```

---

# 🔮 Planned Multi-Agent Architecture

The current milestone implements the Web Search Agent. The architecture is designed to support additional agents in the future.

```text
Web Search Agent
        ↓
Market Analysis Agent
        ↓
Competitor Analysis Agent
        ↓
SWOT & Risk Analysis Agent
        ↓
MVP Recommendation Agent
        ↓
Go-To-Market Agent
        ↓
Report Generation Agent
        ↓
Conversational Startup Advisor
```

These components are part of the **planned complete system architecture**.

Detailed architecture documentation is available in:

**`docs/architecture.md`**

---

# 🛠️ Technology Stack

| Component           | Technology       |
| ------------------- | ---------------- |
| Frontend            | React + Vite     |
| Backend             | Python + FastAPI |
| Server              | Uvicorn          |
| Web Search          | Tavily API       |
| Alternative Search  | DuckDuckGo       |
| Version Control     | Git + GitHub     |
| Frontend Deployment | Vercel           |
| Backend Deployment  | Render           |

---

# 📁 Project Structure

```text
NEXUS-ISB7/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── agents/
│   │   └── web_search_agent.py
│   │
│   ├── routes/
│   │   └── search.py
│   │
│   ├── models/
│   │   └── search.py
│   │
│   ├── main.py
│   ├── requirements.txt
│   └── .env
│
├── docs/
│   ├── architecture.md
│   └── sequence-diagram.md
│
├── README.md
└── .gitignore
```

---

# 🔄 API Communication

The frontend communicates with the FastAPI backend through REST APIs.

```text
React Frontend
      │
      │ HTTP Request
      ↓
FastAPI Backend
      │
      ↓
Web Search Agent
      │
      ↓
Tavily API
      │
      ↓
Search Results
      │
      ↓
FastAPI Backend
      │
      │ JSON Response
      ↓
React Frontend
```

---

# 🚀 Deployment

The project uses separate **staging** and **main** branches.

```text
GitHub
   │
   ├── staging
   │      ↓
   │    Vercel
   │    Frontend
   │      ↓
   │    Render
   │    FastAPI Backend
   │
   └── main
          ↓
        Production
```

### Deployment Stack

* **GitHub** — Source code and branch management
* **Vercel** — Frontend deployment
* **Render** — Backend deployment

---

# 📌 Milestone 1 Deliverables

### Completed /

* [x] System Architecture Design
* [x] Agent Roles and Data Flow Design
* [x] Startup Idea Submission Interface
* [x] FastAPI Backend Setup
* [x] Web Search Agent
* [x] Tavily API Integration
* [x] Web Data Retrieval
* [x] Structured Search Results
* [x] Frontend–Backend API Communication
* [x] GitHub Repository
* [x] Staging and Main Branch Setup

---

# 🎯 Expected Milestone 1 Output

The user submits a startup idea through the frontend.

The system then:

```text
Startup Idea
     ↓
Web Search Agent
     ↓
Tavily API
     ↓
Live Web Data
     ↓
Processed Search Results
     ↓
Results Displayed in Frontend
```

This provides the foundation for the complete **AI Startup Idea Validation platform**.

---

# 📚 Documentation

For the detailed system architecture, agent roles, data flow, and sequence diagrams, see:

* `docs/architecture.md`
* `docs/sequence-diagram.md`

---

## 👥 Team NEXUS

**Project:** AI-Based Startup Idea Validator with Market Analysis Assistance

**Current Focus:** Web Search API + System Architecture + Startup Idea Submission Interface
