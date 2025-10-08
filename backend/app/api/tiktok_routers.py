



from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import require_roles
from app.services.tiktok_service import TikTokService

router = APIRouter(prefix="/tiktok", tags=["tiktok"])
role_dep = lambda: Depends(require_roles(["admin", "staff"]))

class TTPostVideoIn(BaseModel):
    video_id: int
    caption: Optional[str] = None
    schedule_time_iso: Optional[str] = None  

@router.post("/channels/{channel_id}/post-video")
async def post_video(
    channel_id: int,
    body: TTPostVideoIn,
    db: Session = Depends(get_db),
    _ = role_dep(),
):
    svc = TikTokService()
    ok, result = await svc.post_video_via_channel(
        db=db,
        channel_id=channel_id,
        video_id=body.video_id,
        caption=body.caption or "",
    )
    if not ok:
        raise HTTPException(400, result)
    return result
