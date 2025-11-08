from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    title: Optional[str] = None
    content: str
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentCreate(DocumentBase):
    title: str


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentRead(DocumentBase):
    id: int
    embedding: List[float]

    model_config = ConfigDict(from_attributes=True)
