from typing import List, Optional
from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db


from app.api.deps import get_media_service, require_roles
from app.services.media_service import MediaService
from app.schemas.media_schemas import MediaAssetOut, MediaUpdateIn

router = APIRouter(prefix="/media", tags=["media"])

@router.post("/upload", response_model=List[MediaAssetOut], status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(require_roles(["admin","staff"]))])
async def upload_media(files: List[UploadFile] = File(...), db: Session = Depends(get_db), svc: MediaService = Depends(get_media_service)):
    results = []
    for file in files:
        result = await svc.upload(db=db, file=file)  # file thay vì files
        results.append(result)
    return results

@router.get("/", response_model=List[MediaAssetOut], dependencies=[Depends(require_roles(["admin","staff"]))])
async def list_media(type_filter: Optional[str] = None, time_filter: Optional[str] = None, q: Optional[str] = None,
                    db: Session = Depends(get_db), svc: MediaService = Depends(get_media_service)):
    return await svc.list(db=db, type_filter=type_filter, time_filter=time_filter, q=q)

@router.get("/stats", dependencies=[Depends(require_roles(["admin","staff"]))])
async def media_stats(db: Session = Depends(get_db), svc: MediaService = Depends(get_media_service)):
    return await svc.stats(db)

@router.get("/{asset_id}", response_model=MediaAssetOut, dependencies=[Depends(require_roles(["admin","staff"]))])
async def get_media(asset_id: int, db: Session = Depends(get_db), svc: MediaService = Depends(get_media_service)):
    return await svc.get(db=db, asset_id=asset_id)

@router.put("/{asset_id}", response_model=MediaAssetOut, dependencies=[Depends(require_roles(["admin","staff"]))])
async def update_media(asset_id: int, body: MediaUpdateIn, db: Session = Depends(get_db), svc: MediaService = Depends(get_media_service)):
    return await svc.update(db=db, asset_id=asset_id, payload=body)

@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles(["admin","staff"]))])
async def delete_media(asset_id: int, db: Session = Depends(get_db), svc: MediaService = Depends(get_media_service)):
    await svc.delete(db=db, asset_id=asset_id)
