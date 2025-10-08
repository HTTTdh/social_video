


from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from .common import ORMModel

class ScheduleCreateIn(BaseModel):
    name: str
    channel_id: int               
    interval_hours: int = 2
    start_time: str
    end_time: str
    days_of_week: str
    auto_select_videos: bool = True
    template_caption_id: Optional[int] = None
    template_hashtag_id: Optional[int] = None

class ScheduleUpdateIn(BaseModel):
    name: Optional[str] = None
    interval_hours: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    days_of_week: Optional[str] = None
    auto_select_videos: Optional[bool] = None
    template_caption_id: Optional[int] = None
    template_hashtag_id: Optional[int] = None
    is_active: Optional[bool] = None

class ScheduleOut(ORMModel):
    id: int
    name: str
    channel_id: int                   
    interval_hours: int
    start_time: str
    end_time: str
    days_of_week: str
    auto_select_videos: bool
    template_caption_id: int | None = None
    template_hashtag_id: int | None = None
    is_active: bool
    created_by_id: int | None = None
    next_run_time: Optional[datetime] = None
    last_run_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime | None = None

class CalendarOut(BaseModel):
    month: int
    year: int
    items: list[dict]
