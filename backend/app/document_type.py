from pathlib import Path
from typing import Any


def detect_document_type(
    ocr_text: str = "",
    filename: str = ""
) -> dict[str, Any]:
    """
    Detect the likely document type using OCR text and filename.

    This is a lightweight rule-based detector.
    It can be replaced later with an ML/document-classification model.
    """

    text = (ocr_text or "").upper()
    name = Path(filename or "").name.upper()

    # =====================================================
    # PASSPORT
    # =====================================================

    passport_keywords = [
        "PASSPORT",
        "PASSEPORT",
        "REPUBLIC OF",
        "NATIONALITY",
        "DATE OF BIRTH",
        "PLACE OF BIRTH",
        "DATE OF ISSUE",
        "DATE OF EXPIRY",
    ]

    passport_score = 0

    for keyword in passport_keywords:
        if keyword in text:
            passport_score += 1

    # A passport filename can also provide a small signal.
    if "PASSPORT" in name:
        passport_score += 2

    if passport_score >= 2:
        return {
            "type": "passport",
            "displayName": "Passport",
            "confidence": "medium",
            "reason": "Passport-related information was detected in the document."
        }

    # =====================================================
    # DRIVER LICENSE
    # =====================================================

    driver_license_keywords = [
        "DRIVER LICENSE",
        "DRIVER'S LICENSE",
        "DRIVING LICENCE",
        "DRIVING LICENSE",
        "DL NO",
        "DL NUMBER",
        "LICENSE NUMBER",
        "LICENCE NUMBER",
    ]

    driver_license_score = 0

    for keyword in driver_license_keywords:
        if keyword in text:
            driver_license_score += 1

    if "DRIVER" in name or "LICENSE" in name or "LICENCE" in name:
        driver_license_score += 1

    if driver_license_score >= 1:
        return {
            "type": "drivers_license",
            "displayName": "Driver's License",
            "confidence": "medium",
            "reason": "Driver's license-related information was detected in the document."
        }

    # =====================================================
    # NATIONAL ID
    # =====================================================

    national_id_keywords = [
        "NATIONAL ID",
        "NATIONAL IDENTIFICATION",
        "IDENTITY CARD",
        "IDENTIFICATION CARD",
        "ID CARD",
        "IDENTITY NUMBER",
    ]

    national_id_score = 0

    for keyword in national_id_keywords:
        if keyword in text:
            national_id_score += 1

    if "ID" in name or "IDENTITY" in name:
        national_id_score += 1

    if national_id_score >= 1:
        return {
            "type": "national_id",
            "displayName": "National ID",
            "confidence": "medium",
            "reason": "Identity-card-related information was detected in the document."
        }

    # =====================================================
    # UNKNOWN
    # =====================================================

    return {
        "type": "unknown",
        "displayName": "Unknown Document",
        "confidence": "low",
        "reason": "The document type could not be determined from the available information."
    }