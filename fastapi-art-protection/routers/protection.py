from __future__ import annotations

import base64
import json
import uuid
from typing import Any, Dict

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from database import get_db
from database.models.protected_asset import ProtectedAsset
from schemas import ProtectedAssetResponse
from services.crypto import encrypt_watermark_id
from services.watermark import compute_phash, compute_sha256, embed_invisible_watermark

router = APIRouter(prefix="/protection", tags=["protection"])

SUPPORTED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


@router.post(
    "/upload",
    response_model=ProtectedAssetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_protected_image(
    image: UploadFile = File(...),
    metadata: str | None = Form(default=None, description="JSON encoded metadata"),
    google_drive_url: str | None = Form(None),
    db: Session = Depends(get_db),
) -> ProtectedAssetResponse:
    """Embed a watermark, store encrypted identifiers, and return the protected image."""
    if image.content_type not in SUPPORTED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type: {image.content_type}",
        )

    raw_bytes = await image.read()
    if not raw_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    user_metadata = _parse_metadata(metadata)
    watermark_id = str(uuid.uuid4())

    watermarked_bytes = embed_invisible_watermark(raw_bytes, watermark_id)
    sha256_digest = compute_sha256(watermarked_bytes)
    phash_value = compute_phash(watermarked_bytes)
    encrypted_identifier = encrypt_watermark_id(watermark_id)

    asset = ProtectedAsset(
        encrypted_watermark_id=encrypted_identifier,
        sha256=sha256_digest,
        phash=phash_value,
        user_metadata=user_metadata,
        google_drive_url=google_drive_url,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    encoded_image = base64.b64encode(watermarked_bytes).decode("utf-8")
    return ProtectedAssetResponse(
        asset_id=asset.id,
        encrypted_watermark_id=asset.encrypted_watermark_id,
        sha256=asset.sha256,
        phash=asset.phash,
        google_drive_url=asset.google_drive_url,
        user_metadata=asset.user_metadata,
        watermarked_image_b64=encoded_image,
    )


def _parse_metadata(metadata: str | None) -> Dict[str, Any] | None:
    if metadata in (None, "", "null"):
        return None
    try:
        parsed = json.loads(metadata)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="metadata must be valid JSON",
        ) from exc
    if not isinstance(parsed, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="metadata must be a JSON object",
        )
    return parsed
