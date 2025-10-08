from typing import Tuple, Dict, List, Optional
import os
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.schemas.common import ChannelPlatformEnum as PF
from app.repositories import channel_repo
from app.models.video_models import Video

class YouTubeService:
    async def upload_video(
        self,
        access_token: str,
        video_path: str,
        title: str,
        description: str,
        tags: List[str],
        privacy_status: str,
        publish_at_iso: Optional[str] = None,
    ) -> Dict:
        # TODO: Implement YouTube Data API v3 (resumable upload). Đây là mock.
        resp = {"id": "dummy_id"}
        if publish_at_iso:
            resp["publishAt"] = publish_at_iso
        return resp

    async def post_video_via_channel(
        self, db: Session, *, channel_id: int, video_id: int, title: str,
        description: str, tags: Optional[List[str]], privacy_status: str,
        schedule_time_iso: Optional[str],
    ) -> Tuple[bool, Dict]:
        ch = channel_repo.get_by_id(db, channel_id)
        if not ch:
            return False, {"error": "YouTube channel not found"}
        plat = getattr(ch.platform, "value", ch.platform)
        if plat != PF.youtube.value:
            return False, {"error": "YouTube channel not found"}
        if not getattr(ch, "access_token", None):
            return False, {"error": "YouTube access_token missing"}
        video: Video = db.get(Video, video_id)
        if not video or not getattr(video, "file_path", None) or not os.path.exists(video.file_path):
            return False, {"error": "Video file not found"}
        
        
        publish_at_iso: Optional[str] = None
        if schedule_time_iso:
            try:
                dt = datetime.fromisoformat(schedule_time_iso)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                publish_at_iso = dt.isoformat()
            except Exception:
                publish_at_iso = None

        resp = await self.upload_video(
            access_token=ch.access_token,
            video_path=video.file_path,
            title=title or "Untitled",
            description=description or "",
            tags=tags or [],
            privacy_status=privacy_status or ("private" if publish_at_iso else "public"),
            publish_at_iso=publish_at_iso,
        )
        if isinstance(resp, dict) and resp.get("id"):
            out = {"id": resp["id"]}
            if publish_at_iso:
                out["publishAt"] = publish_at_iso
            return True, out
        return False, {"error": resp}