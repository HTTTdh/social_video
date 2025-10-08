


from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import or_
from app.models.video_models import Video

def get_by_id(db: Session, id_: int) -> Optional[Video]:
    return db.query(Video).filter(Video.id == id_).first()

def list_queue(db: Session) -> List[Video]:
    return db.query(Video).filter(Video.status.in_(["processing", "error"])).order_by(Video.id.desc()).all()

def list(
    db: Session,
    status: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Video]:
    qy = db.query(Video)
    if status: qy = qy.filter(Video.status == status)
    if q:
        like = f"%{q}%"
        qy = qy.filter(or_(Video.title.ilike(like), Video.description.ilike(like)))
    return qy.order_by(Video.id.desc()).offset(offset).limit(limit).all()

def create(db: Session, **fields) -> Video:
    obj = Video(**fields)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def update(db: Session, obj: Video, data: dict) -> Video:
    for k, v in data.items():
        setattr(obj, k, v)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def delete(db: Session, obj: Video) -> None:
    db.delete(obj); db.commit()

def list_ready(db: Session, limit: int = 100) -> List[Video]:
    return db.query(Video).filter(Video.status == "ready").order_by(Video.id.desc()).limit(limit).all()

def _safe_name(name: str) -> str:
    import uuid, os
    base = os.path.basename(name or "").strip()
    return base or f"upload_{uuid.uuid4().hex}.bin"
