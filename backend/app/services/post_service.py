from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone

from app.schemas.post_schemas import PostCreateIn, PostUpdateIn
from app.repositories import post_repo, channel_repo
from app.models.post_models import Post
from app.models.channel_models import Channel
from app.services.facebook_service import FacebookService
from app.services.instagram_service import InstagramService
from app.services.tiktok_service import TikTokService
from app.services.youtube_service import YouTubeService
from app.schemas.common import ChannelPlatformEnum as PF
from app.models.post_models import PostTarget, Post


class PostService:
    def create(self, db: Session, payload: PostCreateIn, created_by_id: int | None = None) -> Post:
        if not payload.targets:
            raise HTTPException(422, "At least one target is required")

        def to_aware(dt):
            if not dt:
                return None
            return dt if getattr(dt, "tzinfo", None) else dt.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        default_dt = to_aware(getattr(payload, "default_scheduled_time", None))

        # loại field không có trong model
        data = payload.model_dump(exclude={"targets", "default_scheduled_time"}, by_alias=True)

        # Tính trạng thái Post tổng quát
        any_future = False
        for t in payload.targets:
            st = to_aware(getattr(t, "scheduled_time", None)) or default_dt
            if st and st > now:
                any_future = True
                break
        data["status"] = "scheduled" if any_future else "ready"

        if created_by_id:
            data["created_by_id"] = created_by_id

        post = post_repo.post_create(db, **data)

        # Tạo targets với status đúng
        batch = []
        for t in payload.targets:
            ch = channel_repo.get_by_id(db, t.channel_id)
            if not ch or not ch.is_active:
                raise HTTPException(404, f"Channel {t.channel_id} not found or inactive")

            st = to_aware(getattr(t, "scheduled_time", None)) or default_dt
            tgt_status = "scheduled" if (st and st > now) else "ready"

            batch.append({
                "post_id": post.id,
                "channel_id": ch.id,
                "platform": ch.platform,          # dùng enum trực tiếp
                "scheduled_time": st,
                "status": tgt_status,
            })

        post.targets = post_repo.target_bulk_create(db, batch)
        return post

    def list(self, db: Session, status: Optional[str] = None, q: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Post]:
        return post_repo.post_list(db, status=status, q=q, limit=limit, offset=offset)

    def get(self, db: Session, post_id: int) -> Post:
        post = post_repo.post_get_by_id(db, post_id)
        if not post:
            raise HTTPException(404, "Post not found")
        return post

    def update(self, db: Session, post_id: int, payload: PostUpdateIn) -> Post:
        post = self.get(db, post_id)
        return post_repo.post_update(db, post, payload.model_dump(exclude_unset=True))

    def delete(self, db: Session, post_id: int) -> None:
        post = self.get(db, post_id)
        post_repo.post_delete(db, post)

    async def publish_now(self, db: Session, post_id: int, target_only_id: int | None = None) -> Post:
        post = self.get(db, post_id)
        if not post:
            raise HTTPException(404, "Post not found")
        
        fb = FacebookService()
        ig = InstagramService()
        tk = TikTokService()
        yt = YouTubeService()

        # helpers
        def _now_utc(): return datetime.now(timezone.utc)

        def _ts(dt: Optional[datetime]) -> Optional[int]:
            if not dt:return None
            if dt.tzinfo is None:dt = dt.replace(tzinfo=timezone.utc)
            return int(dt.timestamp())
        
        def _parse_iso(val: Optional[str]) -> Optional[datetime]:
            if not val: return None
            try:
                s = val.replace("Z", "+00:00")
                dt = datetime.fromisoformat(s)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except Exception:
                return None
        
        def _schedule_tuple(post, tgt) -> tuple[Optional[datetime], Optional[int], Optional[str]]:
            pm = post.post_metadata or {}
            dt = getattr(tgt, "scheduled_time", None) or getattr(post, "default_scheduled_time", None) or _parse_iso(pm.get("schedule_time_iso"))
            if dt and dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            unix = int(dt.timestamp()) if dt else (pm.get("schedule_unix") if isinstance(pm.get("schedule_unix"), int) else None)
            iso = dt.isoformat() if dt else (pm.get("schedule_time_iso") if isinstance(pm.get("schedule_time_iso"), str) else None)
            return dt, unix, iso
            
        def _build_message(post) -> str:
            msg = (post.caption or "").strip()
            if getattr(post, "hashtags", None):
                msg = (msg + "\n" + post.hashtags).strip()
            return msg
        
        def _media_sources(post, ch):
            pm = post.post_metadata or {}
            cm = getattr(ch, "channel_metadata", None) or {}
            video_url = pm.get("file_url") or cm.get("file_url")
            image_url = pm.get("image_url") or cm.get("image_url")
            video_path = None
            # Nếu bạn có quan hệ post.video & thuộc tính file_path:
            if getattr(post, "video", None) and getattr(post.video, "file_path", None):
                video_path = post.video.file_path
            return {"video_url": video_url, "image_url": image_url, "video_path": video_path}
        
        def _ensure_success(res, *, id_keys=("id", "post_id", "video_id")) -> str:
            """Trả về platform_post_id; nếu có lỗi/mất id -> raise HTTPException để gom lỗi chung."""
            if not isinstance(res, dict):
                raise HTTPException(400, "Empty or invalid response from platform")
            if res.get("error"):
                detail = res["error"]
                if isinstance(detail, dict):
                    detail = str(detail)
                raise HTTPException(400, detail)
            for k in id_keys:
                if res.get(k):
                    return str(res[k])
            raise HTTPException(400, "Publish succeeded but missing returned id")
        
        # ===== MAIN LOOP =====
        for tgt in (post.targets or []):
            if target_only_id and tgt.id != target_only_id:
                continue
            if tgt.status not in ("ready", "scheduled", "failed"):
                continue

            ch = channel_repo.get_by_id(db, tgt.channel_id)
            if not ch or not ch.is_active:
                tgt.status = "failed"
                tgt.error_message = "Channel not found/inactive"
                db.add(tgt)
                continue

            msg = _build_message(post)
            media = _media_sources(post, ch)
            schedule_dt, schedule_unix, schedule_iso = _schedule_tuple(post, tgt)
            plat = getattr(ch.platform, "value", ch.platform)

            try:
                # FACEBOOK
                if plat == PF.facebook.value:
                    token, page_id = fb.get_channel_token_and_page(db, ch.id)
                    if not token or not page_id:
                        raise HTTPException(400, "Missing FB token/page id")

                    if post.video_id:
                        file_url = (post.post_metadata or {}).get("file_url") \
                                or (ch.channel_metadata or {}).get("file_url")
                        if not file_url:
                            raise HTTPException(400, "Missing file_url for Facebook video post")
                        res = await fb.post_video(
                            page_token=token,
                            page_id=page_id,
                            file_url=str(file_url),
                            description=post.caption or "",
                            # ưu tiên metadata, fallback lịch của target/post
                            schedule_unix=(post.post_metadata or {}).get("schedule_unix") or schedule_unix,
                            schedule_iso=(post.post_metadata or {}).get("schedule_time_iso") or schedule_iso,
                        )
                    elif (post.post_metadata or {}).get("image_url"):
                        image_url = (post.post_metadata or {}).get("image_url")
                        res = await fb.post_photo(
                            page_token=token,
                            page_id=page_id,
                            image_url=str(image_url),
                            caption=post.caption or "",
                            schedule_unix=(post.post_metadata or {}).get("schedule_unix") or schedule_unix,
                            schedule_iso=(post.post_metadata or {}).get("schedule_time_iso") or schedule_iso,
                        )
                    else:
                        res = await fb.post_feed(
                            page_token=token,
                            page_id=page_id,
                            message=post.caption or "",
                            schedule_unix=(post.post_metadata or {}).get("schedule_unix") or schedule_unix,
                            schedule_iso=(post.post_metadata or {}).get("schedule_time_iso") or schedule_iso,
                        )

                    tgt.platform_post_id = res.get("id") or res.get("post_id")
                    tgt.status = "posted"
                    tgt.posted_time = datetime.now(timezone.utc)

                # INSTAGRAM
                elif plat == PF.instagram.value:
                    # IG API không hỗ trợ hẹn giờ -> nếu có lịch tương lai, để scheduler xử lý
                    if schedule_dt and schedule_dt > datetime.now(timezone.utc):
                        tgt.status = "scheduled"
                        db.add(tgt)
                        continue
                    token, ig_id = ig.get_channel_token_and_igid(db, ch.id)
                    if not token or not ig_id:
                        raise HTTPException(400, "Missing Instagram token/ID")
                    if post.video_id:
                        file_url = (post.post_metadata or {}).get("file_url")
                        if not file_url:
                            raise HTTPException(400, "Missing file_url for Instagram video post")
                        res = await ig.post_video(
                            token=token,
                            ig_id=ig_id,
                            video_url=str(file_url),
                            caption=post.caption or "",
                            is_reel=True,
                        )
                    else:
                        image_url = (post.post_metadata or {}).get("image_url")
                        if not image_url:
                            raise HTTPException(400, "Instagram post requires a video or an image.")
                        res = await ig.post_photo(
                            token=token,
                            ig_id=ig_id,
                            image_url=str(image_url),
                            caption=post.caption or "",
                        )
                        
                        if res.get("error"):
                            raise HTTPException(400, str(res["error"]))
                        
                        pid = res.get("id")
                        if not pid:
                            raise HTTPException(400, "Instagram publish failed (missing id)")
                    tgt.platform_post_id = res.get("id")
                    tgt.status = "posted"
                    tgt.posted_time = datetime.now(timezone.utc)

                # TIKTOK
                elif plat == PF.tiktok.value:
                    # TikTok API không hỗ trợ hẹn giờ -> nếu có lịch tương lai, để scheduler xử lý
                    if schedule_dt and schedule_dt > datetime.now(timezone.utc):
                        tgt.status = "scheduled"
                        db.add(tgt)
                        continue
                    if not post.video_id:
                        raise HTTPException(400, "TikTok only supports video posts")

                    ok, res = await tk.post_video_via_channel(
                        db=db,
                        channel_id=ch.id,
                        video_id=post.video_id,
                        caption=post.caption or "",
                    )
                    if not ok:
                        raise HTTPException(400, res.get("error") or "TikTok upload failed")

                    tgt.platform_post_id = res.get("video_id") or res.get("id")
                    tgt.status = "posted"
                    tgt.posted_time = datetime.now(timezone.utc)

                # YOUTUBE
                elif plat == PF.youtube.value:
                    if not post.video_id:
                        raise HTTPException(400, "YouTube only supports video posts")
                    pm = post.post_metadata or {}
                    privacy = pm.get("privacy") or ("private" if schedule_dt else "public")
                    ok, res = await yt.post_video_via_channel(
                        db=db,
                        channel_id=ch.id,
                        video_id=post.video_id,
                        title=(pm.get("title") or (post.caption or "Video Title")),
                        description=post.caption or "",
                        tags=None,
                        privacy_status=privacy,
                        schedule_time_iso=schedule_iso,  # nếu có -> YouTube sẽ hẹn giờ
                    )
                    if not ok:
                        raise HTTPException(400, res.get("error") or "YouTube upload failed")

                    tgt.platform_post_id = res.get("video_id") or res.get("id")
                    tgt.status = "posted"
                    tgt.posted_time = datetime.now(timezone.utc)

                # UNKNOWN 
                else:
                    tgt.status = "failed"
                    tgt.error_message = f"Platform '{ch.platform}' not implemented"

            except HTTPException as he:
                tgt.status = "failed"
                tgt.error_message = f"{he.status_code}: {he.detail}"
            except Exception as e:
                tgt.status = "failed"
                tgt.error_message = str(e)

            db.add(tgt)

        db.commit()
        db.refresh(post)
        return post

    async def publish_target(self, db: Session, target_id: int) -> dict:
        """Background job function để đăng 1 target"""
        
        target = db.get(PostTarget, target_id)
        if not target:
            return {"error": "Target not found"}
        
        if target.status != "scheduled":
            return {"error": f"Target not in scheduled state: {target.status}"}
        
        # Mark as processing
        target.status = "posting"
        db.commit()
        
        try:
            # Get post and channel data
            post = target.post
            channel = db.get(Channel, target.channel_id)
            
            if not channel or not channel.is_active:
                raise Exception("Channel not found or inactive")
            
            await self.publish_now(db, post.id, target_only_id=target.id)  # ensure publish_now accepts target_only_id
            db.refresh(target)
            result = {"success": True, "post_id": target.platform_post_id} if target.platform_post_id else {"error": "Missing platform_post_id"}

            if result.get("success"):
                target.status = "posted"
                target.posted_time = datetime.now(timezone.utc)
            else:
                target.status = "failed"
                target.error_message = result.get("error", "Unknown error")
            
            db.add(target)
            db.commit()
            return result
            
        except Exception as e:
            target.status = "failed"
            target.error_message = str(e)
            db.add(target)
            db.commit()
            return {"error": str(e)}
        

    def _get_media_sources(self, post, ch) -> dict:
        """Nguồn media cho publish (ưu tiên post_metadata, fallback channel_metadata)"""
        pm = getattr(post, "post_metadata", None) or {}
        cm = getattr(ch, "channel_metadata", None) or {}
        video_url = pm.get("file_url") or cm.get("file_url")
        image_url = pm.get("image_url") or cm.get("image_url")
        video_path = getattr(getattr(post, "video", None), "file_path", None)
        return {"video_url": video_url, "image_url": image_url, "video_path": video_path}
