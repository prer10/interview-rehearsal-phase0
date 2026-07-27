"""
Track A retrieval — now indexes BOTH the resume and the job description,
and persists the index to disk so you're not re-embedding on every run.

Same public interface as before: retrieve(query, k) -> list[str].
Sammy's code doesn't need to change at all.
"""

import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

_collection = None


def _chunk_file(path: str, source_label: str):
    """
    Returns (chunks, metadata) — metadata tags each chunk with which
    document it came from, so later you can trace a retrieved chunk
    back to "this came from the resume" vs "this came from the JD."
    That traceability is exactly what a faithfulness eval checks later.
    """
    with open(path, "r") as f:
        text = f.read()
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    chunks = splitter.split_text(text)
    metadata = [{"source": source_label} for _ in chunks]
    return chunks, metadata


def _build_index():
    # PersistentClient writes the index to a local folder ("./chroma_db")
    # so re-running the script reuses the existing index instead of
    # re-embedding everything from scratch every time.
    client = chromadb.PersistentClient(path="./chroma_db")
    embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # get_or_create avoids an error if the index already exists from a
    # previous run.
    collection = client.get_or_create_collection(
        name="rehearsal_docs", embedding_function=embedder
    )

    # Only add documents if the collection is empty — otherwise every run
    # would keep re-adding duplicates.
    if collection.count() == 0:
        resume_chunks, resume_meta = _chunk_file("data/resume.txt", "resume")
        jd_chunks, jd_meta = _chunk_file("data/job_description.txt", "job_description")

        all_chunks = resume_chunks + jd_chunks
        all_meta = resume_meta + jd_meta
        all_ids = [str(i) for i in range(len(all_chunks))]

        collection.add(documents=all_chunks, metadatas=all_meta, ids=all_ids)

    return collection


def retrieve(query: str, k: int = 2) -> list[str]:
    global _collection
    if _collection is None:
        _collection = _build_index()
    results = _collection.query(query_texts=[query], n_results=k)
    return results["documents"][0]


def retrieve_with_source(query: str, k: int = 2):
    """
    Same as retrieve(), but also returns which document each chunk came
    from. Useful for your eval harness later — you can check "did this
    follow-up actually cite something from the JD, or is it making up a
    requirement that isn't there?"
    """
    global _collection
    if _collection is None:
        _collection = _build_index()
    results = _collection.query(query_texts=[query], n_results=k)
    docs = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    return list(zip(docs, sources))


if __name__ == "__main__":
    print("Query: What LangChain or vector search experience do they have?\n")
    for doc, source in retrieve_with_source(
        "What LangChain or vector search experience do they have?", k=3
    ):
        print(f"[{source}] {doc[:100]}...")