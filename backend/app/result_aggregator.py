from typing import Any


def determine_final_status(
    risk_score: float,
    verification_analysis: dict[str, Any] | None = None,
) -> str:
    """
    Determine the final verification status.

    This is a rule-based aggregation layer.
    """

    verification_analysis = verification_analysis or {}

    verification_status = str(
        verification_analysis.get("status", "")
    ).lower()

    if verification_status in {
        "failed",
        "rejected",
        "invalid"
    }:
        return "rejected"

    if risk_score >= 80:
        return "manual_review"

    if risk_score >= 60:
        return "manual_review"

    return "review"


def aggregate_results(
    verification_id: str,
    ocr_analysis: dict[str, Any] | None = None,
    face_analysis: dict[str, Any] | None = None,
    tamper_analysis: dict[str, Any] | None = None,
    verification_analysis: dict[str, Any] | None = None,
    risk_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Combine all backend analysis modules into one
    standardized verification result.
    """

    ocr_analysis = ocr_analysis or {}
    face_analysis = face_analysis or {}
    tamper_analysis = tamper_analysis or {}
    verification_analysis = verification_analysis or {}
    risk_analysis = risk_analysis or {}

    risk_score = float(
        risk_analysis.get("riskScore", 0)
    )

    risk_level = risk_analysis.get(
        "riskLevel",
        "unknown"
    )

    final_status = determine_final_status(
        risk_score,
        verification_analysis
    )

    # --------------------------------------------------
    # DOCUMENT STATUS
    # --------------------------------------------------

    document_data = ocr_analysis.get(
        "document",
        {}
    )

    document_ocr = ocr_analysis.get(
        "ocr",
        {}
    )

    mrz_data = ocr_analysis.get(
        "mrz",
        {}
    )

    # --------------------------------------------------
    # FACE STATUS
    # --------------------------------------------------

    document_face_usable = face_analysis.get(
        "documentFaceUsable",
        False
    )

    live_photo_face_usable = face_analysis.get(
        "livePhotoFaceUsable",
        False
    )

    face_ready = face_analysis.get(
        "readyForBiometricReview",
        False
    )

    # --------------------------------------------------
    # TAMPER STATUS
    # --------------------------------------------------

    tamper_detected = bool(
        tamper_analysis.get("tampered", False)
        or tamper_analysis.get("tamperDetected", False)
        or tamper_analysis.get("isTampered", False)
    )

    nested_tamper = tamper_analysis.get(
        "tamperAnalysis"
    )

    if isinstance(nested_tamper, dict):
        tamper_detected = tamper_detected or bool(
            nested_tamper.get("tampered", False)
            or nested_tamper.get("tamperDetected", False)
            or nested_tamper.get("isTampered", False)
        )

    # --------------------------------------------------
    # VERIFICATION STATUS
    # --------------------------------------------------

    verification_status = verification_analysis.get(
        "status",
        "unknown"
    )

    # --------------------------------------------------
    # BUILD FINAL RESULT
    # --------------------------------------------------

    return {
        "verificationId": verification_id,

        "status": final_status,

        "risk": {
            "score": round(risk_score, 2),
            "level": risk_level,
            "recommendation": risk_analysis.get(
                "recommendation",
                "Manual review recommended."
            ),
            "factors": risk_analysis.get(
                "riskFactors",
                []
            )
        },

        "document": {
            "filename": document_data.get(
                "filename"
            ),
            "width": document_data.get(
                "width"
            ),
            "height": document_data.get(
                "height"
            ),
            "format": document_data.get(
                "format"
            ),
            "ocrSuccessful": document_ocr.get(
                "success",
                False
            ),
            "mrzDetected": mrz_data.get(
                "detected",
                False
            )
        },

        "faceAnalysis": {
            "documentFaceUsable": document_face_usable,
            "livePhotoFaceUsable": live_photo_face_usable,
            "readyForBiometricReview": face_ready
        },

        "tamperAnalysis": {
            "tamperingDetected": tamper_detected
        },

        "verificationAnalysis": {
            "status": verification_status
        }
    }


# Backward-compatible export used by the app entrypoint.
aggregate_result = aggregate_results