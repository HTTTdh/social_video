from __future__ import annotations

import logging
import os
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.settings import get_settings
from app.core.timezone import now_vn
from app.core.database import engine

# Import routers (giữ nguyên file/endpoint hiện có)
from app.api import (
    oauth_router,
    post_routers,
    channel_routers,
    instagram_routers,
    facebook_routers,
    tiktok_routers,
    youtube_routers,
    video_routers,
    media_routers,
    analytics_routers,
    roles_routers,
    schedule_routers,
    template_routers,
    auth_routers,
)

# Import Base và các models để tạo tables
from app.models.base import Base
from app.models.auth_models import User
from app.models.roles_models import Role
from app.models.association import user_roles
from app.models.channel_models import Channel, ChannelPlatformEnum
from app.models.media_models import MediaAsset
from app.models.post_models import Post, PostMedia, PostTarget
from app.models.video_models import Video
from app.models.template_models import Template
from app.models.schedule_models import Schedule
from app.models.analytics_models import ActivityLog

# Import các models khác nếu cần

settings = get_settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")


def create_app() -> FastAPI:
    title = getattr(settings, "APP_NAME", "VideoV02")
    docs_url = "/docs" if getattr(settings, "DEBUG", True) else "/docs"
    redoc_url = "/redoc" if getattr(settings, "DEBUG", True) else "/redoc"

    app = FastAPI(title=title, docs_url=docs_url, redoc_url=redoc_url)

    # CORS
    cors_origins = getattr(settings, "CORS_ORIGINS", ["*"]) or ["*"]
    # Trong main.py
    app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Sử dụng property mới
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

    # Exception handlers ngắn gọn (trả JSON nhất quán)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"error": "validation_error", "detail": exc.errors()},
        )

    # Health & root
    @app.get("/health")
    async def health() -> Dict[str, Any]:
        return {"ok": True, "time_vn": now_vn().isoformat()}

    @app.get("/")
    async def root() -> Dict[str, Any]:
        return {"name": title, "ok": True}

    # Include routers dưới prefix API
    api_prefix = getattr(settings, "API_PREFIX", "/api") or "/api"
    app.include_router(oauth_router.router, prefix=api_prefix)
    app.include_router(post_routers.router, prefix=api_prefix)
    app.include_router(channel_routers.router, prefix=api_prefix)
    app.include_router(instagram_routers.router, prefix=api_prefix)
    app.include_router(facebook_routers.router, prefix=api_prefix)
    app.include_router(tiktok_routers.router, prefix=api_prefix)
    app.include_router(youtube_routers.router, prefix=api_prefix)
    app.include_router(video_routers.router, prefix=api_prefix)
    app.include_router(media_routers.router, prefix=api_prefix)
    app.include_router(analytics_routers.router, prefix=api_prefix)
    app.include_router(roles_routers.router, prefix=api_prefix)
    app.include_router(schedule_routers.router, prefix=api_prefix)
    app.include_router(template_routers.router, prefix=api_prefix)
    app.include_router(auth_routers.router, prefix=api_prefix)

    @app.on_event("startup")
    async def on_startup():
        logger.info("App started")
        # TỰ ĐỘNG TẠO TABLES
        create_tables()

    @app.on_event("shutdown")
    async def on_shutdown():
        logger.info("App stopped")

    return app

# Hàm tạo tables tự động
def create_tables():
    """Tự động tạo tables từ models nếu chưa tồn tại"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        import traceback
        traceback.print_exc()


app = create_app()

# Bạn cũng có thể tạo tables ở đây (ngoài startup event)
# create_tables()

# Ví dụ thư mục chứa file: backend/storage
STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "storage")
STORAGE_DIR = os.path.abspath(STORAGE_DIR)
os.makedirs(STORAGE_DIR, exist_ok=True)

# Phục vụ static tại /storage
app.mount("/storage", StaticFiles(directory=STORAGE_DIR), name="storage")