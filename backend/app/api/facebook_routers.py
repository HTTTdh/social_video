


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.services.facebook_service import FacebookService
from app.api.deps import require_roles
from app.schemas.facebook_schemas import FBPostFeedIn, FBPostPhotoIn, FBPostVideoIn, FBPostPhotosIn

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/facebook", tags=["facebook"])
role_dep = lambda: Depends(require_roles(["admin", "staff", "super_admin"]))

def get_fb_service() -> FacebookService:
    return FacebookService()


@router.post("/channels/{channel_id}/post-feed")
async def post_feed(
    channel_id: int,
    body: FBPostFeedIn,
    db: Session = Depends(get_db),
    svc: FacebookService = Depends(get_fb_service),
    _=role_dep(),
):
    token, page_id = svc.get_channel_token_and_page(db, channel_id)
    if not token or not page_id:
        raise HTTPException(404, "Facebook channel/token not found")

    return await svc.post_feed(
        token,
        page_id,
        message=body.message or "",
        schedule_unix=body.schedule_unix,
        schedule_iso=body.schedule_time_iso,
    )

@router.post("/channels/{channel_id}/post-photo")
async def post_photo(
    channel_id: int,
    body: FBPostPhotoIn,
    db: Session = Depends(get_db),
    svc: FacebookService = Depends(get_fb_service),
    _=role_dep(),
):
    token, page_id = svc.get_channel_token_and_page(db, channel_id)
    if not token or not page_id:
        raise HTTPException(404, "Facebook channel/token not found")

    try:
        result = await svc.post_photo(
            token,
            page_id,
            image_url=str(body.image_url),
            caption=body.message,
            schedule_unix=body.schedule_unix,
            schedule_iso=body.schedule_time_iso,
        )
        return result
    except Exception as e:
        logger.error(f"Facebook post photo failed for channel {channel_id}: {e}")
        raise HTTPException(502, f"Failed to post to Facebook: {str(e)}")


@router.post("/channels/{channel_id}/post-video")
async def post_video(
    channel_id: int,
    body: FBPostVideoIn,
    db: Session = Depends(get_db),
    svc: FacebookService = Depends(get_fb_service),
    _=role_dep(),
):
    token, page_id = svc.get_channel_token_and_page(db, channel_id)
    if not token or not page_id:
        raise HTTPException(404, "Facebook channel/token not found")

    return await svc.post_video(
        token,
        page_id,
        file_url=str(body.file_url),
        description=body.description,
    )
    
@router.post("/channels/{channel_id}/post-photos")
async def post_photos(
    channel_id: int,
    body: FBPostPhotosIn,
    db: Session = Depends(get_db),
    svc: FacebookService = Depends(get_fb_service),
    _ = role_dep()
):
    token, page_id = svc.get_channel_token_and_page(db, channel_id)
    if not token or not page_id:
        raise HTTPException(404, "Facebook channel/token not found")

    res = await svc.post_photos(
        token,
        page_id,
        image_urls=[str(u) for u in body.image_urls],
        message=body.message,
        schedule_unix=body.schedule_unix,
        schedule_iso=body.schedule_time_iso,
    )
    if isinstance(res, dict) and res.get("error"):
        # phản hồi lỗi FB ra client để bạn debug dễ (tránh 500)
        raise HTTPException(status_code=502, detail=res)
    return res
