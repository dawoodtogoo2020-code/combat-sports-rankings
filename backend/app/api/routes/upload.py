"""
Media upload endpoint for social post attachments.

Stores files to local filesystem (configurable to S3 later).
Returns URLs for inclusion in post media_urls.
"""

import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from app.models.user import User
from app.middleware.auth import get_current_active_user

router = APIRouter()

UPLOAD_DIR = Path("uploads/media")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime"}
ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("/media")
async def upload_media(
    file: UploadFile = File(...),
    user: User = Depends(get_current_active_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file.content_type}' not allowed. Accepted: images (JPEG, PNG, WebP, GIF) and videos (MP4, MOV).",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds 50MB limit.",
        )

    # Generate unique filename preserving extension
    ext = os.path.splitext(file.filename or "file")[1] or ".bin"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as f:
        f.write(contents)

    # Return URL relative to API — in production this would be a CDN/S3 URL
    return {
        "url": f"/uploads/media/{filename}",
        "filename": filename,
        "content_type": file.content_type,
        "size": len(contents),
    }
