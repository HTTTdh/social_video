from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.post_models import Post, PostTarget

# Post

def post_get_by_id(db: Session, post_id: int) -> Optional[Post]:
    return db.query(Post).filter(Post.id == post_id).first()

def post_list(
    db: Session,
    status: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Post]:
    query = db.query(Post)
    if status:
        query = query.filter(Post.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Post.caption.ilike(like), Post.hashtags.ilike(like)))
    return query.order_by(Post.created_at.desc()).offset(offset).limit(limit).all()

def post_create(db: Session, **data) -> Post:
    # Phòng ngừa key lạ
    data.pop("default_scheduled_time", None)
    obj = Post(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def post_update(db: Session, obj: Post, data: dict) -> Post:
    for k, v in data.items():
        setattr(obj, k, v)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def post_delete(db: Session, obj: Post) -> None:
    db.delete(obj); db.commit()

# PostTarget 

def target_list_by_post(db: Session, post_id: int) -> List[PostTarget]:
    return db.query(PostTarget).filter(PostTarget.post_id == post_id).all()

def target_create(db: Session, **data) -> PostTarget:
    obj = PostTarget(**data)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def target_bulk_create(db: Session, items: List[dict]) -> List[PostTarget]:
    objs = [PostTarget(**it) for it in items]
    db.add_all(objs); db.commit()
    for o in objs: db.refresh(o)
    return objs

def target_delete_for_post(db: Session, post_id: int) -> None:
    db.query(PostTarget).filter(PostTarget.post_id == post_id).delete(synchronize_session=False)
    db.commit()
