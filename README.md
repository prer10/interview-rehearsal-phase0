# Interview Rehearsal Engine

An adaptive AI interview rehearsal tool. Instead of asking a fixed list
of questions, it decides — in real time — whether an answer was strong
or weak, and either digs deeper on the same topic (grounded in your
actual resume and the job description) or moves on. At the end, an LLM
generates a real score and summary from the full transcript.

## Architecture

```
Resume + JD → RAG index (Chroma, relevance-filtered) → retrieve(query, k)
                                                              │
Question asked → LangGraph agent (classify → follow-up OR advance) ◄──┘
                                                              │
                                                  FastAPI backend
                                                              │
                                          Next.js frontend (separate repo)
                                                              │
                                          Postgres (Neon) — persisted history
```

Every LLM call is traced to Langfuse: prompt, response, tokens, cost,
and latency, with nested traces per session.

## Tech stack

Python, FastAPI, LangGraph, LangChain (text splitting), ChromaDB,
sentence-transformers, PostgreSQL (Neon), Langfuse, Docker, Next.js,
TailwindCSS.

## Two repos

- Backend (this repo): retrieval, agent logic, FastAPI, eval harness
- [Frontend](link-to-your-ui-repo): Next.js UI

They communicate over HTTP and run as separate processes/containers.

## Running locally

```bash
docker build -t interview-rehearsal-backend .
docker run -p 8000:8000 --env-file .env interview-rehearsal-backend
```
See the frontend repo for its own setup. Requires a `.env` with
`GROQ_API_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`,
`LANGFUSE_BASE_URL`, and `DATABASE_URL` (Neon connection string) — none
of these are committed, see `.env.example` for the expected shape.

## Evaluation

Three eval suites, run with `python eval/<name>.py`:

- **Retrieval eval** (5/5 passing) — does semantic search return the
  chunk a human would expect for a given query?
- **Escalation eval** (5/5 passing) — does the agent actually escalate
  on genuinely vague answers and advance on genuinely detailed ones?
- **Faithfulness eval** (2/2 passing) — when a follow-up is grounded in
  retrieved context, does it actually reference that context? **This is
  a keyword-overlap heuristic, not an LLM-judge** — it can catch a
  follow-up that ignores its context entirely, but can't prove the
  absence of a hallucinated detail sitting alongside a real one. Stated
  here explicitly rather than overclaiming what it proves.

## Known limitations / honest notes

A few things were built, found to be wrong or fake, and fixed along the
way — documenting that process here rather than hiding it:

- **Retrieval initially returned irrelevant matches** (e.g. citing an
  unrelated project) because with only a couple of source documents,
  similarity search always returns *something*, even a bad match. Fixed
  with a relevance-distance threshold that discards weak matches instead
  of forcing them into context.
- **The UI originally displayed hardcoded analysis data** (filler-word
  counts, words-per-minute) left over from a design mockup, unconnected
  to any real computation — since this app is currently text-only, that
  data was never computable in the first place. Removed in favor of only
  showing genuinely computed data (real LLM-generated score and summary).
- **Difficulty and Question Type selectors are currently UI-only** — Role
  genuinely changes the question set served; Difficulty/Type do not yet.
  Flagged directly in the UI itself, not hidden.
- **Sessions store history to Postgres on completion**, but in-progress
  session state is still in-memory — a backend restart mid-session loses
  that session (completed ones are safe, since they're already persisted).

## Not yet built

- Real voice input (ASR) / voice output (TTS) — the UI has a toggle for
  this, currently a page-state switch with no real audio behind it yet
- Full Difficulty × Question Type content matrix
- Score-trends / practice-calendar dashboard (Neon integration above is
  the prerequisite for this, now in place)