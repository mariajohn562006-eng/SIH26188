from pathlib import Path
from typing import Any

import cv2

from app.ocr import load_document_image


def detect_faces(image_path: str) -> dict[str, Any]:
    """
    Detect faces using OpenCV's built-in Haar cascade.
    """

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Image file not found: {image_path}"
        )

    image = load_document_image(str(path))

    height, width = image.shape[:2]

    if width <= 0 or height <= 0:
        raise ValueError(
            "Image has invalid dimensions"
        )

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Load OpenCV's face detector
    cascade_path = (
        cv2.data.haarcascades
        + "haarcascade_frontalface_default.xml"
    )

    face_detector = cv2.CascadeClassifier(
        cascade_path
    )

    if face_detector.empty():
        raise RuntimeError(
            "OpenCV face detector could not be loaded"
        )

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )

    detected_faces = []

    for x, y, w, h in faces:
        detected_faces.append({
            "x": int(x),
            "y": int(y),
            "width": int(w),
            "height": int(h)
        })

    sharpness = float(
        cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()
    )

    brightness = float(
        gray.mean()
    )

    if len(detected_faces) == 0:
        status = "no_face"
    elif len(detected_faces) > 1:
        status = "multiple_faces"
    else:
        status = "usable"

    return {
        "success": True,
        "status": status,
        "faceCount": len(detected_faces),
        "faces": detected_faces,
        "image": {
            "width": width,
            "height": height
        },
        "quality": {
            "sharpness": round(sharpness, 2),
            "brightness": round(brightness, 2)
        }
    }


def analyze_face_inputs(
    document_path: str,
    photo_path: str
) -> dict[str, Any]:

    document_result = detect_faces(
        document_path
    )

    photo_result = detect_faces(
        photo_path
    )

    document_usable = (
        document_result["status"] == "usable"
    )

    photo_usable = (
        photo_result["status"] == "usable"
    )

    return {
        "faceAnalysis": {
            "document": document_result,
            "livePhoto": photo_result,
            "documentFaceUsable": document_usable,
            "livePhotoFaceUsable": photo_usable,
            "readyForBiometricReview": (
                document_usable
                and photo_usable
            )
        }
    }