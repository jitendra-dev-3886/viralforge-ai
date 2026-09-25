import os
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.security import get_current_user_id
from app.database import get_db
from app.models.schedule import Schedule
from app.models.content import Content
from app.models.publishing import PublishingAccount, PublishJob, PublishEvent
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate
from app.services.publishing_accounts import now
from app.services.publishing_media import snapshot
from app.services.publishing_worker import event
from app.core.scheduling_route import SchedulingRoute

router = APIRouter(prefix="/api/schedules", tags=["Schedules"], route_class=SchedulingRoute)
STATUSES = {"pending", "approved", "scheduled", "published", "cancelled", "failed"}


def data(item, job=None):
    result = {k: getattr(item, k) for k in ("id", "project_id", "content_id", "platform", "account_name", "scheduled_at", "timezone", "status", "published_at", "post_url", "error_message", "created_at")}
    result["automatic"] = bool(job)
    if job:
        result.update(publishing_account_id=job.account_id, remote_post_id=job.remote_post_id, attempts=job.attempts,
                      title=job.payload["title"], caption=job.payload["caption"], privacy=job.payload["privacy"],
                      media=[{"id": asset["media_id"], "name": asset["name"]} for asset in job.payload["assets"]])
    return result


@router.get("/")
def list_schedules(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    rows = db.query(Schedule).filter(Schedule.user_id == user_id).order_by(Schedule.scheduled_at.desc()).all()
    jobs = {job.schedule_id: job for job in db.query(PublishJob).filter_by(user_id=user_id).all()}
    return {"success": True, "schedules": [data(row, jobs.get(row.id)) for row in rows]}


@router.post("/")
def create_schedule(request: ScheduleCreate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    if request.publishing_account_id and request.request_key:
        existing = db.query(PublishJob).filter_by(user_id=user_id, request_key=str(request.request_key)).first()
        if existing:
            return {"success": True, "schedule": data(db.get(Schedule, existing.schedule_id), existing)}
    content = db.query(Content).filter(Content.id == request.content_id, Content.project_id == request.project_id, Content.user_id == user_id).first()
    if not content:
        raise HTTPException(404, "Content not found in this project.")
    if content.status != "approved":
        raise HTTPException(400, "Approve the content before scheduling it.")
    if request.scheduled_at.tzinfo is None or request.scheduled_at <= now():
        raise HTTPException(400, "Choose a future date and time with a timezone.")
    values = request.model_dump(exclude={"publishing_account_id", "media_ids", "privacy", "made_for_kids", "request_key"})
    values["scheduled_at"] = request.scheduled_at.astimezone(timezone.utc)
    job = None
    if request.publishing_account_id:
        if os.getenv("AUTO_PUBLISH_ENABLED", "true").lower() != "true":
            raise HTTPException(503, "Automatic publishing is disabled on this server.")
        if not request.request_key:
            raise HTTPException(400, "A unique request key is required for automatic scheduling.")
        account = db.query(PublishingAccount).filter_by(id=request.publishing_account_id, user_id=user_id, status="connected").with_for_update().first()
        if not account:
            raise HTTPException(404, "Connected publishing account not found.")
        if account.provider != content.platform.lower() or account.provider != request.platform.lower():
            raise HTTPException(400, "Choose an account matching this content's platform.")
        payload = snapshot(db, user_id, content, account, request.media_ids, request.privacy, request.made_for_kids)
        values.update(platform=account.provider, account_name=account.name[:100])
        job = PublishJob(user_id=user_id, account_id=account.id, payload=payload, status="queued", provider_state={},
                         next_attempt_at=values["scheduled_at"], request_key=str(request.request_key))
    item = Schedule(user_id=user_id, status="scheduled", **values)
    try:
        db.add(item)
        db.flush()
        if job:
            job.schedule_id = item.id
            db.add(job)
            db.flush()
            event(db, job, "queued", "Approved content and selected media saved for automatic publishing.")
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.query(PublishJob).filter_by(user_id=user_id, request_key=str(request.request_key)).first() if job else None
        if existing:
            return {"success": True, "schedule": data(db.get(Schedule, existing.schedule_id), existing)}
        raise HTTPException(409, "The schedule could not be saved. Refresh and try again.") from None
    db.refresh(item)
    return {"success": True, "schedule": data(item, job)}


@router.get("/{schedule_id}/events")
def schedule_events(schedule_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    job = db.query(PublishJob).filter_by(schedule_id=schedule_id, user_id=user_id).first()
    if not job:
        raise HTTPException(404, "Automatic posting record not found.")
    records = db.query(PublishEvent).filter_by(job_id=job.id).order_by(PublishEvent.id).all()
    return {"events": [{"id": row.id, "status": row.status, "message": row.message, "created_at": row.created_at} for row in records]}


@router.put("/{schedule_id}")
def update_schedule(schedule_id: int, request: ScheduleUpdate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    item = db.query(Schedule).filter_by(id=schedule_id, user_id=user_id).first()
    if not item:
        raise HTTPException(404, "Schedule not found.")
    values = request.model_dump(exclude_unset=True)
    job = db.query(PublishJob).filter_by(schedule_id=item.id, user_id=user_id).first()
    if job:
        if values != {"status": "cancelled"}:
            raise HTTPException(400, "Automatic posting records cannot be edited or marked published manually. Cancel and create a new schedule for changes.")
        changed = db.query(PublishJob).filter(PublishJob.id == job.id, PublishJob.status == "queued").update({"status": "cancelled"})
        if changed != 1:
            raise HTTPException(409, "This job has started publishing or already finished. Check its posting record.")
        event(db, job, "cancelled", "Cancelled by the account owner.")
    elif values.get("status") and values["status"] not in STATUSES:
        raise HTTPException(400, "Invalid schedule status.")
    if "scheduled_at" in values:
        date = values["scheduled_at"]
        if not date or date.tzinfo is None or date <= now():
            raise HTTPException(400, "Choose a future date and time with a timezone.")
        values["scheduled_at"] = date.astimezone(timezone.utc)
    if any(value is None for value in values.values()):
        raise HTTPException(400, "Schedule fields cannot be empty.")
    for key, value in values.items():
        setattr(item, key, value)
    if item.status == "published" and not item.published_at:
        item.published_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return {"success": True, "schedule": data(item, job)}


@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    item = db.query(Schedule).filter_by(id=schedule_id, user_id=user_id).first()
    if not item:
        raise HTTPException(404, "Schedule not found.")
    if db.query(PublishJob.id).filter_by(schedule_id=item.id).first():
        raise HTTPException(400, "Automatic posting history is retained. Cancel a pending post instead.")
    db.delete(item)
    db.commit()
    return {"success": True}
