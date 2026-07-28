"""
Track A retrieval — now with a relevance threshold, so weak/irrelevant
matches (like an unrelated "Study Buddy" chunk) get filtered out instead
of always being forced into the context.
"""

import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

_collection = None

# Chroma's default distance is squared L2 — LOWER means more similar.
# This threshold is a starting point, not a scientifically derived
# number — tune it by testing real queries and seeing what distance
# genuinely-relevant vs irrelevant matches land at for your data.
RELEVANCE_THRESHOLD = 1.0


def _chunk_file(path: str, source_label: str):
    with open(path, "r") as f:
        text = f.read()
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    chunks = splitter.split_text(text)
    metadata = [{"source": source_label} for _ in chunks]
    return chunks, metadata


def _build_index():
    client = chromadb.PersistentClient(path="./chroma_db")
    embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = client.get_or_create_collection(
        name="rehearsal_docs", embedding_function=embedder
    )
    if collection.count() == 0:
        resume_chunks, resume_meta = _chunk_file("data/resume.txt", "resume")
        jd_chunks, jd_meta = _chunk_file("data/job_description.txt", "job_description")
        all_chunks = resume_chunks + jd_chunks
        all_meta = resume_meta + jd_meta
        all_ids = [str(i) for i in range(len(all_chunks))]
        collection.add(documents=all_chunks, metadatas=all_meta, ids=all_ids)
    return collection


def retrieve(query: str, k: int = 2) -> list:
    """
    NOW FILTERS by relevance. If nothing scores well enough, returns an
    EMPTY list rather than forcing in a weak match — the caller (agent
    follow-up generation) should treat "no context" as "stay generic"
    rather than "grab whatever's closest regardless of quality."
    """
    global _collection
    if _collection is None:
        _collection = _build_index()

    results = _collection.query(
        query_texts=[query], n_results=k, include=["documents", "distances"]
    )
    docs = results["documents"][0]
    distances = results["distances"][0]

    relevant = [doc for doc, dist in zip(docs, distances) if dist <= RELEVANCE_THRESHOLD]
    return relevant


def retrieve_with_source(query: str, k: int = 2):
    global _collection
    if _collection is None:
        _collection = _build_index()
    results = _collection.query(
        query_texts=[query], n_results=k, include=["documents", "metadatas", "distances"]
    )
    docs = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    distances = results["distances"][0]

    return [
        (doc, source, dist) for doc, source, dist in zip(docs, sources, distances)
        if dist <= RELEVANCE_THRESHOLD
    ]


if __name__ == "__main__":
    # Print actual distances so you can see what a good vs bad match
    # looks like for your data, and adjust RELEVANCE_THRESHOLD if needed.
    for query in ["computer vision projects", "weather forecast tomorrow"]:
        print(f"Query: {query}")
        for doc, source, dist in retrieve_with_source(query, k=3):
            print(f"  [{dist:.3f}] [{source}] {doc[:60]}...")
        print()
