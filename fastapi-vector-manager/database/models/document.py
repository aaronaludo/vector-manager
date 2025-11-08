"""Document model."""

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String, Text, JSON

from ..session import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    metadata_json = Column("metadata", JSON, nullable=True)
    embedding = Column(Vector(768), nullable=False)


Document.metadata = property(  # type: ignore[attr-defined]
    lambda self: self.metadata_json,
    lambda self, value: setattr(self, "metadata_json", value),
)
