

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String, index=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))

    interval_hours: Mapped[int] = mapped_column(Integer, default=2)

    start_time: Mapped[str] = mapped_column(String(5))   # "HH:MM"
    end_time: Mapped[str]   = mapped_column(String(5))   # "HH:MM"
    days_of_week: Mapped[str] = mapped_column(String(20))  # "1,2,3,4,5,6,7"

    auto_select_videos: Mapped[bool] = mapped_column(Boolean, default=True)

    template_caption_id: Mapped[int | None] = mapped_column(ForeignKey("templates.id"))
    template_hashtag_id: Mapped[int | None] = mapped_column(ForeignKey("templates.id"))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    channel = relationship("Channel")
    template_caption = relationship("Template", foreign_keys=[template_caption_id])
    template_hashtag = relationship("Template", foreign_keys=[template_hashtag_id])
    created_by = relationship("User")
