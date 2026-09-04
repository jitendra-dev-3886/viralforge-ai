from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user_id
from app.database import get_db
from app.models.schedule import Schedule
from app.models.content import Content
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate

router = APIRouter(prefix="/api/schedules", tags=["Schedules"])
STATUSES = {"pending", "approved", "scheduled", "published", "cancelled", "failed"}

def data(item):
    return {k: getattr(item, k) for k in ("id","project_id","content_id","platform","account_name","scheduled_at","timezone","status","published_at","post_url","error_message","created_at")}

@router.get("/")
def list_schedules(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    rows = db.query(Schedule).filter(Schedule.user_id == user_id).order_by(Schedule.scheduled_at.asc()).all()
    return {"success": True, "schedules": [data(x) for x in rows]}

@router.post("/")
def create_schedule(request: ScheduleCreate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    content = db.query(Content).filter(Content.id == request.content_id, Content.project_id == request.project_id, Content.user_id == user_id).first()
    if not content: raise HTTPException(status_code=404, detail="Content not found in this project.")
    if content.status != "approved": raise HTTPException(status_code=400, detail="Approve the content before scheduling it.")
    item = Schedule(user_id=user_id, status="scheduled", **request.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return {"success": True, "schedule": data(item)}

@router.put("/{schedule_id}")
def update_schedule(schedule_id: int, request: ScheduleUpdate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    item = db.query(Schedule).filter(Schedule.id == schedule_id, Schedule.user_id == user_id).first()
    if not item: raise HTTPException(status_code=404, detail="Schedule not found.")
    values = request.model_dump(exclude_unset=True)
    if values.get("status") and values["status"] not in STATUSES: raise HTTPException(status_code=400, detail="Invalid schedule status.")
    for key, value in values.items(): setattr(item, key, value)
    if item.status == "published" and not item.published_at: item.published_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(item)
    return {"success": True, "schedule": data(item)}

@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    item = db.query(Schedule).filter(Schedule.id == schedule_id, Schedule.user_id == user_id).first()
    if not item: raise HTTPException(status_code=404, detail="Schedule not found.")
    db.delete(item); db.commit(); return {"success": True}
