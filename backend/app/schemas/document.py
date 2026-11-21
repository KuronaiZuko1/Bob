from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class DocumentBase(BaseModel):
    original_filename: str
    document_category: str = "other"
    is_verified: bool = False
    expiry_date: Optional[str] = None


class DocumentCreate(DocumentBase):
    stored_filename: str
    file_path: str
    file_type: str
    file_size_bytes: int
    extracted_text: Optional[str] = None
    is_encrypted: bool = True
    checksum: Optional[str] = None


class DocumentOut(BaseModel):
    id: int
    profile_id: Optional[int] = None
    original_filename: str
    document_category: str
    category: str = Field(validation_alias="document_category")
    file_type: str
    mime_type: str = Field(validation_alias="file_type")
    file_size_bytes: int
    file_size: int = Field(validation_alias="file_size_bytes")
    is_encrypted: bool
    is_verified: bool
    checksum: Optional[str] = None
    expiry_date: Optional[str] = None
    created_at: Optional[datetime] = None
    uploaded_at: Optional[datetime] = Field(default=None, validation_alias="created_at")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
