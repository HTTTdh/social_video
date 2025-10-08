# Lịch đăng: tạo/đổi trạng thái/CRUD + calendar feed


from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.deps import get_schedule_service, require_roles
from app.services.schedule_service import ScheduleService
from app.schemas.schedule_schemas import ScheduleCreateIn, ScheduleUpdateIn, ScheduleOut, CalendarOut

router = APIRouter(prefix="/schedule", tags=["schedule"])

@router.post("/", response_model=ScheduleOut, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    body: ScheduleCreateIn,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["admin","staff"])),
    svc: ScheduleService = Depends(get_schedule_service),
):
    return await svc.create(db=db, payload=body)

@router.get("/", response_model=List[ScheduleOut])
async def list_schedules(
    active: Optional[bool] = None,
    db: Session = Depends(get_db),
    svc: ScheduleService = Depends(get_schedule_service),
):
    return await svc.list(db=db, active=active)

@router.get("/{schedule_id}", response_model=ScheduleOut)
async def get_schedule(schedule_id: int, db: Session = Depends(get_db), svc: ScheduleService = Depends(get_schedule_service)):
    return await svc.get(db=db, schedule_id=schedule_id)

@router.put("/{schedule_id}", response_model=ScheduleOut)
async def update_schedule(
    schedule_id: int,
    body: ScheduleUpdateIn,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["admin","staff"])),
    svc: ScheduleService = Depends(get_schedule_service),
):
    return await svc.update(db=db, schedule_id=schedule_id, payload=body)

@router.post("/{schedule_id}/pause", response_model=ScheduleOut)
async def pause_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["admin","staff"])),
    svc: ScheduleService = Depends(get_schedule_service),
):
    return await svc.pause(db=db, schedule_id=schedule_id)

@router.post("/{schedule_id}/resume", response_model=ScheduleOut)
async def resume_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["admin","staff"])),
    svc: ScheduleService = Depends(get_schedule_service),
):
    return await svc.resume(db=db, schedule_id=schedule_id)

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["admin","staff"])),
    svc: ScheduleService = Depends(get_schedule_service),
):
    await svc.delete(db=db, schedule_id=schedule_id)

@router.get("/calendar", response_model=CalendarOut)
async def calendar(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    svc: ScheduleService = Depends(get_schedule_service),
):
    return await svc.calendar(db=db, month=month, year=year)

@router.patch("/{schedule_id}/toggle", response_model=ScheduleOut)
async def toggle_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["admin","staff"])),
    svc: ScheduleService = Depends(get_schedule_service),
):
    """Toggle active/inactive schedule"""
    schedule = svc.get(db, schedule_id)
    if not schedule:
        raise HTTPException(404, "Schedule not found")
    
    return await svc.toggle_active(db, schedule_id)

@router.post("/{schedule_id}/run-now")
async def run_schedule_now(
    schedule_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(["admin","staff"])),
    svc: ScheduleService = Depends(get_schedule_service),
):
    """Manually trigger schedule execution"""
    schedule = svc.get(db, schedule_id)
    if not schedule:
        raise HTTPException(404, "Schedule not found")
    
    if not schedule.is_active:
        raise HTTPException(400, "Cannot run inactive schedule")
    
    return await svc.run_now(db, schedule_id)