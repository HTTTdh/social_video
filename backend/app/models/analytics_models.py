


from sqlalchemy import String, Integer, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models.base import Base 

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    activity_metadata: Mapped[dict | None] = mapped_column(JSON)

    # CHỈNH: thêm mapped_column, set nullable
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)   # IPv4/IPv6
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User")

