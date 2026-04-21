# Investor Ops & Intelligence Suite - Central Architecture

## Executive Summary

**Unified fintech product** integrating three AI-powered pillars, implemented in **5 phases** with **3 technical constraints**:

**Modules**:
- **Smart-Sync Knowledge Base** (Pillar A, M1 + M1.1) - 6-bullet answers with citations
- **Insight-Driven Pulse** (Pillar B, M2) - Customer feedback analysis
- **AI Voice Scheduler** (Pillar C, M3) - Voice scheduling + advisor context

**Phase Structure**:
| Phase | Focus | Key Deliverable | Refer To |
|-------|-------|-----------------|----------|
| **1** | Backend - Knowledge Base | Self-RAG API | `rag.md` |
| **2** | Backend - Weekly Pulse | Weekly Pulse API | `themeClassification.md` |
| **3** | Backend - Voice Scheduler | Voice + MCP + HITL API | `voiceAgent.md` + `mcpIntegration.md` |
| **4** | Backend - Integration | API Gateway + Cross-pillar State | `architecture.md` (API Gateway) |
| **5** | **Frontend UI** | **Unified Dashboard** | **`wireframe.md`** |

**Technical Constraints**:
- **Single Entry Point**: One UI for all pillars (Single Dashboard)
- **No PII**: Strict masking with `[REDACTED]` tokens
- **State Persistence**: Booking codes visible in M2 notes/docs

**Environment**: `.env` file at root (`investor-intelligence-suite/.env`) - shared across all phases.

**Pattern**: Phase-wise backend development (1-4) → **Dedicated frontend phase (5)** → Unified dashboard per `wireframe.md` specs.

---

## Documentation Index

| Document | Purpose | Implementation Details |
|----------|---------|------------------------|
| **[architecture.md](architecture.md)** | Central overview (this file) | Cross-cutting concerns, tech stack |
| **[rag.md](rag.md)** | Smart-Sync Knowledge Base (Pillar A) | Chunking, retrieval, 6-bullet constraint |
| **[themeClassification.md](themeClassification.md)** | Insight-Driven Pulse (Pillar B) | Theme extraction, sentiment, confidence scoring |
| **[voiceAgent.md](voiceAgent.md)** | AI Voice Scheduler (Pillar C) | Sarvam API, Silero VAD, booking flow |
| **[mcpIntegration.md](mcpIntegration.md)** | MCP Workflow (Pillar C backend) | FastMCP, HITL, calendar/email |
| **[wireframe.md](wireframe.md)** | **Phase 5: Frontend UI** | **Sidebar navigation, all pillar components** |
| **[rules.md](rules.md)** | Safety & compliance | Guardrails, PII, fintech regulations |
| **[edgeCase.md](edgeCase.md)** | Error handling | Fallbacks, recovery, edge cases |
| **[evals.md](evals.md)** | Evaluation framework | Golden datasets, metrics, test suites |

### Master Documentation Usage by Phase

| Document | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|----------|:-------:|:-------:|:-------:|:-------:|:-------:|
| **[architecture.md](architecture.md)** | ✅ Reference | ✅ Reference | ✅ Reference | ✅ Reference | ✅ Reference |
| **[rag.md](rag.md)** | ✅ **Implement** | 🔍 Review | 🔍 Review | 🔍 Review | 🔍 Review |
| **[themeClassification.md](themeClassification.md)** | 🔍 Review | ✅ **Implement** | ✅ **Uses** | 🔍 Review | 🔍 Review |
| **[voiceAgent.md](voiceAgent.md)** | 🔍 Review | 🔍 Review | ✅ **Implement** | 🔍 Review | 🔍 Review |
| **[mcpIntegration.md](mcpIntegration.md)** | ❌ N/A | ❌ N/A | ✅ **Implement** | ✅ **Uses** | 🔍 Review |
| **[wireframe.md](wireframe.md)** | ❌ N/A | ❌ N/A | ⚠️ HITL UI only | ⚠️ Gateway UI only | ✅ **IMPLEMENT** |
| **[rules.md](rules.md)** | ✅ **Enforce** | ✅ **Enforce** | ✅ **Enforce** | ✅ **Enforce** | ✅ **Enforce** |
| **[edgeCase.md](edgeCase.md)** | ✅ **Handle** | ✅ **Handle** | ✅ **Handle** | ✅ **Handle** | ✅ **Handle** |
| **[evals.md](evals.md)** | ✅ **Run** | ✅ **Run** | ✅ **Run** | ✅ **Run** | ✅ **Run** |

**Legend**:
- ✅ **Implement**: Phase owns implementation of this doc's specs
- ✅ **Uses**: Phase uses implementation from previous phase
- ✅ **Enforce/Handle/Run**: Phase must apply rules/handle cases/run evals
- 🔍 **Review**: Phase should review for context/integration
- ❌ **N/A**: Not applicable to this phase

### Document-to-Phase Responsibility Matrix

| Document | Primary Phase | Implementation Area | Test File |
|----------|---------------|---------------------|-----------|
| **wireframe.md** | **Phase 5** | `phase5_frontend/src/` | `test_wireframe.py` |
| **rules.md** | **All Phases** | Safety guards in each phase | `test_safety.py` per phase |
| **edgeCase.md** | **All Phases** | Error handling in each phase | `test_edge_cases.py` per phase |
| **evals.md** | **Phase 5 (Final)** | Comprehensive test suite | `test_all_evals.py` |

---

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  SINGLE ENTRY POINT (Technical Constraint)                │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │              UNIFIED DASHBOARD                                      │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │  │
│  │  │  Pillar A    │  │  Pillar B    │  │  Pillar C    │               │  │
│  │  │  Self-RAG KB │  │  Weekly Pulse│  │  MCP+HITL    │               │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │  │
│  └─────────┼─────────────────┼─────────────────┼─────────────────────────┘  │
│            │                 │                 │                            │
│  Technical Constraints: All pillars accessible via ONE UI (no redirects)    │
│  • No PII: [REDACTED] tokens enforced                                       │
│  • State Persistence: Booking codes synced to M2 notes                      │
└─────────────────────────────────────────────────────────────────────────────┘
            │                 │                 │
            ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LangChain/LangGraph ─────────────────────────────────────────────────────  │
│  • Self-RAG pipeline (Pillar A) ────► See [rag.md](rag.md)                  │
│  • Theme extraction (Pillar B) ─────► See [themeClassification.md](themeClassification.md)│
│  • MCP workflow (Pillar C) ───────► See [mcpIntegration.md](mcpIntegration.md)│
│  • Cross-pillar state persistence                                           │
└─────────────────────────────────────────────────────────────────────────────┘
            │                 │                 │
            ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  DATA LAYER                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │  Pinecone    │  │  Review CSV  │  │  Theme Store │  │  Booking State   │ │
│  │  (M1+M1.1)   │  │  (M2)        │  │  (Pillar B→C)│  │  (Cross-ref)     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Cross-Pillar Data Flow

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   PILLAR A  │───►  │   PILLAR B  │───►  │   PILLAR C  │      │   HITL      │
│   (M1+M1.1) │      │   (M2)      │      │   (M3)      │      │   Approval  │
│             │      │  Top themes │      │  Greeting   │      │             │
│ Search:     │      │  Sentiment  │───►  │  injection  │      │  Advisor    │
│ "Exit load" │      │             │      │             │      │  reviews    │
└─────────────┘      └─────────────┘      └──────┬──────┘      └──────┬──────┘
                                                  │                     │
                                                  ▼                     ▼
                                         ┌─────────────────────────────────┐
                                         │  Booking: MTG-2024-001           │
                                         │  • Logged to M2 notes            │
                                         │  • Context in advisor email      │
                                         └─────────────────────────────────┘
```

---

## Tech Stack Summary

| Layer | Technology | Implementation Doc |
|-------|------------|-------------------|
| **Frontend** | React / Vanilla JS / HTML-CSS | [wireframe.md](wireframe.md) |
| **Backend** | Python FastAPI/Flask + LangChain | See pillar docs |
| **Pillar A LLM** | OpenRouter GPT-4o + GPT-4o-mini (Self-RAG) | [rag.md](rag.md) |
| **Pillar B LLM** | OpenRouter Claude 3.5 Sonnet (Themes) | [themeClassification.md](themeClassification.md) |
| **Pillar C LLM** | Groq (Voice, low-latency) | [voiceAgent.md](voiceAgent.md) |
| **Vector DB** | Pinecone + OpenRouter embeddings (`openai/text-embedding-3-large`) | [rag.md](rag.md) |
| **Orchestration** | LangGraph | [mcpIntegration.md](mcpIntegration.md) |
| **Safety** | Custom guardrails | [rules.md](rules.md) |
| **Evaluation** | DeepEval + RAGAS | [evals.md](evals.md) |

---

## Pillar Summaries

### Pillar A: Self-RAG Knowledge Base (M1 + M1.1)

**Purpose**: Answer fund/fee questions with 6 bullets + source citations.

**Flow**:
1. Query expansion (GPT-4o-mini)
2. Dense retrieval (Pinecone + OpenRouter embeddings)
3. Sufficiency check (Self-RAG)
4. 6-bullet generation (GPT-4o)

**Key Features**:
- Semantic chunking (M1) + header chunking (M1.1)
- Metadata filtering (exit_load, expense_ratio, AUM)
- Source citations [Source: M1/M1.1]

📄 **Full Implementation**: [rag.md](rag.md)

---

### Pillar B: Theme-Aware Weekly Pulse (M2)

**Purpose**: Extract themes from customer reviews to generate Weekly Product Pulse and inform Voice Agent.

**Flow**:
1. Process reviews CSV
2. Theme extraction (Groq LLaMA 3 + scikit-learn TF-IDF + K-means)
3. Sentiment analysis per theme (TextBlob/vaderSentiment)
4. Generate Weekly Pulse JSON
5. Inject top theme into Voice Agent greeting (if confidence >0.7)

**Key Features**:
- Theme confidence scoring
- Cross-pillar state: Theme Store → Voice Agent
- Dynamic greeting via Jinja2 templating
- **Analytics Dashboard**: Visualizes theme distribution (pie chart), sentiment trends (line graph), mention volume (bar chart), and keyword clouds

**Analytics Dashboard API**:
| Endpoint | Description | Response |
|----------|-------------|----------|
| `/api/pillar-b/analytics` | Get analytics dashboard data | `{themes, sentiment_trends, mention_volume, keywords}` |
| `/api/pillar-b/themes` | List active themes with confidence | `[{theme, confidence, sentiment}]` |

📄 **Full Implementation**: [themeClassification.md](themeClassification.md)

---

### Pillar C: MCP Workflow with HITL (M3)

**Purpose**: Voice-enabled scheduling with advisor context from Pillars A & B.

**Flow**:
1. Voice call (Sarvam STT/TTS + Silero VAD)
2. Theme-aware greeting (injects Pillar B top theme if confidence >0.7)
3. Schedule meeting → Generate booking code
4. Trigger MCP actions (Calendar Hold, Email Draft)
5. HITL Approval Center for advisor review
6. Confirmation sent, booking code logged to Pillar B notes

**Key Features**:
- FastMCP tools with `@mcp.tool()` decorator (Hugging Face MCP Server: https://huggingface.co/spaces/ashishsankhua/google-docs-gmail-mcp-server)
- LangGraph `interrupt()` for HITL
- Context enrichment: Email includes Weekly Pulse themes
- Cross-pillar state: Booking code visible in M2 notes
- **Pipeline Status Tracking**: Real-time VAD › STT › LLM › TTS › Calendar › Doc › Email status monitoring

**Voice Pipeline API**:
| Endpoint | Description | Response |
|----------|-------------|----------|
| `/api/pillar-c/pipeline/status` | Get current pipeline step status | `{current_step, all_steps, status}` |
| `/api/pillar-c/voice/record` | Start voice recording | `{recording_id, stream_url}` |
| `/api/pillar-c/voice/stop` | Stop recording & get audio | `{audio_url}` |
| `/api/pillar-c/tts/play` | Play TTS audio | Audio stream |

📄 **Full Implementation**: [mcpIntegration.md](mcpIntegration.md) | [voiceAgent.md](voiceAgent.md)

---

## Cross-Cutting Concerns

### Technical Constraints

Three hard constraints apply across all phases:

| Constraint | Requirement | Validation |
|------------|-------------|------------|
| **Single Entry Point** | One UI for all pillars (Unified Dashboard) | Check: All 3 pillars accessible without external redirects |
| **No PII** | All sensitive data masked with `[REDACTED]` | Check: 100% redaction of names, emails, phones, Aadhar |
| **State Persistence** | Booking Code (M3) visible in M2 notes/docs | Check: Code appears in tracking doc + M2 notes |

**Implementation**: Enforced via `rules.md` + `evals.md` test suites.

### Session State Management

```
┌─────────────────────────────────────────────────────────────┐
│                    CROSS-PILLAR STATE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Pillar A    │  │  Pillar B    │  │  Pillar C    │     │
│  │  Last Query  │──►│  Theme Store │──►│  Greeting    │     │
│  │  Sources     │  │  Top Theme   │  │  Context     │     │
│  └──────────────┘  └──────────────┘  └──────┬───────┘     │
│                                             │               │
│  ┌──────────────┐  ◄────────────────────────┘               │
│  │  Booking     │  Booking code MTG-XXX                      │
│  │  Code logged │  appears in M2 notes (State Persistence)   │
│  │  to M2       │                                            │
│  └──────────────┘                                            │
│                                                             │
│  Persistence: LocalStorage (user) / Redux (app) / Server      │
└─────────────────────────────────────────────────────────────┘
```

📄 **Details**: State schemas and flows in individual pillar docs

**Key Design Patterns:**
- **MCP server with FastMCP**: Use official `mcp.server.fastmcp` with `@mcp.tool()` decorator pattern:
  ```python
  from mcp.server.fastmcp import FastMCP, Context
  mcp = FastMCP("FintechScheduler", json_response=True)
  
  @mcp.tool()
  async def create_calendar_hold(
      booking_code: str,
      advisor_email: str,
      datetime: str,
      ctx: Context
  ) -> dict:
      """Create calendar hold for advisory meeting"""
      await ctx.info(f"Creating calendar hold for {booking_code}")
      # Implementation returns structured dict
      return {"status": "pending_approval", "booking_code": booking_code}
  ```
- **LangGraph interrupt for HITL**: Use `interrupt()` function to pause workflow for human approval:
  ```python
  from langgraph.types import interrupt
  
  def human_approval_node(state):
      # Interrupt returns user response from frontend UI
      result = interrupt({
          "action": "calendar_hold",
          "booking_code": state["booking_code"],
          "requires_approval": True
      })
      return {"approved": result["decision"] == "approve"}
  ```
- **Unified approval queue**: Single table UI showing all pending MCP actions with approve/reject buttons
- **Context enrichment**: Email drafts include Weekly Pulse market context via template injection
- **State cross-referencing**: Booking codes appear in both M2 notes and M3 output (stored in shared session state)

**MCP Server Deployment:**
```bash
# Run calendar MCP server
uv run --with mcp src/pillar_c/mcp_servers/calendar_server.py

# Run email MCP server
uv run --with mcp src/pillar_c/mcp_servers/email_server.py
```

📄 **Detailed Documentation**:
- See [mcpIntegration.md](mcpIntegration.md) for complete MCP server implementation, HITL workflow, FastMCP tools, and booking integration
- See [voiceAgent.md](voiceAgent.md) for voice pipeline (Sarvam API + Silero VAD), booking flow conversation (voice + text input modes), and pipeline status UI

---

### Dashboard API

**Home Dashboard Endpoints** (supports `wireframe.md` Section 0 - Home View):

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/api/dashboard/stats` | GET | Dashboard stats (KB docs, themes, bookings, pending) | `{kb_docs: 5000, themes: 3, bookings: 12, pending: 2}` |
| `/api/dashboard/activity` | GET | Recent activity feed (last 24h) | `[{time, type, message}]` |
| `/api/dashboard/pillars` | GET | Pillar overview cards data | `[{pillar, stats, trend}]` |
| `/api/dashboard/performance` | GET | Performance score | `{score: 94, status: "operational"}` |

**Example**:
```python
# Get dashboard stats for Home View
GET /api/dashboard/stats
Response: {
  "kb_docs": 5247,
  "themes_active": 3,
  "bookings_this_week": 12,
  "pending_approvals": 2,
  "last_synced": "2024-01-20T10:30:00Z"
}
```

---

### Safety & Compliance

**Guardrails** (see [rules.md](rules.md)):
- PII detection & redaction (regex + NER) - Use `[REDACTED]` token
- Investment advice blocking - 100% refusal enforcement
- 6-bullet response constraint
- Adversarial prompt detection (3 test cases)
- Source citation enforcement
- Fintech disclaimer injection

**Technical Constraints** (see [rules.md](rules.md)):
- **Single Entry Point**: All pillars accessible from one UI (Streamlit/Vercel)
- **No PII**: Strict masking with `[REDACTED]` for names, emails, phones, Aadhar
- **State Persistence**: Booking Code (M3) visible in M2 notes/docs

**Compliance**: RBI/SEBI-aligned risk disclaimers, audit logging.

📄 **Details**: [rules.md](rules.md) | [edgeCase.md](edgeCase.md)

---

### Evaluation Framework

**4 Eval Types** (see [evals.md](evals.md)):
1. **RAG Eval**: Faithfulness, Contextual Precision, Answer Relevancy (DeepEval + RAGAS)
2. **Safety Eval**: Constraint adherence, guardrail effectiveness (3 adversarial prompts - 100% refusal required)
3. **UX Eval**: Tone & Structure - Weekly Pulse (<250 words, 3 actions), Voice Agent (theme mention)
4. **Integration Eval**: Technical Constraints - Single Entry Point, No PII, State Persistence

**Success Criteria (8 metrics)**:
| Criterion | Target |
|-----------|--------|
| Faithfulness | >90% |
| Safety compliance | 100% |
| Pulse quality | 100% |
| Theme propagation | 100% |
| Booking visibility | 100% |
| Single Entry Point | 100% |
| PII Protection | 100% |
| State Persistence | 100% |

**Golden Datasets**: 5 complex hybrid questions combining M1 and M2 data

📄 **Details**: [evals.md](evals.md)

---

## Phase-wise Implementation Structure

**Approach**: Each phase is self-contained in its own folder with independent setup and docs.

```
investor-intelligence-suite/
├── phase1_knowledgeBase/         # Phase 1: Self-RAG Knowledge Base (M1 + M1.1)
│   ├── src/
│   │   ├── rag/                  # Self-RAG pipeline
│   │   ├── chunking/             # Semantic + header chunking
│   │   ├── retrieval/            # Pinecone + OpenRouter embeddings
│   │   └── api.py                # FastAPI endpoints
│   ├── data/
│   │   └── ragData/              # Fund JSONs (M1)
│   ├── tests/
│   │   └── test_rag.py           # RAG eval tests
│   ├── requirements.txt
│   └── README.md                 # Phase 1 specific docs
│
├── phase2_weeklyPulse/           # Phase 2: Weekly Pulse (M2)
│   ├── src/
│   │   ├── theme_extraction/     # GPT-4o + scikit-learn
│   │   ├── sentiment/            # TextBlob/vaderSentiment
│   │   ├── pulse_generator/      # Weekly Pulse JSON
│   │   ├── theme_store/          # Shared state manager
│   │   └── api.py
│   ├── data/
│   │   └── reviews/              # Customer reviews CSV (M2)
│   ├── tests/
│   │   └── test_themes.py        # UX eval tests
│   ├── requirements.txt
│   └── README.md
│
├── phase3_voiceScheduler/        # Phase 3: MCP + Voice + HITL (M3, planned)
│   ├── src/
│   │   ├── voice_agent/          # Sarvam STT/TTS + Silero VAD
│   │   ├── mcp_servers/          # FastMCP tools
│   │   ├── workflow/             # LangGraph HITL
│   │   ├── hitl_ui/              # Approval Center UI
│   │   └── api.py
│   ├── data/
│   │   └── booking_state/        # Booking records
│   ├── tests/
│   │   └── test_mcp.py           # Integration tests
│   ├── requirements.txt
│   └── README.md
│
├── phase4_integrationHub/        # Phase 4: API Integration + Cross-pillar State (planned)
│   ├── src/
│   │   ├── api_gateway/          # Unified FastAPI gateway
│   │   ├── shared/               # Cross-phase state management
│   │   └── orchestrator/         # LangGraph cross-pillar workflows
│   ├── tests/
│   │   ├── test_integration.py   # End-to-end API tests
│   │   └── test_state_sync.py    # State persistence tests
│   ├── requirements.txt
│   ├── README.md
│   └── deploy/
│
├── phase5_frontend/               # Phase 5: Unified Dashboard UI (REFER: wireframe.md)
│   ├── src/
│   │   ├── unified_dashboard/    # Main entry point - sidebar navigation
│   │   │   └── react_app/         # React + Vercel implementation
│   │   ├── components/            # Reusable UI components per wireframe.md
│   │   │   ├── pillar_a/          # RAG Chat components (Sec 2)
│   │   │   ├── pillar_b/          # Weekly Pulse components (Sec 3)
│   │   │   ├── pillar_c/          # Voice Agent components (Sec 4)
│   │   │   ├── hitl_center/       # Approval Center (Sec 5)
│   │   │   └── pipeline_status/   # Pipeline UI (Sec 6)
│   │   ├── styles/                # CSS per wireframe.md Section 7
│   │   └── constraints/           # Technical constraint enforcement in UI
│   │       ├── pii_masking/       # [REDACTED] token display
│   │       ├── state_sync/        # Booking code visibility
│   │       └── single_entry/      # Navigation guard
│   ├── tests/
│   │   ├── test_ui_components.py  # Component tests
│   │   ├── test_constraints_ui.py # Constraint validation
│   │   └── test_wireframe.py      # Wireframe compliance tests
│   ├── docs/
│   │   └── wireframe_reference.md # Local copy/reference to wireframe.md
│   ├── requirements.txt
│   └── README.md
│
└── docs/                         # Master documentation (ALL phases reference these)
    ├── architecture.md           # This file
    ├── rag.md
    ├── themeClassification.md
    ├── voiceAgent.md
    ├── mcpIntegration.md
    ├── wireframe.md
    ├── rules.md
    ├── edgeCase.md
    └── evals.md

.env                              # Root-level environment file (REQUIRED)
```

### Environment File Location

**CRITICAL**: The `.env` file **MUST** be placed at the root of `investor-intelligence-suite/` folder, NOT inside individual phase folders.

```
investor-intelligence-suite/
├── .env                          # ← ROOT LEVEL (all phases read from here)
├── phase1_knowledgeBase/
├── phase2_weeklyPulse/
├── phase3_voiceScheduler/        # planned
├── phase4_integrationHub/        # planned
└── docs/
```

**Rationale**:
- Single source of truth for all API keys and configuration
- Prevents duplication across phases
- All phases load from `../../.env` or use `python-dotenv` with `find_dotenv()`

**Loading Pattern** (used in all phases):
```python
from dotenv import load_dotenv, find_dotenv
import os

# Finds .env at root of investor-intelligence-suite/
load_dotenv(find_dotenv())

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
```

### Phase Dependencies

```
Phase 1 (Pillar A) ──────┐
                         ├──► Phase 4 (Integration)
Phase 2 (Pillar B) ──────┤    & API Gateway
         │               │
         └───────────────┤
              │          │
              ▼          ▼
         Phase 3 (Pillar C) ──────► Phase 5 (Frontend UI)
         (Uses themes from P2)       (REFER: wireframe.md)
                                          │
                                          ▼
                              ┌─────────────────────┐
                              │ Unified Dashboard │
                              │ - Sidebar Nav     │
                              │ - All 3 Pillars   │
                              │ - Constraint UI   │
                              └─────────────────────┘
```

### Phase Timeline

| Phase | Name | Duration | Key Deliverable | Dependencies | Docs Referenced |
|-------|------|----------|-----------------|--------------|-----------------|
| **1** | Pillar A (Backend) | 2 weeks | Self-RAG API answering queries | None | `rag.md`, `rules.md`, `edgeCase.md`, `evals.md` |
| **2** | Pillar B (Backend) | 1 week | Weekly Pulse API generation | None | `themeClassification.md`, `rules.md`, `edgeCase.md`, `evals.md` |
| **3** | Pillar C (Backend) | 2 weeks | Voice + MCP + HITL API | Phase 2 (themes) | `voiceAgent.md`, `mcpIntegration.md`, `rules.md`, `edgeCase.md`, `evals.md` |
| **4** | Integration (Backend) | 1 week | API Gateway + Cross-pillar State | Phases 1-3 | `architecture.md`, `mcpIntegration.md`, `rules.md`, `edgeCase.md`, `evals.md` |
| **5** | **Frontend UI** | 1 week | **Unified Dashboard (Sidebar)** | Phase 4 (API Gateway) | **`wireframe.md` (PRIMARY)**, `rules.md`, `edgeCase.md`, `evals.md` |

### Cross-Phase Communication

Each phase exposes a clean API for integration:

```python
# Phase 1 (Pillar A) exposes:
POST /api/v1/query        → {"query", "bullets", "citations", "self_rag", "sources_used", "self_rag_loops", "query_variants"}
GET  /api/v1/funds/search → {"funds", "count"}
GET  /api/v1/sources      → {"sources"}
POST /api/v1/index        → {"status", "indexed", "message"}

# Phase 2 (Pillar B) exposes:
GET  /api/v1/pulse/current → {"top_themes", "sentiment", "action_ideas"}
POST /api/v1/themes/update → Refresh from reviews

# Phase 3 (Pillar C) exposes:
POST /api/v1/voice/book    → {"booking_code", "status"}
GET  /api/v1/hitl/pending  → List pending approvals
POST /api/v1/hitl/approve  → Approve MCP action

# Phase 4 (Integration) exposes:
POST /api/v1/gateway/query     → Routes to Pillar A/B/C
GET  /api/v1/state/bookings    → Cross-pillar booking codes

# Phase 5 (Frontend) consumes all:
→ Calls Phase 4 Gateway APIs
→ Implements wireframe.md specs
→ Enforces constraints in UI
```

---

## Project Structure Comparison

### Phase-wise Structure (Current - 5 Phases)

```
investor-intelligence-suite/
├── phase1_knowledgeBase/     # Backend: Self-RAG API
├── phase2_weeklyPulse/       # Backend: Weekly Pulse API
├── phase3_voiceScheduler/    # Backend: Voice + MCP + HITL API (planned)
├── phase4_integrationHub/    # Backend: API Gateway + State (planned)
├── phase5_frontend/          # Frontend: Unified Dashboard (REFER: wireframe.md)
│   ├── src/
│   │   ├── unified_dashboard/   # Sidebar navigation (Section 0)
│   │   ├── components/          # Pillar A/B/C/HITL (Sections 2-5)
│   │   ├── styles/              # CSS (Section 7)
│   │   └── constraints/           # Technical constraints UI
│   └── tests/
│       └── test_wireframe.py    # Wireframe compliance tests
├── docs/
│   ├── architecture.md
│   ├── wireframe.md         # ← PRIMARY REF for Phase 5
│   ├── rules.md             # ← ALL phases enforce
│   ├── edgeCase.md          # ← ALL phases handle
│   └── evals.md             # ← ALL phases run
└── .env                     # Root-level environment
```

### Legacy Structure (Flat)

```
investor-intelligence-suite/
├── src/
│   ├── pillar_a/          # Self-RAG → see [rag.md](rag.md)
│   ├── pillar_b/          # Weekly Pulse → see [themeClassification.md](themeClassification.md)
│   ├── pillar_c/          # MCP+HITL → see [mcpIntegration.md](mcpIntegration.md)
│   ├── voice_agent/       # Sarvam + Silero → see [voiceAgent.md](voiceAgent.md)
│   ├── safety/            # Guardrails → see [rules.md](rules.md)
│   ├── evals/             # Test suites → see [evals.md](evals.md)
│   └── shared/            # State, utils, config
├── data/
│   ├── ragData/           # Fund JSONs (M1)
│   └── reviews/           # Customer reviews CSV (M2)
└── docs/                  # All architecture docs
    ├── architecture.md    # This file (central overview)
    ├── rag.md
    ├── themeClassification.md
    ├── voiceAgent.md
    ├── mcpIntegration.md
    ├── wireframe.md       # ← Phase 5 primary reference
    ├── rules.md           # ← Used by ALL phases
    ├── edgeCase.md        # ← Used by ALL phases
    └── evals.md           # ← Used by ALL phases
```

---

## Quick Reference

### Prerequisites

Before starting any phase:

1. **Create root `.env` file** at `investor-intelligence-suite/.env`:
```bash
cd investor-intelligence-suite
cat > .env << 'EOF'
# API Keys
OPENROUTER_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
SARVAM_API_KEY=your_key_here

# Safety & Constraints
GUARDRAILS_ENABLED=true
PII_MASKING_MODE=strict
SINGLE_ENTRY_POINT=true
STATE_PERSISTENCE_CHECK=true
EOF
```

2. **Verify constraints** are documented in:
   - `rules.md` - Implementation rules
   - `evals.md` - Test suites
   - `edgeCase.md` - Edge case handling

### Phase-wise Implementation Order

**Recommended Approach**: Implement in 4 phases, each self-contained and deployable.

| Phase | Focus | Key Tasks | Exit Criteria |
|-------|-------|-----------|---------------|
| **Phase 1** | Pillar A (Self-RAG) | • Pinecone setup + OpenRouter embeddings<br>• Chunking from `data/ragData` into `data/chunking/chunks.json`<br>• Self-RAG pipeline (expansion + sufficiency + max-1 loop)<br>• 6-bullet grounded generation | RAG Eval > 90% faithfulness |
| **Phase 2** | Pillar B (Weekly Pulse) | • Review CSV processing<br>• Theme extraction (GPT-4o + K-means)<br>• Sentiment analysis<br>• Pulse JSON generation | UX Eval: 250 words, 3 actions |
| **Phase 3** | Pillar C (MCP + Voice) | • Sarvam STT/TTS integration<br>• Silero VAD<br>• Theme-aware greeting<br>• MCP servers (calendar/email)<br>• HITL Approval Center | Safety Eval: 100% pass |
| **Phase 4** | Integration | • Unified UI (single entry point)<br>• Cross-phase state management<br>• PII guardrails<br>• End-to-end evals<br>• Deployment | All 8 success criteria met |

**Phase Isolation**: Each phase can be developed, tested, and deployed independently:
- Phase 1 can run standalone (RAG only)
- Phase 2 can run standalone (Pulse generation only)
- Phase 3 depends on Phase 2 API for themes
- Phase 4 integrates all phases into unified product

**Folder Navigation**:
```bash
# Ensure .env exists at root first
cat ../.env  # Verify env file is present at investor-intelligence-suite/

# Run individual phases
cd phase1_knowledgeBase && pip install -r requirements.txt && python -m uvicorn app.main:app --port 8000
cd phase2_weeklyPulse && pip install -r requirements.txt && python src/api.py
cd phase3_voiceScheduler && pip install -r requirements.txt && python src/api.py
cd phase4_integrationHub && pip install -r requirements.txt && streamlit run src/unified_ui/app.py
```

### Environment Variables (.env format)

```bash
# API Keys (all phases)
OPENROUTER_API_KEY=sk-or-v1-...
PINECONE_API_KEY=pcsk_...
SARVAM_API_KEY=...
GROQ_API_KEY=gsk_...

# Pinecone (Phase 1)
PINECONE_INDEX_NAME=fintech-rag
PINECONE_NAMESPACE=mutual-funds

# Safety & Compliance (Phase 4)
GUARDRAILS_ENABLED=true
PII_MASKING_MODE=strict
ADVERSARIAL_DETECTION=true
INVESTMENT_ADVICE_BLOCK=true

# Technical Constraints (Phase 4)
SINGLE_ENTRY_POINT=true
STATE_PERSISTENCE_CHECK=true

# Google Docs MCP (Phase 3)
GOOGLE_DOC_TRACKING_ID=1PtKhugpyu0W1SBhlHcBqlhpHQ1bJnxm9uh0dr-O5LIU
```

### Critical Integration Points

| Integration | From → To | Where Documented |
|-------------|-----------|------------------|
| Theme → Voice | Pillar B → Pillar C | [themeClassification.md](themeClassification.md) |
| Booking → Notes | Pillar C → Pillar B | [mcpIntegration.md](mcpIntegration.md) |
| Query → Context | Pillar A → Pillar C | [voiceAgent.md](voiceAgent.md) |
| 6-Bullet → JSON | All Pillars | [rag.md](rag.md) |

---

**Document Version**: 5.0 (Phase-wise) | **Last Updated**: April 2026 | **Structure**: 4 phases → Master docs → 8 child docs

---

## Why LangChain/LangGraph?

**LangChain** and **LangGraph** are the orchestration layer powering all three pillars:

| Feature | Purpose in Our System |
|---------|----------------------|
| **LangChain** | Standardized LLM interface, prompt templates, output parsers |
| **LangGraph** | Cyclic workflow orchestration (Self-RAG loops, HITL interrupts) |
| **State Management** | Cross-pillar state persistence via graph state |
| **MCP Integration** | Native `@mcp.tool()` decorator support with FastMCP |

**Key Benefits**:
1. **Self-RAG Pipeline (Pillar A)**: LangGraph's cyclical graphs enable the "sufficiency check → re-retrieve" loop
2. **HITL Workflow (Pillar C)**: `interrupt()` function pauses execution for human approval
3. **Cross-Pillar State**: State passes between nodes (Theme Store → Voice Agent → Booking Code)
4. **Tool Integration**: MCP servers integrate seamlessly with LangGraph agents

**Alternative**: Without LangGraph, we'd need custom state machines and manual checkpointing. LangGraph provides this out-of-the-box.

---

## Footer

© 2026 All rights reserved [Ashish Kumar Sankhua](../LICENSE)

**License**: [MIT License](../LICENSE) - Click to view full license terms

**Repository**: `investor-intelligence-suite` | **Author**: Ashish Kumar Sankhua | **Year**: 2026
