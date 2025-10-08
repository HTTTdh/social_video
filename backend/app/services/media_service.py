import os
import uuid
import aiofiles
from pathlib import Path, PurePosixPath
from typing import Optional, List, Dict, Any
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.settings import get_settings
from app.repositories import media_repo
from app.models.media_models import MediaAsset

class MediaService:
    def __init__(self):
        self.settings = get_settings()
        self.media_root = Path(self.settings.MEDIA_ROOT)
        self.media_root.mkdir(parents=True, exist_ok=True)

    async def upload(self, db: Session, file: UploadFile, 
                    uploaded_by_id: Optional[int] = None) -> MediaAsset:
        # Validate file type
        if not file.content_type or not file.content_type.startswith(('image/', 'video/', 'audio/')):
            raise HTTPException(400, "Only image, video and audio files are allowed")
        
        # Generate unique filename
        file_ext = Path(file.filename or "").suffix
        unique_name = f"{uuid.uuid4()}{file_ext}"
        
        # Determine subdirectory by type
        if file.content_type.startswith('image/'):
            subdir = "images"
            media_type = "image"
        elif file.content_type.startswith('video/'):
            subdir = "videos"  
            media_type = "video"
        else:
            subdir = "audio"
            media_type = "audio"
            
        upload_dir = self.media_root / subdir
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / unique_name
        
        # Save file
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
        except Exception as e:
            raise HTTPException(500, f"Failed to save file: {str(e)}")
        
        # Create database record
        file_size = len(content) 
        relative_path = str(file_path.relative_to(self.media_root.parent))
        rel_path = PurePosixPath(relative_path).as_posix()  # ✅ "storage/images/xxx.png"
        
        asset = media_repo.create(
            db,
            type=media_type,
            path=rel_path,  # ✅ lưu path posix
            mime_type=file.content_type,
            size=file_size,
            uploaded_by_id=uploaded_by_id,
            media_metadata={}  # ✅ Khởi tạo empty dict
        )
        
        return asset
    
    # ✅ THÊM METHOD LIST - Router đang gọi svc.list()
    async def list(self, db: Session, type_filter: Optional[str] = None, 
                time_filter: Optional[str] = None, q: Optional[str] = None) -> List[MediaAsset]:
        return media_repo.list_assets(db, 
                                    type_filter=type_filter,
                                    time_filter=time_filter, 
                                    q=q)
    
    # ✅ THÊM METHOD STATS - Router đang gọi svc.stats()
    async def stats(self, db: Session) -> Dict[str, Any]:
        # Thống kê tổng quan
        total_query = db.query(func.count(MediaAsset.id))
        total = total_query.scalar() or 0
        
        # Thống kê theo type
        by_type_query = db.query(MediaAsset.type, func.count(MediaAsset.id)).group_by(MediaAsset.type)
        by_type = {row[0]: row[1] for row in by_type_query.all()}
        
        # Tổng dung lượng
        size_query = db.query(func.sum(MediaAsset.size))
        total_size = size_query.scalar() or 0
        
        return {
            "total": total,
            "by_type": by_type,
            "total_size": total_size
        }
    
    async def get(self, db: Session, asset_id: int) -> MediaAsset:
        asset = media_repo.get(db, asset_id)
        if not asset:
            raise HTTPException(404, "Media asset not found")
        return asset
    
    # ✅ THÊM METHOD UPDATE - Router đang gọi svc.update()
    async def update(self, db: Session, asset_id: int, payload: Dict[str, Any]) -> MediaAsset:
        asset = media_repo.get(db, asset_id)
        if not asset:
            raise HTTPException(404, "Media asset not found")
            
        # Update fields
        for field, value in payload.items():
            if hasattr(asset, field):
                setattr(asset, field, value)
        
        db.commit()
        db.refresh(asset)
        return asset

    async def delete(self, db: Session, asset_id: int):
        obj = media_repo.get(db, asset_id)
        if not obj: 
            raise HTTPException(404, "Asset not found")
        
        # Delete physical file
        try:
            if obj.path:
                base = self.media_root.parent
                abs_path = os.path.join(str(base), obj.path)
                if os.path.exists(abs_path):
                    os.remove(abs_path)
        except Exception: 
            pass
            
        media_repo.delete(db, obj)
