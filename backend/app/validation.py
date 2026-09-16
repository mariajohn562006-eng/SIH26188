from pathlib import Path
from fastapi import HTTPException, UploadFile


MAX_DOCUMENT_SIZE = 10 * 1024 * 1024
MAX_PHOTO_SIZE = 10 * 1024 * 1024


ALLOWED_DOCUMENT_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".pdf",
}

ALLOWED_PHOTO_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
}


ALLOWED_DOCUMENT_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "application/pdf",
}

ALLOWED_PHOTO_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
}


def validate_filename(
    file: UploadFile,
    field_name: str
) -> None:
    """
    Validate that the uploaded file has a safe filename.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} file is required."
        )

    filename = Path(file.filename).name

    if filename != file.filename:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name} filename."
        )


def validate_document(
    document: UploadFile,
    content: bytes
) -> None:
    """
    Validate the uploaded identity document.
    """

    validate_filename(
        document,
        "Document"
    )

    extension = Path(
        document.filename
    ).suffix.lower()

    if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported document format. "
                "Allowed formats: JPG, JPEG, PNG and PDF."
            )
        )

    if (
        document.content_type
        and document.content_type
        not in ALLOWED_DOCUMENT_CONTENT_TYPES
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported document content type: "
                f"{document.content_type}"
            )
        )

    if len(content) > MAX_DOCUMENT_SIZE:
        raise HTTPException(
            status_code=413,
            detail=(
                "Document is too large. "
                "Maximum allowed size is 10 MB."
            )
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded document is empty."
        )


def validate_photo(
    photo: UploadFile,
    content: bytes
) -> None:
    """
    Validate the uploaded live photo.
    """

    validate_filename(
        photo,
        "Live photo"
    )

    extension = Path(
        photo.filename
    ).suffix.lower()

    if extension not in ALLOWED_PHOTO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported photo format. "
                "Allowed formats: JPG, JPEG and PNG."
            )
        )

    if (
        photo.content_type
        and photo.content_type
        not in ALLOWED_PHOTO_CONTENT_TYPES
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported photo content type: "
                f"{photo.content_type}"
            )
        )

    if len(content) > MAX_PHOTO_SIZE:
        raise HTTPException(
            status_code=413,
            detail=(
                "Live photo is too large. "
                "Maximum allowed size is 10 MB."
            )
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded photo is empty."
        )


def validate_image_file(
    file_path: Path
) -> None:
    """
    Confirm that a saved file exists and is not empty.
    """

    if not file_path.exists():
        raise HTTPException(
            status_code=400,
            detail=(
                f"Uploaded file could not be saved: "
                f"{file_path.name}"
            )
        )

    if file_path.stat().st_size == 0:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Uploaded file is empty: "
                f"{file_path.name}"
            )
        )


def format_error(
    module_name: str,
    error: Exception
) -> str:
    """
    Convert an internal exception into a readable
    backend error message.
    """

    message = str(error).strip()

    if not message:
        message = "Unknown error"

    return f"{module_name} failed: {message}"