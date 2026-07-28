"""
agents/session_manager.py — now accepts optional retrieved context, so
follow-up questions can be grounded in real resume/JD facts instead of
being generic. This is the actual "wire Track A into Track B" moment.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
from personas import PERSONAS

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)
MODEL = "llama-3.3-70b-versatile"


def classify_answer_strength(question: str, answer: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=10,
        messages=[
            {"role": "system", "content": "Classify the candidate's answer "
             "as exactly one word: 'strong' or 'weak'. Nothing else."},
            {"role": "user", "content": f"Question: {question}\nAnswer: {answer}"},
        ],
    )
    result = response.choices[0].message.content.strip().lower()
    return "weak" if "weak" in result else "strong"


def generate_deeper_followup(question: str, answer: str, persona: str, context=None) -> str:
    """
    NEW: `context` is a list of retrieved text chunks (from Track A's
    retrieve()). When provided, the follow-up is asked to ground itself
    in that real information instead of staying generic. This is the
    single most important change in the whole project — it's what turns
    "an agent that reacts" into "an agent that reasons using RAG."
    """
    context_block = ""
    if context:
        context_block = (
            "\n\nRelevant background info about the candidate (from their "
            "resume/job description):\n" + "\n".join(f"- {c}" for c in context)
        )

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=120,
        messages=[
            {"role": "system", "content": PERSONAS[persona]},
            {"role": "user", "content": (
                f"The candidate was asked: '{question}'\n"
                f"They answered: '{answer}'\n"
                f"{context_block}\n"
                "That answer was too vague. Ask ONE specific follow-up "
                "question pushing for a concrete detail — reference the "
                "background info above by name if it's relevant. Output "
                "only the question."
            )},
        ],
    )
    return response.choices[0].message.content.strip()


def next_question(question: str, answer: str, remaining_questions: list,
                   persona: str = "behavioral", context=None):
    """
    Returns (next_question_text, is_followup, strength) — now returns
    strength too, so the caller can use it for feedback text without
    re-classifying.
    """
    strength = classify_answer_strength(question, answer)

    if strength == "weak":
        followup = generate_deeper_followup(question, answer, persona, context)
        return followup, True, strength
    else:
        next_q = remaining_questions[0] if remaining_questions else None
        return next_q, False, strength


if __name__ == "__main__":
    # Manual test with fake context, simulating what Track A would return.
    fake_context = ["Built a React and Tailwind study app called Study Buddy."]
    result = next_question(
        "Tell me about a project you're proud of.",
        "I built an app once.",
        remaining_questions=["What are your weaknesses?"],
        context=fake_context,
    )
    print(result)