


from typing import List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app.models.channel_models import Channel
from app.schemas.channel_schemas import ChannelPlatformEnum

WRITEABLE_FIELDS = {
    "name","username","avatar_url","access_token","token_expires_at","status",
    "is_active","owner_user_id","channel_metadata","source_ref_table","source_ref_id"
}

def get_by_id(db: Session, channel_id: int) -> Optional[Channel]:
    return db.get(Channel, channel_id)

def list(
    db: Session,
    platform: Optional[Union[ChannelPlatformEnum, str]] = None,
    q: Optional[str] = None,
    only_active: bool = True,
    limit: int = 100,
    offset: int = 0,
) -> List[Channel]:
    query = db.query(Channel)
    if platform:
        plat_value = platform.value if hasattr(platform, "value") else platform
        query = query.filter(Channel.platform == plat_value)
    if only_active:
        query = query.filter(Channel.is_active.is_(True))
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Channel.name.ilike(like), Channel.username.ilike(like)))
    return query.order_by(Channel.name.asc()).offset(offset).limit(limit).all()

def get_by_platform_external(db: Session, platform: str, external_id: str) -> Optional[Channel]:
    return (
        db.query(Channel)
        .filter(Channel.platform == platform, Channel.external_id == external_id)
        .first()
    )

def create(db: Session, **data) -> Channel:
    obj = Channel(**data)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def update(db: Session, obj: Channel, data: dict) -> Channel:
    for k, v in data.items():
        if k in WRITEABLE_FIELDS:
            if v is None:  # <- nếu bạn muốn cho phép set None thì bỏ if này
                continue
            setattr(obj, k, v)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def delete(db: Session, obj: Channel) -> None:
    db.delete(obj); db.commit()

def upsert(db: Session, platform: str, external_id: str, defaults: Optional[dict] = None) -> Channel:
    defaults = defaults or {}
    obj = get_by_platform_external(db, platform, external_id)
    if not obj:
        obj = Channel(platform=platform, external_id=external_id, **{k:v for k,v in defaults.items() if k in WRITEABLE_FIELDS})
        db.add(obj)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            obj = get_by_platform_external(db, platform, external_id)
            if not obj:
                raise
        db.refresh(obj)
    else:
        if defaults:
            for k, v in defaults.items():
                if k in WRITEABLE_FIELDS:
                    setattr(obj, k, v)
            db.commit(); db.refresh(obj)
    return obj

def update_tokens(
    db: Session,
    channel: Channel,
    *,
    access_token: Optional[str] = None,
    refresh_token: str | None = None,
    token_expires_at: Optional[datetime] = None,
    channel_metadata: dict | None = None,
) -> Channel:
    if access_token is not None:
        channel.access_token = access_token
    if refresh_token is not None:
        # đảm bảo metadata lưu cả refresh_token nếu bạn không có cột riêng
        meta = dict(channel_metadata or {})
        meta["refresh_token"] = refresh_token
        channel_metadata = meta
    if token_expires_at is not None:
        channel.token_expires_at = token_expires_at
    if channel_metadata:
        channel.channel_metadata = {**(channel.channel_metadata or {}), **channel_metadata}
    db.add(channel); db.commit(); db.refresh(channel)
    return channel
