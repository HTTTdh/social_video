


from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List

class IGPostPhotoIn(BaseModel):
    image_url: HttpUrl
    caption: Optional[str] = None

class IGPostVideoIn(BaseModel):
    video_url: HttpUrl
    caption: Optional[str] = None
    is_reel: bool = True

class IGPostCarouselIn(BaseModel):
    image_urls: List[HttpUrl] = Field(min_items=2, max_items=10)
    caption: Optional[str] = None
    
