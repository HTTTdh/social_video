from sqlalchemy import String, Integer, Text, JSON, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin
from sqlalchemy import Enum as SAEnum

from app.schemas.common import ChannelPlatformEnum

class Post(Base, TimestampMixin):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashtags: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)

    video_id: Mapped[int | None] = mapped_column(ForeignKey("videos.id"), nullable=True)
    template_id: Mapped[int | None] = mapped_column(ForeignKey("templates.id"), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    post_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # ✅ thêm

    video = relationship("Video")
    template = relationship("Template")
    created_by = relationship("User")
    media = relationship("PostMedia", back_populates="post", cascade="all, delete-orphan")
    targets = relationship("PostTarget", back_populates="post", cascade="all, delete-orphan")

class PostMedia(Base, TimestampMixin):
    __tablename__ = "post_media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    media_id: Mapped[int] = mapped_column(ForeignKey("media_assets.id"))
    order: Mapped[int] = mapped_column(Integer, default=0)

    post = relationship("Post", back_populates="media")
    media = relationship("MediaAsset")

    __table_args__ = (UniqueConstraint("post_id", "media_id", name="uq_post_media"),)

class PostTarget(Base, TimestampMixin):
    __tablename__ = "post_targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), index=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))
    platform: Mapped[ChannelPlatformEnum] = mapped_column(
        SAEnum(ChannelPlatformEnum, name="channel_platform"),
        index=True,
        nullable=False,
    )

    scheduled_time: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    posted_time: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    platform_post_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    engagement_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    post = relationship("Post", back_populates="targets")
    channel = relationship("Channel", back_populates="targets")

    __table_args__ = (UniqueConstraint("post_id", "channel_id", name="uq_post_channel"),)
