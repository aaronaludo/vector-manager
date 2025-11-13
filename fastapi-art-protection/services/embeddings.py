from typing import List

import google.generativeai as genai

from database import settings


def _configure_client() -> None:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    genai.configure(api_key=settings.gemini_api_key)


def embed_text(text: str) -> List[float]:
    _configure_client()
    response = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
    )
    embedding = response.get("embedding")
    if embedding is None:
        raise RuntimeError("Embedding service did not return an embedding vector")
    return embedding
