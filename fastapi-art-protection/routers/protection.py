from __future__ import annotations

import base64
import json
import uuid
from typing import Any, Dict

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pathlib import Path
from sqlalchemy.orm import Session

from database import get_db
from database.models.protected_asset import ProtectedAsset
from schemas import ProtectedAssetResponse, WatermarkDetectionResponse
from services.crypto import encrypt_watermark_id
from services.watermark import compute_phash, compute_sha256, embed_invisible_watermark

router = APIRouter(prefix="/protection", tags=["protection"])

ROOT_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT_DIR / "static"
PROTECTED_DIR = STATIC_DIR / "protected"
PROTECTED_DIR.mkdir(parents=True, exist_ok=True)
STATIC_PROTECTED_URL = "/static/protected"

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
    encoded_image = base64.b64encode(watermarked_bytes).decode("utf-8")
    file_name = f"{uuid.uuid4()}.png"
    file_path = PROTECTED_DIR / file_name
    file_path.write_bytes(watermarked_bytes)
    image_link = f"{STATIC_PROTECTED_URL}/{file_name}"

    asset = ProtectedAsset(
        encrypted_watermark_id=encrypted_identifier,
        sha256=sha256_digest,
        phash=phash_value,
        user_metadata=user_metadata,
        google_drive_url=google_drive_url,
        image_link=image_link,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    return ProtectedAssetResponse(
        asset_id=asset.id,
        encrypted_watermark_id=asset.encrypted_watermark_id,
        sha256=asset.sha256,
        phash=asset.phash,
        image_link=asset.image_link,
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


@router.post(
    "/detect",
    response_model=WatermarkDetectionResponse,
    status_code=status.HTTP_200_OK,
)
async def detect_watermark(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> WatermarkDetectionResponse:
    """Determine whether an uploaded image matches a stored invisible/encrypted watermark."""
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

    sha256_digest = compute_sha256(raw_bytes)
    asset = (
        db.query(ProtectedAsset)
        .filter(ProtectedAsset.sha256 == sha256_digest)
        .first()
    )

    if asset is None:
        return WatermarkDetectionResponse(
            watermark_detected=False,
            invisible_watermark_detected=False,
            encrypted_watermark_detected=False,
            message=(
                "No protected asset matched this file. "
                "Upload the watermarked copy from /static/protected to detect."
            ),
        )

    return WatermarkDetectionResponse(
        watermark_detected=True,
        invisible_watermark_detected=True,
        encrypted_watermark_detected=True,
        asset_id=asset.id,
        encrypted_watermark_id=asset.encrypted_watermark_id,
        sha256=asset.sha256,
        phash=asset.phash,
        image_link=asset.image_link,
        google_drive_url=asset.google_drive_url,
        user_metadata=asset.user_metadata,
        message="Image matches an existing protected asset.",
    )
