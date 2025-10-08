from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException
import json

from app.repositories import channel_repo
from app.services.BaseSocial_service import BaseSocialService
from app.schemas.common import ChannelPlatformEnum as PF


class FacebookService(BaseSocialService):
    def __init__(self):
        self.settings = self.get_settings()
        self.graph_v = getattr(self.settings, "GRAPH_API_VERSION", "v19.0")
        self.base_url = f"https://graph.facebook.com/{self.graph_v}"

    @staticmethod
    def _iso_to_unix(iso: Optional[str]) -> Optional[int]:
        if not iso:
            return None
        try:
            s = iso.replace("Z", "+00:00")
            dt = datetime.fromisoformat(s)
            return int(dt.timestamp())
        except Exception:
            return None

    def get_channel_token_and_page(self, db: Session, channel_id: int) -> Tuple[Optional[str], Optional[str]]:
        ch = channel_repo.get_by_id(db, channel_id)
        if not ch:
            return None, None
        plat = getattr(ch.platform, "value", ch.platform)
        if plat != PF.facebook.value:
            return None, None
        return getattr(ch, "access_token", None), getattr(ch, "external_id", None)

    async def post_feed(self, page_token: str, page_id: str, *, message: str, schedule_unix: int | None = None, schedule_iso: str | None = None) -> Dict:
        if not page_token or not page_id:
            raise HTTPException(status_code=400, detail="Missing page_token or page_id")
        data: Dict[str, Any] = {"access_token": page_token, "message": message}
        if schedule_unix is not None:
            data["scheduled_publish_time"] = schedule_unix; data["published"] = False
        elif schedule_iso:
            ts = self._iso_to_unix(schedule_iso)
            if ts:
                data["scheduled_publish_time"] = ts; data["published"] = False
        return await self._make_request("POST", f"{self.base_url}/{page_id}/feed", data=data)

    async def post_photo(self, page_token: str, page_id: str, *, image_url: str, caption: str | None = None, schedule_unix: int | None = None, schedule_iso: str | None = None) -> Dict:
        if not page_token or not page_id:
            raise HTTPException(status_code=400, detail="Missing page_token or page_id")
        data: Dict[str, Any] = {"access_token": page_token, "url": image_url}
        if caption: data["caption"] = caption
        if schedule_unix is not None:
            data["scheduled_publish_time"] = schedule_unix; data["published"] = False
        elif schedule_iso:
            ts = self._iso_to_unix(schedule_iso)
            if ts:
                data["scheduled_publish_time"] = ts; data["published"] = False
        return await self._make_request("POST", f"{self.base_url}/{page_id}/photos", data=data)

    async def post_photos(self, page_token: str, page_id: str, *, image_urls: List[str], message: str | None = None, schedule_unix: int | None = None, schedule_iso: str | None = None) -> Dict:
        if not page_token or not page_id:
            raise HTTPException(status_code=400, detail="Missing page_token or page_id")
        attached_media = []
        for url in image_urls:
            up = await self._make_request("POST", f"{self.base_url}/{page_id}/photos", data={
                "access_token": page_token, "url": url, "published": False
            })
            if up.get("id"):
                attached_media.append({"media_fbid": up["id"]})
        payload: Dict[str, Any] = {"access_token": page_token, "attached_media": json.dumps(attached_media)}
        if message: payload["message"] = message
        if schedule_unix is not None:
            payload["scheduled_publish_time"] = schedule_unix; payload["published"] = False
        elif schedule_iso:
            ts = self._iso_to_unix(schedule_iso)
            if ts:
                payload["scheduled_publish_time"] = ts; payload["published"] = False
        return await self._make_request("POST", f"{self.base_url}/{page_id}/feed", data=payload)
    
    async def post_video(self, page_token: str, page_id: str, *, file_url: str, description: str | None = None, schedule_unix: int | None = None, schedule_iso: str | None = None) -> Dict:
        if not page_token or not page_id:
            raise HTTPException(status_code=400, detail="Missing page_token or page_id")
        data: Dict[str, Any] = {"access_token": page_token, "file_url": file_url}
        if description: data["description"] = description
        if schedule_unix is not None:
            data["scheduled_publish_time"] = schedule_unix; data["published"] = False
        elif schedule_iso:
            ts = self._iso_to_unix(schedule_iso)
            if ts:
                data["scheduled_publish_time"] = ts; data["published"] = False
        return await self._make_request("POST", f"{self.base_url}/{page_id}/videos", data=data)