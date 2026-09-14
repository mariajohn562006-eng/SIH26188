from pathlib import Path
import hashlib


def calculate_file_hash(file_path: Path) -> str:
    """
    Calculate SHA-256 hash of a file.
    """
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()


def analyze_verification(document_path: Path, photo_path: Path) -> dict:
    """
    Basic verification pipeline.

    This is the foundation for the real AI/OCR pipeline.
    """

    document_hash = calculate_file_hash(document_path)
    photo_hash = calculate_file_hash(photo_path)

    document_size = document_path.stat().st_size
    photo_size = photo_path.stat().st_size

    # Basic validation for now
    document_valid = document_size > 0
    photo_valid = photo_size > 0

    if document_valid and photo_valid:
        decision = "pending"
        status = "ready"
    else:
        decision = "rejected"
        status = "invalid_files"

    return {
        "decision": decision,
        "status": status,

        "trustScore": None,
        "riskScore": None,

        "faceMatch": {
            "score": None,
            "status": "not_analyzed"
        },

        "document": {
            "status": "received" if document_valid else "invalid",
            "hash": document_hash
        },

        "photo": {
            "status": "received" if photo_valid else "invalid",
            "hash": photo_hash
        },

        "checks": {
            "ocr": "not_analyzed",
            "mrz": "not_analyzed",
            "face_match": "not_analyzed",
            "tamper_detection": "not_analyzed"
        }
    }