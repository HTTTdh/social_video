from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List

from app.models.roles_models import Role
from app.models.auth_models import User

# Roles
def create_role(db: Session, **fields) -> Role:
    role = Role(**fields)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

def list_roles(db: Session) -> List[Role]:
    return db.query(Role).order_by(Role.name.asc()).all()

def get_role(db: Session, role_id: int) -> Role | None:
    return db.query(Role).filter(Role.id == role_id).first()

def delete_role(db: Session, role: Role) -> None:
    db.delete(role)
    db.commit()

def update_role(db: Session, role: Role, data: dict) -> Role:
    for k, v in data.items():
        if hasattr(role, k):
            setattr(role, k, v)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

def get_roles_by_ids(db: Session, ids: List[int]) -> List[Role]:
    if not ids:
        return []
    return db.query(Role).filter(Role.id.in_(ids)).all()

# Users
def create_user(db: Session, **fields) -> User:
    user = User(**fields)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def list_users(db: Session, role_id: Optional[int] = None, is_active: Optional[bool] = None, q: Optional[str] = None) -> List[User]:
    qy = db.query(User)
    if is_active is not None:
        qy = qy.filter(User.is_active == is_active)
    if q:
        like = f"%{q}%"
        qy = qy.filter(or_(User.username.ilike(like), User.email.ilike(like)))
    if role_id:
        qy = qy.join(User.roles).filter(Role.id == role_id)
    return qy.order_by(User.created_at.desc()).all()

def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()

def update_user(db: Session, user: User, data: dict) -> User:
    for k, v in data.items():
        if hasattr(user, k):
            setattr(user, k, v)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def set_user_roles(db: Session, user: User, roles: List[Role]) -> User:
    user.roles = roles or []
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
