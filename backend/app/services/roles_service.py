


from typing import List, Optional
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
import csv, io

from app.repositories import roles_repo
from app.schemas.roles_schemas import RoleCreateIn, RoleUpdateIn, UserCreate, UserUpdate
from app.models.auth_models import User

class RoleService:
    # Roles
    async def create_role(self, db: Session, payload: RoleCreateIn):
        return roles_repo.create_role(db, name=payload.name, permissions=payload.permissions)

    async def list_roles(self, db: Session):
        return roles_repo.list_roles(db)

    async def update_role(self, db: Session, role_id: int, payload: RoleUpdateIn):
        r = roles_repo.get_role(db, role_id)
        if not r: raise HTTPException(404, "Role not found")
        data = {}
        if payload.name is not None: data["name"] = payload.name
        if payload.permissions is not None: data["permissions"] = payload.permissions
        return roles_repo.update_role(db, r, data)

    async def delete_role(self, db: Session, role_id: int):
        role = roles_repo.get_role(db, role_id)
        if not role: raise HTTPException(404, "Role not found")
        roles_repo.delete_role(db, role)

    # Users
    async def create_user(self, db: Session, payload: UserCreate) -> User:
        fields = {
            "username": payload.username,
            "email": payload.email,
            "full_name": payload.full_name,
            "is_active": payload.is_active if payload.is_active is not None else True,
        }
        # Mật khẩu: nếu có, tự hash ở nơi khác (AuthService). Ở đây coi đã là hashed_password nếu bạn muốn.
        if payload.password:
            fields["hashed_password"] = payload.password  # tùy bạn muốn hash trước khi lưu
        u = roles_repo.create_user(db, **fields)
        if payload.role_ids:
            roles = roles_repo.get_roles_by_ids(db, payload.role_ids)
            u = roles_repo.set_user_roles(db, u, roles)
        return u

    async def list_users(self, db: Session, *, role_id: Optional[int], is_active: Optional[bool], q: Optional[str]):
        return roles_repo.list_users(db, role_id=role_id, is_active=is_active, q=q)

    async def update_user(self, db: Session, user_id: int, payload: UserUpdate) -> User:
        u = roles_repo.get_user(db, user_id)
        if not u: raise HTTPException(404, "User not found")
        data = {}
        if payload.username is not None: data["username"] = payload.username
        if payload.email is not None: data["email"] = payload.email
        if payload.password is not None: data["hashed_password"] = payload.password  
        if payload.full_name is not None: data["full_name"] = payload.full_name
        if payload.is_active is not None: data["is_active"] = payload.is_active
        u = roles_repo.update_user(db, u, data)
        role_ids = payload.role_ids
        if role_ids is not None:
            roles = roles_repo.get_roles_by_ids(db, role_ids)
            u = roles_repo.set_user_roles(db, u, roles)
        return u

    async def delete_user(self, db: Session, user_id: int):
        u = roles_repo.get_user(db, user_id)
        if not u: raise HTTPException(404, "User not found")
        roles_repo.delete_user(db, u)

    async def import_users(self, db: Session, file: UploadFile) -> List[User]:
        text = (await file.read()).decode("utf-8", "ignore")
        reader = csv.DictReader(io.StringIO(text))
        created: List[User] = []
        for row in reader:
            username = (row.get("username") or "").strip()
            email    = (row.get("email") or "").strip()
            if not username or not email:  # bỏ dòng lỗi
                continue
            full_name = (row.get("full_name") or "").strip()
            raw_pwd   = (row.get("password") or "ChangeMe123!").strip()
            u = roles_repo.create_user(db, username=username, email=email, full_name=full_name, hashed_password=raw_pwd, is_active=True)
            created.append(u)
        return created

    async def export_users_csv(self, db: Session) -> str:
        users = roles_repo.list_users(db)
        out = io.StringIO()
        w = csv.writer(out)
        w.writerow(["id", "username", "email", "full_name", "is_active", "roles"])
        for u in users:
            roles_names = ",".join([r.name for r in (u.roles or [])])
            w.writerow([u.id, u.username, u.email, u.full_name or "", "1" if u.is_active else "0", roles_names])
        return out.getvalue()

    async def users_metrics(self, db: Session):
        from sqlalchemy import func
        total  = db.query(func.count(User.id)).scalar() or 0
        active = db.query(func.count(User.id)).filter(User.is_active==True).scalar() or 0
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_in_month = db.query(func.count(User.id)).filter(User.created_at >= start).scalar() or 0
        return {"total": total, "active": active, "new_in_month": new_in_month}