import logging
from datetime import timedelta
from fastapi import HTTPException

from app.database import SessionLocal
from app.models.content import Content
from app.models.schedule import Schedule
from app.models.user import User
from app.models.publishing import PublishingAccount, PublishJob, PublishEvent
from app.services.publishing_accounts import now, ProviderError
from app.services.publishing_providers import publish, Pending

logger = logging.getLogger(__name__)


def event(db, job, status, message):
    db.add(PublishEvent(job_id=job.id, status=status, message=message))


def process_job(db, job_id, publisher=publish):
    # Compare-and-swap claims work across API workers without duplicate sends.
    claimed = db.query(PublishJob).filter(PublishJob.id == job_id, PublishJob.status.in_(["queued", "processing"]), PublishJob.next_attempt_at <= now()).update(
        {PublishJob.status: "publishing", PublishJob.started_at: now(), PublishJob.attempts: PublishJob.attempts + 1}, synchronize_session=False)
    db.commit()
    if claimed != 1:
        return
    db.expire_all()
    job = db.get(PublishJob, job_id)
    schedule = db.get(Schedule, job.schedule_id)
    account = db.get(PublishingAccount, job.account_id)
    try:
        content = db.get(Content, schedule.content_id) if schedule else None
        active = db.query(User.id).filter_by(id=job.user_id, is_active=True).first()
        if not active or not schedule or schedule.status not in {"scheduled", "processing"} or not content or content.user_id != job.user_id or content.status != "approved":
            raise ProviderError("Publishing stopped: the account, schedule or content approval is no longer available.")
        if not account or account.user_id != job.user_id or account.status != "connected":
            raise ProviderError("Publishing account is disconnected. Reconnect before scheduling again.")
        if job.attempts > 180:
            raise ProviderError("Platform processing took too long. Check the platform before scheduling another post.", uncertain=True)
        schedule.status = "processing"
        if job.attempts == 1:
            event(db, job, "publishing", "Automatic publishing started.")
        db.commit()
        remote_id, post_url, status = publisher(db, job, account)
        job.status = schedule.status = status
        job.remote_post_id = remote_id
        schedule.post_url = post_url
        schedule.published_at = now() if status == "published" else None
        schedule.error_message = None
        event(db, job, status, "Platform confirmed publication." if status == "published" else "YouTube confirmed the upload with the selected non-public visibility.")
    except Pending:
        job.status = "processing"
        job.next_attempt_at = now() + timedelta(seconds=20)
    except (ProviderError, HTTPException) as exc:
        uncertain = isinstance(exc, ProviderError) and exc.uncertain
        job.status = "needs_review" if uncertain else "failed"
        message = str(exc) if isinstance(exc, ProviderError) else str(exc.detail)
        if schedule:
            schedule.status = job.status
            schedule.error_message = message
        if isinstance(exc, ProviderError) and exc.reconnect and account:
            account.status = "reconnect_required"
        job.remote_post_id = (job.provider_state or {}).get("post_id") or (job.provider_state or {}).get("video_id")
        event(db, job, job.status, message)
    except Exception:
        # A crash may happen after the provider accepted a post. Never retry it blindly.
        db.rollback()
        job = db.get(PublishJob, job_id)
        schedule = db.get(Schedule, job.schedule_id)
        job.status = "needs_review"
        if schedule:
            schedule.status = "needs_review"
            schedule.error_message = "Publishing was interrupted. Check the platform before scheduling again."
        event(db, job, "needs_review", "Publishing was interrupted. Check the platform before scheduling again.")
        logger.error("Publishing job %s requires review", job_id)
    db.commit()


def tick():
    with SessionLocal() as db:
        # A process that died after claiming a job must not cause automatic duplication.
        stale = db.query(PublishJob).filter(PublishJob.status == "publishing", PublishJob.started_at < now() - timedelta(minutes=30)).all()
        for job in stale:
            changed = db.query(PublishJob).filter_by(id=job.id, status="publishing").update({"status": "needs_review"})
            if changed:
                schedule = db.get(Schedule, job.schedule_id)
                if schedule:
                    schedule.status = "needs_review"
                    schedule.error_message = "Worker stopped during publishing. Check the platform before posting again."
                event(db, job, "needs_review", "Worker interrupted; automatic retry blocked to avoid duplicate posts.")
        db.commit()
        ids = [row.id for row in db.query(PublishJob.id).filter(PublishJob.status.in_(["queued", "processing"]), PublishJob.next_attempt_at <= now()).order_by(PublishJob.next_attempt_at, PublishJob.id).limit(10).all()]
        for job_id in ids:
            process_job(db, job_id)


def run_worker(stop):
    while not stop.is_set():
        try:
            tick()
        except Exception:
            logger.error("Publishing worker could not process its queue; it will check again.")
        stop.wait(10)
