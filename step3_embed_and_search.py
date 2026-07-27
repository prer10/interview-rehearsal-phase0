"""
Step 3: embed the chunks and actually search them.

This is the real "R" in RAG. Two new ideas here:

1. Embedding: sentence-transformers turns each chunk into a list of ~384
   numbers (a vector). This runs fully LOCALLY on your machine — free,
   no API call, no internet needed once the model is downloaded once.

2. Chroma: a vector database. You hand it chunks, it embeds and stores
   them for you, and you can then ask "which stored chunks are closest
   in meaning to this new query?" That similarity search is the entire
   trick behind RAG.
"""

import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_resume(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 30) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    return splitter.split_text(text)


def build_index(chunks: list[str]):
    """
    Creates an in-memory Chroma collection, embeds every chunk using a
    free local model, and stores them. `PersistentClient` would save this
    to disk so you don't re-embed every run — using the plain in-memory
    client here first so the mechanics are visible each time you run it.
    """
    client = chromadb.Client()

    # This model runs locally, downloads once (~80MB), then works offline.
    embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    collection = client.create_collection(name="resume", embedding_function=embedder)

    # Chroma needs a unique string ID per chunk — just using the index.
    collection.add(
        documents=chunks,
        ids=[str(i) for i in range(len(chunks))],
    )
    return collection


def retrieve(collection, query: str, k: int = 2) -> list[str]:
    """
    This is the function Sammy's agent code will eventually call. Notice
    the signature — a question in, a list of relevant text chunks out.
    Everything about HOW it works is hidden inside this function.
    """
    results = collection.query(query_texts=[query], n_results=k)
    return results["documents"][0]  # top-k chunks, most relevant first


if __name__ == "__main__":
    resume_text = load_resume("data/resume.txt")
    chunks = chunk_text(resume_text)
    collection = build_index(chunks)

    # Try a few different queries and see what gets retrieved.
    test_queries = [
        "What computer vision projects have they built?",
        "What frontend technologies do they know?",
        "What did they build for coursework?",
    ]

    for query in test_queries:
        print(f"QUERY: {query}")
        results = retrieve(collection, query, k=2)
        for r in results:
            print(f"  -> {r[:100]}...")
        print()