from pathlib import Path
import json
from typing import Any


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

RAG_ROOT = Path(__file__).resolve().parent
DOCUMENTS_DIR = RAG_ROOT / "documents"
DATA_DIR = RAG_ROOT / "data"

CHUNKS_FILE = DATA_DIR / "knowledge_chunks.json"


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


# ---------------------------------------------------------
# Create required directories
# ---------------------------------------------------------

DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Read knowledge documents
# ---------------------------------------------------------

def load_documents() -> list[dict[str, str]]:
    """
    Load all .txt knowledge files from the RAG documents folder.
    """

    documents = []

    for file_path in sorted(DOCUMENTS_DIR.glob("*.txt")):
        try:
            content = file_path.read_text(
                encoding="utf-8"
            ).strip()
        except Exception as error:
            print(
                f"WARNING: Could not read RAG document "
                f"{file_path.name}: {error}"
            )
            continue

        if not content:
            print(
                f"WARNING: RAG document is empty: "
                f"{file_path.name}"
            )
            continue

        documents.append(
            {
                "source": file_path.name,
                "content": content,
            }
        )

    return documents


# ---------------------------------------------------------
# Split text into chunks
# ---------------------------------------------------------

def split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """
    Split a document into overlapping text chunks.
    """

    if not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative")

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size

        chunk_words = words[start:end]

        if not chunk_words:
            break

        chunk = " ".join(chunk_words).strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(words):
            break

        start = end - chunk_overlap

    return chunks


# ---------------------------------------------------------
# Create knowledge chunks
# ---------------------------------------------------------

def create_chunks(
    documents: list[dict[str, str]]
) -> list[dict[str, Any]]:
    """
    Convert loaded documents into searchable chunks.
    """

    chunks = []

    chunk_id = 0

    for document in documents:
        source = document["source"]
        content = document["content"]

        document_chunks = split_text(content)

        for index, chunk_text in enumerate(document_chunks):
            chunks.append(
                {
                    "id": f"chunk-{chunk_id}",
                    "source": source,
                    "chunkIndex": index,
                    "text": chunk_text,
                }
            )

            chunk_id += 1

    return chunks


# ---------------------------------------------------------
# Save chunks
# ---------------------------------------------------------

def save_chunks(
    chunks: list[dict[str, Any]]
) -> None:
    """
    Save processed knowledge chunks to JSON.
    """

    with CHUNKS_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            chunks,
            file,
            indent=2,
            ensure_ascii=False,
        )


# ---------------------------------------------------------
# Main ingestion function
# ---------------------------------------------------------

def ingest_knowledge_base() -> dict[str, Any]:
    """
    Load RAG documents, create chunks,
    and save them for retrieval.
    """

    print("=" * 60)
    print("ByteMind RAG Knowledge Ingestion")
    print("=" * 60)

    print(
        "DEBUG: RAG documents directory:",
        DOCUMENTS_DIR
    )

    documents = load_documents()

    print(
        "DEBUG: documents loaded:",
        len(documents)
    )

    if not documents:
        print(
            "WARNING: No RAG knowledge documents found."
        )

        save_chunks([])

        return {
            "success": False,
            "documents": 0,
            "chunks": 0,
            "output": str(CHUNKS_FILE),
            "message": "No knowledge documents found."
        }

    chunks = create_chunks(documents)

    print(
        "DEBUG: knowledge chunks created:",
        len(chunks)
    )

    save_chunks(chunks)

    print(
        "DEBUG: chunks saved to:",
        CHUNKS_FILE
    )

    print("=" * 60)

    return {
        "success": True,
        "documents": len(documents),
        "chunks": len(chunks),
        "output": str(CHUNKS_FILE),
        "message": "RAG knowledge base ingested successfully."
    }


# ---------------------------------------------------------
# Run directly
# ---------------------------------------------------------

if __name__ == "__main__":
    result = ingest_knowledge_base()

    print()
    print("RAG ingestion result:")
    print(json.dumps(result, indent=2))