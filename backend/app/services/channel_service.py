from typing import Optional, List, Union
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import channel_repo
from app.schemas.channel_schemas import ChannelCreateIn, ChannelUpdateIn
from app.models.channel_models import Channel
from app.schemas.common import ChannelPlatformEnum as PF

class ChannelService:
    ALLOWED_PLATFORMS = {e.value for e in PF}

    @staticmethod
    def _to_value(platform: Union[str, PF, None]) -> Optional[str]:
        if platform is None:
            return None
        return getattr(platform, "value", platform)

    def _validate_platform(self, platform: Union[str, PF]):
        val = self._to_value(platform)
        if val not in self.ALLOWED_PLATFORMS:
            raise HTTPException(status_code=422, detail=f"Unsupported platform '{platform}'")

    # CRUD 
    def list(
        self,
        db: Session,
        platform: Optional[Union[str, PF]] = None,
        q: Optional[str] = None,
        only_active: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Channel]:
        plat_val = self._to_value(platform)
        if plat_val:
            self._validate_platform(plat_val)
        return channel_repo.list(
            db, platform=plat_val, q=q, only_active=only_active, limit=limit, offset=offset
        )

    def get(self, db: Session, channel_id: int) -> Channel:
        ch = channel_repo.get_by_id(db, channel_id)
        if not ch:
            raise HTTPException(status_code=404, detail="Channel not found")
        return ch

    def create(self, db: Session, payload: ChannelCreateIn) -> Channel:
        plat_val = self._to_value(payload.platform)
        self._validate_platform(plat_val)
        exist = channel_repo.get_by_platform_external(db, plat_val, payload.external_id)
        if exist:
            raise HTTPException(status_code=409, detail="Channel already exists")

        data = payload.model_dump()
        data["platform"] = plat_val  # lưu string value
        if "metadata" in data:
            data["channel_metadata"] = data.pop("metadata")
        return channel_repo.create(db, **data)

    def update(self, db: Session, channel_id: int, payload: ChannelUpdateIn) -> Channel:
        ch = self.get(db, channel_id)
        data = payload.model_dump(exclude_unset=True)
        if "platform" in data and data["platform"] is not None:
            plat_val = self._to_value(data["platform"])
            self._validate_platform(plat_val)
            data["platform"] = plat_val
        if "metadata" in data:
            data["channel_metadata"] = data.pop("metadata")
        return channel_repo.update(db, ch, data)

    def delete(self, db: Session, channel_id: int) -> None:
        ch = self.get(db, channel_id)
        channel_repo.delete(db, ch)

    def toggle_active(self, db: Session, channel_id: int, active: bool) -> Channel:
        ch = self.get(db, channel_id)
        return channel_repo.update(db, ch, {"is_active": active})

    def upsert_from_fb(
        self,
        db: Session,
        page_id: str,
        *,
        page_name: Optional[str] = None,
        access_token: Optional[str] = None,
        owner_user_id: Optional[int] = None,
    ) -> Channel:
        defaults = {
            "name": page_name or "Facebook Page",
            "access_token": access_token,
            "is_active": True,
            "owner_user_id": owner_user_id,
        }
        # dùng Enum value thay vì chuỗi tự do
        return channel_repo.upsert(db, PF.facebook.value, page_id, defaults=defaults)
