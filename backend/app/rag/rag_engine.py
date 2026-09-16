from typing import Any

from app.rag.retriever import search_knowledge


# ---------------------------------------------------------
# Build verification query
# ---------------------------------------------------------

def build_verification_query(
    ocr_analysis: dict[str, Any] | None = None,
    face_analysis: dict[str, Any] | None = None,
    tamper_analysis: dict[str, Any] | None = None,
    verification_analysis: dict[str, Any] | None = None,
) -> str:
    """
    Build a search query from the results produced by
    ByteMind's existing verification modules.
    """

    ocr_analysis = ocr_analysis or {}
    face_analysis = face_analysis or {}
    tamper_analysis = tamper_analysis or {}
    verification_analysis = verification_analysis or {}

    findings = []

    # -----------------------------------------------------
    # OCR
    # -----------------------------------------------------

    ocr_result = ocr_analysis.get("ocr", {})

    if not ocr_result.get("success", False):
        findings.append(
            "OCR document text extraction failed"
        )

    # -----------------------------------------------------
    # MRZ
    # -----------------------------------------------------

    mrz_result = ocr_analysis.get("mrz", {})

    if not mrz_result.get("detected", False):
        findings.append(
            "MRZ not detected"
        )
    else:
        parsed_mrz = mrz_result.get(
            "parsed",
            {}
        )

        if isinstance(parsed_mrz, dict):
            if not parsed_mrz.get(
                "success",
                False
            ):
                findings.append(
                    "MRZ parsing failed"
                )

    # -----------------------------------------------------
    # Face analysis
    # -----------------------------------------------------

    if not face_analysis.get(
        "documentFaceUsable",
        False
    ):
        findings.append(
            "document face unavailable"
        )

    if not face_analysis.get(
        "livePhotoFaceUsable",
        False
    ):
        findings.append(
            "live photo face unavailable"
        )

    document_face = face_analysis.get(
        "document",
        {}
    )

    live_photo = face_analysis.get(
        "livePhoto",
        {}
    )

    if isinstance(document_face, dict):
        if document_face.get(
            "status"
        ) == "multiple_faces":
            findings.append(
                "multiple faces in document"
            )

    if isinstance(live_photo, dict):
        if live_photo.get(
            "status"
        ) == "multiple_faces":
            findings.append(
                "multiple faces in live photo"
            )

    # -----------------------------------------------------
    # Tamper analysis
    # -----------------------------------------------------

    tampered = bool(
        tamper_analysis.get(
            "tampered",
            False
        )
        or tamper_analysis.get(
            "tamperDetected",
            False
        )
        or tamper_analysis.get(
            "isTampered",
            False
        )
    )

    nested_tamper = tamper_analysis.get(
        "tamperAnalysis"
    )

    if isinstance(
        nested_tamper,
        dict
    ):
        tampered = tampered or bool(
            nested_tamper.get(
                "tampered",
                False
            )
            or nested_tamper.get(
                "tamperDetected",
                False
            )
            or nested_tamper.get(
                "isTampered",
                False
            )
        )

    if tampered:
        findings.append(
            "possible document tampering"
        )

    # -----------------------------------------------------
    # Verification status
    # -----------------------------------------------------

    verification_status = str(
        verification_analysis.get(
            "status",
            ""
        )
    ).lower()

    if verification_status:
        findings.append(
            f"verification status {verification_status}"
        )

    # -----------------------------------------------------
    # Build final query
    # -----------------------------------------------------

    if not findings:
        return (
            "document verification rules "
            "and normal verification procedure"
        )

    return (
        "document verification "
        + " ".join(findings)
    )


# ---------------------------------------------------------
# Generate RAG explanation
# ---------------------------------------------------------

def generate_rag_explanation(
    query: str,
    results: list[dict[str, Any]],
) -> str:
    """
    Create a simple evidence-grounded explanation
    from retrieved knowledge chunks.
    """

    if not results:
        return (
            "No relevant knowledge was found in "
            "the ByteMind verification knowledge base."
        )

    explanations = []

    for result in results:

        source = result.get(
            "source",
            "unknown source"
        )

        text = result.get(
            "text",
            ""
        ).strip()

        if not text:
            continue

        explanations.append(
            f"According to {source}: {text}"
        )

    if not explanations:
        return (
            "Relevant knowledge was retrieved, "
            "but no explanation could be generated."
        )

    return "\n\n".join(
        explanations
    )


# ---------------------------------------------------------
# Main RAG analysis
# ---------------------------------------------------------

def analyze_with_rag(
    ocr_analysis: dict[str, Any] | None = None,
    face_analysis: dict[str, Any] | None = None,
    tamper_analysis: dict[str, Any] | None = None,
    verification_analysis: dict[str, Any] | None = None,
    top_k: int = 3,
) -> dict[str, Any]:
    """
    Run the ByteMind RAG knowledge retrieval process.
    """

    query = build_verification_query(
        ocr_analysis=ocr_analysis,
        face_analysis=face_analysis,
        tamper_analysis=tamper_analysis,
        verification_analysis=verification_analysis,
    )

    print(
        "DEBUG: RAG query:",
        query
    )

    search_result = search_knowledge(
        query=query,
        top_k=top_k,
    )

    results = search_result.get(
        "results",
        []
    )

    explanation = generate_rag_explanation(
        query=query,
        results=results,
    )

    return {
        "enabled": True,
        "query": query,
        "resultCount": len(results),
        "sources": [
            {
                "source": result.get(
                    "source"
                ),
                "score": result.get(
                    "score"
                ),
            }
            for result in results
        ],
        "retrievedKnowledge": results,
        "context": search_result.get(
            "context",
            ""
        ),
        "explanation": explanation,
    }


# ---------------------------------------------------------
# Simple RAG query
# ---------------------------------------------------------

def ask_rag(
    query: str,
    top_k: int = 3,
) -> dict[str, Any]:
    """
    Directly query the ByteMind RAG knowledge base.
    """

    if not query or not query.strip():
        return {
            "enabled": True,
            "query": query,
            "resultCount": 0,
            "sources": [],
            "retrievedKnowledge": [],
            "context": "",
            "explanation": (
                "No query was provided."
            ),
        }

    search_result = search_knowledge(
        query=query,
        top_k=top_k,
    )

    results = search_result.get(
        "results",
        []
    )

    explanation = generate_rag_explanation(
        query=query,
        results=results,
    )

    return {
        "enabled": True,
        "query": query,
        "resultCount": len(results),
        "sources": [
            {
                "source": result.get(
                    "source"
                ),
                "score": result.get(
                    "score"
                ),
            }
            for result in results
        ],
        "retrievedKnowledge": results,
        "context": search_result.get(
            "context",
            ""
        ),
        "explanation": explanation,
    }


# ---------------------------------------------------------
# Command-line test
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("ByteMind RAG Engine Test")
    print("=" * 60)

    query = input(
        "Enter a question: "
    ).strip()

    result = ask_rag(
        query=query,
        top_k=3,
    )

    print()
    print(
        "Results found:",
        result["resultCount"]
    )

    print()
    print("Explanation:")
    print(
        result["explanation"]
    )

    print()
    print("=" * 60)