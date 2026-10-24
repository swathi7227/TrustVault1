from fastapi.responses import FileResponse
import os
from pathlib import Path
from uuid import uuid4
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.auth.dependencies import CurrentUser
from backend.app.db.dependencies import get_db
from backend.app.models.database import AuditLog, Document, DocumentPermission
from backend.app.schemas.documents import (
    DocumentPermissionRequest,
    DocumentPermissionResponse,
    DocumentResponse,
)

router = APIRouter(prefix="/documents", tags=["Documents"])

# Store files outside the source-code directory.
STORAGE_DIR = Path("private_storage").resolve()
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_TYPES = {"text/plain", "application/pdf"}


def write_audit(
    db: Session,
    user_id: int,
    action: str,
    resource_id: str | None,
    outcome: str,
) -> None:
    db.add(
        AuditLog(
            actor_user_id=user_id,
            action=action,
            resource_type="document",
            resource_id=resource_id,
            outcome=outcome,
        )
    )


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    file: Annotated[UploadFile, File(...)],
    title: Annotated[str, File(...)],
):
    safe_title = title.strip()
    if not safe_title or len(safe_title) > 255:
        raise HTTPException(status_code=400, detail="Invalid document title")

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Only PDF and plain-text files are allowed")

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid4().hex}.bin"
    destination = STORAGE_DIR / stored_filename
    size = 0

    try:
        with destination.open("xb") as output:
            while True:
                chunk = await file.read(64 * 1024)
                if not chunk:
                    break

                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    raise HTTPException(status_code=413, detail="File exceeds 10 MB limit")

                output.write(chunk)

        if size == 0:
            raise HTTPException(status_code=400, detail="Empty files are not allowed")

        document = Document(
            owner_id=current_user.id,
            title=safe_title,
            stored_filename=stored_filename,
            content_type=file.content_type,
            size_bytes=size,
        )
        db.add(document)
        db.flush()

        write_audit(db, current_user.id, "DOCUMENT_UPLOAD", str(document.id), "success")
        db.commit()
        db.refresh(document)
        return document

    except Exception:
        db.rollback()
        if destination.exists():
            destination.unlink()
        raise
    finally:
        await file.close()


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    statement = (
        select(Document)
        .where(Document.owner_id == current_user.id)
        .order_by(Document.created_at.desc())
    )
    return list(db.scalars(statement).all())

@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    # Find the document.
    document = db.get(Document, document_id)

    # Use the same response for missing and unauthorized documents
    # to avoid revealing whether a document exists.
    if document is None:
        write_audit(
            db, current_user.id, "DOCUMENT_DOWNLOAD", str(document_id), "denied"
        )
        db.commit()
        raise HTTPException(status_code=404, detail="Document not found")

    # Owners can read their own documents.
    is_owner = document.owner_id == current_user.id

    # Other users need explicit read permission.
    permission = db.scalar(
        select(DocumentPermission).where(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == current_user.id,
            DocumentPermission.can_read.is_(True),
        )
    )

    if not is_owner and permission is None:
        write_audit(
            db, current_user.id, "DOCUMENT_DOWNLOAD", str(document_id), "denied"
        )
        db.commit()
        raise HTTPException(status_code=404, detail="Document not found")

    # Resolve the storage path and ensure it stays inside private storage.
    storage_root = STORAGE_DIR.resolve()
    file_path = (storage_root / document.stored_filename).resolve()

    if file_path.parent != storage_root or not file_path.is_file():
        write_audit(
            db, current_user.id, "DOCUMENT_DOWNLOAD", str(document_id), "error"
        )
        db.commit()
        raise HTTPException(status_code=404, detail="Document file not found")

    write_audit(
        db, current_user.id, "DOCUMENT_DOWNLOAD", str(document_id), "success"
    )
    db.commit()

    return FileResponse(
        path=file_path,
        media_type=document.content_type,
        filename=document.title,
    )

@router.put(
    "/{document_id}/permissions",
    response_model=DocumentPermissionResponse,
)
def set_document_permission(
    document_id: int,
    request: DocumentPermissionRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    document = db.get(Document, document_id)

    # Only the document owner may manage sharing.
    if document is None or document.owner_id != current_user.id:
        write_audit(
            db, current_user.id, "PERMISSION_UPDATE", str(document_id), "denied"
        )
        db.commit()
        raise HTTPException(status_code=404, detail="Document not found")

    # The recipient must be a registered user.
    from backend.app.models.database import User

    recipient = db.get(User, request.user_id)
    if recipient is None or not recipient.is_active:
        raise HTTPException(status_code=404, detail="Recipient not found")

    if recipient.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You already have owner access",
        )

    permission = db.scalar(
        select(DocumentPermission).where(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == recipient.id,
        )
    )

    if permission is None:
        permission = DocumentPermission(
            document_id=document_id,
            user_id=recipient.id,
            can_read=request.can_read,
            can_edit=request.can_edit,
        )
        db.add(permission)
    else:
        permission.can_read = request.can_read
        permission.can_edit = request.can_edit

    write_audit(
        db, current_user.id, "PERMISSION_UPDATE", str(document_id), "success"
    )
    db.commit()
    db.refresh(permission)
    return permission

@router.delete(
    "/{document_id}/permissions/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def revoke_document_permission(
    document_id: int,
    user_id: int,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    document = db.get(Document, document_id)

    # Only the owner may revoke sharing permissions.
    if document is None or document.owner_id != current_user.id:
        write_audit(
            db, current_user.id, "PERMISSION_REVOKE", str(document_id), "denied"
        )
        db.commit()
        raise HTTPException(status_code=404, detail="Document not found")

    permission = db.scalar(
        select(DocumentPermission).where(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == user_id,
        )
    )

    if permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")

    db.delete(permission)

    write_audit(
        db, current_user.id, "PERMISSION_REVOKE", str(document_id), "success"
    )
    db.commit()

    return None