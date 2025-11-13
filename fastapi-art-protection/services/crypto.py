from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from database import settings


def _get_cipher() -> Fernet:
    key = settings.watermark_encryption_key
    if not key:
        raise RuntimeError("WATERMARK_ENCRYPTION_KEY is not configured")
    return Fernet(key.encode("utf-8"))


def encrypt_watermark_id(watermark_id: str) -> str:
    cipher = _get_cipher()
    token = cipher.encrypt(watermark_id.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_watermark_id(token: str) -> str:
    cipher = _get_cipher()
    try:
        decrypted = cipher.decrypt(token.encode("utf-8"))
    except InvalidToken as exc:
        raise ValueError("Failed to decrypt watermark ID") from exc
    return decrypted.decode("utf-8")
