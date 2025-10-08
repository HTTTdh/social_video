

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from .common import ORMModel, VideoStatus

class VideoImportIn(BaseModel):
    urls: List[str]
    source_platform: Optional[str] = None
    remove_watermark: bool = False
    use_proxy: bool = False

class VideoProcessIn(BaseModel):
    ids: List[int]
    add_watermark_template_id: Optional[int] = None
    add_frame_template_id: Optional[int] = None

class VideoOut(ORMModel):
    id: int
    title: str
    description: Optional[str] = None
    original_url: Optional[str] = None
    source_platform: Optional[str] = None
    source_video_id: Optional[str] = None
    file_path: str
    file_size: Optional[int] = None
    duration: Optional[float] = None
    resolution: Optional[str] = None
    format: str
    thumbnail_path: Optional[str] = None
    video_metadata: Optional[Dict[str, Any]] = Field(default=None)  # giữ cùng tên model
    status: VideoStatus
    uploaded_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class VideoUpdateIn(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[VideoStatus] = None
    thumbnail_path: Optional[str] = None
    video_metadata: Optional[Dict[str, Any]] = None

class TrimIn(BaseModel):
    video_id: int
    start: float = 0.0          
    end: float | None = None   
    reencode: bool = False      

class CropIn(BaseModel):
    video_id: int
    width: int
    height: int
    x: int = 0
    y: int = 0

class WatermarkIn(BaseModel):
    video_id: int
    watermark_path: str        
    x: int = 10
    y: int = 10
    opacity: float = 1.0        

class ThumbnailIn(BaseModel):
    video_id: int
    method: Literal["scene","middle"] = "scene"  