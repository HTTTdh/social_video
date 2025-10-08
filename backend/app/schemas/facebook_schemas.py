



from pydantic import BaseModel, HttpUrl, field_validator, model_validator, Field, AnyUrl
from typing import Optional, List

class FBPostFeedIn(BaseModel):
    message: Optional[str] = None
    schedule_time_iso: Optional[str] = None   
    schedule_unix: Optional[int] = None       

    @field_validator("schedule_unix")
    @classmethod
    def _non_negative_unix(cls, v):
        if v is not None and v < 0:
            raise ValueError("schedule_unix must be >= 0")
        return v
    @model_validator(mode="after")
    def _xor_schedule(self):
        if self.schedule_unix and self.schedule_time_iso:
            raise ValueError("Provide only one of schedule_unix or schedule_time_iso")
        return self

class FBPostPhotoIn(FBPostFeedIn):
    image_url: HttpUrl

class FBPostVideoIn(BaseModel):
    file_url: HttpUrl
    description: Optional[str] = None
    published: bool = True
    schedule_time_iso: Optional[str] = None
    schedule_unix: Optional[int] = None

    @field_validator("schedule_unix")
    @classmethod
    def _non_negative_unix(cls, v):
        if v is not None and v < 0:
            raise ValueError("schedule_unix must be >= 0")
        return v

    @model_validator(mode="after")
    def _video_schedule_rules(self):
        if self.schedule_unix and self.schedule_time_iso:
            raise ValueError("Provide only one of schedule_unix or schedule_time_iso")
        if (self.schedule_unix or self.schedule_time_iso) and self.published:
            raise ValueError("When scheduling a video, set published=False")
        return self
class FBPostPhotosIn(BaseModel):
    image_urls: List[AnyUrl] = Field(min_items=2, max_items=10)
    message: Optional[str] = None
    schedule_unix: Optional[int] = None
    schedule_time_iso: Optional[str] = None  
    @field_validator("schedule_unix")
    @classmethod
    def _non_negative_unix(cls, v):
        if v is not None and v < 0:
            raise ValueError("schedule_unix must be >= 0")
        return v

    @model_validator(mode="after")
    def _xor_schedule(self):
        if self.schedule_unix and self.schedule_time_iso:
            raise ValueError("Provide only one of schedule_unix or schedule_time_iso")
        return self
