



from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.instagram_service import InstagramService
from app.repositories import channel_repo
from app.schemas.channel_schemas import ChannelOut
from app.schemas.instagram_schemas import IGPostPhotoIn, IGPostVideoIn, IGPostCarouselIn
from app.api.deps import require_roles

role_dep = lambda: Depends(require_roles(["admin", "staff"]))
router = APIRouter(prefix="/instagram", tags=["instagram"])

def get_ig_service() -> InstagramService:
    return InstagramService()


@router.get("/channels", response_model=List[ChannelOut])
def list_instagram_channels(
    q: Optional[str] = None,
    only_active: bool = True,
    db: Session = Depends(get_db),
    _ = role_dep(),
):
    """
    Trả về danh sách kênh Instagram (để UI dropdown).
    """
    return channel_repo.list(db, platform="instagram", q=q, only_active=only_active)

@router.post("/channels/{channel_id}/post-photo")
async def post_photo(
    channel_id: int,
    body: IGPostPhotoIn,
    db: Session = Depends(get_db),
    svc: InstagramService = Depends(get_ig_service),
    _ = role_dep(),
):
    """
    Đăng ảnh IG: tạo container -> publish.
    """
    token, ig_id = svc.get_channel_token_and_igid(db, channel_id)
    if not token or not ig_id:
        raise HTTPException(status_code=404, detail="Instagram channel/token not found")
    return await svc.post_photo(token, ig_id, image_url=str(body.image_url), caption=body.caption)

@router.post("/channels/{channel_id}/post-video")
async def post_video(
    channel_id: int,
    body: IGPostVideoIn,
    db: Session = Depends(get_db),
    svc: InstagramService = Depends(get_ig_service),
    _ = role_dep(),
):
    """
    Đăng video IG (mặc định là reels): tạo container -> publish.
    """
    token, ig_id = svc.get_channel_token_and_igid(db, channel_id)
    if not token or not ig_id:
        raise HTTPException(status_code=404, detail="Instagram channel/token not found")
    return await svc.post_video(
        token,
        ig_id,
        video_url=str(body.video_url),
        caption=body.caption,
        is_reel=body.is_reel,
    )

@router.post("/channels/{channel_id}/post-carousel")
async def post_carousel(
    channel_id: int,
    body: IGPostCarouselIn,
    db: Session = Depends(get_db),
    svc: InstagramService = Depends(get_ig_service),
    _ = role_dep(),
):
    token, ig_id = svc.get_channel_token_and_igid(db, channel_id)
    if not token or not ig_id:
        raise HTTPException(status_code=404, detail="Instagram channel/token not found")
    return await svc.post_carousel(token, ig_id, [str(u) for u in body.image_urls], body.caption)