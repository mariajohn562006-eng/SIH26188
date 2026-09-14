from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uuid

from app.verification import analyze_verification
from app.ocr import analyze_document
from app.face_match import analyze_face_inputs
from app.tamper_detection import analyze_tampering


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="ByteMind API",
    description="AI-Based Fake Identity and Document Screening System",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

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


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "system": "ByteMind",
        "status": "Backend is running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "ByteMind Backend"
    }


# ============================================================
# START VERIFICATION
# ============================================================

@app.post("/api/verification/start")
async def start_verification(
    document: UploadFile = File(...),
    photo: UploadFile = File(...)
):

    # --------------------------------------------------------
    # 1. Validate uploaded files
    # --------------------------------------------------------

    if not document.filename:
        raise HTTPException(
            status_code=400,
            detail="Document file is required"
        )

    if not photo.filename:
        raise HTTPException(
            status_code=400,
            detail="Live photo is required"
        )

    # --------------------------------------------------------
    # 2. Generate verification ID
    # --------------------------------------------------------

    verification_id = (
        f"BM-{uuid.uuid4().hex[:8].upper()}"
    )

    # --------------------------------------------------------
    # 3. Get file extensions
    # --------------------------------------------------------

    document_extension = (
        Path(document.filename).suffix.lower()
    )

    photo_extension = (
        Path(photo.filename).suffix.lower()
    )

    # --------------------------------------------------------
    # 4. Create file paths
    # --------------------------------------------------------

    document_path = (
        UPLOAD_DIR
        / f"{verification_id}_document{document_extension}"
    )

    photo_path = (
        UPLOAD_DIR
        / f"{verification_id}_photo{photo_extension}"
    )

    # --------------------------------------------------------
    # 5. Save document
    # --------------------------------------------------------

    print("DEBUG: reading document")

    document_content = await document.read()

    if not document_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded document is empty"
        )

    document_path.write_bytes(
        document_content
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

    # --------------------------------------------------------
    # 6. Save live photo
    # --------------------------------------------------------

    print("DEBUG: reading photo")

    photo_content = await photo.read()

    if not photo_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded photo is empty"
        )

    photo_path.write_bytes(
        photo_content
    )

    print(
        "DEBUG: photo saved:",
        photo_path
    )

    # ========================================================
    # 7. OCR + MRZ ANALYSIS
    # ========================================================

    print("DEBUG: starting OCR")

    try:

        document_analysis = analyze_document(
            str(document_path)
        )

        print("DEBUG: OCR finished")

    except Exception as error:

        print(
            "DEBUG: OCR failed:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=f"OCR analysis failed: {error}"
        )

    # ========================================================
    # 8. FACE ANALYSIS
    # ========================================================

    print(
        "DEBUG: starting face analysis"
    )

    try:

        face_analysis = analyze_face_inputs(
            str(document_path),
            str(photo_path)
        )

        print(
            "DEBUG: face analysis finished"
        )

    except Exception as error:

        print(
            "DEBUG: face analysis failed:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=f"Face analysis failed: {error}"
        )

    # ========================================================
    # 9. TAMPER / IMAGE INTEGRITY ANALYSIS
    # ========================================================

    print(
        "DEBUG: starting tamper analysis"
    )

    try:

        tamper_analysis = analyze_tampering(
            str(document_path)
        )

        print(
            "DEBUG: tamper analysis finished"
        )

    except Exception as error:

        print(
            "DEBUG: tamper analysis failed:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=f"Tamper analysis failed: {error}"
        )

    # ========================================================
    # 10. VERIFICATION ANALYSIS
    # ========================================================

    print(
        "DEBUG: starting verification analysis"
    )

    try:

        # IMPORTANT:
        # Pass Path objects here.
        # Do NOT use str(document_path).
        # The verification module expects Path objects.

        analysis = analyze_verification(
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
            detail=f"Verification analysis failed: {error}"
        )

    # ========================================================
    # 11. RETURN COMPLETE RESULT
    # ========================================================

    print(
        "DEBUG: verification completed:",
        verification_id
    )

    return {

        "verification_id": verification_id,

        "status": "completed",

        "message": (
            "Document and live photo "
            "received and analyzed successfully"
        ),

        "document": document.filename,

        "photo": photo.filename,

        "ocr": document_analysis,

        "faceAnalysis": face_analysis,

        "tamperAnalysis": tamper_analysis,

        "analysis": analysis
    }