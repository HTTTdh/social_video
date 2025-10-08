# Caption/Hashtag/Watermark/Frame + preview


from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.deps import get_template_service, require_roles
from app.services.template_service import TemplateService
from app.schemas.template_schemas import TemplateCreateIn, TemplateUpdateIn, TemplateOut, TemplatePreviewIn, TemplatePreviewOut

router = APIRouter(prefix="/templates", tags=["templates"])

@router.post("/", response_model=TemplateOut, status_code=status.HTTP_201_CREATED)
async def create_template(
    body: TemplateCreateIn,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["admin","staff"])),
    svc: TemplateService = Depends(get_template_service),
):
    return await svc.create(db=db, payload=body)

@router.get("/", response_model=List[TemplateOut])
async def list_templates(
    type_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    svc: TemplateService = Depends(get_template_service),
):
    return await svc.list(db=db, type_filter=type_filter)

@router.get("/{template_id}", response_model=TemplateOut)
async def get_template(template_id: int, db: Session = Depends(get_db), svc: TemplateService = Depends(get_template_service)):
    return await svc.get(db=db, template_id=template_id)

@router.put("/{template_id}", response_model=TemplateOut)
async def update_template(
    template_id: int,
    body: TemplateUpdateIn,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["admin","staff"])),
    svc: TemplateService = Depends(get_template_service),
):
    return await svc.update(db=db, template_id=template_id, payload=body)

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["admin","staff"])),
    svc: TemplateService = Depends(get_template_service),
):
    await svc.delete(db=db, template_id=template_id)

@router.post("/{template_id}/preview", response_model=TemplatePreviewOut)
async def preview_template(
    template_id: int,
    body: TemplatePreviewIn,
    db: Session = Depends(get_db),
    svc: TemplateService = Depends(get_template_service),
):
    return await svc.preview(db=db, template_id=template_id, payload=body)
