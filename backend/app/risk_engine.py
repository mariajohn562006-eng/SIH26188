from typing import Any


# =========================================================
# CLAMP RISK SCORE
# =========================================================

def clamp_score(score: float) -> float:
    """
    Keep the risk score between 0 and 100.
    """

    return max(
        0.0,
        min(100.0, float(score))
    )


# =========================================================
# CALCULATE RISK LEVEL
# =========================================================

def calculate_risk_level(
    risk_score: float
) -> str:

    if risk_score < 30:
        return "low"

    if risk_score < 60:
        return "medium"

    if risk_score < 80:
        return "high"

    return "critical"


# =========================================================
# CALCULATE OVERALL RISK SCORE
# =========================================================

def calculate_risk_score(
    ocr_analysis: dict[str, Any] | None = None,
    face_analysis: dict[str, Any] | None = None,
    tamper_analysis: dict[str, Any] | None = None,
    verification_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:

    ocr_analysis = ocr_analysis or {}
    face_analysis = face_analysis or {}
    tamper_analysis = tamper_analysis or {}
    verification_analysis = verification_analysis or {}

    risk_score = 0.0
    risk_factors = []

    # =====================================================
    # OCR RISK
    # =====================================================

    ocr_data = ocr_analysis.get(
        "ocr",
        {}
    )

    ocr_success = ocr_data.get(
        "success",
        False
    )

    if not ocr_success:

        risk_score += 20

        risk_factors.append({
            "factor": "OCR failure",
            "impact": 20,
            "reason": (
                "Document text could not be "
                "reliably extracted."
            )
        })

    # =====================================================
    # MRZ RISK
    # =====================================================

    mrz_data = ocr_analysis.get(
        "mrz",
        {}
    )

    mrz_required = mrz_data.get(
        "required",
        True
    )

    mrz_detected = mrz_data.get(
        "detected",
        False
    )

    mrz_status = str(
        mrz_data.get(
            "status",
            ""
        )
    ).lower()

    if mrz_required:

        if not mrz_detected:

            risk_score += 20

            risk_factors.append({
                "factor": "MRZ not detected",
                "impact": 20,
                "reason": (
                    "MRZ was required for this "
                    "document but was not detected."
                )
            })

        else:

            parsed_mrz = mrz_data.get(
                "parsed",
                {}
            )

            if isinstance(
                parsed_mrz,
                dict
            ):

                mrz_success = parsed_mrz.get(
                    "success",
                    False
                )

                if not mrz_success:

                    risk_score += 10

                    risk_factors.append({
                        "factor": "MRZ parsing failure",
                        "impact": 10,
                        "reason": (
                            "MRZ was detected but "
                            "could not be parsed successfully."
                        )
                    })

    elif mrz_status == "not required":

        print(
            "DEBUG: MRZ not required - "
            "no MRZ risk added"
        )

    # =====================================================
    # FACE ANALYSIS
    # =====================================================

    document_face_usable = face_analysis.get(
        "documentFaceUsable",
        False
    )

    live_photo_face_usable = face_analysis.get(
        "livePhotoFaceUsable",
        False
    )

    document_face_data = face_analysis.get(
        "document",
        {}
    )

    live_photo_data = face_analysis.get(
        "livePhoto",
        {}
    )

    face_match = face_analysis.get(
        "faceMatch",
        {}
    )

    face_risk = False
    face_reasons = []

    # -----------------------------------------------------
    # Document face unavailable
    # -----------------------------------------------------

    if not document_face_usable:

        face_risk = True

        face_reasons.append(
            "A usable face was not detected "
            "in the document."
        )

    # -----------------------------------------------------
    # Live photo face unavailable
    # -----------------------------------------------------

    if not live_photo_face_usable:

        face_risk = True

        face_reasons.append(
            "A usable face was not detected "
            "in the live photo."
        )

    # -----------------------------------------------------
    # Multiple document faces
    # -----------------------------------------------------

    if isinstance(
        document_face_data,
        dict
    ):

        if document_face_data.get(
            "status"
        ) == "multiple_faces":

            face_risk = True

            face_reasons.append(
                "Multiple faces were detected "
                "in the document."
            )

    # -----------------------------------------------------
    # Multiple live-photo faces
    # -----------------------------------------------------

    if isinstance(
        live_photo_data,
        dict
    ):

        if live_photo_data.get(
            "status"
        ) == "multiple_faces":

            face_risk = True

            face_reasons.append(
                "Multiple faces were detected "
                "in the live photo."
            )

    # -----------------------------------------------------
    # Actual face mismatch
    # -----------------------------------------------------

    if isinstance(
        face_match,
        dict
    ):

        match_status = str(
            face_match.get(
                "status",
                ""
            )
        ).lower()

        match_value = face_match.get(
            "match"
        )

        # Only treat an explicit no_match result
        # as a face verification risk.
        #
        # "not_comparable" and
        # "insufficient_features" are handled
        # as unavailable comparison evidence,
        # not as proof of a mismatch.

        if (
            match_status == "no_match"
            or match_value is False
        ):

            face_risk = True

            face_reasons.append(
                "The document portrait and "
                "live photo did not show "
                "sufficient visual similarity."
            )

    # -----------------------------------------------------
    # Apply face risk
    # -----------------------------------------------------

    if face_risk:

        risk_score += 30

        risk_factors.append({
            "factor": "Face verification issue",
            "impact": 30,
            "reason": " ".join(face_reasons)
        })

    # =====================================================
    # TAMPER RISK
    # =====================================================

    tamper_detected = False

    if isinstance(
        tamper_analysis,
        dict
    ):

        tamper_detected = bool(
            tamper_analysis.get(
                "tampered",
                False
            )
            or tamper_analysis.get(
                "tamperingDetected",
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

            tamper_detected = (
                tamper_detected
                or bool(
                    nested_tamper.get(
                        "tampered",
                        False
                    )
                    or nested_tamper.get(
                        "tamperingDetected",
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
            )

    if tamper_detected:

        risk_score += 30

        risk_factors.append({
            "factor": "Possible document tampering",
            "impact": 30,
            "reason": (
                "Document integrity analysis "
                "reported possible manipulation."
            )
        })

    # =====================================================
    # VERIFICATION RISK
    # =====================================================

    verification_status = ""

    if isinstance(
        verification_analysis,
        dict
    ):

        verification_status = str(
            verification_analysis.get(
                "status",
                ""
            )
        ).lower()

        nested_analysis = (
            verification_analysis.get(
                "analysis"
            )
        )

        if isinstance(
            nested_analysis,
            dict
        ):

            verification_status = str(
                nested_analysis.get(
                    "status",
                    verification_status
                )
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
            "reason": (
                "Verification analysis returned "
                f"status: {verification_status}."
            )
        })

    # =====================================================
    # FINAL SCORE
    # =====================================================

    risk_score = clamp_score(
        risk_score
    )

    risk_level = calculate_risk_level(
        risk_score
    )

    # =====================================================
    # RECOMMENDATION
    # =====================================================

    if risk_level == "low":

        recommendation = (
            "Proceed with normal verification review."
        )

    elif risk_level == "medium":

        recommendation = (
            "Perform additional verification checks."
        )

    elif risk_level == "high":

        recommendation = (
            "Require manual review before approval."
        )

    else:

        recommendation = (
            "Hold verification for detailed "
            "manual investigation."
        )

    # =====================================================
    # FINAL RESULT
    # =====================================================

    return {

        "riskScore": round(
            risk_score,
            2
        ),

        "riskLevel": risk_level,

        "riskFactors": risk_factors,

        "recommendation": recommendation
    }