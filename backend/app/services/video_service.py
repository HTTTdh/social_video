

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func, or_
import os
import subprocess

from app.repositories import video_repo, media_repo
from app.schemas.video_schemas import VideoImportIn, VideoProcessIn, VideoUpdateIn, TrimIn, CropIn, WatermarkIn, ThumbnailIn
from app.models.video_models import Video

UPLOAD_DIR = os.getenv("VIDEO_UPLOAD_DIR", "storage/videos")
FFMPEG_BIN = os.getenv("FFMPEG_BIN", "ffmpeg")

def _safe_filename(name: str) -> str:
    import re, uuid, os
    base = os.path.basename(name or "")
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", base) or f"out_{uuid.uuid4().hex}.mp4"
    return base

def _derive_output_path(src: str, suffix: str, ext: str = "mp4") -> str:
    root, _ = os.path.splitext(os.path.basename(src))
    out_name = _safe_filename(f"{root}_{suffix}.{ext}")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    return os.path.join(UPLOAD_DIR, out_name)

def _run_ffmpeg(args: list[str]) -> None:
    # raise nếu ffmpeg trả mã lỗi
    proc = subprocess.run([FFMPEG_BIN, *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {proc.stdout.decode(errors='ignore')[:2000]}")

class VideoService:
    async def import_urls(self, db: Session, payload: VideoImportIn) -> List[Video]:
        videos: List[Video] = []
        for url in payload.urls:
            v = video_repo.create(
                db,
                title=url.split("/")[-1] or "video",
                description=None,
                original_url=url,
                source_platform=payload.source_platform,
                file_path="",
                status="processing",
                video_metadata={"remove_watermark": payload.remove_watermark, "use_proxy": payload.use_proxy},
            )
            videos.append(v)
        return videos

    async def upload(self, db: Session, files: List[UploadFile], remove_watermark: bool = False) -> List[Video]:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        out: List[Video] = []
        for f in files:
            # ghi file thực
            dest = os.path.join(UPLOAD_DIR, f.filename)
            size = 0
            with open(dest, "wb") as w:
                while True:
                    chunk = await f.read(1024 * 1024)
                    if not chunk: break
                    w.write(chunk)
                    size += len(chunk)

            v = video_repo.create(
                db,
                title=f.filename,
                description=None,
                original_url=None,
                source_platform=None,
                file_path=dest,
                file_size=size,
                status="ready" if not remove_watermark else "processing",
                video_metadata={"original_filename": f.filename, "remove_watermark": remove_watermark},
            )
            out.append(v)

            media_repo.create(
                db,
                type="video",
                path=str(dest),                              
                mime_type=(getattr(f, "content_type", None) or "video/mp4"),
                size=size,                                  
                media_metadata={"source": "upload", "video_id": v.id}, 
                uploaded_by_id=None,
            )
        return out

    async def update(self, db: Session, video_id: int, payload: VideoUpdateIn) -> Video:
        v = video_repo.get_by_id(db, video_id)
        if not v:
            raise HTTPException(404, "Video not found")
        data = payload.model_dump(exclude_unset=True)
        # gộp meta thay vì overwrite
        if "video_metadata" in data and v.video_metadata:
            merged = dict(v.video_metadata); merged.update(data["video_metadata"])
            data["video_metadata"] = merged
        return video_repo.update(db, v, data)

    async def list(
                self,
                db: Session,
                status: Optional[str] = None,
                source: Optional[str] = None,  
                q: Optional[str] = None,
                limit: int = 100,
                offset: int = 0
                ) -> List[Video]:
        query = db.query(Video)
        if status:
            query = query.filter(Video.status == status)
        if source:  # tiktok/youtube/douyin/upload
            if source.lower() == "upload":
                query = query.filter(Video.source_platform.is_(None))
            else:
                query = query.filter(Video.source_platform.ilike(source))
        if q:
            like = f"%{q.strip()}%"
            query = query.filter(or_(Video.title.ilike(like), Video.description.ilike(like)))
        return (
            query.order_by(Video.created_at.desc(), Video.id.desc())
                .offset(offset).limit(limit)
                .all()
        )
    
    async def queue(self, db: Session) -> List[Video]:
        return video_repo.list_queue(db)

    async def get(self, db: Session, video_id: int) -> Video:
        v = video_repo.get_by_id(db, video_id)
        if not v:
            raise HTTPException(404, "Video not found")
        return v

    async def process(self, db: Session, payload: VideoProcessIn) -> List[Video]:
        out: List[Video] = []
        for vid in payload.ids:
            v = video_repo.get_by_id(db, vid)
            if not v:
                continue
            meta = dict(v.video_metadata or {})
            if payload.add_watermark_template_id:
                meta["watermark_template_id"] = payload.add_watermark_template_id
            if payload.add_frame_template_id:
                meta["frame_template_id"] = payload.add_frame_template_id
            v = video_repo.update(db, v, {"video_metadata": meta, "status": "ready"})
            out.append(v)
        return out

    async def delete(self, db: Session, video_id: int) -> None:
        v = video_repo.get_by_id(db, video_id)
        if not v:
            raise HTTPException(404, "Video not found")
        # TODO: xóa file storage nếu có
        video_repo.delete(db, v)
    
    async def stats(self, db: Session) -> dict:
        total = db.query(func.count(Video.id)).scalar() or 0
        ready = db.query(func.count(Video.id)).filter(Video.status == "ready").scalar() or 0
        processing = db.query(func.count(Video.id)).filter(Video.status == "processing").scalar() or 0
        error = db.query(func.count(Video.id)).filter(Video.status == "error").scalar() or 0
    # nếu có file_size: tính GB storage
        size_bytes = db.query(func.coalesce(func.sum(Video.file_size), 0)).scalar() or 0
        storage_gb = round(size_bytes / (1024**3), 2)
        return {"total": total, "ready": ready, "processing": processing, "error": error, "storage_gb": storage_gb}    

    async def trim(self, db: Session, body: TrimIn) -> Video:
        v = video_repo.get_by_id(db, body.video_id)
        if not v: raise HTTPException(404, "Video not found")
        out_path = _derive_output_path(v.file_path, f"trim_{int(body.start)}_{'' if body.end is None else int(body.end)}")
        # chọn copy stream (nhanh) hay re-encode
        if body.reencode:
            ff = ["-ss", str(body.start)]
            if body.end is not None: ff += ["-to", str(body.end)]
            ff += ["-i", v.file_path, "-c:v", "libx264", "-c:a", "aac", "-y", out_path]
        else:
            ff = ["-ss", str(body.start)]
            if body.end is not None: ff += ["-to", str(body.end)]
            ff += ["-i", v.file_path, "-c", "copy", "-y", out_path]
        _run_ffmpeg(ff)
        size = os.path.getsize(out_path)
        # cập nhật file_path (giữ path cũ trong metadata)
        meta = dict(v.video_metadata or {})
        meta.setdefault("prev_files", []).append(v.file_path)
        v = video_repo.update(db, v, {"file_path": out_path, "file_size": size, "video_metadata": meta, "status": "ready"})
        return v

    async def crop(self, db: Session, body: CropIn) -> Video:
        v = video_repo.get_by_id(db, body.video_id)
        if not v: raise HTTPException(404, "Video not found")
        out_path = _derive_output_path(v.file_path, f"crop_{body.width}x{body.height}_{body.x}_{body.y}")
        filt = f"crop={body.width}:{body.height}:{body.x}:{body.y}"
        _run_ffmpeg(["-i", v.file_path, "-vf", filt, "-c:v", "libx264", "-c:a", "copy", "-y", out_path])
        size = os.path.getsize(out_path)
        meta = dict(v.video_metadata or {})
        meta.setdefault("prev_files", []).append(v.file_path)
        v = video_repo.update(db, v, {"file_path": out_path, "file_size": size, "video_metadata": meta, "status": "ready"})
        return v

    async def watermark(self, db: Session, body: WatermarkIn) -> Video:
        v = video_repo.get_by_id(db, body.video_id)
        if not v: raise HTTPException(404, "Video not found")
        mark = body.watermark_path
        if not os.path.isfile(mark):
            raise HTTPException(400, "watermark_path not found")
        out_path = _derive_output_path(v.file_path, "wm")
        # nếu cần opacity < 1: chuyển watermark sang alpha bằng filter
        overlay = f"overlay={body.x}:{body.y}"
        if body.opacity < 1.0:
            filt = f"[1]format=rgba,colorchannelmixer=aa={body.opacity}[wm];[0][wm]{overlay}"
            _run_ffmpeg(["-i", v.file_path, "-i", mark, "-filter_complex", filt, "-c:v", "libx264", "-c:a", "copy", "-y", out_path])
        else:
            _run_ffmpeg(["-i", v.file_path, "-i", mark, "-filter_complex", overlay, "-c:v", "libx264", "-c:a", "copy", "-y", out_path])
        size = os.path.getsize(out_path)
        meta = dict(v.video_metadata or {})
        meta.setdefault("prev_files", []).append(v.file_path)
        meta["watermark_path"] = mark
        v = video_repo.update(db, v, {"file_path": out_path, "file_size": size, "video_metadata": meta, "status": "ready"})
        return v

    async def thumbnail_auto(self, db: Session, body: ThumbnailIn) -> Video:
        v = video_repo.get_by_id(db, body.video_id)
        if not v: raise HTTPException(404, "Video not found")
        # xuất 1 ảnh thumbnail
        out_jpg = _derive_output_path(v.file_path, "thumb", ext="jpg")
        if body.method == "scene":
            # chọn khung có scene-change lớn (thường là khung rõ nhất)
            _run_ffmpeg(["-i", v.file_path, "-vf", "select=gt(scene\\,0.4),thumbnail,scale=640:-1", "-frames:v", "1", "-y", out_jpg])
        else:
            # lấy khung giữa video
            _run_ffmpeg(["-i", v.file_path, "-vf", "thumbnail,scale=640:-1", "-frames:v", "1", "-y", out_jpg])
        meta = dict(v.video_metadata or {})
        meta["thumbnail_generated"] = True
        v = video_repo.update(db, v, {"thumbnail_path": out_jpg, "video_metadata": meta})
        # lưu vào Media Library
        try:
            from app.repositories import media_repo
            media_repo.create(db, type="image", path=out_jpg, mime_type="image/jpeg", size=os.path.getsize(out_jpg),
                    media_metadata={"source": "thumbnail", "video_id": v.id}, uploaded_by_id=None)
        except Exception:
            pass
        return v