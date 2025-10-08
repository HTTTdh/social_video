from typing import Optional
from calendar import monthrange
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories import schedule_repo
from app.schemas.schedule_schemas import ScheduleCreateIn, ScheduleUpdateIn
from app.models.post_models import PostTarget

class ScheduleService:
    async def create(self, db: Session, payload: ScheduleCreateIn):
        return schedule_repo.create(db, **payload.model_dump())

    async def list(self, db: Session, active: Optional[bool] = None):
        return schedule_repo.list_schedules(db, active)

    async def get(self, db: Session, schedule_id: int):
        s = schedule_repo.get(db, schedule_id)
        if not s: raise HTTPException(404, "Schedule not found")
        return s

    async def update(self, db: Session, schedule_id: int, payload: ScheduleUpdateIn):
        s = schedule_repo.get(db, schedule_id)
        if not s: raise HTTPException(404, "Schedule not found")
        return schedule_repo.update(db, s, payload.model_dump(exclude_unset=True))

    async def pause(self, db: Session, schedule_id: int):
        s = await self.get(db, schedule_id)
        if s.is_active:
            return schedule_repo.update(db, s, {"is_active": False})
        return s

    async def resume(self, db: Session, schedule_id: int):
        s = await self.get(db, schedule_id)
        if not s.is_active:
            return schedule_repo.update(db, s, {"is_active": True})
        return s

    async def delete(self, db: Session, schedule_id: int):
        s = schedule_repo.get(db, schedule_id)
        if not s: raise HTTPException(404, "Schedule not found")
        schedule_repo.delete(db, s)

    async def calendar(self, db: Session, month: int, year: int):
        # Validate input
        if not (1 <= month <= 12):
            raise HTTPException(422, "month must be in 1..12")
        if year < 1970:
            raise HTTPException(422, "year must be >= 1970")

        days = monthrange(year, month)[1]
        start = datetime(year, month, 1, 0, 0, 0)
        end = datetime(year, month, days, 23, 59, 59)

        # Lấy các target có lịch trong tháng (bao gồm scheduled/queued/posting/posted)
        targets = db.query(PostTarget).filter(
            PostTarget.scheduled_time.isnot(None),
            PostTarget.scheduled_time >= start,
            PostTarget.scheduled_time <= end,
        ).all()

        by_day: dict[int, list] = {d: [] for d in range(1, days + 1)}
        for t in targets:
            dt = t.scheduled_time
            day = dt.day
            by_day.setdefault(day, []).append({
                "target_id": t.id,
                "post_id": t.post_id,
                "channel_id": t.channel_id,
                "status": t.status,
                "scheduled_time": dt.isoformat(),
                "platform_post_id": getattr(t, "platform_post_id", None),
            })

        return {
            "month": month,
            "year": year,
            "items": [{"day": d, "posts": by_day.get(d, [])} for d in range(1, days + 1)],
        }
