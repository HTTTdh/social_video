# Import/Upload/Process Video



from typing import List, Optional
from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db

from app.api.deps import get_video_service, require_roles
from app.services.video_service import VideoService
from app.schemas.video_schemas import VideoImportIn, VideoOut, VideoProcessIn, VideoUpdateIn, TrimIn, CropIn, WatermarkIn, ThumbnailIn


router = APIRouter(prefix="/videos", tags=["videos"])

@router.get("/stats")
async def video_stats(
    db: Session = Depends(get_db),
    _ = Depends(require_roles(["admin","staff"])),
    svc: VideoService = Depends(get_video_service),
):
    return await svc.stats(db)

@router.get("/queue", response_model=List[VideoOut])
async def video_queue(
    db: Session = Depends(get_db), 
    _ = Depends(require_roles(["admin","staff"])), 
    svc: VideoService = Depends(get_video_service)):
    return await svc.queue(db)

@router.post("/import", response_model=List[VideoOut], status_code=status.HTTP_202_ACCEPTED)
async def import_videos(
    body: VideoImportIn,
    db: Session = Depends(get_db),
    _ = Depends(require_roles(["admin","staff"])),
    svc: VideoService = Depends(get_video_service),
):
    return await svc.import_urls(db=db, payload=body)

@router.post("/upload", response_model=List[VideoOut], status_code=status.HTTP_201_CREATED)
async def upload_videos(
    files: List[UploadFile] = File(...),          # KEY phải tên đúng "files"
    title: Optional[str] = Form(None),            # mọi metadata khác dùng Form(...)
    channel_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    _ = Depends(require_roles(["admin","staff"])),
    svc: VideoService = Depends(get_video_service),
):
    return await svc.upload(db=db, files=files, title=title, channel_id=channel_id)

@router.post("/process", response_model=List[VideoOut])
async def process_videos(
    body: VideoProcessIn,
    db: Session = Depends(get_db),
    _ = Depends(require_roles(["admin","staff"])),
    svc: VideoService = Depends(get_video_service),
):
    return await svc.process(db=db, payload=body)

@router.get("/", response_model=List[VideoOut])
async def list_videos(
    status: str | None = None,
    source: str | None = None,
    q: str | None = None,
    page: int = 1,
    page_size: int = 24,
    db: Session = Depends(get_db),
    _ = Depends(require_roles(["admin","staff"])),
    svc: VideoService = Depends(get_video_service),
):
    offset = (page - 1) * page_size
    return await svc.list(db=db, status=status, source=source, q=q, limit=page_size, offset=offset)

@router.get("/{video_id}", response_model=VideoOut)
async def get_video(
    video_id: int, 
    db: Session = Depends(get_db), 
    _ = Depends(require_roles(["admin","staff"])), 
    svc: VideoService = Depends(get_video_service)):
    return await svc.get(db=db, video_id=video_id)

@router.put("/{video_id}", response_model=VideoOut)
async def update_video(
    video_id: int, 
    body: VideoUpdateIn, 
    db: Session = Depends(get_db), 
    _ = Depends(require_roles(["admin","staff"])), 
    svc: VideoService = Depends(get_video_service)
):
    return await svc.update(db=db, video_id=video_id, payload=body)

@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: int, 
    db: Session = Depends(get_db), 
    _ = Depends(require_roles(["admin","staff"])), 
    svc: VideoService = Depends(get_video_service)
):
    await svc.delete(db=db, video_id=video_id)
    
@router.post("/trim", response_model=VideoOut)
async def trim_video(
    body: TrimIn,
    db: Session = Depends(get_db),
    _ = Depends(require_roles(["admin","staff"])),
    svc: VideoService = Depends(get_video_service),
):
    return await svc.trim(db, body)

@router.post("/crop", response_model=VideoOut)
async def crop_video(
    body: CropIn,
    db: Session = Depends(get_db),
    _ = Depends(require_roles(["admin","staff"])),
    svc: VideoService = Depends(get_video_service),
):
    return await svc.crop(db, body)

@router.post("/watermark", response_model=VideoOut)
async def watermark_video(
    body: WatermarkIn,
    db: Session = Depends(get_db),
    _ = Depends(require_roles(["admin","staff"])),
    svc: VideoService = Depends(get_video_service),
):
    return await svc.watermark(db, body)

@router.post("/thumbnail/auto", response_model=VideoOut)
async def auto_thumbnail(
    body: ThumbnailIn,
    db: Session = Depends(get_db),
    _ = Depends(require_roles(["admin","staff"])),
    svc: VideoService = Depends(get_video_service),
):
    return await svc.thumbnail_auto(db, body)