# Quản trị Roles & Users (chỉ Admin)



from typing import List, Optional
from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import io

from app.core.database import get_db
from app.api.deps import get_role_service, require_roles
from app.services.roles_service import RoleService
from app.schemas.roles_schemas import RoleCreateIn, RoleUpdateIn, RoleOut, UserCreate, UserUpdate, UserOut

router = APIRouter(prefix="/admin", tags=["admin"])

# Roles
@router.post("/roles", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
async def create_role(body: RoleCreateIn, db: Session = Depends(get_db), _ = Depends(require_roles(["admin"])), svc: RoleService = Depends(get_role_service)):
    return await svc.create_role(db=db, payload=body)

@router.get("/roles", response_model=List[RoleOut])
async def list_roles(db: Session = Depends(get_db), _ = Depends(require_roles(["admin"])), svc: RoleService = Depends(get_role_service)):
    return await svc.list_roles(db=db)

@router.put("/roles/{role_id}", response_model=RoleOut)
async def update_role(role_id: int, body: RoleUpdateIn, db: Session = Depends(get_db), _ = Depends(require_roles(["admin"])), svc: RoleService = Depends(get_role_service)):
    return await svc.update_role(db=db, role_id=role_id, payload=body)

@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: int, db: Session = Depends(get_db), _ = Depends(require_roles(["admin"])), svc: RoleService = Depends(get_role_service)):
    await svc.delete_role(db=db, role_id=role_id)

# Users
@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["admin"]))])
async def create_user(body: UserCreate, db: Session = Depends(get_db), svc: RoleService = Depends(get_role_service)):
    return await svc.create_user(db=db, payload=body)

@router.get("/users", response_model=List[UserOut], dependencies=[Depends(require_roles(["admin"]))])
async def list_users(
    role_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    svc: RoleService = Depends(get_role_service),
):
    return await svc.list_users(db=db, role_id=role_id, is_active=is_active, q=q)

@router.put("/users/{user_id}", response_model=UserOut, dependencies=[Depends(require_roles(["admin"]))])
async def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db), svc: RoleService = Depends(get_role_service)):
    return await svc.update_user(db=db, user_id=user_id, payload=body)

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles(["admin"]))])
async def delete_user(user_id: int, db: Session = Depends(get_db), svc: RoleService = Depends(get_role_service)):
    await svc.delete_user(db=db, user_id=user_id)

@router.post("/users/import", response_model=List[UserOut], status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles(["admin"]))])
async def import_users(file: UploadFile = File(...), db: Session = Depends(get_db), svc: RoleService = Depends(get_role_service)):
    return await svc.import_users(db=db, file=file)

@router.get("/users/export", dependencies=[Depends(require_roles(["admin"]))])
async def export_users(db: Session = Depends(get_db), svc: RoleService = Depends(get_role_service)):
    csv_text = await svc.export_users_csv(db)
    return StreamingResponse(io.StringIO(csv_text), media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="users.csv"'}
    )

@router.get("/users/metrics", dependencies=[Depends(require_roles(["admin"]))])
async def users_metrics(db: Session = Depends(get_db), svc: RoleService = Depends(get_role_service)):
    return await svc.users_metrics(db)