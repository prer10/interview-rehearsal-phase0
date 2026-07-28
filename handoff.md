# Interview Rehearsal — Handoff / Current State (for Sammy)

Self-contained — written so you can get productive without needing the
history of how we got here. Read top to bottom once.

## What this project is

An adaptive AI interview rehearsal tool. You answer a question, the
system decides whether the answer was strong or weak, and either digs
deeper on the same topic (grounded in your real resume/JD) or advances
to the next question. At the end, an LLM generates a real score and
summary from your actual transcript.

## Architecture, current state

```
Resume + JD  ──►  RAG index (Chroma)  ──►  retrieve(query, k)
                                                   │
Question asked ──► LangGraph agent ◄───────────────┘
  (classify → follow-up OR advance, grounded in retrieved context)
                                                   │
                                          FastAPI backend (main.py)
                                                   │
                                    Next.js frontend (separate repo)
```

Every LLM call is traced to Langfuse (cost, latency, prompt/response)
automatically.

## Two separate repos

1. **`interview-rehearsal-phase0`** (Python) — backend: retrieval,
   agent logic, FastAPI, eval harness
2. **`interview-rehearsal-ui`** (Next.js) — frontend

They talk over HTTP (`localhost:8000` ↔ `localhost:3000`), run as two
separate processes, two separate terminals.

## Backend folder structure

```
interview-rehearsal-phase0/
├── main.py                     ← FastAPI app, all endpoints
├── rag/
│   └── retrieve.py             ← chunking, embeddings, Chroma, relevance
│                                   threshold filtering
├── agents/
│   ├── personas.py             ← interviewer persona prompts
│   ├── graph_session_manager.py ← LangGraph: classify/followup/advance,
│   │                                Langfuse-traced
│   └── scorer.py               ← LLM-generated session score + summary,
│                                   Langfuse-traced
├── eval/
│   ├── retrieval_eval.py       ← 5/5 passing
│   ├── escalation_eval.py      ← 5/5 passing
│   └── faithfulness_eval.py    ← 2/2 passing (heuristic keyword check,
│                                   documented as such in the file)
├── data/
│   ├── resume.txt
│   └── job_description.txt
├── .env                        ← NOT in git. Contains GROQ_API_KEY,
│                                   LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY,
│                                   LANGFUSE_BASE_URL
└── requirements.txt
```

## Setup, from zero

1. Clone the repo, pull latest `main`
2. `python -m venv venv` → activate it
3. `pip install -r requirements.txt`
4. Create your OWN `.env` file (never share real keys over chat) with:
   ```
   GROQ_API_KEY=your-own-groq-key       # free, console.groq.com
   LANGFUSE_PUBLIC_KEY=your-own-key     # free, cloud.langfuse.com
   LANGFUSE_SECRET_KEY=your-own-key
   LANGFUSE_BASE_URL=https://cloud.langfuse.com
   ```
5. Run backend: `uvicorn main:app --reload --port 8000`
6. Separately, clone/pull `interview-rehearsal-ui`, `npm install`,
   `npm run dev`
7. Open `localhost:3000`, both servers need to stay running

## What's genuinely done

- Real RAG (chunking, embeddings, Chroma, relevance filtering — weak
  matches get filtered out, not forced in)
- Real multi-agent escalation via LangGraph (not just an if/else)
- Real per-role question banks (Role selector actually changes questions)
- Real LLM-generated scoring/summary (not hardcoded)
- Full eval harness, all passing
- Langfuse tracing on every LLM call

## What's genuinely still open — pick one

- **Dockerfile** — containerize the backend. Cheap, high resume value.
- **README** — architecture overview, real eval numbers, honest known
  limitations section (there's good material here — several things got
  built with fake/hardcoded data at first and were caught and fixed;
  documenting that honestly is a good look, not something to hide)
- **Difficulty / Question Type real wiring** — currently UI-only
  (there's an honest note about this directly in the selector component).
  Would mean expanding the question banks into a role × difficulty ×
  type matrix — real content work, not a quick fix.
- **Persistent storage** — sessions currently live in memory and reset
  on backend restart. A real database (even SQLite to start) would fix
  this and is a prerequisite for any kind of history/dashboard feature.
- **Voice mode** — real ASR/TTS. The UI already has a "switch to voice"
  button that's currently just a page-state toggle with no real audio
  behind it yet. This is the biggest, most technically separate piece
  — good to scope as its own effort, not squeezed in alongside others.

## Known, deliberate simplifications (say these out loud, don't hide them)

- Sessions are in-memory only (see "persistent storage" above)
- Faithfulness eval is a keyword-overlap heuristic, not a full
  LLM-judge — documented honestly in the file itself
- Difficulty/Question Type selectors are currently decorative