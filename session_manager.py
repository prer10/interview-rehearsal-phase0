"""
TRACK B — session manager stub.

This is the piece that decides what happens next in a rehearsal session.
It imports `retrieve` from Track A's module but doesn't need to know how
retrieval works internally — that's the point of splitting the work.
"""

import os
from openai import OpenAI

# Swapped-in during the "wire together" step. Until then, use the
# placeholder in rag/retrieve.py directly, or copy the stub locally.
# from rag.retrieve import retrieve

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)
MODEL = "llama-3.3-70b-versatile"


def classify_answer_strength(question: str, answer: str) -> str:
    """
    The simplest possible version of "escalation logic": one extra LLM
    call that classifies the answer, which the session manager then
    branches on. This is intentionally not fancy yet — get this working
    before making it smarter.

    Returns "strong" or "weak".
    """
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=10,
        messages=[
            {
                "role": "system",
                "content": "Classify the candidate's answer as exactly "
                "one word: 'strong' or 'weak'. Nothing else.",
            },
            {
                "role": "user",
                "content": f"Question: {question}\nAnswer: {answer}",
            },
        ],
    )
    result = response.choices[0].message.content.strip().lower()
    return "weak" if "weak" in result else "strong"


def next_question(question: str, answer: str) -> str:
    """
    TODO: this is where you decide the next question.
    - If classify_answer_strength() says "weak", dig deeper on the same
      topic (use retrieve() to ground the follow-up in something real
      from the resume/JD)
    - If "strong", move to the next topic

    Left unimplemented on purpose — this branching logic is the actual
    hard, interesting part of the project. Build it incrementally: get
    "weak -> ask a generic deeper follow-up" working first, then make
    the follow-up grounded in retrieval.
    """
    strength = classify_answer_strength(question, answer)
    raise NotImplementedError(f"Answer classified as {strength} — now build the branch")


if __name__ == "__main__":
    result = classify_answer_strength(
        "Tell me about a project you're proud of.",
        "I worked on a to-do list app once.",
    )
    print(f"Classified as: {result}")
