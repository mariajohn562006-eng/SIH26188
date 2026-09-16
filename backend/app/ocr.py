from pathlib import Path
from typing import Any

import cv2
import pytesseract
import fitz

from app.mrz import detect_mrz, parse_passport_mrz


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
        "DEBUG: Tesseract detected:",
        tesseract_version
    )
except Exception as error:
    print(
        "DEBUG: Tesseract test failed:",
        error
    )
    raise RuntimeError(
        f"Tesseract is installed but Python could not execute it: {error}"
    )


def load_document_image(
    image_path: str
):
    """
    Load JPG/PNG directly.

    If the document is a PDF, render the first
    page into an OpenCV image.
    """

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document file not found: {image_path}"
        )

    extension = path.suffix.lower()

    # --------------------------------------------------
    # PDF
    # --------------------------------------------------

    if extension == ".pdf":

        try:
            pdf = fitz.open(str(path))

            if pdf.page_count == 0:
                pdf.close()
                raise ValueError(
                    "PDF does not contain any pages."
                )

            page = pdf.load_page(0)

            # Render PDF page at higher resolution
            matrix = fitz.Matrix(2, 2)

            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )

            image_bytes = pixmap.tobytes(
                "png"
            )

            pdf.close()

            # Convert PNG bytes to OpenCV image
            import numpy as np

            image_array = np.frombuffer(
                image_bytes,
                dtype=np.uint8
            )

            image = cv2.imdecode(
                image_array,
                cv2.IMREAD_COLOR
            )

            if image is None:
                raise ValueError(
                    "Could not convert PDF page to image."
                )

            return image

        except Exception as error:
            raise ValueError(
                f"Could not read PDF document: {error}"
            )


    # --------------------------------------------------
    # NORMAL IMAGE
    # --------------------------------------------------

    image = cv2.imread(
        str(path)
    )

    if image is None:
        raise ValueError(
            f"Could not read document image: {image_path}. "
            f"Unsupported or corrupted image format."
        )

    return image


def preprocess_image(
    image_path: str
):
    image = load_document_image(
        image_path
    )

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    threshold = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    return threshold


def extract_text(
    image_path: str
) -> str:

    image = preprocess_image(
        image_path
    )

    text = pytesseract.image_to_string(
        image,
        config="--psm 6"
    )

    return text.strip()


def analyze_document(
    document_path: str
) -> dict[str, Any]:

    path = Path(
        document_path
    )

    if not path.exists():
        raise FileNotFoundError(
            f"Document file not found: {document_path}"
        )

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

    print(
        "DEBUG: extracting OCR text"
    )

    text = extract_text(
        str(path)
    )

    print(
        "DEBUG: OCR text length:",
        len(text)
    )

    print(
        "DEBUG: detecting MRZ"
    )

    mrz = detect_mrz(
        text
    )

    parsed_mrz = {
        "success": False,
        "reason": "MRZ not detected"
    }

    if mrz["detected"]:

        print(
            "DEBUG: MRZ detected"
        )

        parsed_mrz = parse_passport_mrz(
            mrz["lines"]
        )

    else:

        print(
            "DEBUG: MRZ not detected"
        )

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