"""Document tagging router."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user_data
from ..models import Document, DocumentTag
from ..modules.documents.tagger import match_tags_to_filename
from ..schemas import DocumentTagSchema, DocumentWithTagsSchema

router = APIRouter(tags=["tags"])


@router.get("/tags", response_model=list[DocumentTagSchema])
def list_tags(db: Session = Depends(get_db)):
    """List all available document tags."""
    tags = db.query(DocumentTag).all()
    return tags


@router.post("/documents/auto-tag")
def auto_tag_documents(
    client_phone: str,
    year: int,
    tag_ids: Optional[list[int]] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """Auto-tag documents for a client/year combination."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can auto-tag documents")

    # Get all documents for this client/year
    documents = (
        db.query(Document)
        .filter(
            Document.client_phone == client_phone,
            Document.year == str(year),
            Document.is_deleted.is_(False),
        )
        .all()
    )

    if not documents:
        raise HTTPException(status_code=404, detail="No documents found for this client/year")

    # Get all tags for matching
    all_tags = db.query(DocumentTag).all()
    assigned_count = 0

    for doc in documents:
        # Skip if already tagged and not forcing re-tag
        if doc.is_tagged and not tag_ids:
            continue

        # Auto-tag based on filename
        match = match_tags_to_filename(doc.file_name, all_tags)

        if match:
            best_tag, confidence = match
            doc.tags.clear()
            doc.tags.append(best_tag)
            doc.is_tagged = True
            doc.tag_confidence = confidence
            assigned_count += 1

        # Or use manually specified tags
        if tag_ids:
            doc.tags.clear()
            for tag_id in tag_ids:
                tag = db.query(DocumentTag).filter(DocumentTag.id == tag_id).first()
                if tag:
                    doc.tags.append(tag)
            doc.is_tagged = True
            doc.tag_confidence = 0.9
            assigned_count += 1

    db.commit()

    return {
        "assigned_count": assigned_count,
        "total_documents": len(documents),
        "message": f"Auto-tagged {assigned_count} documents",
    }


@router.get("/documents/{document_id}/tags", response_model=list[DocumentTagSchema])
def get_document_tags(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """Get tags for a specific document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Verify access: CA can see all, client can only see their own
    if current_user.get("user_type") == "client":
        if doc.client_phone != current_user.get("phone_number"):
            raise HTTPException(status_code=403, detail="Unauthorized")

    return doc.tags


@router.post("/documents/{document_id}/tags", response_model=DocumentWithTagsSchema)
def add_document_tags(
    document_id: int,
    tag_ids: list[int],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """Add tags to a document (CA only)."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can modify tags")

    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Clear existing tags
    doc.tags.clear()

    # Add new tags
    for tag_id in tag_ids:
        tag = db.query(DocumentTag).filter(DocumentTag.id == tag_id).first()
        if tag:
            doc.tags.append(tag)

    doc.is_tagged = True
    db.commit()
    db.refresh(doc)

    return DocumentWithTagsSchema.from_orm(doc)


@router.delete("/documents/{document_id}/tags/{tag_id}")
def remove_document_tag(
    document_id: int,
    tag_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """Remove a specific tag from a document (CA only)."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can modify tags")

    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    tag = db.query(DocumentTag).filter(DocumentTag.id == tag_id).first()
    if tag and tag in doc.tags:
        doc.tags.remove(tag)
        db.commit()

    return {"status": "success", "message": "Tag removed"}
