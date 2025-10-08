

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_auth_service, get_current_user_id, get_bearer_token
from app.schemas.auth_schemas import LoginIn, LoginOut, RefreshIn, RefreshOut, MeOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginOut, status_code=status.HTTP_200_OK)
async def login(body: LoginIn, db: Session = Depends(get_db), svc: AuthService = Depends(get_auth_service)):
    return await svc.login(db=db, payload=body)

@router.post("/refresh", response_model=RefreshOut)
async def refresh(body: RefreshIn, db: Session = Depends(get_db), svc: AuthService = Depends(get_auth_service)):
    return await svc.refresh(db=db, payload=body)

@router.get("/me", response_model=MeOut)
async def me(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db), 
    svc: AuthService = Depends(get_auth_service)
):
    return await svc.me(db=db, user_id=user_id)

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    token: str = Depends(get_bearer_token),
    db: Session = Depends(get_db), 
    svc: AuthService = Depends(get_auth_service)
):
    await svc.logout(db=db, token=token)
