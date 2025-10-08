import os
import httpx
from typing import Tuple, Dict
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.core.settings import get_settings
from app.schemas.common import ChannelPlatformEnum as PF

from app.repositories import channel_repo
from app.models.video_models import Video

TIKTOK_TOKEN_URL   = "https://open.tiktokapis.com/v2/oauth/token/"
TIKTOK_INIT_URL    = "https://open.tiktokapis.com/v2/post/publish/video/init/"
TIKTOK_PUBLISH_URL = "https://open.tiktokapis.com/v2/post/publish/video/"

class TikTokService:
    def __init__(self):
        self.base_url = "https://open-api.tiktok.com"
        self.settings = get_settings()
        
    def get_auth_url(self, redirect_uri: str) -> str:
        """Tạo URL để user authorize TikTok"""
        client_key = self.settings.TIKTOK_CLIENT_KEY
        if not client_key:
            raise ValueError("TIKTOK_CLIENT_KEY not configured")
        # cần cả video.publish để publish sau khi upload
        scope = "video.upload,video.publish,user.info.basic"
        return f"{self.base_url}/platform/oauth/connect/?client_key={client_key}&scope={scope}&redirect_uri={redirect_uri}"
        
    def upload_video(self, access_token: str, video_path: str, caption: str) -> Dict:
        """Upload video lên TikTok"""
        # Implement TikTok video upload API
        pass

    async def _ensure_access_token(self, db: Session, channel) -> str:
        """
        Trả về access_token hợp lệ. Nếu hết hạn và có refresh_token thì refresh.
        """
        if channel.token_expires_at:
            exp = channel.token_expires_at
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            if exp <= now:
                refresh = (channel.channel_metadata or {}).get("refresh_token")
                if not refresh:
                    raise RuntimeError("TikTok token expired and no refresh_token")

                async with httpx.AsyncClient(timeout=20) as client:
                    r = await client.post(
                        TIKTOK_TOKEN_URL,
                        data={
                            "grant_type": "refresh_token",
                            "client_key": self.settings.TIKTOK_CLIENT_KEY,
                            "client_secret": self.settings.TIKTOK_CLIENT_SECRET,
                            "refresh_token": refresh,
                        },
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                    )
                r.raise_for_status()
                js = r.json()

                new_access  = js["access_token"]
                expires_in  = int(js.get("expires_in", 3600))
                expires_at  = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

                # cập nhật lại token vào DB
                channel_repo.update_tokens(
                    db, channel,
                    access_token=new_access,
                    token_expires_at=expires_at,
                )
                return new_access

        return channel.access_token

    async def post_video_via_channel(
        self, db: Session, *, channel_id: int, video_id: int, caption: str
    ) -> Tuple[bool, dict]:
        """
        Flow TikTok:
        1) INIT -> trả upload_url + publish_id
        2) PUT video bytes -> upload_url
        3) PUBLISH -> dùng publish_id + caption
        Yêu cầu scope: `video.upload` (upload) và `video.publish` (publish).
        """
        ch = channel_repo.get_by_id(db, channel_id)
        if not ch:
            return False, {"error": "TikTok channel not found"}
        plat = getattr(ch.platform, "value", ch.platform)
        if plat != PF.tiktok.value:
            return False, {"error": "TikTok channel not found"}

        try:
            token = await self._ensure_access_token(db, ch)
        except Exception as e:
            return False, {"error": "ensure_token_failed", "detail": str(e)}

        video: Video = db.get(Video, video_id)
        if not video or not getattr(video, "file_path", None):
            return False, {"error": "Video file not found"}
        file_path = Path(video.file_path)
        if not file_path.exists():
            return False, {"error": "Video path missing on disk"}
        data = file_path.read_bytes()

        try:
            async with httpx.AsyncClient(timeout=None) as client:
                # 1) INIT (TikTok trả upload_url + publish_id)
                r1 = await client.post(
                    TIKTOK_INIT_URL,
                    headers={"Authorization": f"Bearer {token}"},
                    json={"source": "FILE"},  # tuỳ theo app: FILE/URL...
                )
                r1.raise_for_status()
                ctx = r1.json().get("data") or {}
                upload_url = ctx.get("upload_url")
                publish_id = ctx.get("publish_id")
                if not upload_url or not publish_id:
                    return False, {"error": "init_failed", "detail": r1.text}

                # 2) UPLOAD file video (PUT raw bytes)
                r2 = await client.put(
                    upload_url,
                    content=data,
                    headers={"Content-Type": "video/mp4"},
                )
                r2.raise_for_status()

                # 3) PUBLISH
                r3 = await client.post(
                    TIKTOK_PUBLISH_URL,
                    headers={"Authorization": f"Bearer {token}"},
                    json={"publish_id": publish_id, "caption": caption or ""},
                )
                r3.raise_for_status()
                out = r3.json().get("data") or {}

            return True, {"video_id": out.get("video_id"), "publish_id": publish_id}

        except httpx.HTTPStatusError as e:
            # trả body lỗi của TikTok để dễ debug (thường 403 do thiếu scope video.publish)
            body = e.response.text if e.response is not None else str(e)
            return False, {"error": "http_error", "status": getattr(e.response, "status_code", None), "detail": body}
        except Exception as e:
            return False, {"error": "unexpected", "detail": str(e)}
