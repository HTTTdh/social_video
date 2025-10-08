


from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_roles
from app.services.youtube_service import YouTubeService

router = APIRouter(prefix="/youtube", tags=["youtube"])
role_dep = lambda: Depends(require_roles(["admin", "staff"]))

class YTPostVideoIn(BaseModel):
    video_id: int
    title: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    privacy_status: str = "public"         
    schedule_time_iso: Optional[str] = None  

@router.post("/channels/{channel_id}/post-video")
async def post_video(
    channel_id: int,
    body: YTPostVideoIn,
    db: Session = Depends(get_db),
    _ = role_dep(),
):
    svc = YouTubeService()
    ok, result = await svc.post_video_via_channel(
        db=db,
        channel_id=channel_id,
        video_id=body.video_id,
        title=body.title,
        description=body.description or "",
        tags=body.tags,
        privacy_status=body.privacy_status,
        schedule_time_iso=body.schedule_time_iso,
    )
    if not ok:
        raise HTTPException(400, result)
    return result
