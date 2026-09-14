from pathlib import Path
from datetime import datetime, timezone


def run_verification(
    verification_id: str,
    document_path: Path,
    photo_path: Path,
    document_type: str | None = None,
):
    """
    Main ByteMind verification pipeline.

    Each analysis stage will be connected here as the
    backend is expanded.
    """

    # --------------------------------------------------
    # Stage 1: Validate input files
    # --------------------------------------------------

    document_exists = document_path.exists()
    photo_exists = photo_path.exists()

    if not document_exists:
        raise FileNotFoundError(
            "Document file was not found."
        )

    if not photo_exists:
        raise FileNotFoundError(
            "Live photo file was not found."
        )

    # --------------------------------------------------
    # Stage 2: OCR
    # --------------------------------------------------

    ocr_result = run_ocr(
        document_path
    )

    # --------------------------------------------------
    # Stage 3: MRZ parsing
    # --------------------------------------------------

    mrz_result = parse_mrz(
        ocr_result
    )

    # --------------------------------------------------
    # Stage 4: Face matching
    # --------------------------------------------------

    face_result = match_face(
        document_path,
        photo_path
    )

    # --------------------------------------------------
    # Stage 5: Tamper detection
    # --------------------------------------------------

    tamper_result = detect_tampering(
        document_path
    )

    # --------------------------------------------------
    # Stage 6: Risk calculation
    # --------------------------------------------------

    risk_result = calculate_risk(
        ocr_result,
        mrz_result,
        face_result,
        tamper_result
    )

    # --------------------------------------------------
    # Final result
    # --------------------------------------------------

    return {
        "id": verification_id,
        "status": "completed",
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "document_type": document_type,

        "ocr": ocr_result,
        "mrz": mrz_result,
        "face_match": face_result,
        "tamper_detection": tamper_result,
        "risk": risk_result,

        "decision": risk_result["decision"],
        "trust_score": risk_result["trust_score"],
        "risk_score": risk_result["risk_score"],
    }


# ======================================================
# OCR
# ======================================================

def run_ocr(document_path: Path):
    """
    Extract text from the uploaded document.

    OCR engine will be connected in a later step.
    """

    return {
        "status": "pending",
        "text": "",
        "confidence": 0,
        "source": str(document_path.name),
    }


# ======================================================
# MRZ
# ======================================================

def parse_mrz(ocr_result):
    """
    Parse Machine Readable Zone information.

    Real MRZ parsing will be connected later.
    """

    return {
        "status": "pending",
        "document_number": None,
        "date_of_birth": None,
        "date_of_expiry": None,
        "nationality": None,
        "valid": False,
    }


# ======================================================
# Face matching
# ======================================================

def match_face(
    document_path: Path,
    photo_path: Path,
):
    """
    Compare the face on the identity document
    against the live photo.

    Real face recognition will be connected later.
    """

    return {
        "status": "pending",
        "score": 0,
        "matched": False,
    }


# ======================================================
# Tamper detection
# ======================================================

def detect_tampering(document_path: Path):
    """
    Check whether the uploaded document shows
    signs of manipulation or tampering.

    Real image/document analysis will be connected later.
    """

    return {
        "status": "pending",
        "tampered": False,
        "confidence": 0,
        "signals": [],
    }


# ======================================================
# Risk engine
# ======================================================

def calculate_risk(
    ocr_result,
    mrz_result,
    face_result,
    tamper_result,
):
    """
    Combine verification signals into a final
    risk/decision result.

    The production scoring rules will be added later.
    """

    # No real analysis has been connected yet,
    # so don't approve or reject the identity.
    return {
        "decision": "pending",
        "risk_score": None,
        "trust_score": None,
        "reasons": [
            "Verification analysis is not fully configured yet."
        ],
    }