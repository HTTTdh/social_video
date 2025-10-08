


# app/services/template_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories import template_repo
from app.schemas.template_schemas import TemplateCreateIn, TemplateUpdateIn

class TemplateService:
    async def create(self, db: Session, payload: TemplateCreateIn):
        return template_repo.create(
            db,
            name=payload.name,
            type=payload.type.value,
            content=payload.content,
            template_metadata=payload.metadata,
        )

    async def list(self, db: Session, type_filter: str | None):
        return template_repo.list_templates(db, type_filter)

    async def get(self, db: Session, template_id: int):
        t = template_repo.get(db, template_id)
        if not t:
            raise HTTPException(404, "Template not found")
        return t

    async def update(self, db: Session, template_id: int, payload: TemplateUpdateIn):
        t = template_repo.get(db, template_id)
        if not t:
            raise HTTPException(404, "Template not found")
        data = payload.model_dump(exclude_unset=True)
        if "metadata" in data:
            data["template_metadata"] = data.pop("metadata")
        return template_repo.update(db, t, data)

    async def delete(self, db: Session, template_id: int):
        t = template_repo.get(db, template_id)
        if not t:
            raise HTTPException(404, "Template not found")
        template_repo.delete(db, t)

    async def preview(self, db: Session, template_id: int, payload):
        t = await self.get(db, template_id)
        # TODO: thay bằng render biến thực tế
        return {"preview_text": t.content}
