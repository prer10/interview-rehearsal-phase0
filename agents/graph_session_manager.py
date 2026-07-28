"""
agents/graph_session_manager.py — the LangGraph version, now also
grounded in retrieved context (the piece the earlier version didn't
have yet). This REPLACES the plain if/else session_manager.py logic
inside main.py from here on.
"""

import os
from typing import TypedDict
from dotenv import load_dotenv
from langfuse.openai import OpenAI  # drop-in — traces every call automatically
from langfuse import observe
from langgraph.graph import StateGraph, END
from personas import PERSONAS

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)
MODEL = "llama-3.3-70b-versatile"


class SessionState(TypedDict):
    question: str
    answer: str
    persona: str
    remaining_questions: list
    context: list          # NEW — retrieved chunks from Track A
    strength: str
    next_question: str
    is_followup: bool


@observe(name="classify-answer")
def classify_node(state: SessionState) -> dict:
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=10,
        messages=[
            {"role": "system", "content": "Classify the candidate's answer "
             "as exactly one word: 'strong' or 'weak'. Nothing else."},
            {"role": "user", "content": f"Question: {state['question']}\n"
             f"Answer: {state['answer']}"},
        ],
    )
    result = response.choices[0].message.content.strip().lower()
    return {"strength": "weak" if "weak" in result else "strong"}


@observe(name="generate-followup")
def followup_node(state: SessionState) -> dict:
    context = state.get("context") or []
    context_block = ""
    if context:
        context_block = (
            "\n\nRelevant background info about the candidate:\n"
            + "\n".join(f"- {c}" for c in context)
        )

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=120,
        messages=[
            {"role": "system", "content": PERSONAS[state["persona"]]},
            {"role": "user", "content": (
                f"The candidate was asked: '{state['question']}'\n"
                f"They answered: '{state['answer']}'\n"
                f"{context_block}\n"
                "That answer was too vague. Ask ONE specific follow-up "
                "question pushing for a concrete detail — reference the "
                "background info above by name if it's relevant. Output "
                "only the question."
            )},
        ],
    )
    followup = response.choices[0].message.content.strip()
    return {"next_question": followup, "is_followup": True}


def advance_node(state: SessionState) -> dict:
    remaining = state["remaining_questions"]
    next_q = remaining[0] if remaining else None
    return {"next_question": next_q, "is_followup": False}


def route_on_strength(state: SessionState) -> str:
    return "followup" if state["strength"] == "weak" else "advance"


def build_graph():
    graph = StateGraph(SessionState)
    graph.add_node("classify", classify_node)
    graph.add_node("followup", followup_node)
    graph.add_node("advance", advance_node)
    graph.set_entry_point("classify")
    graph.add_conditional_edges(
        "classify", route_on_strength, {"followup": "followup", "advance": "advance"},
    )
    graph.add_edge("followup", END)
    graph.add_edge("advance", END)
    return graph.compile()


# Built once at import time — main.py imports this directly.
rehearsal_graph = build_graph()


if __name__ == "__main__":
    result = rehearsal_graph.invoke({
        "question": "Tell me about a project you're proud of.",
        "answer": "I worked on a to-do list app once.",
        "persona": "behavioral",
        "remaining_questions": ["What are your weaknesses?"],
        "context": ["Built a React and Tailwind study app called Study Buddy."],
        "strength": "",
        "next_question": "",
        "is_followup": False,
    })
    print(result)