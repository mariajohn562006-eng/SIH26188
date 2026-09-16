import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.risk_engine import calculate_risk_score
from app.result_aggregator import aggregate_results


client = TestClient(app)


# ---------------------------------------------------------
# Basic API tests
# ---------------------------------------------------------

def test_home():
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()

    assert data["system"] == "ByteMind"
    assert data["status"] == "Backend is running"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "ByteMind Backend"


# ---------------------------------------------------------
# Module/import tests
# ---------------------------------------------------------

def test_required_backend_files_exist():
    backend_dir = Path(__file__).resolve().parents[1]
    app_dir = backend_dir / "app"

    required_files = [
        "main.py",
        "ocr.py",
        "mrz.py",
        "face_match.py",
        "verification.py",
        "tamper_detection.py",
        "risk_engine.py",
        "result_aggregator.py",
        "validation.py",
        "document_type.py",
    ]

    for filename in required_files:
        assert (app_dir / filename).exists(), (
            f"Missing backend file: {filename}"
        )


    def test_mrz_passes_when_two_lines_are_detected():
        from app.mrz import parse_passport_mrz

        result = parse_passport_mrz([
            "DAMAGEDPREFIX<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
            "L898902C36UTO7408122F1204159ZE184226B<<",
        ])

        assert result["success"] is True
        assert result["documentCodeValid"] is False


def test_modules_import():
    from app import document_type
    from app import face_match
    from app import mrz
    from app import ocr
    from app import result_aggregator
    from app import risk_engine
    from app import tamper_detection
    from app import validation
    from app import verification

    assert document_type is not None
    assert face_match is not None
    assert mrz is not None
    assert ocr is not None
    assert result_aggregator is not None
    assert risk_engine is not None
    assert tamper_detection is not None
    assert validation is not None
    assert verification is not None


# ---------------------------------------------------------
# Document type tests
# ---------------------------------------------------------

def test_passport_document_type():
    from app.document_type import detect_document_type

    result = detect_document_type(
        ocr_text="PASSPORT NATIONALITY DATE OF BIRTH",
        filename="passport.jpg",
    )

    assert result["type"] == "passport"
    assert result["displayName"] == "Passport"


def test_driver_license_document_type():
    from app.document_type import detect_document_type

    result = detect_document_type(
        ocr_text="DRIVER LICENSE LICENSE NUMBER DATE OF BIRTH",
        filename="license.jpg",
    )

    assert result["type"] == "drivers_license"


def test_unknown_document_type():
    from app.document_type import detect_document_type

    result = detect_document_type(
        ocr_text="RANDOM DOCUMENT TEXT",
        filename="document.jpg",
    )

    assert result["type"] == "unknown"


# ---------------------------------------------------------
# Risk engine tests
# ---------------------------------------------------------

def test_low_risk_score():
    ocr_analysis = {
        "ocr": {
            "success": True,
        },
        "mrz": {
            "required": False,
            "detected": False,
            "status": "not required",
        },
    }

    face_analysis = {
        "documentFaceUsable": True,
        "livePhotoFaceUsable": True,
        "faceMatch": {
            "status": "match",
            "match": True,
            "score": 80,
        },
    }

    tamper_analysis = {
        "tamperingDetected": False,
    }

    verification_analysis = {
        "status": "verified",
    }

    result = calculate_risk_score(
        ocr_analysis=ocr_analysis,
        face_analysis=face_analysis,
        tamper_analysis=tamper_analysis,
        verification_analysis=verification_analysis,
    )

    assert result["riskScore"] == 0
    assert result["riskLevel"] == "low"


def test_face_mismatch_adds_30_risk():
    ocr_analysis = {
        "ocr": {
            "success": True,
        },
        "mrz": {
            "required": False,
            "detected": False,
            "status": "not required",
        },
    }

    face_analysis = {
        "documentFaceUsable": True,
        "livePhotoFaceUsable": True,
        "faceMatch": {
            "status": "no_match",
            "match": False,
            "score": 5,
        },
    }

    tamper_analysis = {
        "tamperingDetected": False,
    }

    verification_analysis = {
        "status": "verified",
    }

    result = calculate_risk_score(
        ocr_analysis=ocr_analysis,
        face_analysis=face_analysis,
        tamper_analysis=tamper_analysis,
        verification_analysis=verification_analysis,
    )

    assert result["riskScore"] == 30
    assert result["riskLevel"] == "medium"


def test_tampering_adds_30_risk():
    ocr_analysis = {
        "ocr": {
            "success": True,
        },
        "mrz": {
            "required": False,
            "detected": False,
            "status": "not required",
        },
    }

    face_analysis = {
        "documentFaceUsable": True,
        "livePhotoFaceUsable": True,
        "faceMatch": {
            "status": "match",
            "match": True,
            "score": 80,
        },
    }

    tamper_analysis = {
        "tamperingDetected": True,
    }

    verification_analysis = {
        "status": "verified",
    }

    result = calculate_risk_score(
        ocr_analysis=ocr_analysis,
        face_analysis=face_analysis,
        tamper_analysis=tamper_analysis,
        verification_analysis=verification_analysis,
    )

    assert result["riskScore"] == 30


def test_passport_missing_mrz_adds_risk():
    ocr_analysis = {
        "ocr": {
            "success": True,
        },
        "mrz": {
            "required": True,
            "detected": False,
            "status": "failed",
        },
    }

    face_analysis = {
        "documentFaceUsable": True,
        "livePhotoFaceUsable": True,
        "faceMatch": {
            "status": "match",
            "match": True,
            "score": 80,
        },
    }

    tamper_analysis = {
        "tamperingDetected": False,
    }

    verification_analysis = {
        "status": "verified",
    }

    result = calculate_risk_score(
        ocr_analysis=ocr_analysis,
        face_analysis=face_analysis,
        tamper_analysis=tamper_analysis,
        verification_analysis=verification_analysis,
    )

    assert result["riskScore"] == 20


# ---------------------------------------------------------
# Result aggregation tests
# ---------------------------------------------------------

def test_result_aggregation():
    document_analysis = {
        "document": {
            "filename": "passport.jpg",
            "width": 1000,
            "height": 700,
            "format": ".jpg",
        },
        "documentType": {
            "type": "passport",
            "displayName": "Passport",
            "confidence": "medium",
        },
        "ocr": {
            "success": True,
            "text": "PASSPORT",
        },
        "mrz": {
            "required": True,
            "detected": True,
            "status": "verified",
            "parsed": {
                "success": True,
            },
        },
    }

    face_analysis = {
        "documentFaceUsable": True,
        "livePhotoFaceUsable": True,
        "readyForBiometricReview": True,
        "faceMatch": {
            "status": "match",
            "match": True,
            "score": 75,
            "goodMatches": 30,
            "documentFeatures": 100,
            "livePhotoFeatures": 110,
            "method": "OpenCV ORB feature similarity screening",
            "biometricVerification": False,
            "reason": "Sufficient visual similarity.",
        },
    }

    tamper_analysis = {
        "tamperingDetected": False,
        "status": "clean",
    }

    verification_analysis = {
        "status": "verified",
        "reason": "Verification checks completed.",
        "analysis": {},
    }

    risk_analysis = {
        "riskScore": 0,
        "riskLevel": "low",
        "riskFactors": [],
        "recommendation": "Proceed with normal review.",
    }

    result = aggregate_results(
        document_analysis=document_analysis,
        face_analysis=face_analysis,
        tamper_analysis=tamper_analysis,
        verification_analysis=verification_analysis,
        risk_analysis=risk_analysis,
    )

    assert result["success"] is True

    final_result = result["finalResult"]

    assert final_result["status"] == "review"

    assert final_result["document"]["type"] == "passport"

    assert final_result["document"]["mrz"]["required"] is True
    assert final_result["document"]["mrz"]["detected"] is True

    assert final_result["face"]["match"]["status"] == "match"
    assert final_result["face"]["match"]["match"] is True
    assert final_result["face"]["match"]["score"] == 75

    assert final_result["tampering"]["detected"] is False

    assert final_result["risk"]["score"] == 0
    assert final_result["risk"]["level"] == "low"


# ---------------------------------------------------------
# Face mismatch aggregation test
# ---------------------------------------------------------

def test_face_mismatch_is_exposed_in_final_result():
    document_analysis = {
        "document": {
            "filename": "id.jpg",
            "width": 1000,
            "height": 700,
            "format": ".jpg",
        },
        "documentType": {
            "type": "national_id",
            "displayName": "National ID",
            "confidence": "medium",
        },
        "ocr": {
            "success": True,
            "text": "NATIONAL ID",
        },
        "mrz": {
            "required": False,
            "detected": False,
            "status": "not required",
        },
    }

    face_analysis = {
        "documentFaceUsable": True,
        "livePhotoFaceUsable": True,
        "readyForBiometricReview": True,
        "faceMatch": {
            "status": "no_match",
            "match": False,
            "score": 5,
            "goodMatches": 2,
            "documentFeatures": 100,
            "livePhotoFeatures": 110,
            "method": "OpenCV ORB feature similarity screening",
            "biometricVerification": False,
            "reason": "Insufficient visual similarity.",
        },
    }

    tamper_analysis = {
        "tamperingDetected": False,
        "status": "clean",
    }

    verification_analysis = {
        "status": "verified",
        "reason": "Verification checks completed.",
        "analysis": {},
    }

    risk_analysis = {
        "riskScore": 30,
        "riskLevel": "medium",
        "riskFactors": [
            "Face verification issue",
        ],
        "recommendation": "Additional review is recommended.",
    }

    result = aggregate_results(
        document_analysis=document_analysis,
        face_analysis=face_analysis,
        tamper_analysis=tamper_analysis,
        verification_analysis=verification_analysis,
        risk_analysis=risk_analysis,
    )

    final_result = result["finalResult"]

    assert final_result["face"]["match"]["status"] == "no_match"
    assert final_result["face"]["match"]["match"] is False
    assert final_result["face"]["match"]["score"] == 5

    assert final_result["risk"]["score"] == 30
    assert final_result["risk"]["level"] == "medium"