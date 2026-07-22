# Task split — Interview Rehearsal Engine

Both of you: run Phase 0 (the single-file Groq script) individually first.
Don't start below until you've both done that.

## Track A — Retrieval & data (owner: ___________)

Lives in `/rag`. Your job: given a resume and a job description, retrieve
the pieces that should ground the interviewer's questions.

- [ ] `rag/ingest.py` — load a resume (PDF/txt) and a job description,
      split into chunks (don't cross section boundaries)
- [ ] `rag/embed.py` — embed the chunks (start with any free embedding
      model — sentence-transformers running locally is free and enough
      for this stage, no API needed for embeddings)
- [ ] `rag/retrieve.py` — given a query ("what should I ask about their
      last project?"), return the top-k most relevant chunks
- [ ] `data/questions.json` — curate 15-20 real interview questions
      (behavioral + technical), tagged by category
- [ ] Write 5 test queries with the answer you'd expect retrieved, so
      Track B can trust your module without reading its internals

Deliverable Track B depends on: a function
`retrieve(query: str, k: int) -> list[str]` that Track B can import and
call without knowing how it works inside.

## Track B — Agents & orchestration (owner: ___________)

Lives in `/agents`. Your job: the interviewer's behavior.

- [ ] `agents/personas.py` — system prompts for 2-3 personas (technical,
      behavioral). Start with just static prompts, no escalation yet.
- [ ] `agents/session_manager.py` — decides which persona asks next,
      and (once retrieval is ready) calls Track A's `retrieve()` to
      ground the question in something real
- [ ] `agents/escalate.py` — the hard part: given the last answer, decide
      "go deeper on this weak spot" vs "move on." Start simple: a second
      LLM call that just classifies the last answer as strong/weak, then
      branch on that.
- [ ] `agents/scorer.py` — after the session, produce a summary + score

While Track A is still building retrieval, stub it out:
`def retrieve(query, k): return ["<placeholder context>"]` — build and
test your agent logic against that, swap in the real one later.

## Both — do together

- [ ] `eval/escalation_eval.py` — canned weak/strong test answers, check
      the agent escalates on the right thing
- [ ] `eval/faithfulness_eval.py` — check every question references
      something real from Track A's retrieved chunks, not invented
- [ ] Wire Track A + Track B together in `main.py`
- [ ] README with your architecture, what you'd do differently, and your
      eval numbers — this is what a reviewer actually reads

## Git workflow to avoid stepping on each other

- One shared repo, one branch each: `track-a-retrieval`, `track-b-agents`
- Each of you only edits files in your own folder until the "wire
  together" step — this avoids merge conflicts entirely
- Small, frequent commits with real messages, not "wip" — you'll want
  this history to point to in interviews
