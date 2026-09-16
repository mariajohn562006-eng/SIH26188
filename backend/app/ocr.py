from pathlib import Path
from typing import Any

import cv2
import fitz
import pytesseract

from app.document_type import detect_document_type
from app.mrz import detect_mrz, parse_passport_mrz


# =========================================================
# TESSERACT CONFIGURATION
# =========================================================

TESSERACT_PATH = Path(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

if not TESSERACT_PATH.exists():
    raise RuntimeError(
        f"Tesseract executable not found at: {TESSERACT_PATH}"
    )

pytesseract.pytesseract.tesseract_cmd = str(
    TESSERACT_PATH
)

try:
    tesseract_version = pytesseract.get_tesseract_version()
    print(
        f"DEBUG: Tesseract version detected: "
        f"{tesseract_version}"
    )
except Exception as error:
    print(
        f"WARNING: Could not determine Tesseract version: "
        f"{error}"
    )


# =========================================================
# LOAD DOCUMENT IMAGE
# =========================================================

def load_document_image(
    file_path: str | Path,
):
    """
    Load an image or the first page of a PDF.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document file not found: {path}"
        )

    suffix = path.suffix.lower()

    # -----------------------------------------------------
    # PDF
    # -----------------------------------------------------

    if suffix == ".pdf":

        pdf = fitz.open(str(path))

        if len(pdf) == 0:
            pdf.close()

            raise ValueError(
                "PDF contains no pages."
            )

        page = pdf[0]

        # Render PDF at higher resolution for OCR.
        matrix = fitz.Matrix(2, 2)

        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False,
        )

        width = pixmap.width
        height = pixmap.height

        image = cv2.imdecode(
            __import__("numpy").frombuffer(
                pixmap.tobytes("png"),
                dtype=__import__("numpy").uint8,
            ),
            cv2.IMREAD_COLOR,
        )

        pdf.close()

        if image is None:
            raise ValueError(
                "Unable to convert PDF page to image."
            )

        return image

    # -----------------------------------------------------
    # Normal image
    # -----------------------------------------------------

    image = cv2.imread(
        str(path),
        cv2.IMREAD_COLOR,
    )

    if image is None:
        raise ValueError(
            f"Unable to read image file: {path}"
        )

    return image


# =========================================================
# IMAGE PREPROCESSING
# =========================================================

def preprocess_image(image):
    """
    Prepare image for OCR.
    """

    if image is None:
        raise ValueError(
            "Cannot preprocess an empty image."
        )

    # Convert to grayscale
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY,
    )

    # Enlarge image for better OCR
    resized = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC,
    )

    # Reduce small noise
    blurred = cv2.GaussianBlur(
        resized,
        (3, 3),
        0,
    )

    # Adaptive threshold is generally more tolerant
    # of uneven passport/document lighting.
    thresholded = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )[1]

    return thresholded


# =========================================================
# OCR
# =========================================================

def extract_text(image) -> str:
    """
    Extract text using Tesseract OCR.
    """

    processed = preprocess_image(image)

    text = pytesseract.image_to_string(
        processed,
        config="--psm 6",
    )

    return text or ""


# =========================================================
# DOCUMENT ANALYSIS
# =========================================================

def analyze_document(
    file_path: str | Path,
) -> dict[str, Any]:
    """
    Analyze a document using OCR, document-type detection,
    and MRZ detection.

    Important:
    MRZ detection happens BEFORE the final document-type
    decision. This allows passports to be detected even when
    OCR fails to recognize the word 'PASSPORT'.
    """

    path = Path(file_path)

    # -----------------------------------------------------
    # Load image
    # -----------------------------------------------------

    try:
        image = load_document_image(path)

    except Exception as error:

        return {
            "document": {
                "filename": path.name,
            },

            "documentType": {
                "type": "unknown",
                "displayName": "Unknown Document",
                "confidence": "low",
                "reason": (
                    f"Unable to load document: {error}"
                ),
            },

            "ocr": {
                "success": False,
                "text": "",
                "reason": str(error),
            },

            "mrz": {
                "required": False,
                "detected": False,
                "status": "not required",
                "lines": [],
                "parsed": {
                    "success": False,
                    "reason": (
                        "Document could not be loaded."
                    ),
                },
            },
        }

    # -----------------------------------------------------
    # OCR
    # -----------------------------------------------------

    try:
        ocr_text = extract_text(image)

    except Exception as error:

        ocr_text = ""

        print(
            f"WARNING: OCR failed for "
            f"{path.name}: {error}"
        )

    ocr_success = bool(
        ocr_text.strip()
    )

    # -----------------------------------------------------
    # MRZ DETECTION
    # -----------------------------------------------------
    #
    # IMPORTANT:
    # Detect MRZ BEFORE document type.
    #
    # This means:
    #
    # OCR misses "PASSPORT"
    #          ↓
    # MRZ still detected
    #          ↓
    # Document classified as Passport
    #
    # -----------------------------------------------------

    try:
        mrz = detect_mrz(
            ocr_text
        )

    except Exception as error:

        print(
            f"WARNING: MRZ detection failed: {error}"
        )

        mrz = {
            "detected": False,
            "lines": [],
            "confidence": "low",
            "reason": str(error),
        }

    # -----------------------------------------------------
    # DOCUMENT TYPE
    # -----------------------------------------------------

    try:

        document_type = detect_document_type(
            ocr_text=ocr_text,
            filename=path.name,
        )

    except Exception as error:

        print(
            f"WARNING: Document type detection failed: "
            f"{error}"
        )

        document_type = {
            "type": "unknown",
            "displayName": "Unknown Document",
            "confidence": "low",
            "reason": str(error),
        }

    # -----------------------------------------------------
    # MRZ OVERRIDES DOCUMENT TYPE
    # -----------------------------------------------------

    if mrz.get("detected", False):

        document_type = {
            "type": "passport",
            "displayName": "Passport",
            "confidence": mrz.get(
                "confidence",
                "medium",
            ),
            "reason": (
                "Passport detected from MRZ."
            ),
        }

        print(
            "DEBUG: Passport detected from MRZ."
        )

    else:

        print(
            "DEBUG: No MRZ detected."
        )

    # -----------------------------------------------------
    # DEBUG DOCUMENT TYPE
    # -----------------------------------------------------

    print(
        f"DEBUG: Detected document type: "
        f"{document_type.get('type', 'unknown')}"
    )

    # -----------------------------------------------------
    # PASSPORT MRZ PROCESSING
    # -----------------------------------------------------

    if document_type.get("type") == "passport":

        parsed_mrz = {
            "success": False,
            "reason": "MRZ not detected.",
        }

        if mrz.get("detected", False):

            try:

                parsed_mrz = parse_passport_mrz(
                    mrz.get(
                        "lines",
                        [],
                    )
                )

            except Exception as error:

                print(
                    f"WARNING: Passport MRZ parsing "
                    f"failed: {error}"
                )

                parsed_mrz = {
                    "success": False,
                    "reason": str(error),
                }

        # -------------------------------------------------
        # MRZ STATUS
        # -------------------------------------------------

        if mrz.get("detected", False):

            if parsed_mrz.get(
                "success",
                False,
            ):

                mrz_status = "verified"

            else:

                # MRZ exists but parser could not completely
                # validate it. Do NOT treat it as missing.
                mrz_status = "detected"

        else:

            mrz_status = "failed"

        mrz_result = {

            "required": True,

            "detected": mrz.get(
                "detected",
                False,
            ),

            "status": mrz_status,

            "confidence": mrz.get(
                "confidence",
                "low",
            ),

            "lines": mrz.get(
                "lines",
                [],
            ),

            "parsed": parsed_mrz,
        }

    # -----------------------------------------------------
    # NON-PASSPORT DOCUMENT
    # -----------------------------------------------------

    else:

        mrz_result = {

            "required": False,

            "detected": False,

            "status": "not required",

            "lines": [],

            "parsed": {

                "success": False,

                "reason": (
                    "MRZ is not required for this "
                    "document type."
                ),
            },
        }

    # -----------------------------------------------------
    # FINAL RESULT
    # -----------------------------------------------------

    return {

        "document": {

            "filename": path.name,

            "width": int(
                image.shape[1]
            ),

            "height": int(
                image.shape[0]
            ),

            "format": path.suffix.lower(),
        },

        "documentType": document_type,

        "ocr": {

            "success": ocr_success,

            "text": ocr_text,
        },

        "mrz": mrz_result,
    }