"""
Standalone text-loop test — updated for next_question()'s new 3-value
return (next_question, is_followup, strength).
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "agents"))

from session_manager import next_question

QUESTIONS = [
    "Tell me about a project you're proud of and why.",
    "Describe a time you disagreed with a teammate.",
    "What are your weaknesses?",
]


def main():
    print("=== Rehearsal session (standalone test) ===\n")

    remaining = QUESTIONS.copy()
    current_question = remaining.pop(0)

    while current_question:
        print(f"Q: {current_question}")
        answer = input("Your answer: ")

        next_q, is_followup, strength = next_question(current_question, answer, remaining)

        print(f"(classified as: {strength})")
        if is_followup:
            print("(digging deeper on the same topic)\n")
        else:
            print("(moving on)\n")
            if remaining:
                remaining.pop(0)
        current_question = next_q

    print("Session complete.")


if __name__ == "__main__":
    main()