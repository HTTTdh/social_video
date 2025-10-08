# app/api/deps.py
from typing import List
from fastapi import Depends, HTTPException, Header, status
from jose import jwt

from app.core.settings import get_settings
from app.services.roles_service import RoleService
from app.services.auth_service import AuthService
from app.services.post_service import PostService
from app.services.video_service import VideoService
from app.services.auth_service import AuthService
from app.services.analytics_service import AnalyticsService
from app.services.channel_service import ChannelService
from app.services.instagram_service import InstagramService
from app.services.facebook_service import FacebookService
from app.services.tiktok_service import TikTokService
from app.services.youtube_service import YouTubeService
from app.services.media_service import MediaService
from app.services.schedule_service import ScheduleService
from app.services.template_service import TemplateService



_settings = get_settings()

def get_auth_service() -> AuthService:
    return AuthService()

def get_post_service() -> PostService:
    return PostService()

def get_role_service() -> RoleService:
    return RoleService()

def get_video_service() -> VideoService:
    return VideoService()

def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()

def get_channel_service() -> ChannelService:
    return ChannelService()

def get_instagram_service() -> InstagramService:
    return InstagramService()

def get_facebook_service() -> FacebookService:
    return FacebookService()

def get_tiktok_service() -> TikTokService:
    return TikTokService()

def get_youtube_service() -> YouTubeService:
    return YouTubeService()

def get_media_service() -> MediaService:
    return MediaService()

def get_schedule_service() -> ScheduleService:
    return ScheduleService()

def get_template_service() -> TemplateService:
    return TemplateService()



def get_bearer_token(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    return authorization.split(" ", 1)[1]

def get_current_user_id(token: str = Depends(get_bearer_token)) -> int:
    try:
        data = jwt.decode(token, _settings.JWT_SECRET, algorithms=[_settings.JWT_ALG])
    except Exception:
        raise HTTPException(401, "Invalid token")
    sub = data.get("sub")
    if not sub:
        raise HTTPException(401, "Invalid token")
    return int(sub)

def require_roles(required: List[str]):
    def _inner(token: str = Depends(get_bearer_token)):
        try:
            data = jwt.decode(token, _settings.JWT_SECRET, algorithms=[_settings.JWT_ALG])
        except Exception:
            raise HTTPException(401, "Invalid token")
        roles = data.get("roles") or []
        if not any(r in roles for r in required):
            raise HTTPException(403, "Forbidden")
        return True
    return _inner

def get_role_service() -> RoleService:
    return RoleService()