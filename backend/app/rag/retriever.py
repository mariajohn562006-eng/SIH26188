from pathlib import Path
import json
import re
from typing import Any


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

RAG_ROOT = Path(__file__).resolve().parent
DATA_DIR = RAG_ROOT / "data"

CHUNKS_FILE = DATA_DIR / "knowledge_chunks.json"


# ---------------------------------------------------------
# Text processing
# ---------------------------------------------------------

def normalize_text(text: str) -> str:
    """
    Normalize text for keyword-based retrieval.
    """

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def tokenize(text: str) -> set[str]:
    """
    Convert text into a set of searchable words.
    """

    normalized = normalize_text(text)

    if not normalized:
        return set()

    return set(normalized.split())


# ---------------------------------------------------------
# Load chunks
# ---------------------------------------------------------

def load_chunks() -> list[dict[str, Any]]:
    """
    Load prepared knowledge chunks from JSON.
    """

    if not CHUNKS_FILE.exists():
        print(
            "WARNING: RAG knowledge chunks file not found:",
            CHUNKS_FILE
        )

        return []

    try:
        with CHUNKS_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

    except Exception as error:
        print(
            "WARNING: Could not load RAG knowledge chunks:",
            error
        )

        return []

    if not isinstance(data, list):
        print(
            "WARNING: RAG knowledge chunks must be a list."
        )

        return []

    return data


# ---------------------------------------------------------
# Calculate relevance
# ---------------------------------------------------------

def calculate_relevance(
    query: str,
    chunk_text: str
) -> float:
    """
    Calculate a simple keyword-based relevance score.

    This is intentionally lightweight for the first
    RAG implementation. A vector embedding retriever
    can be added later.
    """

    query_words = tokenize(query)
    chunk_words = tokenize(chunk_text)

    if not query_words or not chunk_words:
        return 0.0

    matched_words = query_words.intersection(
        chunk_words
    )

    if not matched_words:
        return 0.0

    score = (
        len(matched_words)
        / len(query_words)
    ) * 100

    return round(score, 2)


# ---------------------------------------------------------
# Retrieve relevant chunks
# ---------------------------------------------------------

def retrieve(
    query: str,
    top_k: int = 3
) -> list[dict[str, Any]]:
    """
    Retrieve the most relevant knowledge chunks.
    """

    if not query or not query.strip():
        return []

    if top_k <= 0:
        return []

    chunks = load_chunks()

    if not chunks:
        return []

    results = []

    for chunk in chunks:
        chunk_text = str(
            chunk.get("text", "")
        )

        if not chunk_text:
            continue

        score = calculate_relevance(
            query,
            chunk_text
        )

        if score <= 0:
            continue

        results.append(
            {
                "id": chunk.get("id"),
                "source": chunk.get("source"),
                "chunkIndex": chunk.get(
                    "chunkIndex",
                    0
                ),
                "text": chunk_text,
                "score": score,
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:top_k]


# ---------------------------------------------------------
# Retrieve with minimum relevance
# ---------------------------------------------------------

def retrieve_relevant(
    query: str,
    top_k: int = 3,
    minimum_score: float = 10.0
) -> list[dict[str, Any]]:
    """
    Retrieve chunks and remove results below
    the minimum relevance score.
    """

    results = retrieve(
        query=query,
        top_k=top_k
    )

    return [
        result
        for result in results
        if result["score"] >= minimum_score
    ]


# ---------------------------------------------------------
# Build context
# ---------------------------------------------------------

def build_context(
    results: list[dict[str, Any]]
) -> str:
    """
    Combine retrieved chunks into a context string.
    """

    if not results:
        return ""

    context_parts = []

    for result in results:
        source = result.get(
            "source",
            "unknown"
        )

        text = result.get(
            "text",
            ""
        )

        context_parts.append(
            f"[Source: {source}]\n{text}"
        )

    return "\n\n".join(context_parts)


# ---------------------------------------------------------
# Main retrieval helper
# ---------------------------------------------------------

def search_knowledge(
    query: str,
    top_k: int = 3
) -> dict[str, Any]:
    """
    Search the RAG knowledge base and return
    both retrieved chunks and combined context.
    """

    results = retrieve_relevant(
        query=query,
        top_k=top_k
    )

    context = build_context(results)

    return {
        "query": query,
        "results": results,
        "resultCount": len(results),
        "context": context,
    }


# ---------------------------------------------------------
# Command-line test
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("ByteMind RAG Retriever Test")
    print("=" * 60)

    query = input(
        "Enter a verification question: "
    ).strip()

    if not query:
        print(
            "No query provided."
        )

    else:
        result = search_knowledge(
            query=query,
            top_k=3
        )

        print()
        print(
            "Retrieved results:",
            result["resultCount"]
        )

        for index, item in enumerate(
            result["results"],
            start=1
        ):
            print()
            print(
                f"Result {index}"
            )
            print(
                "Source:",
                item["source"]
            )
            print(
                "Score:",
                item["score"]
            )
            print(
                "Text:",
                item["text"]
            )

        print()
        print("=" * 60)