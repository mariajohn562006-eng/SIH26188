from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.face_match import analyze_face_inputs
from app.ocr import analyze_document
from app.risk_engine import calculate_risk_score
from app.result_aggregator import aggregate_results
from app.tamper_detection import analyze_tampering
from app.validation import (
    validate_document,
    validate_image_file,
    validate_photo,
)

# =========================================================
# OPTIONAL RAG
# =========================================================

try:
    from app.rag.rag_engine import analyze_with_rag

    RAG_AVAILABLE = True

except Exception as error:
    print(
        f"WARNING: RAG module unavailable: {error}"
    )

    analyze_with_rag = None
    RAG_AVAILABLE = False


# =========================================================
# APP CONFIGURATION
# =========================================================

app = FastAPI(
    title="ByteMind Verification API",
    description=(
        "Document verification backend for OCR, MRZ, "
        "face matching, tamper detection, risk analysis, "
        "and RAG-based verification explanations."
    ),
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# UPLOAD DIRECTORY
# =========================================================

UPLOAD_DIR = Path("uploads")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# BASIC ROUTES
# =========================================================

@app.get("/")
def root():
    return {
        "message": "ByteMind Verification API",
        "system": "ByteMind",
        "status": "Backend is running",
        "apiStatus": "running",
        "legacyStatus": "Backend is running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "ByteMind Backend",
        "apiService": "ByteMind Verification API",
        "ragAvailable": RAG_AVAILABLE,
    }


# =========================================================
# START VERIFICATION
# =========================================================

@app.post("/api/verification/start")
async def start_verification(
    document: UploadFile = File(...),
    live_photo: UploadFile | None = File(default=None),
    photo: UploadFile | None = File(default=None),
    user_id: str | None = Form(default=None),
):
    """
    Run the complete document verification pipeline.

    Pipeline:

        1. Validate uploads
        2. Save files
        3. OCR
        4. MRZ detection/parsing
        5. Face analysis
        6. Tamper detection
        7. Verification analysis
        8. Risk analysis
        9. RAG explanation
        10. Final result aggregation
    """

    # =====================================================
    # VALIDATION
    # =====================================================

    uploaded_photo = live_photo or photo

    if uploaded_photo is None:
        raise HTTPException(
            status_code=422,
            detail="Live photo is required. Use 'live_photo' or 'photo'.",
        )


    # =====================================================
    # CREATE UNIQUE FILE NAMES
    # =====================================================

    verification_id = str(uuid4())

    document_suffix = Path(
        document.filename or ""
    ).suffix.lower()

    photo_suffix = Path(
        uploaded_photo.filename or ""
    ).suffix.lower()

    document_path = (
        UPLOAD_DIR
        / f"{verification_id}_document{document_suffix}"
    )

    photo_path = (
        UPLOAD_DIR
        / f"{verification_id}_photo{photo_suffix}"
    )


    # =====================================================
    # SAVE DOCUMENT
    # =====================================================

    try:

        document_content = await document.read()
        photo_content = await uploaded_photo.read()

        validate_document(
            document,
            document_content,
        )

        validate_photo(
            uploaded_photo,
            photo_content,
        )

        with open(
            document_path,
            "wb",
        ) as file:

            file.write(
                document_content
            )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Document upload failed: "
                f"{error}"
            ),
        )


    # =====================================================
    # SAVE LIVE PHOTO
    # =====================================================

    try:

        with open(
            photo_path,
            "wb",
        ) as file:

            file.write(
                photo_content
            )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Live photo upload failed: "
                f"{error}"
            ),
        )


    # =====================================================
    # VERIFY SAVED FILES
    # =====================================================

    try:

        validate_image_file(
            document_path
        )

        validate_image_file(
            photo_path
        )

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Saved file validation failed: "
                f"{error}"
            ),
        )


    # =====================================================
    # OCR + MRZ + DOCUMENT TYPE
    # =====================================================

    try:

        document_analysis = analyze_document(
            document_path
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"OCR analysis failed: "
                f"{error}"
            ),
        )


    # =====================================================
    # FACE ANALYSIS
    # =====================================================

    try:

        face_analysis = analyze_face_inputs(
            document_path=str(
                document_path
            ),
            photo_path=str(
                photo_path
            ),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Face analysis failed: "
                f"{error}"
            ),
        )


    # =====================================================
    # TAMPER DETECTION
    # =====================================================

    try:

        tamper_analysis = analyze_tampering(
            document_path
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Tamper detection failed: "
                f"{error}"
            ),
        )


    # =====================================================
    # BASE VERIFICATION
    # =====================================================

    try:

        from app.verification import (
            analyze_verification
        )

        verification_analysis = (
            analyze_verification(
                document_path,
                photo_path,
            )
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Verification analysis failed: "
                f"{error}"
            ),
        )


    # =====================================================
    # RISK ENGINE
    # =====================================================

    try:

        risk_analysis = calculate_risk_score(
            ocr_analysis=document_analysis,
            face_analysis=face_analysis,
            tamper_analysis=tamper_analysis,
            verification_analysis=(
                verification_analysis
            ),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Risk analysis failed: "
                f"{error}"
            ),
        )


    # =====================================================
    # RAG ANALYSIS
    # =====================================================

    if RAG_AVAILABLE and analyze_with_rag:

        try:

            rag_analysis = analyze_with_rag(
                ocr_analysis=document_analysis,
                face_analysis=face_analysis.get(
                    "faceAnalysis",
                    face_analysis,
                ),
                tamper_analysis=tamper_analysis,
                verification_analysis=(
                    verification_analysis
                ),
                top_k=3,
            )

        except Exception as error:

            print(
                f"WARNING: RAG analysis failed: "
                f"{error}"
            )

            rag_analysis = {
                "enabled": False,
                "query": "",
                "resultCount": 0,
                "sources": [],
                "retrievedKnowledge": [],
                "context": "",
                "explanation": (
                    "RAG analysis was unavailable."
                ),
            }

    else:

        rag_analysis = {
            "enabled": False,
            "query": "",
            "resultCount": 0,
            "sources": [],
            "retrievedKnowledge": [],
            "context": "",
            "explanation": (
                "RAG is not available."
            ),
        }


    # =====================================================
    # FINAL RESULT AGGREGATION
    # =====================================================

    try:

        final_result = aggregate_results(
            ocr_analysis=document_analysis,
            face_analysis=face_analysis,
            tamper_analysis=tamper_analysis,
            verification_analysis=(
                verification_analysis
            ),
            risk_analysis=risk_analysis,
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Result aggregation failed: "
                f"{error}"
            ),
        )


    # =====================================================
    # FINAL RESPONSE
    # =====================================================

    return {
        "success": True,

        "verificationId": verification_id,

        "userId": user_id,

        "finalResult": final_result.get(
            "finalResult",
            {},
        ),

        "documentAnalysis": document_analysis,

        "faceAnalysis": face_analysis,

        "tamperAnalysis": tamper_analysis,

        "verificationAnalysis": (
            verification_analysis
        ),

        "riskAnalysis": risk_analysis,

        "rag": rag_analysis,
    }