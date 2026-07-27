"""
The real retrieve() — same interface as the placeholder stub, so Sammy's
session_manager.py can import this with zero changes on their end.

This wraps everything from step3 into the one function that matters:
retrieve(query, k) -> list of relevant text chunks.
"""

import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

_collection = None  # built once, reused across calls


def _load_and_index(resume_path: str = "data/resume.txt"):
    with open(resume_path, "r") as f:
        text = f.read()

    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    chunks = splitter.split_text(text)

    client = chromadb.Client()
    embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = client.create_collection(name="resume", embedding_function=embedder)
    collection.add(documents=chunks, ids=[str(i) for i in range(len(chunks))])
    return collection


def retrieve(query: str, k: int = 2) -> list[str]:
    """
    Same signature as the stub Sammy is building against:
    retrieve(query: str, k: int) -> list[str]
    """
    global _collection
    if _collection is None:
        _collection = _load_and_index()
    results = _collection.query(query_texts=[query], n_results=k)
    return results["documents"][0]


if __name__ == "__main__":
    print(retrieve("What computer vision projects have they built?"))