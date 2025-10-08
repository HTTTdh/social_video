


from sqlalchemy import String, Integer, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import Enum as SAEnum

from app.models.base import Base, TimestampMixin
from app.schemas.common import ChannelPlatformEnum

class Channel(Base, TimestampMixin):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    platform: Mapped[ChannelPlatformEnum] = mapped_column(
        SAEnum(ChannelPlatformEnum, name="channel_platform"),
        index=True,
        nullable=False,
    )         
    external_id: Mapped[str] = mapped_column(String(120), index=True)     
    name: Mapped[str] = mapped_column(String(255))
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    channel_metadata: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    source_ref_table: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_ref_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Quan hệ ngược với PostTarget (tiện truy vấn)
    targets = relationship("PostTarget", back_populates="channel")