from __future__ import annotations

import hashlib
import math
from functools import lru_cache
from io import BytesIO
from typing import Iterable, List

import numpy as np
from PIL import Image


def embed_invisible_watermark(
    image_bytes: bytes, watermark_id: str, *, strength: float = 3.0
) -> bytes:
    """Embed a spread-spectrum style watermark into the luminance channel."""
    if not image_bytes:
        raise ValueError("image_bytes cannot be empty")

    with Image.open(BytesIO(image_bytes)) as image:
        image = image.convert("YCbCr")
        luminance, cb, cr = image.split()
        y_channel = np.asarray(luminance, dtype=np.float32)

    bitstream = _watermark_bits(watermark_id)
    rng_seed = int(hashlib.sha256(watermark_id.encode("utf-8")).hexdigest(), 16)
    rng = np.random.default_rng(rng_seed)

    for idx, bit in enumerate(bitstream):
        mask = rng.normal(size=y_channel.shape).astype(np.float32)
        norm = np.linalg.norm(mask)
        if norm == 0:
            continue
        mask /= norm
        direction = 1.0 if bit else -1.0
        y_channel += direction * strength * mask

    y_channel = np.clip(y_channel, 0, 255).astype(np.uint8)
    watermarked_image = Image.merge(
        "YCbCr",
        (
            Image.fromarray(y_channel, mode="L"),
            cb,
            cr,
        ),
    ).convert("RGB")

    buffer = BytesIO()
    watermarked_image.save(buffer, format="PNG")
    return buffer.getvalue()


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_phash(image_bytes: bytes) -> str:
    """Compute a perceptual hash using a DCT-based pHash implementation."""
    with Image.open(BytesIO(image_bytes)) as image:
        grayscale = image.convert("L").resize((32, 32), Image.Resampling.LANCZOS)
        matrix = np.asarray(grayscale, dtype=np.float32)

    dct_matrix = _dct2(matrix)
    low_freq = dct_matrix[:8, :8].copy()
    low_freq[0, 0] = 0  # Ignore the DC component
    median = np.median(low_freq)
    bits = (low_freq > median).astype(int).flatten()
    return _bits_to_hex(bits)


def _watermark_bits(watermark_id: str) -> List[int]:
    digest = hashlib.sha256(watermark_id.encode("utf-8")).digest()
    bits: List[int] = []
    for byte in digest:
        for shift in range(7, -1, -1):
            bits.append((byte >> shift) & 1)
    return bits


def _bits_to_hex(bits: Iterable[int]) -> str:
    value = 0
    count = 0
    for bit in bits:
        value = (value << 1) | int(bit)
        count += 1
    width = max(1, count // 4)
    return f"{value:0{width}x}"


@lru_cache(maxsize=8)
def _dct_basis(size: int) -> np.ndarray:
    n = np.arange(size)
    k = n.reshape(-1, 1)
    transform = np.cos((math.pi / size) * (n + 0.5) * k)
    transform[0, :] *= math.sqrt(1 / size)
    transform[1:, :] *= math.sqrt(2 / size)
    return transform


def _dct2(block: np.ndarray) -> np.ndarray:
    if block.shape[0] != block.shape[1]:
        raise ValueError("Only square matrices are supported for pHash computation")
    basis = _dct_basis(block.shape[0])
    return basis @ block @ basis.T
