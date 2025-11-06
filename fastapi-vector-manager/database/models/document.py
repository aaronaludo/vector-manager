"""Document model."""

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String, Text

from ..session import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    # text-embedding-004 returns 768-dimensional vectors
    embedding = Column(Vector(768), nullable=False)
