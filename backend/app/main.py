from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uuid

from app.verification import analyze_verification
from app.ocr import analyze_document
from app.face_match import analyze_face_inputs
from app.tamper_detection import analyze_tampering
from app.risk_engine import calculate_risk_score
from app.result_aggregator import aggregate_results

from app.validation import (
    validate_document,
    validate_photo,
    validate_image_file,
    format_error,
)


app = FastAPI(
    title="ByteMind API",
    description="AI-Based Fake Identity and Document Screening System",
    version="1.0.0",
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# UPLOAD DIRECTORY
# --------------------------------------------------

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "system": "ByteMind",
        "status": "Backend is running",
        "version": "1.0.0",
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "ByteMind Backend",
    }


# --------------------------------------------------
# START VERIFICATION
# --------------------------------------------------

@app.post("/api/verification/start")
async def start_verification(
    document: UploadFile = File(...),
    photo: UploadFile = File(...),
):
    """
    Complete ByteMind verification pipeline:

    1. Validate uploaded files
    2. Save files
    3. OCR + MRZ analysis
    4. Face analysis
    5. Tamper analysis
    6. Verification analysis
    7. Risk calculation
    8. Final result aggregation
    """

    # --------------------------------------------------
    # CREATE VERIFICATION ID
    # --------------------------------------------------

    verification_id = f"BM-{uuid.uuid4().hex[:8].upper()}"

    print("=" * 60)
    print("DEBUG: verification started:", verification_id)
    print("=" * 60)


    # --------------------------------------------------
    # READ DOCUMENT
    # --------------------------------------------------

    print("DEBUG: reading document")

    try:
        document_content = await document.read()
    except Exception as error:
        print("DEBUG: document read failed:", error)

        raise HTTPException(
            status_code=400,
            detail=format_error(
                "Document upload",
                error
            )
        )


    # --------------------------------------------------
    # READ PHOTO
    # --------------------------------------------------

    print("DEBUG: reading photo")

    try:
        photo_content = await photo.read()
    except Exception as error:
        print("DEBUG: photo read failed:", error)

        raise HTTPException(
            status_code=400,
            detail=format_error(
                "Photo upload",
                error
            )
        )


    # --------------------------------------------------
    # VALIDATE UPLOADS
    # --------------------------------------------------

    print("DEBUG: validating document")

    validate_document(
        document,
        document_content
    )

    print("DEBUG: validating photo")

    validate_photo(
        photo,
        photo_content
    )


    # --------------------------------------------------
    # FILE EXTENSIONS
    # --------------------------------------------------

    document_extension = Path(
        document.filename
    ).suffix.lower()

    photo_extension = Path(
        photo.filename
    ).suffix.lower()


    # --------------------------------------------------
    # CREATE FILE PATHS
    # --------------------------------------------------

    document_path = (
        UPLOAD_DIR
        / f"{verification_id}_document{document_extension}"
    )

    photo_path = (
        UPLOAD_DIR
        / f"{verification_id}_photo{photo_extension}"
    )


    # --------------------------------------------------
    # SAVE DOCUMENT
    # --------------------------------------------------

    print("DEBUG: saving document")

    try:
        document_path.write_bytes(
            document_content
        )

        validate_image_file(
            document_path
        )

    except HTTPException:
        raise

    except Exception as error:
        print("DEBUG: document save failed:", error)

        raise HTTPException(
            status_code=500,
            detail=format_error(
                "Document storage",
                error
            )
        )

    print(
        "DEBUG: document saved:",
        document_path
    )

    print(
        "DEBUG: document size:",
        len(document_content),
        "bytes"
    )

    print(
        "DEBUG: document extension:",
        document_extension
    )


    # --------------------------------------------------
    # SAVE PHOTO
    # --------------------------------------------------

    print("DEBUG: saving photo")

    try:
        photo_path.write_bytes(
            photo_content
        )

        validate_image_file(
            photo_path
        )

    except HTTPException:
        raise

    except Exception as error:
        print("DEBUG: photo save failed:", error)

        raise HTTPException(
            status_code=500,
            detail=format_error(
                "Photo storage",
                error
            )
        )

    print(
        "DEBUG: photo saved:",
        photo_path
    )


    # --------------------------------------------------
    # OCR + MRZ ANALYSIS
    # --------------------------------------------------

    print("DEBUG: starting OCR")

    try:
        document_analysis = analyze_document(
            str(document_path)
        )

        print("DEBUG: OCR finished")

    except Exception as error:
        print("DEBUG: OCR failed:", error)

        raise HTTPException(
            status_code=500,
            detail=format_error(
                "OCR analysis",
                error
            )
        )


    # --------------------------------------------------
    # FACE ANALYSIS
    # --------------------------------------------------

    print("DEBUG: starting face analysis")

    try:
        face_analysis = analyze_face_inputs(
            str(document_path),
            str(photo_path)
        )

        print("DEBUG: face analysis finished")

    except Exception as error:
        print("DEBUG: face analysis failed:", error)

        raise HTTPException(
            status_code=500,
            detail=format_error(
                "Face analysis",
                error
            )
        )


    # --------------------------------------------------
    # TAMPER ANALYSIS
    # --------------------------------------------------

    print("DEBUG: starting tamper analysis")

    try:
        tamper_analysis = analyze_tampering(
            str(document_path)
        )

        print("DEBUG: tamper analysis finished")

    except Exception as error:
        print("DEBUG: tamper analysis failed:", error)

        raise HTTPException(
            status_code=500,
            detail=format_error(
                "Tamper analysis",
                error
            )
        )


    # --------------------------------------------------
    # VERIFICATION ANALYSIS
    # --------------------------------------------------

    print("DEBUG: starting verification analysis")

    try:
        # analyze_verification expects Path objects
        verification_analysis = analyze_verification(
            document_path,
            photo_path
        )

        print(
            "DEBUG: verification analysis finished"
        )

    except Exception as error:
        print(
            "DEBUG: verification analysis failed:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=format_error(
                "Verification analysis",
                error
            )
        )


    # --------------------------------------------------
    # RISK ENGINE
    # --------------------------------------------------

    print("DEBUG: starting risk analysis")

    try:
        risk_analysis = calculate_risk_score(
            ocr_analysis=document_analysis,
            face_analysis=face_analysis.get(
                "faceAnalysis",
                face_analysis
            ),
            tamper_analysis=tamper_analysis,
            verification_analysis=verification_analysis,
        )

        print("DEBUG: risk analysis finished")

    except Exception as error:
        print("DEBUG: risk analysis failed:", error)

        raise HTTPException(
            status_code=500,
            detail=format_error(
                "Risk analysis",
                error
            )
        )


    # --------------------------------------------------
    # FINAL RESULT AGGREGATION
    # --------------------------------------------------

    print("DEBUG: aggregating final result")

    try:
        final_result = aggregate_results(
            verification_id=verification_id,
            ocr_analysis=document_analysis,
            face_analysis=face_analysis.get(
                "faceAnalysis",
                face_analysis
            ),
            tamper_analysis=tamper_analysis,
            verification_analysis=verification_analysis,
            risk_analysis=risk_analysis,
        )

        print(
            "DEBUG: final result aggregation finished"
        )

    except Exception as error:
        print(
            "DEBUG: result aggregation failed:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=format_error(
                "Result aggregation",
                error
            )
        )


    # --------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------

    print(
        "DEBUG: verification completed:",
        verification_id
    )

    print(
        "DEBUG: risk score:",
        risk_analysis.get("riskScore")
    )

    print(
        "DEBUG: risk level:",
        risk_analysis.get("riskLevel")
    )

    print("=" * 60)


    return {
        "verification_id": verification_id,

        "status": "completed",

        "message": (
            "Document and live photo received "
            "and analyzed successfully."
        ),

        "document": document.filename,

        "photo": photo.filename,

        "ocr": document_analysis,

        "faceAnalysis": face_analysis,

        "tamperAnalysis": tamper_analysis,

        "analysis": verification_analysis,

        "risk": risk_analysis,

        "finalResult": final_result,
    }