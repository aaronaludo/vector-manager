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
