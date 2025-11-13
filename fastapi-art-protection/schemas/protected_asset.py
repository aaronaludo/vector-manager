from __future__ import annotations

from typing import Any, Dict
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel


class ProtectedAssetResponse(BaseModel):
    asset_id: UUID
    encrypted_watermark_id: str
    sha256: str
    phash: str
    image_link: str | None = None
    google_drive_url: AnyHttpUrl | None = None
    user_metadata: Dict[str, Any] | None = None
    watermarked_image_b64: str


class WatermarkDetectionResponse(BaseModel):
    watermark_detected: bool
    invisible_watermark_detected: bool
    encrypted_watermark_detected: bool
    asset_id: UUID | None = None
    encrypted_watermark_id: str | None = None
    sha256: str | None = None
    phash: str | None = None
    image_link: str | None = None
    google_drive_url: AnyHttpUrl | None = None
    user_metadata: Dict[str, Any] | None = None
    message: str
