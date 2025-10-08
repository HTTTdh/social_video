

from sqlalchemy import String, Integer, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)

    original_url: Mapped[str | None] = mapped_column(String)
    source_platform: Mapped[str | None] = mapped_column(String)
    source_video_id: Mapped[str | None] = mapped_column(String)

    file_path: Mapped[str] = mapped_column(String)
    file_size: Mapped[int | None] = mapped_column(Integer)
    duration: Mapped[float | None] = mapped_column(Float)
    resolution: Mapped[str | None] = mapped_column(String)
    format: Mapped[str] = mapped_column(String, default="mp4")
    thumbnail_path: Mapped[str | None] = mapped_column(String)

    video_metadata: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String, default="processing")

    uploaded_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    uploaded_by = relationship("User")
    posts = relationship("Post", back_populates="video")
