


from pydantic import BaseModel
from typing import List, Dict, Any

class AnalyticsOverviewOut(BaseModel):
    total_posts: int
    posted: int
    scheduled: int
    failed: int
    total_pages: int
    total_videos: int

class PlatformStat(BaseModel):
    platform: str
    posts: int
    views: int
    likes: int
    comments: int
    shares: int

class AnalyticsPlatformsOut(BaseModel):
    items: List[PlatformStat]

class TopPost(BaseModel):
    post_id: int
    page_name: str
    caption: str | None = None
    views: int
    likes: int
    comments: int
    shares: int

class AnalyticsTopPostsOut(BaseModel):
    items: List[TopPost]
