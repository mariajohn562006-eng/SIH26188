import sys
from pathlib import Path

# ---------------------------------------------------------
# Make sure Python can find the backend/app package
# ---------------------------------------------------------

BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from fastapi.testclient import TestClient

from app.main import app


# ---------------------------------------------------------
# Test client
# ---------------------------------------------------------

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
    assert data["version"] == "1.0.0"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "ByteMind Backend"


# ---------------------------------------------------------
# Upload validation tests
# ---------------------------------------------------------

def test_verification_requires_document():
    response = client.post(
        "/api/verification/start",
        files={
            "photo": (
                "photo.jpg",
                b"fake-photo-data",
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 422


def test_verification_requires_photo():
    response = client.post(
        "/api/verification/start",
        files={
            "document": (
                "document.jpg",
                b"fake-document-data",
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 422


# ---------------------------------------------------------
# Validation module tests
# ---------------------------------------------------------

def test_validation_module_imports():
    from app.validation import (
        validate_document,
        validate_photo,
        validate_filename,
        validate_image_file,
        format_error,
    )

    assert callable(validate_document)
    assert callable(validate_photo)
    assert callable(validate_filename)
    assert callable(validate_image_file)
    assert callable(format_error)


# ---------------------------------------------------------
# Risk engine tests
# ---------------------------------------------------------

def test_risk_engine_imports():
    from app.risk_engine import (
        calculate_risk_score,
        calculate_risk_level,
    )

    assert callable(calculate_risk_score)
    assert callable(calculate_risk_level)


def test_risk_engine_basic_result():
    from app.risk_engine import calculate_risk_score

    result = calculate_risk_score(
        ocr_analysis={
            "ocr": {
                "success": True
            },
            "mrz": {
                "detected": True,
                "parsed": {
                    "success": True
                }
            }
        },
        face_analysis={
            "documentFaceUsable": True,
            "livePhotoFaceUsable": True,
            "document": {
                "status": "usable"
            },
            "livePhoto": {
                "status": "usable"
            }
        },
        tamper_analysis={
            "tampered": False
        },
        verification_analysis={
            "status": "completed"
        }
    )

    assert "riskScore" in result
    assert "riskLevel" in result
    assert "riskFactors" in result
    assert "recommendation" in result

    assert 0 <= result["riskScore"] <= 100


def test_risk_engine_detects_missing_mrz():
    from app.risk_engine import calculate_risk_score

    result = calculate_risk_score(
        ocr_analysis={
            "ocr": {
                "success": True
            },
            "mrz": {
                "detected": False
            }
        },
        face_analysis={
            "documentFaceUsable": True,
            "livePhotoFaceUsable": True,
            "document": {
                "status": "usable"
            },
            "livePhoto": {
                "status": "usable"
            }
        },
        tamper_analysis={
            "tampered": False
        },
        verification_analysis={
            "status": "completed"
        }
    )

    assert result["riskScore"] > 0

    factors = result["riskFactors"]

    assert any(
        factor["factor"] == "MRZ not detected"
        for factor in factors
    )


def test_risk_engine_detects_tampering():
    from app.risk_engine import calculate_risk_score

    result = calculate_risk_score(
        ocr_analysis={
            "ocr": {
                "success": True
            },
            "mrz": {
                "detected": True,
                "parsed": {
                    "success": True
                }
            }
        },
        face_analysis={
            "documentFaceUsable": True,
            "livePhotoFaceUsable": True,
            "document": {
                "status": "usable"
            },
            "livePhoto": {
                "status": "usable"
            }
        },
        tamper_analysis={
            "tampered": True
        },
        verification_analysis={
            "status": "completed"
        }
    )

    assert result["riskScore"] >= 30

    factors = result["riskFactors"]

    assert any(
        factor["factor"] == "Possible document tampering"
        for factor in factors
    )


def test_risk_engine_detects_missing_faces():
    from app.risk_engine import calculate_risk_score

    result = calculate_risk_score(
        ocr_analysis={
            "ocr": {
                "success": True
            },
            "mrz": {
                "detected": True,
                "parsed": {
                    "success": True
                }
            }
        },
        face_analysis={
            "documentFaceUsable": False,
            "livePhotoFaceUsable": False,
            "document": {
                "status": "no_face"
            },
            "livePhoto": {
                "status": "no_face"
            }
        },
        tamper_analysis={
            "tampered": False
        },
        verification_analysis={
            "status": "completed"
        }
    )

    assert result["riskScore"] >= 30

    factors = result["riskFactors"]

    assert any(
        factor["factor"] == "Document face unavailable"
        for factor in factors
    )

    assert any(
        factor["factor"] == "Live photo face unavailable"
        for factor in factors
    )


# ---------------------------------------------------------
# Risk level tests
# ---------------------------------------------------------

def test_risk_levels():
    from app.risk_engine import calculate_risk_level

    assert calculate_risk_level(0) == "low"
    assert calculate_risk_level(29) == "low"

    assert calculate_risk_level(30) == "medium"
    assert calculate_risk_level(59) == "medium"

    assert calculate_risk_level(60) == "high"
    assert calculate_risk_level(79) == "high"

    assert calculate_risk_level(80) == "critical"
    assert calculate_risk_level(100) == "critical"


# ---------------------------------------------------------
# Result aggregator tests
# ---------------------------------------------------------

def test_result_aggregator_imports():
    from app.result_aggregator import (
        aggregate_results,
        determine_final_status,
    )

    assert callable(aggregate_results)
    assert callable(determine_final_status)


def test_result_aggregation():
    from app.result_aggregator import aggregate_results

    result = aggregate_results(
        verification_id="BM-TEST123",
        ocr_analysis={
            "document": {
                "filename": "test.jpg",
                "width": 1200,
                "height": 800,
                "format": ".jpg",
            },
            "ocr": {
                "success": True
            },
            "mrz": {
                "detected": True
            }
        },
        face_analysis={
            "documentFaceUsable": True,
            "livePhotoFaceUsable": True,
            "readyForBiometricReview": True,
        },
        tamper_analysis={
            "tampered": False
        },
        verification_analysis={
            "status": "completed"
        },
        risk_analysis={
            "riskScore": 10,
            "riskLevel": "low",
            "riskFactors": [],
            "recommendation": "Proceed with normal verification review.",
        }
    )

    assert result["verificationId"] == "BM-TEST123"

    assert "status" in result
    assert "risk" in result
    assert "document" in result
    assert "faceAnalysis" in result
    assert "tamperAnalysis" in result
    assert "verificationAnalysis" in result

    assert result["risk"]["score"] == 10
    assert result["risk"]["level"] == "low"

    assert result["document"]["ocrSuccessful"] is True
    assert result["document"]["mrzDetected"] is True

    assert result["faceAnalysis"]["documentFaceUsable"] is True
    assert result["faceAnalysis"]["livePhotoFaceUsable"] is True


def test_result_aggregation_manual_review():
    from app.result_aggregator import aggregate_results

    result = aggregate_results(
        verification_id="BM-TEST456",
        ocr_analysis={
            "document": {
                "filename": "test.jpg",
                "width": 1200,
                "height": 800,
                "format": ".jpg",
            },
            "ocr": {
                "success": True
            },
            "mrz": {
                "detected": True
            }
        },
        face_analysis={
            "documentFaceUsable": True,
            "livePhotoFaceUsable": True,
            "readyForBiometricReview": True,
        },
        tamper_analysis={
            "tampered": True
        },
        verification_analysis={
            "status": "completed"
        },
        risk_analysis={
            "riskScore": 80,
            "riskLevel": "critical",
            "riskFactors": [
                {
                    "factor": "Possible document tampering",
                    "impact": 30,
                    "reason": "Document integrity analysis reported possible manipulation.",
                }
            ],
            "recommendation": "Hold verification for detailed manual investigation.",
        }
    )

    assert result["verificationId"] == "BM-TEST456"
    assert result["status"] == "manual_review"
    assert result["risk"]["score"] == 80
    assert result["risk"]["level"] == "critical"


# ---------------------------------------------------------
# Verification status tests
# ---------------------------------------------------------

def test_result_aggregation_rejected_verification():
    from app.result_aggregator import aggregate_results

    result = aggregate_results(
        verification_id="BM-TEST789",
        ocr_analysis={
            "document": {
                "filename": "test.jpg",
                "width": 1200,
                "height": 800,
                "format": ".jpg",
            },
            "ocr": {
                "success": True
            },
            "mrz": {
                "detected": True
            }
        },
        face_analysis={
            "documentFaceUsable": True,
            "livePhotoFaceUsable": True,
            "readyForBiometricReview": True,
        },
        tamper_analysis={
            "tampered": False
        },
        verification_analysis={
            "status": "rejected"
        },
        risk_analysis={
            "riskScore": 20,
            "riskLevel": "low",
            "riskFactors": [],
            "recommendation": "Proceed with normal verification review.",
        }
    )

    assert result["status"] == "rejected"


# ---------------------------------------------------------
# File validation behavior tests
# ---------------------------------------------------------

def test_invalid_document_extension():
    from fastapi import UploadFile
    from io import BytesIO

    from app.validation import validate_document

    file = UploadFile(
        filename="document.exe",
        file=BytesIO(b"fake data"),
        headers={
            "content-type": "application/octet-stream"
        }
    )

    try:
        validate_document(file, b"fake data")
        assert False, "Expected validation to reject the file"
    except Exception as error:
        assert getattr(error, "status_code", None) == 400


def test_invalid_photo_extension():
    from fastapi import UploadFile
    from io import BytesIO

    from app.validation import validate_photo

    file = UploadFile(
        filename="photo.pdf",
        file=BytesIO(b"fake data"),
        headers={
            "content-type": "application/pdf"
        }
    )

    try:
        validate_photo(file, b"fake data")
        assert False, "Expected validation to reject the file"
    except Exception as error:
        assert getattr(error, "status_code", None) == 400


def test_empty_document_rejected():
    from fastapi import UploadFile
    from io import BytesIO

    from app.validation import validate_document

    file = UploadFile(
        filename="document.jpg",
        file=BytesIO(b""),
        headers={
            "content-type": "image/jpeg"
        }
    )

    try:
        validate_document(file, b"")
        assert False, "Expected validation to reject empty document"
    except Exception as error:
        assert getattr(error, "status_code", None) == 400


def test_empty_photo_rejected():
    from fastapi import UploadFile
    from io import BytesIO

    from app.validation import validate_photo

    file = UploadFile(
        filename="photo.jpg",
        file=BytesIO(b""),
        headers={
            "content-type": "image/jpeg"
        }
    )

    try:
        validate_photo(file, b"")
        assert False, "Expected validation to reject empty photo"
    except Exception as error:
        assert getattr(error, "status_code", None) == 400


# ---------------------------------------------------------
# Error formatting test
# ---------------------------------------------------------

def test_format_error():
    from app.validation import format_error

    error_message = format_error(
        "OCR analysis",
        ValueError("Test error")
    )

    assert error_message == "OCR analysis failed: Test error"