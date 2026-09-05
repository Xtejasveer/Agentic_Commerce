# 🛒 VendIQ: AI-Native Merchant Infrastructure

![VendIQ - Commerce that runs itself](assets/vendiq_hero.png)

> **An autonomous Agent-to-Merchant transaction platform powered by the Model Context Protocol (MCP), LangGraph, FastAPI, PostgreSQL, and ChromaDB.**

[![Live Application](https://img.shields.io/badge/Live_Application-Login-c4622d?style=for-the-badge&logo=railway&logoColor=white)](https://agenticcommerce-production-cce1.up.railway.app/login)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.0-1C3C3C.svg?style=flat)](https://github.com/langchain-ai/langgraph)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Standard-purple.svg?style=flat)](https://modelcontextprotocol.io/)
[![React](https://img.shields.io/badge/React-19.0-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Razorpay](https://img.shields.io/badge/Razorpay-API-02042B.svg?style=flat&logo=razorpay&logoColor=white)](https://razorpay.com)

---

## 🌐 Live Application & Links

* 🔐 **Live Application (Sign In)**: **[https://agenticcommerce-production-cce1.up.railway.app/login](https://agenticcommerce-production-cce1.up.railway.app/login)**
* 📁 **GitHub Repository**: **[https://github.com/Xtejasveer/Agentic_Commerce](https://github.com/Xtejasveer/Agentic_Commerce)**

---

## 🌟 Executive Overview

Today's e-commerce is built for human eyeballs: visual storefronts, marketing banners, and multi-click checkout funnels. As autonomous AI agents (Claude Desktop, personal procurement bots, OpenAI Operator) become the primary consumers on the internet, commerce infrastructure must transition from human-facing click funnels to **machine-readable, policy-governed endpoints**.

When AI agents buy on behalf of individuals or businesses, two fundamental challenges emerge:
1. **The Discovery & Negotiation Void**: Merchants have no standardized protocol to expose inventory, price dynamics, and upsell pitches directly to autonomous agents.
2. **The Runaway Agent Risk**: Users cannot safely hand credit cards to autonomous bots without risking hallucinated purchases, broken spending budgets, or unauthorized category buying.

**VendIQ** provides the complete reference architecture for an **AI-Native Merchant**. It standardizes machine-to-machine commerce using Anthropic's **Model Context Protocol (MCP)**, coordinates complex procurement flows using **LangGraph**, enforces deterministic spending mandates in **PostgreSQL**, and provides **Human-in-the-Loop (HITL)** governance with live real-time observability.

---

## 🚀 Deep Dive: Core Features

### 1. 🧠 Multi-Step LangGraph Buyer Pipeline
The buyer agent is built on a stateful **LangGraph StateGraph** that models the full cognitive lifecycle of an enterprise procurement manager:
* **`Search Node`**: Translates natural language requests into structured queries with price bounds and semantic filters.
* **`Evaluate Node`**: Evaluates returned candidates against user constraints, customer ratings, and specs to select the best match.
* **`Validate Node`**: Checks organizational mandate policies before committing to any product.
* **`Evaluate Upsell Node`**: Analyzes merchant-pitched add-ons, evaluates bundle value, and triggers human approval gates.
* **`Purchase Node`**: Atomically executes stock deduction, final policy validation, and headless payment generation.
* **`Respond Node`**: Synthesizes a conversational response with order confirmation and payment links.

### 2. 🔌 Standard Model Context Protocol (MCP) Gateway
VendIQ implements a full **FastMCP** server exposing structured merchant tools to external agents over standard `stdio` or HTTP:
* **`search_products`**: Semantic vector search over the product catalog with category and price filtering.
* **`validate_purchase_mandate`**: Verification of spending authority against database policy records.
* **`suggest_addon`**: Algorithmic merchant engine proposing complementary accessories, bundled discounts, and protection plans.
* **`execute_purchase`**: Idempotent order placement, live stock reservation, and headless payment creation.
> *Compatible out of the box with **Claude Desktop**, OpenAI tool calling, and any MCP-compliant client.*

### 3. 🛡️ Deterministic Defense-in-Depth Policy Engine
To guarantee enterprise safety, VendIQ eliminates "hallucinated purchases" through dual-layer deterministic enforcement:
* **Agent-Level Policy Checks**: The buyer agent consults the policy engine during reasoning to disqualify non-compliant items early.
* **Transactional Database Guard**: The final purchase execution strictly enforces policy validation at the PostgreSQL database level. Even if an LLM hallucinates an approval, the transaction will fail.
* **Enforced Parameters**: Single-transaction limits (₹), daily spending ceilings (₹), allowed category whitelists, and active mandate status.
* **Idempotency Protection**: Prevents duplicate charges by hashing cart contents and enforcing order cooldown windows.

### 4. 👤 Human-in-the-Loop (HITL) Upsell Approvals
Commercial negotiations often introduce new variables—such as merchant upsell pitches. VendIQ balances agent autonomy with human agency:
* When the merchant suggests a complementary add-on (e.g., offering a braided 100W cable with a charger or a memory foam wrist rest with a mouse), the agent **pauses its workflow**.
* An **Interactive Human Feedback Card** renders in real time with the merchant's pitch and action buttons: **Accept Offer** and **Decline Offer**.
* If the user accepts, the agent seamlessly updates the cart to both items.
* If the user declines, the agent drops the add-on and **still safely completes the purchase of the primary product**.

### 5. 🧶 Visual Thought-Process Rope (Cognitive Transparency)
Instead of a black-box answer, VendIQ features a clean, collapsible vertical "rope" stepper showing every cognitive step the agent executed:
* Visualizes circular event nodes connected by an active line: `Search` ➔ `Evaluate` ➔ `Validate` ➔ `Upsell` ➔ `Purchase`.
* Expands on demand to reveal the agent's internal reasoning, candidate product scoring, and policy verification traces.

### 6. 📊 Real-Time Observability & Live SSE Audit Feed
Every agent action is treated as an immutable audit event streamed over **Server-Sent Events (SSE)**:
* Tracks tool invocations, candidate evaluation traces, mandate approvals, rejections, and payment settlements.
* Surfaces real-time merchant KPI metrics:
  * **Unmet Demand Signals**: Automatically logs when an agent searches for out-of-stock items or uncataloged goods to inform merchant restocking.
  * **Sales Recovered**: Tracks conversions facilitated through dynamic alternatives.
  * **Upsell Acceptance Rate**: Live telemetry on merchant bundle conversion.

### 7. 📦 50-Product Catalog with Hybrid Vector + Keyword Search
* 50 realistic consumer electronics products across **12 tech categories**: chargers, cables, power banks, earbuds, headphones, speakers, smartwatches, keyboards, mice, storage, cases, and screen protectors.
* **Dense Semantic Search**: Indexed in **ChromaDB** with cosine similarity embeddings to understand vague intent (e.g., *"comfortable mouse for wrist pain"* maps to the *Logitech MX Master 3S*).
* **SQL Keyword Fallback**: Automatic PostgreSQL `ILIKE` fallback ensures search resilience even during cold-starts.

### 8. 💳 Headless Razorpay Integration
* Direct server-to-server integration with Razorpay's order and payment link API.
* Generates live, payable checkout links (`https://rzp.io/...`) delivered directly in the agent's final response.
* Automated webhook endpoint with cryptographic signature verification for transaction lifecycle synchronization.

### 9. 🔐 Multi-User Authentication & Dynamic Agent Mandates
* Supports **Google OAuth 2.0** and session-based email/password authentication.
* **Live Agent Creator**: Users can register new buyer agents on the fly in the UI, assigning custom budgets and whitelisting specific categories to test real-time policy adherence.

---

## 🏗️ Architecture

```mermaid
flowchart TD
    subgraph Clients["Client Layer"]
        UI["React SPA (Dashboard & Demo)"]
        Claude["Claude Desktop / External AI Agents"]
    end

    subgraph Core["VendIQ Core Gateway"]
        API["FastAPI Web Server<br/>• REST APIs & Auth<br/>• Real-Time SSE Audit Stream<br/>• SPA Static Hosting"]
        MCP["FastMCP Server<br/>• search_products<br/>• validate_purchase_mandate<br/>• suggest_addon<br/>• execute_purchase"]
        
        subgraph Agent["LangGraph Buyer Agent"]
            Pipeline["Purchase StateGraph<br/>Search → Evaluate → Validate → Upsell → Purchase"]
            HITL["Human-in-the-Loop Hook<br/>(Interactive Card Approval)"]
            Pipeline <--> HITL
        end
    end

    subgraph Storage["Data & Storage"]
        PG[("PostgreSQL Database<br/>• Orders & Transactions<br/>• Audit Logs<br/>• Mandates & Users")]
        Chroma[("ChromaDB Vector Store<br/>• 50 Product Embeddings<br/>• Semantic Search")]
    end

    subgraph External["External Services"]
        Razorpay["Razorpay API<br/>(Headless Order & Link Gen)"]
        OpenRouter["OpenRouter API<br/>(LLM Inference)"]
        GoogleAuth["Google OAuth 2.0"]
    end

    UI -->|"HTTP / SSE"| API
    Claude -->|"stdio / MCP"| MCP
    API --> Agent
    Agent --> MCP

    Agent --> OpenRouter
    API --> GoogleAuth
    API --> PG

    MCP --> Chroma
    MCP --> PG
    MCP --> Razorpay
```

---

## 🗂️ Repository Structure

```
VendIQ/
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
│   │   ├── service.py          # Search service with ChromaDB + SQL fallback
│   │   └── vector_store.py     # ChromaDB collection initialization & search
│   │
│   ├── dashboard/              # FastAPI Merchant Backend
│   │   ├── app.py              # FastAPI app, static SPA mounting & background auto-seed
│   │   └── routes.py           # REST APIs, SSE audit stream, HITL resolution
│   │
│   ├── database/               # Relational persistence
│   │   ├── models.py           # SQLAlchemy models (Order, Audit, Mandate, Product)
│   │   ├── session.py          # PostgreSQL engine and session factory
│   │   └── vector.py           # ChromaDB client wrapper
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

VendIQ functions as a standard MCP server that any MCP-compliant client (like Claude Desktop) can connect to.

### 1. Configure Claude Desktop
Add this server to your Claude Desktop configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "vendiq": {
      "command": "python",
      "args": [
        "/absolute/path/to/VendIQ/main.py",
        "mcp"
      ],
      "env": {
        "DATABASE_URL": "postgresql://postgres:postgres@localhost:5432/vendiq",
        "CHROMA_PERSIST_DIR": "/absolute/path/to/VendIQ/chroma_db",
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

- **Deterministic Defense-in-Depth**: Policy checks are evaluated both during agent reasoning and strictly verified inside the database layer before any payment link can be generated.
- **Idempotency Guard**: Prevents duplicate charges by hashing cart contents and enforcing order cooldown windows.
- **Audit Immutability**: Every policy decision (`POLICY_APPROVED`, `POLICY_REJECTED`, `UPSELL_PROPOSED`, `PAYMENT_SUCCESS`) is logged with timestamps, agent IDs, and full rationale traces.

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
