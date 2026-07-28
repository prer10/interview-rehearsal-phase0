"""
agents/scorer.py — Step B5, the piece we planned early on and never
built until now. A real LLM call that reads the FULL session transcript
and produces an actual score + specific summary, instead of a hardcoded
placeholder.
"""

import os
import json
from dotenv import load_dotenv
from langfuse.openai import OpenAI  # drop-in — traces every call automatically
from langfuse import observe

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)
MODEL = "llama-3.3-70b-versatile"

SCORER_SYSTEM_PROMPT = """You are an experienced interview coach reviewing
a full mock interview transcript. Read every question and answer, then
output ONLY valid JSON in this exact shape, nothing else — no markdown
fences, no extra commentary:

{"score": <integer 1-10>, "summary": "<2-3 sentences>"}

The summary must reference SPECIFIC things from this transcript (name an
actual answer that was strong or weak) — never a generic template like
"good job overall." If most answers were vague, say so plainly and say
which ones."""


@observe(name="generate-session-report")
def generate_session_report(history: list) -> dict:
    """
    `history` is a list of {"question": ..., "answer": ...} dicts, in
    order — exactly what main.py's session["history"] already collects.
    Returns {"score": int, "summary": str}.
    """
    if not history:
        return {"score": 0, "summary": "No answers were given this session."}

    transcript = "\n\n".join(
        f"Q: {turn['question']}\nA: {turn['answer']}" for turn in history
    )

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=300,
        messages=[
            {"role": "system", "content": SCORER_SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
    )

    raw = response.choices[0].message.content.strip()
    # Models sometimes wrap JSON in markdown fences despite instructions
    # not to — strip those defensively rather than trusting compliance.
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(raw)
        return {
            "score": int(data.get("score", 5)),
            "summary": data.get("summary", "No summary generated."),
        }
    except (json.JSONDecodeError, ValueError):
        # If the model didn't return valid JSON, fail gracefully instead
        # of crashing the whole session-finish request.
        return {"score": 5, "summary": "Could not parse a detailed summary this time."}


if __name__ == "__main__":
    fake_history = [
        {"question": "Tell me about a project you're proud of.",
         "answer": "I built a to-do app once."},
        {"question": "Can you give one concrete detail about that?",
         "answer": "It used React and had a delete button."},
    ]
    print(generate_session_report(fake_history))