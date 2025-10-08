from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_
from app.models.auth_models import User
from typing import Optional

def get_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID with roles loaded"""
    return (
        db.query(User)
        .options(selectinload(User.roles))  # ✅ Eager load roles
        .filter(User.id == user_id)
        .first()
    )

def get_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email with roles loaded"""
    return (
        db.query(User)
        .options(selectinload(User.roles))  # ✅ Eager load roles
        .filter(User.email == email)
        .first()
    )

def get_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username with roles loaded"""
    return (
        db.query(User)
        .options(selectinload(User.roles))  # ✅ Eager load roles
        .filter(User.username == username)
        .first()
    )

def get_by_username_or_email(db: Session, identifier: str) -> Optional[User]:
    """Get user by username OR email with roles loaded"""
    return (
        db.query(User)
        .options(selectinload(User.roles))  # ✅ Eager load roles
        .filter(or_(User.username == identifier, User.email == identifier))
        .first()
    )

def create(db: Session, **data) -> User:
    """Create new user"""
    user = User(**data)
    db.add(user)
    db.commit()
    db.refresh(user)
    # Load roles after creation
    db.refresh(user, ["roles"])
    return user

def update(db: Session, user: User, **data) -> User:
    """Update user fields"""
    for key, value in data.items():
        if hasattr(user, key) and key != "id":  # ✅ Không cho update ID
            setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(user, ["roles"])  # ✅ Refresh roles
    return user

def delete(db: Session, user: User) -> None:
    """Delete user (soft delete recommended)"""
    db.delete(user)
    db.commit()

def list_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    is_active: Optional[bool] = None
) -> list[User]:
    """List users with pagination and optional filter"""
    query = db.query(User).options(selectinload(User.roles))
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()

def count_users(db: Session, is_active: Optional[bool] = None) -> int:
    """Count users with optional filter"""
    query = db.query(User)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    return query.count()

def exists_username(db: Session, username: str) -> bool:
    """Check if username exists"""
    return db.query(User).filter(User.username == username).count() > 0

def exists_email(db: Session, email: str) -> bool:
    """Check if email exists"""
    return db.query(User).filter(User.email == email).count() > 0
