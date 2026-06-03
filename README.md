# AI Customer Support Agent (Refund Processing)

A production-ready, fully containerized web application representing an AI-powered customer support agent that processes or denies e-commerce refunds based on strict company policies.

## Features

- **Next.js Customer UI**: A premium consumer interface featuring a modern **Liquid Glassmorphism** design, collapsible sidebar, suggestions chips, markdown response rendering, and micro-animated avatars.
- **Streamlit UI**: An operational dashboard for viewing live customer threads side-by-side with real-time agent reasoning logs and tool calls.
- **FastAPI Backend**: Built using official FastAPI best practices and SOLID design principles, utilizing the standard OpenAI SDK for LLM agent routing.
- **Deterministic Security Boundary**: Hardcoded Python logic acting as a safety gate for refund verification.
- **SQLite Database**: A relational database seeded with realistic customer data and edge cases (expired orders, final sale items, high-value orders).

---

## Directory Structure

Following SOLID design principles, the backend code has been decoupled into distinct layers:

```text
├── backend/
│   ├── app/
│   │   ├── api/            # API routing and endpoint declarations (main.py, chat.py)
│   │   ├── core/           # Configuration management (config.py, settings)
│   │   ├── db/             # Database connectivity and seeding (database.py, init_db.py)
│   │   ├── schemas/        # Pydantic validation models (chat.py)
│   │   └── services/       # Core business logic (agent.py, tools.py)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend-nextjs/        # Next.js Liquid Glass customer interface
├── frontend/               # Streamlit Admin Portal
└── docker-compose.yml      # Multi-container orchestration
```

---

## Quick Start

Experience zero-configuration setup with Docker Compose.

1. **Configure Environment & API Keys**
   ```bash
   cp .env.example .env
   ```
   Open the `.env` file and insert your API credentials.
   
   > [!IMPORTANT]
   > You **must** provide a valid LLM API key (e.g., `GEMINI_API_KEY` or `OPENAI_API_KEY` depending on your provider) inside the `.env` file to get the project working. Without this key/token, the backend agent service will not be able to answer customer queries.


2. **Boot the System (Choose your Profile)**
   
   To boot the Next.js Customer UI and Backend:
   ```bash
   docker compose up --build -d
   ```

3. **Access the Applications**
   - **Customer UI (Next.js)**: [http://localhost:3000](http://localhost:3000)
   - **Admin UI (Streamlit)**: [http://localhost:8501](http://localhost:8501)
   - **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Database Management

### Resetting & Seeding Mock Data
The database file is persistent and stored in a shared volume. To force-reset or update your mock database schema/data after modifying `backend/app/db/init_db.py`:

1. Delete the persistent SQLite file:
   ```bash
   rm data/database.db
   ```
2. Restart the backend container:
   ```bash
   docker compose restart backend
   ```
On startup, the backend automatically detects that the file is missing and executes a fresh initialization run.

---

## Headless Architecture & Security

### Headless Design
The FastAPI backend acts as a completely UI-agnostic engine that solely reads and writes standard JSON schemas. The client interfaces (Next.js and Streamlit) can be swapped or modified independently of the core agent loop.

### Dual-Layer Security Model
Security boundaries prevent the LLM from making unauthorized decisions (e.g. bypassing refund limits or final-sale terms):
1. **LLM Reasoning Layer**: The agent evaluates policies, requests details, and formulates user-facing steps.
2. **Deterministic Code Boundary**: Inside the `process_refund` tool execution, a hardcoded Python validation validates the database. If an order violates constraints (e.g., exceeds $500, final sale, or over 30 days old), the Python script rejects the action directly and sends a block message to the LLM. The LLM cannot override this code boundary.

---

## Vendor-Agnostic LLM Routing
This project leverages standard OpenAI SDK syntax, allowing you to route traffic to any OpenAI-compatible provider (such as Gemini, Groq, or local vLLM instances) simply by modifying the base URL in your `.env` file:

* **Gemini (OpenAI compatibility)**: `BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/`
* **Groq**: `BASE_URL=https://api.groq.com/openai/v1`
