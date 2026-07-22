"""
TRACK A — retrieval stub.

Fill this in. Track B will import `retrieve()` and treat it as a black
box, so make sure the function signature below stays stable even while
you're rewriting the internals.
"""

from typing import List


def retrieve(query: str, k: int = 3) -> List[str]:
    """
    Given a query (e.g. "what should I probe about their last project?"),
    return the top-k most relevant chunks from the resume + job description.

    Steps to build this for real (in order):
    1. Load and chunk the resume + JD (see ingest.py — build that first)
    2. Embed all chunks once, embed the incoming query each call
    3. Compute similarity (cosine similarity is fine to start) between
       the query embedding and every chunk embedding
    4. Return the text of the top-k highest-scoring chunks

    For now this returns a placeholder so Track B can build against a
    stable interface before your real implementation is ready.
    """
    return [f"[placeholder context for query: {query}]"] * k


if __name__ == "__main__":
    # Quick manual test — run this file directly to sanity check
    results = retrieve("tell me about a challenging project", k=2)
    for r in results:
        print(r)
