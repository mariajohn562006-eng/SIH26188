from typing import Any


def clamp_score(score: float) -> float:
    """
    Keep a score between 0 and 100.
    """
    return max(0.0, min(100.0, float(score)))


def calculate_risk_level(risk_score: float) -> str:
    """
    Convert numerical risk score into a readable risk level.
    """

    if risk_score < 30:
        return "low"

    if risk_score < 60:
        return "medium"

    if risk_score < 80:
        return "high"

    return "critical"


def calculate_risk_score(
    ocr_analysis: dict[str, Any] | None = None,
    face_analysis: dict[str, Any] | None = None,
    tamper_analysis: dict[str, Any] | None = None,
    verification_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Calculate an overall risk score using the results
    produced by the different verification modules.

    Score:
        0   = lowest detected risk
        100 = highest detected risk
    """

    ocr_analysis = ocr_analysis or {}
    face_analysis = face_analysis or {}
    tamper_analysis = tamper_analysis or {}
    verification_analysis = verification_analysis or {}

    risk_score = 0.0
    risk_factors = []

    # --------------------------------------------------
    # 1. OCR / DOCUMENT TEXT
    # --------------------------------------------------

    ocr_success = ocr_analysis.get("ocr", {}).get("success", False)

    if not ocr_success:
        risk_score += 20

        risk_factors.append({
            "factor": "OCR failure",
            "impact": 20,
            "reason": "Document text could not be reliably extracted."
        })

    # --------------------------------------------------
    # 2. MRZ
    # --------------------------------------------------

    mrz_data = ocr_analysis.get("mrz", {})

    mrz_detected = mrz_data.get("detected", False)

    if not mrz_detected:
        risk_score += 20

        risk_factors.append({
            "factor": "MRZ not detected",
            "impact": 20,
            "reason": "Machine-readable zone was not detected."
        })
    else:
        parsed_mrz = mrz_data.get("parsed", {})

        if isinstance(parsed_mrz, dict):
            mrz_success = parsed_mrz.get("success", False)

            if not mrz_success:
                risk_score += 10

                risk_factors.append({
                    "factor": "MRZ parsing failure",
                    "impact": 10,
                    "reason": "MRZ was detected but could not be parsed successfully."
                })

    # --------------------------------------------------
    # 3. FACE ANALYSIS
    # --------------------------------------------------

    document_face_usable = face_analysis.get(
        "documentFaceUsable",
        False
    )

    live_photo_face_usable = face_analysis.get(
        "livePhotoFaceUsable",
        False
    )

    if not document_face_usable:
        risk_score += 15

        risk_factors.append({
            "factor": "Document face unavailable",
            "impact": 15,
            "reason": "A usable face was not detected in the document."
        })

    if not live_photo_face_usable:
        risk_score += 15

        risk_factors.append({
            "factor": "Live photo face unavailable",
            "impact": 15,
            "reason": "A usable face was not detected in the live photo."
        })

    # --------------------------------------------------
    # 4. MULTIPLE FACES
    # --------------------------------------------------

    document_face_data = face_analysis.get("document", {})
    live_photo_data = face_analysis.get("livePhoto", {})

    if document_face_data.get("status") == "multiple_faces":
        risk_score += 10

        risk_factors.append({
            "factor": "Multiple document faces",
            "impact": 10,
            "reason": "More than one face was detected in the document image."
        })

    if live_photo_data.get("status") == "multiple_faces":
        risk_score += 10

        risk_factors.append({
            "factor": "Multiple live-photo faces",
            "impact": 10,
            "reason": "More than one face was detected in the live photo."
        })

    # --------------------------------------------------
    # 5. TAMPER ANALYSIS
    # --------------------------------------------------

    tamper_detected = False

    if isinstance(tamper_analysis, dict):

        # Support several possible field names so the
        # risk engine remains compatible with tamper_detection.py.
        tamper_detected = bool(
            tamper_analysis.get("tampered", False)
            or tamper_analysis.get("tamperDetected", False)
            or tamper_analysis.get("isTampered", False)
        )

        tamper_result = tamper_analysis.get("tamperAnalysis")

        if isinstance(tamper_result, dict):
            tamper_detected = tamper_detected or bool(
                tamper_result.get("tampered", False)
                or tamper_result.get("tamperDetected", False)
                or tamper_result.get("isTampered", False)
            )

    if tamper_detected:
        risk_score += 30

        risk_factors.append({
            "factor": "Possible document tampering",
            "impact": 30,
            "reason": "Document integrity analysis reported possible manipulation."
        })

    # --------------------------------------------------
    # 6. VERIFICATION ANALYSIS
    # --------------------------------------------------

    verification_status = ""

    if isinstance(verification_analysis, dict):

        verification_status = str(
            verification_analysis.get("status", "")
        ).lower()

        nested_analysis = verification_analysis.get("analysis")

        if isinstance(nested_analysis, dict):
            verification_status = str(
                nested_analysis.get("status", verification_status)
            ).lower()

    if verification_status in {
        "failed",
        "rejected",
        "invalid",
        "suspicious"
    }:
        risk_score += 25

        risk_factors.append({
            "factor": "Verification warning",
            "impact": 25,
            "reason": f"Verification analysis returned status: {verification_status}."
        })

    # --------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------

    risk_score = clamp_score(risk_score)

    risk_level = calculate_risk_level(risk_score)

    # --------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------

    if risk_level == "low":
        recommendation = "Proceed with normal verification review."

    elif risk_level == "medium":
        recommendation = "Perform additional verification checks."

    elif risk_level == "high":
        recommendation = "Require manual review before approval."

    else:
        recommendation = "Hold verification for detailed manual investigation."

    return {
        "riskScore": round(risk_score, 2),
        "riskLevel": risk_level,
        "riskFactors": risk_factors,
        "recommendation": recommendation
    }


# Backward-compatible export used by the app entrypoint.
calculate_risk = calculate_risk_score