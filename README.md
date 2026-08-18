# Enterprise HR & General Affairs AI Assistant

An agentic AI assistant that answers HR and General Affairs policy questions using RAG, and automatically creates ServiceNow tickets when an employee needs action taken — a laptop issue, an access request, or a policy question the knowledge base can't answer.

Employees currently lose time searching scattered HR/GA policies and manually raising support tickets, while HR/GA teams field the same repetitive questions. This assistant answers policy questions directly from company documentation and escalates anything it can't resolve into a real, trackable ServiceNow ticket — automatically.

---

## Demo

> _Add a screenshot of the chat UI here, ideally showing one grounded policy answer and one ticket-creation response side by side._

---

## What Makes This Agentic, Not Just RAG

A plain RAG assistant always follows the same path: question → retrieve → generate → answer. This system has to **decide what to do** before it can answer:

- A policy question ("what time does the office open?") is answered directly from retrieved documentation.
- An action request ("my laptop screen is cracked") skips retrieval entirely and creates a ServiceNow ticket.
- **A policy question the knowledge base can't actually answer also escalates to a ticket automatically** — instead of leaving the employee with a dead end, the system recognizes the gap and routes it to a human via ServiceNow.

That branching logic — implemented as a LangGraph state graph with two conditional decision points — is what makes this an agent rather than a chatbot with a search function.

---

## Architecture

```
Employee question
      |
Authenticate request  (JWT + RBAC)
      |
Classify intent  (LangGraph agent decision)
      |
      +---------------------------+
      |                           |
Retrieve & answer           Collect & create ticket
(ChromaDB + grounded LLM)   (ServiceNow API call)
      |                           |
      +------------ if no answer found in context ------------+
      |                                                        |
      +----------------------------+---------------------------+
                                   |
                     Log conversation & ticket (PostgreSQL)
                                   |
                     Response shown in React UI
```

**Two databases, two different jobs:**
- **ChromaDB** stores unstructured policy text as embeddings, for semantic search.
- **PostgreSQL** stores structured, queryable data — users, conversation history, and a local ticket log — the kind of data that needs precise lookups and relationships, not similarity search.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Python, FastAPI, Uvicorn |
| Agent orchestration | LangGraph (stateful, conditional multi-node graph) |
| RAG orchestration | LangChain |
| LLM | Groq (`llama-3.3-70b-versatile`) |
| Vector database | ChromaDB (persistent, local) |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`, local) |
| Relational database | PostgreSQL (via SQLAlchemy ORM) |
| Authentication | JWT (`python-jose`) + bcrypt (`passlib`), RBAC via FastAPI dependency |
| Enterprise integration | ServiceNow REST API (Table API) |
| Frontend | React + Vite, Tailwind CSS |
| Document processing | PyPDF, python-docx |

---

## Key Design Decisions

- **Second conditional decision point after generation, not just before retrieval.** Most intent-classifier agents route once, upfront, and stop. This agent also checks whether the generated answer actually resolved the question — if the LLM responds with a `NO_INFO_FOUND` sentinel (meaning the retrieved context didn't cover the question), the graph automatically re-routes to ticket creation instead of leaving the employee with an unhelpful "I don't know." This was verified against a real gap in the test knowledge base, not a contrived case.
- **Two databases used for what they're actually good at.** ChromaDB for semantic search over unstructured policy text; PostgreSQL for structured, relational data (users, conversation logs, ticket records) that needs precise queries and joins, not similarity search.
- **JWT + RBAC via a FastAPI dependency factory.** `require_role(*roles)` returns a configured dependency, so any endpoint can declare which roles are allowed to call it without duplicating permission-checking logic across routes.
- **`HTTPBearer`, not `OAuth2PasswordBearer`, for the security scheme.** The login endpoint is a custom JSON API, not the OAuth2 password-grant flow — `HTTPBearer` correctly reflects "verify a bearer token" without assuming how that token was issued.
- **ServiceNow client isolated from agent logic.** `app/integrations/servicenow/client.py` has zero knowledge of LangGraph or agent state — it just takes a description and returns a ticket or raises a typed `ServiceNowError`. This keeps the integration independently testable and swappable (e.g., for Jira or Zendesk) without touching the agent.
- **Failures are surfaced honestly, not swallowed.** If the ServiceNow API call fails, the agent explicitly tells the employee the ticket wasn't created and to contact support directly — never silently returns a generic error that could be mistaken for success.
- **LLM provider isolated behind one client object**, the same pattern used in an earlier RAG project — swapping providers (this project uses Groq instead of the original OpenAI proposal) required changing only the client initialization, nothing else in the agent or RAG logic.

---

## Project Structure

```
app/
  ingestion/          # PDF/DOCX loading and chunking
  retrieval/           # embeddings, ChromaDB vectorstore
  agent/                # LangGraph state, nodes, and graph definition
  auth/                 # JWT security and RBAC dependencies
  integrations/servicenow/  # ServiceNow REST API client
  db/                   # SQLAlchemy models and CRUD helpers
  api/                   # FastAPI app and routes
frontend/               # React + Vite + Tailwind chat UI
data/raw/                # source PDF/DOCX policy documents
vectorstore/              # ChromaDB persistent storage
ingest.py                  # ingestion entry point
requirements.txt
```

---

## Running Locally

### 1. Backend setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment variables (`.env`)
```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/hr_ga_assistant
JWT_SECRET_KEY=your-generated-secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
GROQ_API_KEY=your-groq-key
SERVICENOW_INSTANCE_URL=https://devXXXXX.service-now.com
SERVICENOW_USERNAME=your-username
SERVICENOW_PASSWORD=your-password
```

### 3. Database
```bash
createdb hr_ga_assistant
python init_db.py
```

### 4. Ingest policy documents
Place PDF/DOCX HR/GA policy documents into `data/raw/`, then:
```bash
python ingest.py
```

### 5. Start the backend
```bash
python -m uvicorn app.api.main:app --reload
```
API docs at `http://127.0.0.1:8000/docs`.

### 6. Start the frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173`.

---

## API

**`POST /auth/signup`** / **`POST /auth/login`** — returns a JWT `access_token`.

**`POST /ask`** (requires `Authorization: Bearer <token>`)
```json
{ "question": "How many casual leave days do I get per year?" }
```
Returns either a grounded answer or a ServiceNow ticket confirmation:
```json
{ "answer": "...", "ticket_number": "INC0010008" }
```

---

## Limitations & Future Improvements

- **No automated test suite yet.** The testing strategy is defined (pytest with an in-memory SQLite database for auth tests, and the LangGraph agent mocked for endpoint contract tests) but not yet implemented, in favor of completing the full feature set first.
- **Not yet deployed publicly.** Runs locally; a planned next step is deploying to a VPS and load-testing the deployment against realistic concurrent traffic to validate it under load, rather than just claiming it works at scale.
- **No distance/similarity threshold on retrieval**, same known gap as the vector-search approach generally — the system currently relies on the LLM's `NO_INFO_FOUND` self-assessment rather than a numeric confidence cutoff.
- **Ticket creation doesn't yet support multi-turn slot-filling.** If a ticket needs details the employee didn't provide in their first message, the current graph doesn't loop back to ask follow-up questions before calling ServiceNow — the whole question is passed through as the ticket description as-is.
- **Signup currently has no dedicated UI** — new users are created via the API directly; a signup form would be a natural addition alongside login.

---

## Business Value

- Faster resolution of HR/GA questions without waiting on a human
- Automated, trackable ticket creation instead of manual request submission
- Centralized, searchable policy knowledge base
- Reduced repetitive query load on HR/GA teams
- A consistent, auditable record of every conversation and ticket via PostgreSQL logging
