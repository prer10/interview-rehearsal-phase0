"""
Phase 0: Interview Rehearsal — bare-bones version, running on Groq's FREE API.

No frameworks. No RAG. No agents. Just you, a loop, and raw API calls.
The goal of this file is to SEE exactly what happens on every request,
so read every line before you run it, not after.

Why Groq instead of Claude here: Groq has a genuinely free tier with no
credit card required, which makes it the right choice while you're
learning and don't want to spend anything. The concepts you learn here
(system prompt, messages array, response parsing) are identical no
matter which provider you use later.
"""

import os
from openai import OpenAI  # Groq uses an OpenAI-compatible interface

# Groq keys are free, no credit card. Get one at https://console.groq.com
# Set it before running: export GROQ_API_KEY="your-key-here"
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "llama-3.3-70b-versatile"  # a strong open model, free on Groq

# A fixed, hardcoded set of interview questions. No escalation logic yet —
# that's Phase 2. Right now we're just proving the request/response loop works.
QUESTIONS = [
    "Tell me about a project you're proud of and why.",
    "Describe a time you disagreed with a teammate. How did you handle it?",
    "Why do you want to work in AI engineering specifically?",
]

# The system prompt sets the model's role for the whole conversation.
# Everything the interviewer "is" lives in this one string right now.
SYSTEM_PROMPT = """You are a friendly but rigorous technical interviewer
conducting a mock interview. After the candidate answers, give brief,
honest, specific feedback (2-3 sentences) on what was strong and what
was missing. Do not ask the next question yourself — the script controls
that. Just give feedback on the answer you were given."""


def get_feedback(question: str, answer: str) -> str:
    """
    This is the entire "AI" part of this script. One function, one API call.
    Study this function until you could rewrite it from memory — everything
    else you build later is this same call, just wrapped in more logic.
    """
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=300,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Question: {question}\n\nCandidate's answer: {answer}",
            },
        ],
    )
    # Note the shape difference from Anthropic's SDK: here it's
    # response.choices[0].message.content — every provider structures
    # its response slightly differently. Getting comfortable reading a
    # new SDK's response shape is itself a real skill.
    return response.choices[0].message.content


def main():
    print("=== Interview Rehearsal — Phase 0 (running on Groq, free) ===\n")
    for i, question in enumerate(QUESTIONS, start=1):
        print(f"Q{i}: {question}")
        answer = input("Your answer: ")
        print("\nThinking...\n")

        feedback = get_feedback(question, answer)
        print(f"Feedback: {feedback}\n")
        print("-" * 50 + "\n")

    print("Session complete. (No scoring, no memory of past sessions yet — that's later.)")


if __name__ == "__main__":
    main()