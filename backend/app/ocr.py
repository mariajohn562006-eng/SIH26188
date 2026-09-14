import os
import shutil
from pathlib import Path
from typing import Any

import cv2
import pytesseract

from app.mrz import detect_mrz, parse_passport_mrz


# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

TESSERACT_CANDIDATES = [
    shutil.which("tesseract"),
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]

TESSERACT_PATH = next(
    (
        Path(candidate)
        for candidate in TESSERACT_CANDIDATES
        if candidate and Path(candidate).exists()
    ),
    None,
)

if TESSERACT_PATH is None:
    raise RuntimeError(
        "Tesseract executable not found. Install Tesseract OCR and ensure "
        "C:\\Program Files\\Tesseract-OCR\\tesseract.exe is available."
    )

os.environ["PATH"] = (
    str(TESSERACT_PATH.parent) + os.pathsep + os.environ.get("PATH", "")
).strip(os.pathsep)

pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_PATH)


# Verify that Python can actually execute Tesseract
try:
    tesseract_version = pytesseract.get_tesseract_version()
    print("DEBUG: Tesseract detected:", tesseract_version)
except Exception as error:
    print("DEBUG: Tesseract test failed:", error)
    raise RuntimeError(
        f"Tesseract is installed but Python could not execute it: {error}"
    )


# ============================================================
# IMAGE LOADING
# ============================================================

def load_document_image(image_path: str):
    """
    Load the uploaded document image using OpenCV.
    """

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document file not found: {image_path}"
        )

    image = cv2.imread(str(path))

    if image is None:
        raise ValueError(
            f"Could not read document image: {image_path}. "
            f"Unsupported or corrupted image format."
        )

    return image


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image_path: str):
    """
    Prepare the document image for OCR.
    """

    image = load_document_image(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Increase resolution
    gray = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    # Reduce noise
    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    # Automatic thresholding
    threshold = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    return threshold


# ============================================================
# OCR TEXT EXTRACTION
# ============================================================

def extract_text(image_path: str) -> str:
    """
    Extract text from the document using Tesseract OCR.
    """

    image = preprocess_image(image_path)

    text = pytesseract.image_to_string(
        image,
        config="--psm 6"
    )

    return text.strip()


# ============================================================
# DOCUMENT ANALYSIS
# ============================================================

def analyze_document(document_path: str) -> dict[str, Any]:
    """
    Complete document analysis.

    Steps:
        1. Validate document
        2. Load image
        3. Run OCR
        4. Detect MRZ
        5. Parse MRZ
    """

    path = Path(document_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document file not found: {document_path}"
        )

    # Make sure OpenCV can read the image
    image = load_document_image(
        str(path)
    )

    height, width = image.shape[:2]

    if width <= 0 or height <= 0:
        raise ValueError(
            "Document image has invalid dimensions"
        )

    print(
        "DEBUG: document image loaded:",
        width,
        "x",
        height
    )

    # --------------------------------------------------------
    # OCR
    # --------------------------------------------------------

    print("DEBUG: extracting OCR text")

    text = extract_text(
        str(path)
    )

    print(
        "DEBUG: OCR text length:",
        len(text)
    )

    # --------------------------------------------------------
    # MRZ DETECTION
    # --------------------------------------------------------

    print("DEBUG: detecting MRZ")

    mrz = detect_mrz(text)

    parsed_mrz = {
        "success": False,
        "reason": "MRZ not detected"
    }

    if mrz["detected"]:
        print("DEBUG: MRZ detected")

        parsed_mrz = parse_passport_mrz(
            mrz["lines"]
        )

    else:
        print("DEBUG: MRZ not detected")

    # --------------------------------------------------------
    # RETURN RESULT
    # --------------------------------------------------------

    return {
        "document": {
            "filename": path.name,
            "width": width,
            "height": height,
            "format": path.suffix.lower()
        },

        "ocr": {
            "success": bool(text),
            "text": text,
            "textLength": len(text)
        },

        "mrz": {
            "detected": mrz["detected"],
            "lines": mrz["lines"],
            "parsed": parsed_mrz
        }
    }