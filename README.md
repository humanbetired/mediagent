# MediAgent

**Patient Health Monitoring System built on a multi-agent architecture**

MediAgent simulates a real-time clinical decision support system. Three specialized agents work in sequence to monitor vital signs, assess patient risk, and surface relevant clinical guidance from a medical knowledge base all running on local, open-source LLMs.

---

## Overview

Modern ICU monitoring systems generate continuous streams of vital sign data, but raw numbers alone don't translate into actionable clinical insight. MediAgent demonstrates how a multi-agent pipeline can bridge that gap: a deterministic rule-based agent flags anomalies, a reasoning agent contextualizes those anomalies against patient history, and a retrieval-augmented agent grounds recommendations in actual clinical protocol documents.

The entire system runs locally, no external API calls, no cloud dependency, full data privacy by design.

A full diagram with the Docker Compose deployment topology is available in [`archi\Archi_MediAgent.png`](archi\Archi_MediAgent.png).

---

## Core Components

### Agent 1 — Vital Signs Monitor

A deterministic, rule-based agent that evaluates incoming vitals against clinical thresholds (heart rate, blood pressure, SpO2, temperature, respiratory rate, blood glucose). Each parameter is classified as `NORMAL`, `WARNING`, or `CRITICAL`, and the overall patient status follows a worst-case escalation rule consistent with Early Warning Score (EWS) principles.

No LLM involved here by design — anomaly detection on numeric thresholds should be deterministic and auditable.

### Agent 2 — Risk Analysis

Takes the structured output of Agent 1, combines it with the patient's known conditions and prior session history (retrieved from Redis), and produces a clinical risk assessment: risk level, primary concern, immediate actions, and a monitoring plan. This is where LLM reasoning adds value — interpreting how abnormal vitals interact with a patient's specific clinical background.

### Agent 3 — Medical RAG

Triggered conditionally, only when a patient's status is `WARNING` or `CRITICAL`. Queries a ChromaDB vector store built from synthetic clinical documents (vital sign reference ranges, emergency protocols, patient risk stratification guides) and returns grounded, source-referenced guidance — reducing hallucination risk compared to an unconstrained LLM response.

### Orchestrator

Coordinates the three agents in sequence, manages conditional execution, persists session state to Redis, and assembles the final response streamed back to the client.

### Agent Memory (Redis)

Each patient session is stored with a 24-hour TTL. On subsequent visits, the Risk Analysis agent receives a summary of prior sessions, allowing it to identify trends (e.g., a recurring critical parameter) rather than evaluating each visit in isolation.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| LLM Runtime | Ollama (llama3.2:1b) | Local inference, no external API |
| Embeddings | nomic-embed-text | Vector embeddings for RAG |
| Orchestration | LlamaIndex | LLM integration, RAG pipeline |
| Vector Store | ChromaDB | Persistent semantic search over clinical documents |
| Session Memory | Redis | Conversation history, alert logging |
| Backend | FastAPI | REST API, Server-Sent Events streaming |
| Frontend | React + Vite | Real-time monitoring dashboard |
| Styling | Tailwind CSS / CSS variables | ICU-monitor inspired UI |
| Containerization | Docker Compose | Reproducible local deployment |

---

## Project Structure

```
mediagent/
├── agents/
│   ├── vital_monitor.py       # Agent 1 — rule-based anomaly detection
│   ├── risk_analysis.py       # Agent 2 — LLM-based risk assessment
│   ├── medical_rag.py         # Agent 3 — RAG pipeline
│   ├── memory_manager.py      # Redis session memory
│   └── orchestrator.py        # Multi-agent coordination
├── api/
│   └── main.py                # FastAPI application, REST + SSE endpoints
├── data/
│   └── patient_data.py        # Synthetic patient profiles and vitals
├── knowledge_base/
│   ├── vital_signs_guide.txt
│   ├── emergency_protocols.txt
│   └── patient_risk_factors.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   └── App.jsx
│   └── Dockerfile
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 22+
- Docker and Docker Compose
- [Ollama](https://ollama.com) installed on the host machine

### 1. Pull Required Models

```bash
ollama pull llama3.2:1b
ollama pull nomic-embed-text
```

Ensure Ollama is reachable from containers:

```bash
# Windows (PowerShell)
setx OLLAMA_HOST "0.0.0.0:11434"
```

Restart Ollama after setting this.

### 2. Configure Environment

```bash
cp .env.example .env
```

Adjust values if needed — defaults work for local development.

### 3. Run with Docker Compose

```bash
docker-compose up --build
```

This starts Redis, the FastAPI backend, and the React frontend. ChromaDB runs as an embedded persistent client and requires no separate container.

### 4. Access the Application

| Service | URL |
|---|---|
| Dashboard | http://localhost:5173 |
| API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

---

## Running Locally Without Docker

```bash
# Backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Redis must be running separately (`docker run -d -p 6379:6379 redis:alpine` or a local install).

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/patients` | List all simulated patients |
| GET | `/api/patients/{id}` | Get a single patient's profile and current vitals |
| POST | `/api/analyze/{id}` | Run the full multi-agent analysis (synchronous) |
| GET | `/api/stream/{id}` | Run analysis with real-time SSE streaming |
| GET | `/api/history/{id}` | Retrieve a patient's session history |
| GET | `/api/alerts/{id}` | Retrieve a patient's alert log |
| GET | `/health` | Service health check |

Full interactive documentation is available at `/docs` once the API is running.

---

## Important Notes

All patient data is synthetic and generated for demonstration purposes only. This project is not a certified medical device and is not intended for clinical use. No fine-tuning was performed; domain knowledge is provided entirely through retrieval-augmented generation and prompt engineering.


