from pathlib import Path
from typing import Any

import cv2

from app.ocr import load_document_image


# =========================================================
# FACE DETECTION
# =========================================================

def detect_faces(image_path: str) -> dict[str, Any]:
    """
    Detect faces and calculate basic image-quality signals.
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

        "faceCount": len(
            detected_faces
        ),

        "faces": detected_faces,

        "image": {
            "width": width,
            "height": height
        },

        "quality": {
            "sharpness": round(
                sharpness,
                2
            ),
            "brightness": round(
                brightness,
                2
            )
        }
    }


# =========================================================
# CROP FACE
# =========================================================

def crop_face(
    image_path: str,
    face: dict[str, Any]
):
    """
    Crop the detected face from an image.
    """

    image = load_document_image(str(image_path))

    x = int(face["x"])
    y = int(face["y"])
    w = int(face["width"])
    h = int(face["height"])

    height, width = image.shape[:2]

    # Add a small margin around the face.
    margin_x = int(w * 0.20)
    margin_y = int(h * 0.20)

    x1 = max(
        0,
        x - margin_x
    )

    y1 = max(
        0,
        y - margin_y
    )

    x2 = min(
        width,
        x + w + margin_x
    )

    y2 = min(
        height,
        y + h + margin_y
    )

    face_image = image[
        y1:y2,
        x1:x2
    ]

    if face_image.size == 0:
        raise ValueError(
            "Could not crop detected face."
        )

    return face_image


# =========================================================
# NORMALIZE FACE
# =========================================================

def normalize_face(
    face_image
):
    """
    Convert the face image to a normalized grayscale image.
    """

    gray = cv2.cvtColor(
        face_image,
        cv2.COLOR_BGR2GRAY
    )

    normalized = cv2.resize(
        gray,
        (200, 200),
        interpolation=cv2.INTER_AREA
    )

    normalized = cv2.equalizeHist(
        normalized
    )

    return normalized


# =========================================================
# FACE COMPARISON
# =========================================================

def compare_faces(
    document_path: str,
    photo_path: str,
    document_face: dict[str, Any],
    live_photo_face: dict[str, Any]
) -> dict[str, Any]:
    """
    Compare the document portrait with the live-photo face.

    This is an image-similarity screening method using
    ORB feature matching. It is NOT biometric identity
    verification.
    """

    if document_face.get(
        "status"
    ) != "usable":

        return {
            "success": False,
            "status": "not_comparable",
            "match": False,
            "score": 0.0,
            "reason": (
                "Document does not contain "
                "exactly one usable face."
            )
        }

    if live_photo_face.get(
        "status"
    ) != "usable":

        return {
            "success": False,
            "status": "not_comparable",
            "match": False,
            "score": 0.0,
            "reason": (
                "Live photo does not contain "
                "exactly one usable face."
            )
        }

    document_crop = crop_face(
        document_path,
        document_face["faces"][0]
    )

    live_photo_crop = crop_face(
        photo_path,
        live_photo_face["faces"][0]
    )

    document_normalized = normalize_face(
        document_crop
    )

    live_photo_normalized = normalize_face(
        live_photo_crop
    )

    # -----------------------------------------------------
    # ORB feature extraction
    # -----------------------------------------------------

    orb = cv2.ORB_create(
        nfeatures=500
    )

    keypoints_1, descriptors_1 = (
        orb.detectAndCompute(
            document_normalized,
            None
        )
    )

    keypoints_2, descriptors_2 = (
        orb.detectAndCompute(
            live_photo_normalized,
            None
        )
    )

    if descriptors_1 is None or descriptors_2 is None:

        return {
            "success": False,
            "status": "insufficient_features",
            "match": False,
            "score": 0.0,
            "reason": (
                "Insufficient visual features "
                "were available for comparison."
            )
        }

    if len(descriptors_1) < 2 or len(descriptors_2) < 2:

        return {
            "success": False,
            "status": "insufficient_features",
            "match": False,
            "score": 0.0,
            "reason": (
                "Insufficient visual features "
                "were available for comparison."
            )
        }

    # -----------------------------------------------------
    # Feature matching
    # -----------------------------------------------------

    matcher = cv2.BFMatcher(
        cv2.NORM_HAMMING,
        crossCheck=False
    )

    matches = matcher.knnMatch(
        descriptors_1,
        descriptors_2,
        k=2
    )

    good_matches = []

    for pair in matches:

        if len(pair) < 2:
            continue

        first, second = pair

        if first.distance < 0.75 * second.distance:

            good_matches.append(
                first
            )

    # -----------------------------------------------------
    # Calculate similarity score
    # -----------------------------------------------------

    feature_count = max(
        len(keypoints_1),
        len(keypoints_2),
        1
    )

    match_ratio = (
        len(good_matches)
        / feature_count
    )

    # Convert to a 0-100 screening score.
    score = min(
        100.0,
        match_ratio * 500.0
    )

    # Conservative threshold.
    is_match = score >= 25

    return {

        "success": True,

        "status": (
            "match"
            if is_match
            else "no_match"
        ),

        "match": is_match,

        "score": round(
            score,
            2
        ),

        "goodMatches": len(
            good_matches
        ),

        "documentFeatures": len(
            keypoints_1
        ),

        "livePhotoFeatures": len(
            keypoints_2
        ),

        "reason": (
            "The document portrait and live photo "
            "show sufficient visual similarity."
            if is_match
            else
            "The document portrait and live photo "
            "did not show sufficient visual similarity."
        ),

        "method": (
            "OpenCV ORB feature similarity screening"
        ),

        "biometricVerification": False
    }


# =========================================================
# COMPLETE FACE ANALYSIS
# =========================================================

def analyze_face_inputs(
    document_path: str,
    photo_path: str
) -> dict[str, Any]:

    # -----------------------------------------------------
    # Detect document face
    # -----------------------------------------------------

    document_result = detect_faces(
        document_path
    )

    # -----------------------------------------------------
    # Detect live-photo face
    # -----------------------------------------------------

    photo_result = detect_faces(
        photo_path
    )

    document_usable = (
        document_result["status"]
        == "usable"
    )

    photo_usable = (
        photo_result["status"]
        == "usable"
    )

    # -----------------------------------------------------
    # Compare faces
    # -----------------------------------------------------

    face_match = compare_faces(
        document_path=document_path,
        photo_path=photo_path,
        document_face=document_result,
        live_photo_face=photo_result
    )

    # -----------------------------------------------------
    # Final biometric-review readiness
    # -----------------------------------------------------

    ready_for_review = (
        document_usable
        and photo_usable
        and face_match.get(
            "success",
            False
        )
    )

    return {

        "faceAnalysis": {

            "document": document_result,

            "livePhoto": photo_result,

            "documentFaceUsable": (
                document_usable
            ),

            "livePhotoFaceUsable": (
                photo_usable
            ),

            "faceMatch": face_match,

            "readyForBiometricReview": (
                ready_for_review
            )
        }
    }