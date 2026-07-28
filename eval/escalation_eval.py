"""
eval/escalation_eval.py — does the agent actually escalate on the RIGHT
answers and advance on the right ones? This tests classify_node +
routing directly, with no retrieval involved (context=[]) — isolating
the escalation decision from the grounding piece, which faithfulness_eval
tests separately.

Run from project root: python eval/escalation_eval.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "agents"))

from graph_session_manager import rehearsal_graph

# Each case: (question, answer, expected_is_followup)
# expected_is_followup=True means "this SHOULD trigger a follow-up"
TEST_CASES = [
    (
        "Tell me about a project you're proud of.",
        "I built an app once.",
        True,  # vague — no specifics, should escalate
    ),
    (
        "Tell me about a project you're proud of.",
        "I built Study Buddy, a React and Tailwind study app powered by "
        "the Claude API, with quiz, flashcard, and pomodoro panels. The "
        "hardest part was managing state across the different panels.",
        False,  # specific and detailed — should advance
    ),
    (
        "Describe a time you disagreed with a teammate.",
        "I don't really remember, it was fine I guess.",
        True,  # vague, dismissive — should escalate
    ),
    (
        "Describe a time you disagreed with a teammate.",
        "We disagreed on whether to use REST or GraphQL for a project. "
        "I proposed we prototype both for a day and compare, which we "
        "did, and the data settled the disagreement.",
        False,  # concrete example with resolution — should advance
    ),
    (
        "What are your weaknesses?",
        "idk",
        True,  # clearly too vague
    ),
]


def run_eval():
    passed = 0
    for question, answer, expected in TEST_CASES:
        result = rehearsal_graph.invoke({
            "question": question,
            "answer": answer,
            "persona": "behavioral",
            "remaining_questions": ["placeholder next question"],
            "context": [],
            "strength": "",
            "next_question": "",
            "is_followup": False,
        })

        actual = result["is_followup"]
        ok = actual == expected
        passed += ok

        status = "PASS" if ok else "FAIL"
        print(f"[{status}] \"{answer[:50]}...\"")
        if not ok:
            print(f"       expected is_followup={expected}, got {actual} "
                  f"(classified as: {result['strength']})")

    print(f"\n{passed}/{len(TEST_CASES)} passed")


if __name__ == "__main__":
    run_eval()