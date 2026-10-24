
from datetime import datetime

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: int
    owner_id: int
    title: str
    content_type: str
    size_bytes: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentPermissionRequest(BaseModel):
    user_id: int = Field(gt=0)
    can_read: bool = False
    can_edit: bool = False
	
class DocumentPermissionResponse(BaseModel):
    id: int
    document_id: int
    user_id: int
    can_read: bool
    can_edit: bool

    model_config = {"from_attributes": True}