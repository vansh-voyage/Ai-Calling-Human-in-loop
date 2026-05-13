# Frontdesk AI — Human-in-the-Loop Supervisor

A human-in-the-loop system for an AI salon receptionist. When the AI doesn't know an answer, it escalates to a human supervisor, follows up with the caller, and saves the answer so it never has to ask again.

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- API keys: Anthropic, Deepgram, Cartesia, LiveKit (free tiers work)

### 1. Configure environment

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 2. Start the backend

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
# → http://localhost:8000
# → Database created and seeded with 12 salon Q&As on first start
```

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### 4. (Optional) Start the voice agent

```bash
pip install -r agent/requirements.txt
python -m agent.main dev
# → Connects to LiveKit room, ready to receive calls
```

### Test without LiveKit

```bash
curl -X POST http://localhost:8000/api/v1/simulate/call \
  -H "Content-Type: application/json" \
  -d '{"caller_id": "+15550100", "caller_name": "Jane", "question": "Do you offer hot stone massage?"}'
```

---

## How It Works

### The Loop

```
Caller speaks
  → Agent checks knowledge base (/api/v1/knowledge/lookup)
  → KB hit? Answer directly, no escalation
  → KB miss? Create help_request + tell caller "I'll follow up"
      → Supervisor sees it in Dashboard
      → Types answer → PATCH /resolve
          → Answer saved to knowledge base
          → Simulated SMS to caller
  → 24h with no answer → request marked "unresolved"
```

### The Self-Learning Part

Every supervisor answer is stored with a normalized question key. The next time any caller asks a matching question, the agent answers from the knowledge base — no escalation needed. The "Served" count on the Knowledge page shows which answers are most valuable.

---

## Key Design Decisions

**Why SQLite?**
Zero-config, ships with Python, no cloud account needed. Swap to Postgres by changing `DATABASE_URL` in `.env` — zero code changes anywhere else.

**Why `question_normalized` as the shared key?**
It's the stable identifier that links `help_requests` to `knowledge_entries`. Normalizing (lowercase, strip punctuation) before storing means "Do you offer extensions??" and "do you offer extensions" hit the same entry.

**Why `timeout_at` stored at insert time?**
The timeout reaper job runs `WHERE status='pending' AND timeout_at < NOW()` — a fast index scan. Computing it at query time would require date arithmetic on every row.

**Why separate `notification_service.py` and `sms_service.py`?**
Both are purely console output today. Either can be upgraded to real SMS (Twilio) or real push notifications without touching any agent or API code — just swap the implementation in its own file.

**Why a 2-second timeout on KB lookup in the agent?**
A slow backend should not leave the caller in silence. If the lookup times out, the agent escalates and tells the caller it will follow up. The call never hangs.

**How this scales from 10/day to 1,000/day:**
- DB: `DATABASE_URL=postgresql+asyncpg://...` — nothing else changes
- KB lookup: replace `LIKE` fuzzy match with `pgvector` in `knowledge_service.py` — same function signature
- Notifications: set `SUPERVISOR_WEBHOOK_URL` to a queue endpoint — no code changes
- Timeout jobs: replace APScheduler with Celery Beat — job body unchanged
- Agent workers: LiveKit already load-balances multiple `python -m agent.main` processes

---

## What I Would Improve Next

1. **Vector search for KB** — Replace keyword LIKE matching with embedding-based similarity search (`pgvector` or a hosted vector store). Would dramatically improve "Did you mean X?" matching for long-tail questions.

2. **Supervisor auth** — Currently the dashboard is open. Add a simple API key header or OAuth so only authorized supervisors can resolve requests.

3. **Real-time UI updates** — Replace 30-second polling with Server-Sent Events on `GET /help-requests/stream`. Supervisors would see new cards appear instantly.

4. **Call hold + live transfer (Phase 2)** — If the supervisor is online when the call comes in, check their availability and offer to transfer the live call rather than falling back to async text-based follow-up.

5. **Question clustering** — Group similar unanswered questions together in the KB view so supervisors can answer multiple callers with one response.

---

## Running Tests

```bash
python -m pytest backend/tests/ -v
# 18 tests, all passing
```

Tests cover:
- `normalize_question` edge cases
- KB lookup (exact match, fuzzy match, miss, lookup_count increment)
- KB upsert
- Help request creation and resolution
- 409 on double-resolve
- Timeout reaper (past/future/resolved not touched)
