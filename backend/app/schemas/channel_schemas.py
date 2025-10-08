



from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from .common import ChannelPlatformEnum, ORMModel


class ChannelCreateIn(BaseModel):
    platform: ChannelPlatformEnum
    external_id: str
    name: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    access_token: Optional[str] = None
    is_active: bool = True
    channel_metadata: Optional[dict] = Field(default=None, alias="metadata")
    model_config = ConfigDict(populate_by_name=True)

class ChannelUpdateIn(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    access_token: Optional[str] = None
    is_active: Optional[bool] = None
    channel_metadata: Optional[dict] = Field(default=None, alias="metadata")
    model_config = ConfigDict(populate_by_name=True)

class ChannelOut(ORMModel):
    id: int
    platform: ChannelPlatformEnum
    external_id: str
    name: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    token_expires_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
    
class ChannelTokenIn(BaseModel):
    platform: ChannelPlatformEnum
    access_token: str
    token_expires_at: Optional[datetime] = None
    refresh_token: Optional[str] = None
    external_id: Optional[str] = None
