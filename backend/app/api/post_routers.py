from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.api.deps import require_roles, get_current_user_id
from app.schemas.post_schemas import PostCreateIn, PostUpdateIn, PostOut
from app.services.post_service import PostService

router = APIRouter(prefix="/posts", tags=["posts"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_service() -> PostService:
    return PostService()

@router.post("/", response_model=PostOut, dependencies=[Depends(require_roles(["admin", "staff"]))])
def create_post(
    body: PostCreateIn,
    publish: bool = Query(False, description="Đăng ngay sau khi tạo nếu True"),
    db: Session = Depends(get_db),
    svc: PostService = Depends(get_service),
    user_id: Optional[int] = None,
):
    post = svc.create(db, body, created_by_id=user_id)
    # Đăng ngay nếu được yêu cầu
    if publish:
        # publish tất cả target có trạng thái ready/scheduled (IG/TikTok chỉ post ngay nếu ready)
        import anyio
        anyio.run(svc.publish_now, db, post.id, None)  # hoặc await nếu router async
        post = svc.get(db, post.id)
    return post

@router.get("/", response_model=List[PostOut], dependencies=[Depends(require_roles(["admin", "staff"]))])
def list_posts(
    status: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    svc: PostService = Depends(get_service),
):
    return svc.list(db, status=status, q=q, limit=limit, offset=offset)

@router.get("/{post_id}", response_model=PostOut, dependencies=[Depends(require_roles(["admin", "staff"]))])
def get_post(
    post_id: int,
    db: Session = Depends(get_db),
    svc: PostService = Depends(get_service),
):
    return svc.get(db, post_id)

@router.patch("/{post_id}", response_model=PostOut, dependencies=[Depends(require_roles(["admin", "staff"]))])
def update_post(
    post_id: int,
    body: PostUpdateIn,
    db: Session = Depends(get_db),
    svc: PostService = Depends(get_service),
):
    return svc.update(db, post_id, body)

@router.delete("/{post_id}", status_code=204, dependencies=[Depends(require_roles(["admin", "staff"]))])
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    svc: PostService = Depends(get_service),
):
    post = svc.get(db, post_id)
    if not post:
        raise HTTPException(404, "Post not found")
    
    try:
        svc.delete(db, post_id)
        # Không return gì với status_code=204
    except Exception as e:
        logger.error(f"Failed to delete post {post_id}: {e}")
        raise HTTPException(500, "Failed to delete post")

@router.post("/{post_id}/publish", response_model=PostOut, dependencies=[Depends(require_roles(["admin", "staff"]))])
async def publish_post(
    post_id: int,
    db: Session = Depends(get_db),
    svc: PostService = Depends(get_service),
):
    return await svc.publish_now(db, post_id)

@router.post("/targets/{target_id}/publish", dependencies=[Depends(require_roles(["admin", "staff"]))])
async def publish_one_target(
    target_id: int,
    db: Session = Depends(get_db),
    svc: PostService = Depends(get_service),
):
    return await svc.publish_target(db, target_id)
