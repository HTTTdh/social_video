from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.channel_schemas import ChannelCreateIn, ChannelUpdateIn, ChannelOut, ChannelTokenIn
from app.repositories import channel_repo
from app.api.deps import require_roles
from app.schemas.common import ChannelPlatformEnum

role_dep = lambda: Depends(require_roles(["admin","staff"]))

router = APIRouter(prefix="/channels", tags=["channels"])

@router.get("/", response_model=List[ChannelOut])
def list_channels(platform: Optional[ChannelPlatformEnum] = None, q: Optional[str] = None, db: Session = Depends(get_db), _=role_dep()):
    return channel_repo.list(db, platform=platform, q=q)

@router.post("/", response_model=ChannelOut)
def create_channel(body: ChannelCreateIn, db: Session = Depends(get_db), _=role_dep()):
    exist = channel_repo.get_by_platform_external(db, body.platform, body.external_id)
    if exist:
        raise HTTPException(409, "Channel already exists")
    return channel_repo.create(db, **body.model_dump())

@router.get("/{channel_id}", response_model=ChannelOut)
def get_channel(channel_id: int, db: Session = Depends(get_db), _=role_dep()):
    obj = channel_repo.get_by_id(db, channel_id)
    if not obj:
        raise HTTPException(404, "Channel not found")
    return obj

@router.patch("/{channel_id}", response_model=ChannelOut)
def update_channel(channel_id: int, body: ChannelUpdateIn, db: Session = Depends(get_db), _=role_dep()):
    obj = channel_repo.get_by_id(db, channel_id)
    if not obj:
        raise HTTPException(404, "Channel not found")
    return channel_repo.update(db, obj, body.model_dump(exclude_unset=True))

@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_channel(channel_id: int, db: Session = Depends(get_db), _=role_dep()):
    obj = channel_repo.get_by_id(db, channel_id)
    if not obj:
        raise HTTPException(404, "Channel not found")
    channel_repo.delete(db, obj)

# Nhập token thủ công (FB/IG/YT/TikTok)
@router.post("/{channel_id}/token", status_code=status.HTTP_200_OK)
def set_channel_token(channel_id: int, body: ChannelTokenIn, db: Session = Depends(get_db), _=role_dep()):
    ch = channel_repo.get_by_id(db, channel_id)
    if not ch:
        raise HTTPException(404, "Channel not found")
    if str(getattr(ch, "platform", "")) != str(body.platform):
        raise HTTPException(400, f"Channel platform mismatch: {ch.platform} != {body.platform}")

    meta = dict(getattr(ch, "channel_metadata", {}) or {})
    # lưu refresh_token (nếu có)
    if body.refresh_token:
        meta["refresh_token"] = body.refresh_token
    # đồng bộ external_id (nếu có)
    external_id = body.external_id or getattr(ch, "external_id", None)
    if body.external_id:
        if body.platform == "facebook":
            meta["page_id"] = body.external_id
        elif body.platform == "instagram":
            meta["ig_user_id"] = body.external_id
        elif body.platform == "youtube":
            meta["yt_channel_id"] = body.external_id
        elif body.platform == "tiktok":
            meta["open_id"] = body.external_id

    ch = channel_repo.update(db, ch, {
        "access_token": body.access_token,
        "token_expires_at": body.token_expires_at,
        "external_id": external_id,
        "channel_metadata": meta,
    })
    return {"success": True, "id": ch.id}