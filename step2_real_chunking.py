"""
Step 2: real chunking using LangChain's text splitter.

Instead of cutting every N characters blindly (Step 1), this tries to
split on paragraph breaks first, then sentences, only falling back to
a hard cut if a piece is still too big. This is the "boring plumbing"
LangChain saves you from writing yourself.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_resume(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def real_chunk(text: str, chunk_size: int = 300, overlap: int = 30) -> list[str]:
    """
    RecursiveCharacterTextSplitter tries a list of separators in order:
    "\n\n" (paragraph breaks) first, then "\n" (line breaks), then " "
    (word breaks), only cutting mid-word as an absolute last resort.

    `overlap` means each chunk repeats a few characters from the end of
    the previous one — this helps when an important fact sits right on
    a chunk boundary, so it doesn't get orphaned in a way that loses
    context. Small (like 30) is enough to start.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
    )
    return splitter.split_text(text)


if __name__ == "__main__":
    resume_text = load_resume("data/resume.txt")
    chunks = real_chunk(resume_text)

    print(f"Split into {len(chunks)} chunks.\n")
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i} ---")
        print(chunk)
        print()
