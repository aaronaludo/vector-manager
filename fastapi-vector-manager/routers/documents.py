from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import Document, get_db
from schemas import DocumentCreate, DocumentRead, DocumentUpdate
from services import embed_text

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
def create_document(
    document_in: DocumentCreate, db: Session = Depends(get_db)
) -> DocumentRead:
    try:
        embedding = embed_text(document_in.content)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)
        ) from exc

    document = Document(
        title=document_in.title,
        content=document_in.content,
        metadata=document_in.metadata,
        embedding=embedding,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("/", response_model=List[DocumentRead])
def list_documents(db: Session = Depends(get_db)) -> List[DocumentRead]:
    return db.query(Document).all()


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(document_id: int, db: Session = Depends(get_db)) -> DocumentRead:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return document


@router.put("/{document_id}", response_model=DocumentRead)
def update_document(
    document_id: int, document_in: DocumentUpdate, db: Session = Depends(get_db)
) -> DocumentRead:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if document_in.title is not None:
        document.title = document_in.title
    if document_in.content is not None:
        document.content = document_in.content
        try:
            document.embedding = embed_text(document.content)
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)
            ) from exc
    if "metadata" in document_in.model_fields_set:
        document.metadata = document_in.metadata

    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)) -> None:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    db.delete(document)
    db.commit()
