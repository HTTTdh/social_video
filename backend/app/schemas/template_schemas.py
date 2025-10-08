


from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from .common import ORMModel, TemplateType

class TemplateCreateIn(BaseModel):
    name: str
    type: TemplateType
    content: str
    template_metadata: Optional[Dict[str, Any]] = None

class TemplateUpdateIn(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    template_metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class TemplateOut(ORMModel):
    id: int
    name: str
    type: TemplateType
    content: str
    template_metadata: Optional[dict] = None
    created_by_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

class TemplatePreviewIn(BaseModel):
    caption_vars: dict | None = None
    hashtag_vars: dict | None = None

class TemplatePreviewOut(BaseModel):
    preview_text: str | None = None
