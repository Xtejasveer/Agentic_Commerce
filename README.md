# 🛒 Agentic Commerce: AI-Native Merchant Infrastructure

> **An autonomous Agent-to-Merchant transaction platform powered by the Model Context Protocol (MCP), LangGraph, FastAPI, PostgreSQL, and ChromaDB.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.0-1C3C3C.svg?style=flat)](https://github.com/langchain-ai/langgraph)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Standard-purple.svg?style=flat)](https://modelcontextprotocol.io/)
[![React](https://img.shields.io/badge/React-19.0-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Razorpay](https://img.shields.io/badge/Razorpay-API-02042B.svg?style=flat&logo=razorpay&logoColor=white)](https://razorpay.com)

---

## 🌟 Executive Overview

As autonomous AI agents (personal assistants, enterprise procurement bots, OpenAI Operator, Claude Desktop) become the primary consumers on the internet, e-commerce infrastructure must transition from human-facing click funnels to **machine-readable, policy-governed endpoints**.

**Agentic Commerce** provides the complete reference architecture for an **AI-Native Merchant**. It enables autonomous buyer agents to discover products, negotiate dynamic bundles, validate organizational spending mandates, and execute transactions programmatically via the **Model Context Protocol (MCP)** — with built-in **Human-in-the-Loop (HITL)** governance and real-time observability.

---

## 🚀 Key Features

- **🧠 Autonomous Buyer Agent (LangGraph)**: Multi-step reasoning pipeline (`Search` → `Evaluate` → `Validate` → `Upsell Evaluation` → `Purchase Execution` → `Respond`).
- **🔌 Model Context Protocol (MCP) Server**: Full `FastMCP` implementation exposing product catalog search, mandate checks, add-on pitches, and purchase execution. Compatible out of the box with **Claude Desktop**.
- **🛡️ Deterministic Policy Engine**: Defense-in-depth safety checks ensuring agents cannot exceed daily budgets, buy disallowed categories, or double-charge orders (idempotency guarantees).
- **👤 Human-in-the-Loop (HITL) Upsell Approvals**: When a merchant offers a complementary upsell, the agent evaluates the pitch, pauses execution, and requests human confirmation via an interactive card before committing payment.
- **🧶 Visual Thought-Process Rope**: Collapsible interactive stepper visualizing each internal cognitive step (search queries, LLM scoring, policy verification traces, and decision rationale).
- **📊 Real-Time Merchant Dashboard & Audit Trail**: Live Server-Sent Events (SSE) stream capturing every agent action, tool invocation, mandate verification, and transaction status in real time.
- **📦 50-Product Consumer Electronics Catalog**: 50 realistic products indexed across 12 categories in PostgreSQL with dense semantic embeddings stored in ChromaDB.
- **💳 Headless Razorpay Checkout**: Server-to-server payment order generation with automated webhook signature verification.
- **🔐 Multi-User Authentication & Mandate Scoping**: Google OAuth 2.0 and session-based authentication allowing individual users to define and customize their buyer agents' budget limits and approved categories.

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                  │
│   React SPA (Dashboard & Demo)       │       Claude Desktop / External Bot │
└───────────────────────┬──────────────────────────────────┬─────────────────┘
                        │ HTTP / SSE                       │ stdio / MCP
                        ▼                                  ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                    AGENTIC COMMERCE CORE GATEWAY                           │
│                                                                            │
│  ┌─────────────────────────┐           ┌────────────────────────────────┐  │
│  │   FastAPI Web Server    │           │    FastMCP Server              │  │
│  │   - REST Endpoints      │           │    - search_products           │  │
│  │   - Real-Time SSE Stream│           │    - validate_purchase_mandate │  │
│  │   - Auth & Session Mgmt │           │    - suggest_addon             │  │
│  │   - SPA Static Hosting  │           │    - execute_purchase          │  │
│  └────────────┬────────────┘           └───────────────┬────────────────┘  │
│               │                                        │                   │
│               ▼                                        ▼                   │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                 LangGraph Autonomous Buyer Agent                     │  │
│  │  [search] ➔ [evaluate] ➔ [validate] ➔ [upsell] ➔ [purchase] ➔ [end]  │  │
│  │                              ▲                                       │  │
│  │                              └── [HITL Pause / Resume Hook]          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────┬─────────────────────────────────────┘
                                       │
                        ┌──────────────┴──────────────┐
                        ▼                             ▼
┌─────────────────────────────────┐       ┌──────────────────────────────────┐
│        DATA & STORAGE           │       │       PAYMENTS & SERVICES        │
│  - PostgreSQL (Orders, Audits,  │       │  - Razorpay Headless API         │
│    Mandates, Catalog, Users)    │       │  - OpenRouter (Gemini / Claude)  │
│  - ChromaDB (Vector Embeddings) │       │  - Google OAuth 2.0              │
└─────────────────────────────────┘       └──────────────────────────────────┘
```

---

## 🔄 End-to-End Purchase Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Human User
    participant Agent as LangGraph Buyer Agent
    participant MCP as FastMCP Merchant Server
    participant Policy as Policy & Mandate Engine
    participant Payment as Razorpay / PostgreSQL
    
    User->>Agent: "Buy a fast charger under ₹2,000"
    
    rect rgb(240, 248, 255)
        Note over Agent, MCP: 1. Discovery & Selection
        Agent->>MCP: search_products("fast charger")
        MCP-->>Agent: Semantic search matches (ChromaDB)
        Agent->>Agent: LLM evaluates specs, ratings, and price
    end
    
    rect rgb(255, 245, 238)
        Note over Agent, Policy: 2. Primary Mandate Validation
        Agent->>MCP: validate_purchase_mandate(prod_id, price)
        MCP->>Policy: Verify budget & allowed categories
        Policy-->>MCP: ✅ POLICY_APPROVED
        MCP-->>Agent: Approved
    end
    
    rect rgb(255, 250, 230)
        Note over Agent, User: 3. Upsell Pitch & HITL Feedback
        Agent->>MCP: suggest_addon(primary_product)
        MCP-->>Agent: Proposes "Braided USB-C Cable (₹499)"
        Agent->>Agent: Evaluates pitch and pauses workflow
        Agent-->>User: Renders Interactive Upsell Approval Card
        User->>Agent: Clicks "Accept" or "Decline"
    end
    
    rect rgb(245, 255, 245)
        Note over Agent, Payment: 4. Execution & Settlement
        Agent->>MCP: execute_purchase(final_cart, human_feedback)
        MCP->>Policy: Final strict policy & idempotency check
        Policy-->>MCP: Passed
        MCP->>Payment: Deduct stock & create Razorpay order
        Payment-->>MCP: Razorpay payment link & order ID
        MCP-->>Agent: PAYMENT_SUCCESS
    end
    
    Agent-->>User: "Order complete! Payment link: https://rzp.io/..."
```

---

## 🗂️ Repository Structure

```
Agentic Commerce/
├── main.py                     # Unified CLI entrypoint (dashboard, mcp, seed)
├── requirements.txt            # Python production dependencies
├── pyproject.toml              # Project metadata and package specs
├── nixpacks.toml               # Multi-language build config for Railway
├── Procfile                    # Web service process declaration
├── seed_category.py            # Comprehensive 50-product catalog & vector seeder
│
├── src/
│   ├── config.py               # Central environment settings (Pydantic / dotenv)
│   ├── mcp_server.py           # FastMCP server exposing merchant tools
│   │
│   ├── agent/                  # Autonomous Buyer Agent implementation
│   │   ├── buyer.py            # LangGraph StateGraph, workflow orchestrator & HITL
│   │   ├── nodes.py            # Graph node definitions (search, evaluate, purchase)
│   │   ├── state.py            # AgentState type schema and reduction logic
│   │   └── tools.py            # LangChain MCP client adapters
│   │
│   ├── catalog/                # Product catalog & vector storage
│   │   ├── seed_data.py        # 50 electronics products across 12 categories
│   │   └── vector_store.py     # ChromaDB collection initialization & search
│   │
│   ├── dashboard/              # FastAPI Merchant Backend
│   │   ├── app.py              # FastAPI app setup, CORS, static SPA mounting
│   │   └── routes.py           # REST APIs, SSE audit stream, HITL resolution
│   │
│   ├── database/               # Relational persistence
│   │   ├── models.py           # SQLAlchemy models (Order, Audit, Mandate, Product)
│   │   └── session.py          # PostgreSQL engine and session factory
│   │
│   └── payments/               # Payment gateways
│       └── razorpay_client.py  # Razorpay client & webhook signature verification
│
└── frontend/                   # Modern React SPA (Vite + Tailwind CSS)
    ├── dist/                   # Compiled production bundle
    ├── src/
    │   ├── pages/
    │   │   ├── LoginPage.jsx   # Google OAuth & email authentication
    │   │   ├── LandingPage.jsx # Product intro and marketing overview
    │   │   └── DemoPage.jsx    # Interactive live demo, thought rope & dashboard
    │   ├── components/         # Reusable UI widgets and charts
    │   └── App.jsx             # Client-side router configuration
    └── package.json            # Node.js dependencies
```

---

## ⚙️ Environment Variables

The application relies on the following environment variables:

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection URI | `postgresql://postgres:password@host:5432/dbname` |
| `OPENROUTER_API_KEY` | OpenRouter API Key for agent LLM inference | `sk-or-v1-...` |
| `OPENAI_API_KEY` | Mirrored API Key required by LangChain OpenAI adapters | `sk-or-v1-...` |
| `OPENROUTER_MODEL` | LLM model identifier on OpenRouter | `google/gemini-2.5-flash` |
| `RAZORPAY_KEY_ID` | Razorpay Key ID (Test Mode) | `rzp_test_...` |
| `RAZORPAY_KEY_SECRET` | Razorpay Key Secret | `your_secret` |
| `RAZORPAY_WEBHOOK_SECRET`| Webhook verification secret | `mock_webhook_secret` |
| `CHROMA_PERSIST_DIR` | Directory for persistent vector embeddings | `./chroma_db` |
| `MCP_TRANSPORT` | MCP server transport protocol | `stdio` |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID for dashboard authentication | `your_client_id.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret | `your_client_secret` |
| `ENVIRONMENT` | Environment runtime mode | `production` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

---

## 🤖 Connecting to Claude Desktop (MCP)

This project functions as a standard MCP server that any MCP-compliant client (like Claude Desktop) can connect to.

### 1. Configure Claude Desktop
Add this server to your Claude Desktop configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "agentic-commerce": {
      "command": "python",
      "args": [
        "/absolute/path/to/Agentic_Commerce/main.py",
        "mcp"
      ],
      "env": {
        "DATABASE_URL": "postgresql://postgres:postgres@localhost:5432/agentic_commerce",
        "CHROMA_PERSIST_DIR": "/absolute/path/to/Agentic_Commerce/chroma_db",
        "RAZORPAY_KEY_ID": "rzp_test_your_key_id",
        "RAZORPAY_KEY_SECRET": "your_key_secret"
      }
    }
  }
}
```

### 2. Available MCP Tools
When Claude Desktop connects, it automatically gains access to:

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `search_products` | `query: str`, `top_k: int` | Performs dense semantic vector search over the 50-product catalog using ChromaDB. |
| `validate_purchase_mandate` | `product_id: str`, `price: float`, `category: str` | Validates candidate purchases against spending budgets and category white-lists. |
| `suggest_addon` | `product_id: str` | Merchant upsell engine proposing complementary bundles and accessories. |
| `execute_purchase` | `product_id: str`, `cart: list` | Atomically executes stock reservation, policy verification, and payment link creation. |

---

## 🔒 Security & Policy Governance

- **Deterministic Defense-in-Depth**: Policy checks are executed both at the agent reasoning level and enforced independently inside the transactional database layer before payment link generation.
- **Idempotency Guard**: Prevents accidental duplicate purchases of identical items within configurable time windows.
- **Audit Immutability**: Every policy decision (`POLICY_APPROVED`, `POLICY_REJECTED`, `UPSELL_PROPOSED`, `PAYMENT_SUCCESS`) is logged with timestamps, agent IDs, and full rationale traces.

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
