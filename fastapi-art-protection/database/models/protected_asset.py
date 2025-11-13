from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from database.session import Base


class ProtectedAsset(Base):
    __tablename__ = "protected_assets"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    encrypted_watermark_id = Column(String(512), nullable=False)
    sha256 = Column(String(64), nullable=False)
    phash = Column(String(64), nullable=False)
    user_metadata = Column(JSONB, nullable=True)
    google_drive_url = Column(String, nullable=True)
    image_link = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
