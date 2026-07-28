"""
eval/faithfulness_eval.py — when a follow-up is grounded in retrieved
context, does it actually REFERENCE that context, or does it just
generate a generic follow-up and ignore what it was given?

This is a heuristic check (keyword overlap), not a perfect one — it
can't prove the model didn't hallucinate a DIFFERENT specific claim
alongside real ones. Worth stating that limitation honestly rather than
overclaiming what this eval proves. A stronger version later would use
an LLM-as-judge to check groundedness directly.

Run from project root: python eval/faithfulness_eval.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "agents"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "rag"))

from graph_session_manager import rehearsal_graph
from retrieve import retrieve

# Each case: a weak answer that should trigger a grounded follow-up, plus
# a keyword we'd expect to see if the follow-up genuinely used the
# retrieved context instead of staying generic.
TEST_CASES = [
    {
        "question": "Tell me about a project you're proud of.",
        "answer": "I built an app once.",
        "expect_keyword_options": ["study buddy", "react", "claude", "tailwind"],
    },
    {
        "question": "What computer vision work have you done?",
        "answer": "I did some CV stuff.",
        "expect_keyword_options": ["skin", "shade", "makeup", "vision"],
    },
]


def run_eval(k: int = 2):
    passed = 0
    for case in TEST_CASES:
        context = retrieve(f"{case['question']} {case['answer']}", k=k)

        result = rehearsal_graph.invoke({
            "question": case["question"],
            "answer": case["answer"],
            "persona": "behavioral",
            "remaining_questions": [],
            "context": context,
            "strength": "",
            "next_question": "",
            "is_followup": False,
        })

        followup_text = (result["next_question"] or "").lower()
        grounded = any(kw in followup_text for kw in case["expect_keyword_options"])

        status = "PASS" if grounded else "FAIL"
        passed += grounded

        print(f"[{status}] Q: {case['question']}")
        print(f"       Retrieved context: {len(context)} chunk(s)")
        print(f"       Follow-up: {result['next_question']}")
        if not grounded:
            print(f"       Expected one of: {case['expect_keyword_options']}")
        print()

    print(f"{passed}/{len(TEST_CASES)} passed (grounded follow-ups)")


if __name__ == "__main__":
    run_eval()