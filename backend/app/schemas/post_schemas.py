# app/schemas/post_schemas.py
from typing import Any, Dict, Optional, List
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator

class PostStatusEnum(str, Enum):
    draft = "draft"          # cho phép nếu DB còn dữ liệu cũ; có thể bỏ nếu bạn migrate về ready/scheduled
    ready = "ready"
    scheduled = "scheduled"
    posted = "posted"
    failed = "failed"
    cancelled = "cancelled"

class PostTargetIn(BaseModel):
    channel_id: int
    scheduled_time: Optional[datetime] = None

class PostTargetOut(BaseModel):
    id: int
    channel_id: int
    platform: str
    status: PostStatusEnum
    scheduled_time: Optional[datetime] = None
    posted_time: Optional[datetime] = None
    error_message: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class PostCreateIn(BaseModel):
    video_id: Optional[int] = None
    caption: Optional[str] = None
    hashtags: Optional[str] = None
    default_scheduled_time: Optional[datetime] = None
    post_metadata: Optional[dict] = Field(default=None, alias="metadata")
    targets: List[PostTargetIn]
    model_config = ConfigDict(populate_by_name=True)

class PostUpdateIn(BaseModel):
    video_id: Optional[int] = None
    caption: Optional[str] = None
    hashtags: Optional[str] = None
    default_scheduled_time: Optional[datetime] = None
    status: Optional[str] = None
    post_metadata: Optional[dict] = Field(default=None, alias="metadata")
    model_config = ConfigDict(populate_by_name=True)

class PostOut(BaseModel):
    id: int
    caption: Optional[str] = None
    hashtags: Optional[str] = None
    status: PostStatusEnum
    video_id: Optional[int] = None
    template_id: Optional[int] = None
    created_by_id: Optional[int] = None

    # KHÔNG dùng tên "metadata" làm tên field. Dùng post_metadata + serialization_alias.
    post_metadata: Dict[str, Any] = Field(default_factory=dict, serialization_alias="metadata")

    targets: List[PostTargetOut] = []

    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @field_validator("post_metadata", mode="before")
    @classmethod
    def coerce_metadata(cls, v):
        if v is None:
            return {}
        if isinstance(v, dict):
            return v
        if hasattr(v, "__dict__"):
            return {k: val for k, val in v.__dict__.items() if not k.startswith("_")}
        # chặn SQLAlchemy MetaData/Table rơi vào đây
        if v.__class__.__name__ in ("MetaData", "Table"):
            return {}
        return {}