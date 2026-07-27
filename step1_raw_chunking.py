"""
Step 1: raw chunking, no libraries.

Goal: understand what a "chunk" actually is before LangChain does it for
you. Run this and read the output — that's the whole exercise.
"""


def load_resume(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def naive_chunk(text: str, chunk_size: int = 300) -> list[str]:
    """
    The simplest possible chunking: just cut every `chunk_size` characters.
    This is intentionally bad — it will cut mid-sentence sometimes. You'll
    see why that's a problem when you read the output. Real chunking
    (which LangChain gives you for free) tries to split on paragraph or
    sentence boundaries instead. Understanding why naive chunking is bad
    is the actual point of this step.
    """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


if __name__ == "__main__":
    resume_text = load_resume("data/resume.txt")
    chunks = naive_chunk(resume_text)

    print(f"Split into {len(chunks)} chunks.\n")
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i} ---")
        print(chunk)
        print()
