from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator
from .common import ORMModel

class MediaAssetOut(ORMModel):
    id: int
    type: str
    path: str
    mime_type: Optional[str] = None
    size: Optional[int] = None

    # Đặt tên field là media_metadata, xuất JSON với key "metadata"
    media_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        serialization_alias="metadata",
        validation_alias="media_metadata",
    )

    uploaded_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @field_validator("media_metadata", mode="before")
    @classmethod
    def coerce_metadata(cls, v):
        if v is None:
            return {}
        if isinstance(v, dict):
            return v
        # Nếu là object ORM, lấy __dict__ và lọc nội bộ
        if hasattr(v, "__dict__"):
            return {k: val for k, val in v.__dict__.items() if not k.startswith("_")}
        # Tránh rơi vào SQLAlchemy MetaData/Table
        if hasattr(v, "__table__") or v.__class__.__name__ in ("MetaData", "Table"):
            return {}
        return {}

class MediaUpdateIn(BaseModel):
    path: Optional[str] = None
    mime_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None