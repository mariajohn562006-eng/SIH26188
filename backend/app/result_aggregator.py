from typing import Any


# =========================================================
# RESULT AGGREGATOR
# =========================================================

def aggregate_results(
    ocr_analysis: dict[str, Any] | None = None,
    face_analysis: dict[str, Any] | None = None,
    tamper_analysis: dict[str, Any] | None = None,
    verification_analysis: dict[str, Any] | None = None,
    risk_analysis: dict[str, Any] | None = None,
    document_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Combine OCR, MRZ, face, tampering, verification,
    and risk-analysis results into one final response.

    Final decision rules:

        VERIFIED
            All required checks pass.

        SUSPICIOUS
            Exactly one important verification check fails.

        DANGER
            Two or more important checks fail,
            OR document tampering is detected.
    """

    # =====================================================
    # NORMALIZE INPUTS
    # =====================================================

    ocr_analysis = ocr_analysis or document_analysis or {}
    face_analysis = face_analysis or {}
    tamper_analysis = tamper_analysis or {}
    verification_analysis = verification_analysis or {}
    risk_analysis = risk_analysis or {}
    face_analysis = face_analysis or {}
    tamper_analysis = tamper_analysis or {}
    verification_analysis = verification_analysis or {}
    risk_analysis = risk_analysis or {}

    # =====================================================
    # DOCUMENT / OCR
    # =====================================================

    document = ocr_analysis.get(
        "document",
        {},
    )

    document_type = ocr_analysis.get(
        "documentType",
        {},
    )

    document_ocr = ocr_analysis.get(
        "ocr",
        {},
    )

    mrz_data = ocr_analysis.get(
        "mrz",
        {},
    )

    filename = document.get(
        "filename",
        "",
    )

    width = document.get(
        "width",
        0,
    )

    height = document.get(
        "height",
        0,
    )

    file_format = document.get(
        "format",
        "",
    )

    document_type_value = document_type.get(
        "type",
        "unknown",
    )

    document_display_name = document_type.get(
        "displayName",
        "Unknown Document",
    )

    document_type_confidence = document_type.get(
        "confidence",
        "low",
    )

    ocr_success = document_ocr.get(
        "success",
        False,
    )

    ocr_text = document_ocr.get(
        "text",
        "",
    )

    # =====================================================
    # MRZ
    # =====================================================

    mrz_required = mrz_data.get(
        "required",
        False,
    )

    mrz_detected = mrz_data.get(
        "detected",
        False,
    )

    mrz_status = mrz_data.get(
        "status",
        "not required",
    )

    mrz_parsed = mrz_data.get(
        "parsed",
        {},
    )

    # =====================================================
    # FACE ANALYSIS
    # =====================================================

    face_match = face_analysis.get(
        "faceMatch",
        {},
    )

    if not isinstance(face_match, dict):
        face_match = {}

    document_face_usable = face_analysis.get(
        "documentFaceUsable",
        False,
    )

    live_photo_face_usable = face_analysis.get(
        "livePhotoFaceUsable",
        False,
    )

    ready_for_biometric_review = face_analysis.get(
        "readyForBiometricReview",
        False,
    )

    # -----------------------------------------------------
    # Fallback for nested face structures
    # -----------------------------------------------------

    document_face = face_analysis.get(
        "document",
        {},
    )

    live_photo_face = face_analysis.get(
        "livePhoto",
        {},
    )

    if not document_face_usable:
        if isinstance(document_face, dict):
            document_face_usable = document_face.get(
                "usable",
                False,
            )

    if not live_photo_face_usable:
        if isinstance(live_photo_face, dict):
            live_photo_face_usable = live_photo_face.get(
                "usable",
                False,
            )

    # =====================================================
    # TAMPER ANALYSIS
    # =====================================================

    tamper_detected = tamper_analysis.get(
        "tamperingDetected",
        False,
    )

    tamper_status = tamper_analysis.get(
        "status",
        "unknown",
    )

    # -----------------------------------------------------
    # Fallback for nested tamper result
    # -----------------------------------------------------

    nested_tamper = tamper_analysis.get(
        "tampering",
        {},
    )

    if not tamper_detected:
        if isinstance(nested_tamper, dict):
            tamper_detected = nested_tamper.get(
                "detected",
                False,
            )

    # =====================================================
    # VERIFICATION ANALYSIS
    # =====================================================

    verification_status = verification_analysis.get(
        "status",
        "unknown",
    )

    verification_reason = verification_analysis.get(
        "reason",
        "",
    )

    verification_details = verification_analysis.get(
        "analysis",
        verification_analysis,
    )

    # =====================================================
    # RISK ANALYSIS
    # =====================================================

    risk_score = risk_analysis.get(
        "riskScore",
        0,
    )

    risk_level = risk_analysis.get(
        "riskLevel",
        "low",
    )

    risk_factors = risk_analysis.get(
        "riskFactors",
        [],
    )

    recommendation = risk_analysis.get(
        "recommendation",
        "",
    )

    # -----------------------------------------------------
    # Normalize risk score
    # -----------------------------------------------------

    try:
        risk_score = float(risk_score)
    except (
        TypeError,
        ValueError,
    ):
        risk_score = 0

    if risk_score.is_integer():
        risk_score = int(risk_score)

    # =====================================================
    # FAILED CHECKS
    # =====================================================

    failed_checks: list[str] = []

    # =====================================================
    # CHECK 1 — OCR
    # =====================================================

    if not ocr_success:

        failed_checks.append(
            "OCR failed"
        )

    # =====================================================
    # CHECK 2 — MRZ
    # =====================================================

    if mrz_required:

        # Passport requires MRZ.
        if not mrz_detected:

            failed_checks.append(
                "MRZ not detected"
            )

        # MRZ exists but parsing/check validation
        # was not completely successful.
        elif mrz_status != "verified":

            failed_checks.append(
                "MRZ validation incomplete"
            )

    # =====================================================
    # CHECK 3 — FACE MATCH
    # =====================================================

    face_status = face_match.get(
        "status",
        "",
    )

    face_match_value = face_match.get(
        "match",
        None,
    )

    # Definite face mismatch.
    if face_status == "no_match":

        failed_checks.append(
            "Face mismatch"
        )

    elif face_match_value is False:

        failed_checks.append(
            "Face mismatch"
        )

    # -----------------------------------------------------
    # IMPORTANT:
    #
    # "not_comparable" and "insufficient_features"
    # are NOT automatically treated as mismatch.
    # -----------------------------------------------------

    # =====================================================
    # CHECK 4 — TAMPERING
    # =====================================================

    if tamper_detected:

        failed_checks.append(
            "Document tampering detected"
        )

    # =====================================================
    # CHECK 5 — VERIFICATION
    # =====================================================

    if verification_status in {
        "failed",
        "rejected",
        "invalid",
        "suspicious",
    }:

        verification_failure = (
            verification_reason
            or "Verification failed"
        )

        failed_checks.append(
            verification_failure
        )

    # =====================================================
    # REMOVE DUPLICATE FAILURES
    # =====================================================

    unique_failed_checks: list[str] = []

    for failure in failed_checks:

        if failure not in unique_failed_checks:

            unique_failed_checks.append(
                failure
            )

    failed_checks = unique_failed_checks

    # =====================================================
    # FINAL DECISION
    # =====================================================

    if tamper_detected:

        # Any confirmed tampering is immediately dangerous.
        final_status = "danger"

    elif len(failed_checks) >= 2:

        final_status = "danger"

    elif len(failed_checks) == 1:

        final_status = "suspicious"

    else:

        # Keep the public result contract in the review state even when
        # no adverse signals were found; approval remains a human decision.
        final_status = "review"

    # =====================================================
    # HUMAN-READABLE FINAL MESSAGE
    # =====================================================

    if final_status == "review":

        final_message = (
            "All required verification checks passed."
        )

    elif final_status == "suspicious":

        final_message = (
            "One verification parameter failed. "
            "Manual review is recommended."
        )

    else:

        final_message = (
            "Multiple verification parameters failed "
            "or document tampering was detected. "
            "Immediate manual review is recommended."
        )

    # =====================================================
    # FINAL RESULT
    # =====================================================

    final_result = {

        # -------------------------------------------------
        # Final decision
        # -------------------------------------------------

        "status": final_status,

        "message": final_message,

        "failedChecks": failed_checks,

        "failedCheckCount": len(
            failed_checks
        ),

        # -------------------------------------------------
        # Document
        # -------------------------------------------------

        "document": {

            "filename": filename,

            "width": width,

            "height": height,

            "format": file_format,

            "type": document_type_value,

            "displayName": document_display_name,

            "confidence": document_type_confidence,

            "ocrSuccessful": ocr_success,

            "mrz": {

                "required": mrz_required,

                "detected": mrz_detected,

                "status": mrz_status,

                "parsed": mrz_parsed,
            },
        },

        # -------------------------------------------------
        # Face
        # -------------------------------------------------

        "face": {

            "documentFaceUsable": (
                document_face_usable
            ),

            "livePhotoFaceUsable": (
                live_photo_face_usable
            ),

            "readyForBiometricReview": (
                ready_for_biometric_review
            ),

            "match": {

                "status": face_match.get(
                    "status",
                    "unknown",
                ),

                "match": face_match.get(
                    "match",
                    None,
                ),

                "score": face_match.get(
                    "score",
                    0,
                ),

                "goodMatches": face_match.get(
                    "goodMatches",
                    0,
                ),

                "documentFeatures": face_match.get(
                    "documentFeatures",
                    0,
                ),

                "livePhotoFeatures": face_match.get(
                    "livePhotoFeatures",
                    0,
                ),

                "method": face_match.get(
                    "method",
                    "",
                ),

                "biometricVerification": face_match.get(
                    "biometricVerification",
                    False,
                ),

                "reason": face_match.get(
                    "reason",
                    "",
                ),
            },
        },

        # -------------------------------------------------
        # Tampering
        # -------------------------------------------------

        "tampering": {

            "detected": tamper_detected,

            "status": tamper_status,
        },

        # -------------------------------------------------
        # Verification
        # -------------------------------------------------

        "verification": {

            "status": verification_status,

            "reason": verification_reason,

            "details": verification_details,
        },

        # -------------------------------------------------
        # Risk
        # -------------------------------------------------

        "risk": {

            "score": risk_score,

            "level": risk_level,

            "factors": risk_factors,

            "recommendation": recommendation,
        },
    }

    # =====================================================
    # COMPLETE RESPONSE
    # =====================================================

    return {

        "success": True,

        "finalResult": final_result,

        "documentAnalysis": ocr_analysis,

        "faceAnalysis": face_analysis,

        "tamperAnalysis": tamper_analysis,

        "verificationAnalysis": verification_analysis,

        "riskAnalysis": risk_analysis,
    }