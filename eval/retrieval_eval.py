"""
Track A's retrieval eval — the beginning of a real eval harness.

The idea: for each test query, you already know (by reading the source
documents yourself) roughly what SHOULD come back. This script checks
whether retrieve() actually returns that, instead of you eyeballing
results by hand every time you change something.

This is intentionally simple — a real eval framework (Ragas, DeepEval)
does this more rigorously later. Understanding why you'd want this
FIRST is the point before reaching for a library that does it for you.
"""

import sys
import os

# Allows importing retrieve.py from the parent folder.
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from retrieve import retrieve_with_source


# Each test case: a query, and a keyword you'd expect somewhere in the
# top results if retrieval is working correctly. You write these by
# reading the source docs yourself and deciding what SHOULD come back —
# this is "ground truth" you're defining, same idea as labeling data.
TEST_CASES = [
    {
        "query": "What computer vision projects have they built?",
        "expect_keyword": "Skin Shade",
        "expect_source": "resume",
    },
    {
        "query": "What frontend technologies do they know?",
        "expect_keyword": "React",
        "expect_source": "resume",
    },
    {
        "query": "What LangChain or vector search experience do they have?",
        "expect_keyword": "LangChain",
        "expect_source": "job_description",
        # NOTE: we already saw this one FAIL in manual testing — the
        # LangChain bullet didn't surface in the top 3. Keeping it here
        # on purpose, as a known failing case to track and improve,
        # rather than deleting it because it's inconvenient.
    },
    {
        "query": "What are the Python requirements for this role?",
        "expect_keyword": "Python",
        "expect_source": "job_description",
    },
    {
        "query": "What did they build for university coursework?",
        "expect_keyword": "quiz",
        "expect_source": "resume",
    },
]


def run_eval(k: int = 3):
    passed = 0
    for case in TEST_CASES:
        results = retrieve_with_source(case["query"], k=k)
        combined_text = " ".join(doc for doc, source in results).lower()
        sources_returned = [source for doc, source in results]

        keyword_found = case["expect_keyword"].lower() in combined_text
        source_found = case["expect_source"] in sources_returned

        ok = keyword_found and source_found
        passed += ok

        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {case['query']}")
        if not ok:
            print(f"       expected keyword '{case['expect_keyword']}' "
                  f"from source '{case['expect_source']}'")
            print(f"       got sources: {sources_returned}")

    print(f"\n{passed}/{len(TEST_CASES)} passed")


if __name__ == "__main__":
    run_eval()