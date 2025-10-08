


from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.schedule_models import Schedule

def create(db: Session, **fields) -> Schedule:
    obj = Schedule(**fields); db.add(obj); db.commit(); db.refresh(obj); return obj

def list_schedules(db: Session, active: Optional[bool] = None, channel_id: Optional[int] = None) -> List[Schedule]:
    q = db.query(Schedule)
    if active is not None: q = q.filter(Schedule.is_active.is_(active))
    if channel_id is not None: q = q.filter(Schedule.channel_id == channel_id)
    return q.order_by(Schedule.id.desc()).all()

def get(db: Session, schedule_id: int) -> Schedule | None:
    return db.query(Schedule).filter(Schedule.id == schedule_id).first()

def update(db: Session, obj: Schedule, data: dict) -> Schedule:
    for k, v in data.items(): setattr(obj, k, v)
    db.commit(); db.refresh(obj); return obj

def toggle_active(db: Session, obj: Schedule, active: bool) -> Schedule:
    obj.is_active = active
    db.commit(); db.refresh(obj); return obj

def delete(db: Session, obj: Schedule):
    db.delete(obj); db.commit()
