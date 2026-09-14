from pathlib import Path
from typing import Any

import cv2


def analyze_tampering(image_path: str) -> dict[str, Any]:
    """
    Basic document-image integrity analysis.

    This module checks image-level characteristics such as:
    - image readability
    - dimensions
    - blur
    - brightness
    - edge density

    It does not claim that a document is genuine or fake.
    """

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document file not found: {image_path}"
        )

    image = cv2.imread(str(path))

    if image is None:
        raise ValueError(
            f"Could not read image: {image_path}"
        )

    height, width = image.shape[:2]

    if width <= 0 or height <= 0:
        raise ValueError(
            "Invalid document image dimensions"
        )

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Blur/sharpness measurement
    sharpness = float(
        cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()
    )

    # Brightness
    brightness = float(gray.mean())

    # Edge density
    edges = cv2.Canny(
        gray,
        100,
        200
    )

    edge_density = float(
        (edges > 0).mean()
    )

    # Basic quality classification
    warnings = []

    if sharpness < 50:
        warnings.append("Image may be blurry")

    if brightness < 40:
        warnings.append("Image may be too dark")

    if brightness > 220:
        warnings.append("Image may be overexposed")

    if edge_density < 0.01:
        warnings.append(
            "Document structure is difficult to detect"
        )

    return {
        "success": True,

        "image": {
            "width": width,
            "height": height,
            "format": path.suffix.lower()
        },

        "quality": {
            "sharpness": round(sharpness, 2),
            "brightness": round(brightness, 2),
            "edgeDensity": round(edge_density, 4)
        },

        "tamperAnalysis": {
            "warnings": warnings,
            "warningCount": len(warnings),
            "reviewRequired": len(warnings) > 0
        }
    }