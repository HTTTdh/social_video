


from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.template_models import Template

def create(db: Session, **fields) -> Template:
    obj = Template(**fields); db.add(obj); db.commit(); db.refresh(obj); return obj

def list_templates(db: Session, type_filter: Optional[str] = None) -> List[Template]:
    q = db.query(Template)
    if type_filter: q = q.filter(Template.type == type_filter)
    return q.order_by(Template.id.desc()).all()

def get(db: Session, template_id: int) -> Template | None:
    return db.query(Template).filter(Template.id == template_id).first()

def get_by_name_type(db: Session, name: str, type_: str) -> Template | None:
    return db.query(Template).filter(Template.name == name, Template.type == type_).first()

def upsert(db: Session, name: str, type_: str, defaults: dict) -> Template:
    obj = get_by_name_type(db, name, type_)
    if obj:
        for k, v in defaults.items(): setattr(obj, k, v)
        db.commit(); db.refresh(obj); return obj
    obj = Template(name=name, type=type_, **defaults)
    db.add(obj); db.commit(); db.refresh(obj); return obj

def update(db: Session, obj: Template, data: dict) -> Template:
    for k, v in data.items(): setattr(obj, k, v)
    db.commit(); db.refresh(obj); return obj

def delete(db: Session, obj: Template):
    db.delete(obj); db.commit()
