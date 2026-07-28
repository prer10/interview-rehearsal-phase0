# Track B Guide — Agents & Orchestration (for Sammy)

This is a complete, standalone guide — everything you need from zero to
where the project currently stands, written so you don't need to see any
prior conversation to follow it. Read it top to bottom once before doing
anything.

## What this project is

We're building an adaptive interview rehearsal tool: you type an answer
to an interview question, and instead of generic canned feedback, the
system decides whether your answer was strong or weak and adjusts what
happens next — digging deeper into a weak spot instead of moving on, the
way a real interviewer would. That adaptive part is your job. Prerana's
half (Track A) handles retrieval — pulling relevant facts from a resume
and job description so questions are grounded in something real. You
don't need to understand her internals, just one function she hands you.

## Setup — do this first

### 1. Get the shared repo
Prerana has a shared GitHub repo with the project skeleton. Get the
clone URL from her, then in VS Code:
- `Ctrl+Shift+P` → **Git: Clone** → paste the URL → pick a folder → Open

### 2. Create your own branch (important — avoids overlapping edits)
In VS Code's terminal:
```
git checkout -b track-b-agents
```
This means your work lives on its own branch until you're ready to merge
with Prerana's. **You only edit files inside the `agents/` folder** —
never touch anything in `rag/`, that's Prerana's territory. This alone
prevents almost all merge conflicts between you two.

### 3. Virtual environment + dependencies
In the terminal, inside the project folder:
```
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate        # Mac/Linux
pip install -r requirements.txt
```
If you get "running scripts is disabled" on Windows, run this once first:
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. Get your own free Groq API key
Go to console.groq.com, sign up (no credit card needed), create an API
key. Then in your terminal:
```
export GROQ_API_KEY="your-key-here"          # Mac/Linux
$env:GROQ_API_KEY="your-key-here"             # Windows PowerShell
```
This resets every time you open a new terminal — you'll need to re-set
it each session for now.

## The core idea you're building: escalation

Normal chatbots ask a fixed list of questions no matter what you answer.
Yours should behave more like a real interviewer: if your answer was
vague or weak, the next question should push on that same weak spot
instead of politely moving to a new topic. That branching decision is
the single most important piece of this whole project — everything else
is scaffolding around it.

## Step-by-step build

### Step B1 — verify the classifier works (starting point)

There's already a file `agents/session_manager.py` in the repo with one
working function: `classify_answer_strength(question, answer)`. It makes
one API call and returns the single word `"strong"` or `"weak"`.

Run this to confirm it works for you:
```
python agents/session_manager.py
```
It should print `Classified as: weak` for the placeholder test case
already in the file. Try changing the test answer in the file to
something clearly detailed and strong, rerun, and confirm it flips to
`"strong"`. Don't move on until this works — everything else depends on
this function being reliable.

### Step B2 — build persona prompts

Create a new file `agents/personas.py`. This defines what different
"interviewer personalities" sound like. Start with just two.

### Step B3 — build the escalation branch

This is the real task: given whether the last answer was strong or weak,
decide the next question. Simplest working version first:
- weak → ask a generic deeper follow-up on the same topic
- strong → move to the next question in a fixed list

Only once that works do you make the follow-up smarter (grounded in
Prerana's retrieved context instead of generic).

### Step B4 — test standalone, without Track A yet

Don't wait for Prerana's retrieval to be ready. Use a placeholder
function that returns fake text, so you can build and test your
escalation logic in isolation. Swapping in her real function later is a
one-line change, not a rewrite — that's the whole point of splitting the
work this way.

### Step B5 — session scoring

After all questions are done, one more agent call that summarizes the
whole session: what was strong overall, what to work on. This is
`agents/scorer.py` — build this last, after escalation is solid.

## Files you'll create/edit, in order

1. `agents/personas.py` — new file, persona system prompts
2. `agents/session_manager.py` — already exists, you'll extend it
3. `run_session.py` — new file, project root, ties it together so you
   can actually run and test a full session end to end
4. `agents/scorer.py` — new file, built last

## Git — commit often

After each step works:
```
git add .
git commit -m "describe what now works"
git push -u origin track-b-agents
```
