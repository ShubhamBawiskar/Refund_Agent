# AI Customer Support Agent (Refund Processing)

A functional, fully containerized web application representing an AI-powered customer support agent that processes or denies e-commerce refunds based on strict company policies.

## Features

- **Frontend**: Streamlit-based dual-pane UI.
- **Backend**: FastAPI with standard OpenAI SDK for LLM tool routing.
- **Database**: SQLite with synthetic edge-case data.
- **Orchestration**: Fully dockerized with persistence.

## Quick Start

Experience zero-configuration setup with Docker.

1. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and insert your API key
   ```

2. **Boot the System (Choose your Profile)**
   
   To boot the Admin UI (Streamlit):
   ```bash
   docker-compose --profile admin up --build -d
   ```
   
   To boot the Premium Customer UI (Next.js):
   ```bash
   docker-compose --profile public up --build -d
   ```

3. **Access the Application**
   - Admin Frontend (Streamlit): [http://localhost:8501](http://localhost:8501)
   - Public Frontend (Next.js): [http://localhost:3000](http://localhost:3000)
   - Backend API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Headless Architecture

The system is designed with a completely swappable UI by utilizing a "Headless Architecture". The FastAPI backend is entirely UI-agnostic; it solely accepts and returns standard JSON. 
Because the API layer is decoupled, you can effortlessly switch between the Streamlit internal ops interface and the custom-styled Next.js consumer interface without touching the core agent logic. Docker Compose profiles (`admin` vs `public`) handle orchestrating the chosen experience.

## Architecture & Dual-Layer Security

The system employs a **Dual-Layer Security** model to strictly enforce refund policies without relying solely on the LLM's non-deterministic reasoning.

1. **LLM Reasoning Layer**: The agent attempts to query orders, read policies, and understand the customer intent. It uses tools to fetch context.
2. **Deterministic Code Boundary**: Inside the `process_refund` tool execution, a hardcoded Python policy validation checks the actual database record. If an item is marked as "Final Sale" or exceeds $500 in value, the Python function immediately blocks the refund and returns a refusal string back to the LLM. The LLM cannot override this deterministic lock.

## Vendor Agnostic API Hot-Swapping

This project uses the standard OpenAI Python SDK, but is architected to instantly hot-swap the underlying LLM provider.

By modifying the `OPENAI_BASE_URL` and `OPENAI_API_KEY` in the `.env` file, you can effortlessly route all agent traffic to Groq, Gemini (if using an OpenAI-compatible endpoint), or any vLLM local instance.

See `.env.example` for examples.
