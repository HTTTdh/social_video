


from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.media_models import MediaAsset
from sqlalchemy import or_


def create(db: Session, **fields) -> MediaAsset:
    obj = MediaAsset(**fields); db.add(obj); db.commit(); db.refresh(obj); return obj

def list_assets(
    db: Session,
    type_filter: Optional[str] = None,
    time_filter: Optional[str] = None,
    q: Optional[str] = None,
    mime: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[MediaAsset]:
    qy = db.query(MediaAsset)
    if type_filter: qy = qy.filter(MediaAsset.type == type_filter)
    if mime: qy = qy.filter(MediaAsset.mime_type == mime)
    if q:
        like = f"%{q}%"
        qy = qy.filter(or_(MediaAsset.path.ilike(like)))
    # time_filter ("7d","30d") nên xử lý ở service → chuyển sang khoảng created_at
    return qy.order_by(MediaAsset.id.desc()).offset(offset).limit(limit).all()

def get(db: Session, asset_id: int) -> MediaAsset | None:
    return db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()

def update(db: Session, obj: MediaAsset, data: dict) -> MediaAsset:
    for k, v in data.items():
        setattr(obj, k, v)
    db.add(obj); db.commit(); db.refresh(obj); return obj

def delete(db: Session, obj: MediaAsset) -> None:
    db.delete(obj); db.commit()
