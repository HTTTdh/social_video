from pydantic import BaseModel, ConfigDict
from enum import Enum

class UserRoleEnum(str, Enum):
    admin = "admin"
    staff = "staff"
    viewer = "viewer"

class VideoStatus(str, Enum):
    processing = "processing"
    ready = "ready"
    error = "error"

class PostStatus(str, Enum):
    ready = "ready"
    scheduled = "scheduled"
    posted = "posted"
    failed = "failed"
    cancelled = "cancelled"

class TemplateType(str, Enum):
    caption = "caption"
    hashtag = "hashtag"
    watermark = "watermark"
    thumbnail = "thumbnail"

class ChannelPlatformEnum(str, Enum):
    facebook = "facebook"
    instagram = "instagram"
    tiktok = "tiktok"
    youtube = "youtube"
    twitter = "twitter"
    threads = "threads"
    pinterest = "pinterest"

ChannelPlatform = ChannelPlatformEnum

class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)