from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    title: str
    content: str

    model_config = ConfigDict(from_attributes=True)


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentRead(DocumentBase):
    id: int
    embedding: List[float]

    model_config = ConfigDict(from_attributes=True)
