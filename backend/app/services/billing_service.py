"""Database-enforced pilot plans. No checkout, payment collection or auto-renewal."""
import math
import uuid
from types import SimpleNamespace
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from app.models.billing import BillingPlan, ExportUsage, PlanGrant
from app.models.subscription import Subscription
from app.models.user import User
from app.models.brand import Brand
from app.models.scene import Scene
from app.models.voice import Voice

DEFAULT_PLANS = [
    dict(code="trial", name="Trial", price_inr=0, period_days=7, brands=1, video_seconds=None, video_exports=None, image_exports=10),
    dict(code="creator", name="Creator", price_inr=499, period_days=30, brands=1, video_seconds=1800, video_exports=None, image_exports=100),
    dict(code="pro", name="Pro", price_inr=999, period_days=30, brands=5, video_seconds=5400, video_exports=None, image_exports=300),
    dict(code="agency", name="Agency", price_inr=2499, period_days=30, brands=15, video_seconds=15000, video_exports=None, image_exports=1000),
]

# Account-specific access; assigning the admin role does not grant this exemption.
PLAN_EXEMPT_EMAILS = frozenset({"super_admin@gmail.com", "ystechlab@gmail.com"})


def has_unlimited_access(db, user_id):
    user = db.query(User.email, User.is_active).filter(User.id == user_id).first()
    return bool(user and user.is_active and user.email.strip().lower() in PLAN_EXEMPT_EMAILS)


def unlimited_plan():
    # Effective permissions only: do not change stored subscriptions or the catalog.
    return SimpleNamespace(code="owner", name="Owner access", price_inr=0,
                           period_days=None, brands=None, video_seconds=None,
                           video_exports=None, image_exports=None)


def now():
    return datetime.now(timezone.utc)


def utc(value):
    return value.replace(tzinfo=timezone.utc) if value and value.tzinfo is None else value


def seed_plans(db):
    # Upgrade existing installations as well as newly created plans.
    db.query(BillingPlan).filter(BillingPlan.code == "trial").update({BillingPlan.video_exports: None})
    for values in DEFAULT_PLANS:
        if db.get(BillingPlan, values["code"]) is None:
            try:
                with db.begin_nested():
                    db.add(BillingPlan(**values))
                    db.flush()
            except IntegrityError:
                pass  # Another startup worker seeded this plan.
    db.commit()


def lock_account(db, user_id):
    # An actual write serializes quota checks on PostgreSQL and SQLite alike.
    count = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).update({User.updated_at: User.updated_at}, synchronize_session=False)
    if not count:
        raise HTTPException(403, "Active account required.")


def subscription(db, user_id):
    row = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if row is None:
        start = now()
        row = Subscription(user_id=user_id, plan_name="trial", status="active", billing_cycle="trial", amount=0, currency="INR", starts_at=start, expires_at=start + timedelta(days=7), auto_renew=False)
        db.add(row)
        db.flush()
    return row


def require_plan(db, user_id):
    lock_account(db, user_id)
    sub = subscription(db, user_id)
    if has_unlimited_access(db, user_id):
        return sub, unlimited_plan()
    plan = db.get(BillingPlan, sub.plan_name.lower())
    if not plan or sub.status != "active" or not sub.expires_at or utc(sub.expires_at) <= now():
        raise HTTPException(403, "Your plan has expired or is inactive. Open Plans & usage for access options. Existing content remains available.")
    return sub, plan


def used(db, user_id, period_start):
    rows = db.query(ExportUsage).filter(ExportUsage.user_id == user_id, ExportUsage.period_start == period_start, ExportUsage.status.in_(["reserved", "completed"])).all()
    return {"video_seconds": sum(x.units for x in rows if x.kind == "video"), "video_exports": sum(1 for x in rows if x.kind == "video"), "image_exports": sum(x.units for x in rows if x.kind == "image"), "pending": sum(1 for x in rows if x.status == "reserved")}


def check_brand_limit(db, user_id):
    _, plan = require_plan(db, user_id)
    if plan.brands is not None and db.query(func.count(Brand.id)).filter(Brand.user_id == user_id).scalar() >= plan.brands:
        raise HTTPException(403, f"Your {plan.name} plan allows {plan.brands} brand(s). Open Plans & usage to upgrade.")
    # Caller creates the brand and commits while still holding this account lock.


def snapshot(db, user_id):
    lock_account(db, user_id)
    sub = subscription(db, user_id)
    plan = db.get(BillingPlan, sub.plan_name.lower())
    result = {"plan": plan_dict(plan) if plan else None, "status": sub.status if sub.expires_at and utc(sub.expires_at) > now() else "expired", "starts_at": utc(sub.starts_at), "expires_at": utc(sub.expires_at), "auto_renew": False, "usage": used(db, user_id, sub.starts_at), "brands_used": db.query(func.count(Brand.id)).filter(Brand.user_id == user_id).scalar(), "payments_enabled": False}
    result["limits_exempt"] = has_unlimited_access(db, user_id)
    if result["limits_exempt"]:
        result.update(plan=plan_dict(unlimited_plan()), status="active", expires_at=None)
    db.commit()
    return result


def plan_dict(plan):
    return {field: getattr(plan, field) for field in DEFAULT_PLANS[0]}


def reserve(db, user_id, kind, units, resource, request_key=None):
    sub, plan = require_plan(db, user_id)
    key = request_key or str(uuid.uuid4())
    previous = db.query(ExportUsage).filter_by(user_id=user_id, request_key=key).first()
    if previous:
        if previous.resource != resource or previous.kind != kind:
            raise HTTPException(409, "This export request key belongs to a different export.")
        if previous.status == "completed":
            db.commit()
            return previous, True
        if previous.status == "reserved":
            raise HTTPException(409, "This export is already running. Wait for it to finish.")
        # A failed attempt can be retried with the same key and consumes no quota.
    if db.query(ExportUsage).filter_by(active_user=user_id).first():
        raise HTTPException(409, "An export is already running for your account. Wait for it to finish. Contact an administrator if a server interruption left it pending.")
    totals = used(db, user_id, sub.starts_at)
    if kind == "image" and plan.image_exports is not None and totals["image_exports"] + units > plan.image_exports:
        raise HTTPException(403, "Your image export allowance is used up. Open Plans & usage.")
    if kind == "video":
        if plan.video_seconds is not None and totals["video_seconds"] + units > plan.video_seconds:
            raise HTTPException(403, "This video exceeds your remaining video-minute allowance. Shorten it or open Plans & usage.")
        if plan.video_exports is not None and totals["video_exports"] + 1 > plan.video_exports:
            raise HTTPException(403, "Your video export allowance is used up. Open Plans & usage.")
    row = previous or ExportUsage(id=str(uuid.uuid4()), user_id=user_id, request_key=key, resource=resource, kind=kind)
    row.units, row.period_start, row.status, row.active_user, row.created_at = units, sub.starts_at, "reserved", user_id, now()
    row.result, row.finished_at = None, None
    db.add(row)
    db.commit()
    return row, False


def scenes_for(db, user_id, kwargs):
    query = db.query(Scene).filter(Scene.user_id == user_id)
    if "scene_ids" in kwargs:
        ids = list(dict.fromkeys(kwargs["scene_ids"]))
        kwargs["scene_ids"] = ids
        scenes = query.filter(Scene.id.in_(ids)).all()
        if len(scenes) != len(ids) or len({s.content_id for s in scenes}) != 1:
            raise HTTPException(404, "Select saved scenes from one content item owned by your account.")
    elif "scene_id" in kwargs:
        scenes = query.filter(Scene.id == kwargs["scene_id"]).all()
    else:
        query = query.filter(Scene.project_id == kwargs["project_id"])
        content_id = kwargs.get("content_id")
        if content_id is None:
            latest = query.order_by(Scene.created_at.desc()).first()
            content_id = latest.content_id if latest else None
            kwargs["content_id"] = content_id
        scenes = query.filter(Scene.content_id == content_id).all()
    if not scenes:
        raise HTTPException(404, "No scenes found for this account.")
    return scenes


def estimate_seconds(db, scenes, user_id):
    from app.core.ffmpeg_client import FFmpegClient
    from app.services.render_service import _stored_path
    total = 0
    for scene in scenes:
        duration = max(1, float(scene.duration or 5))
        if (scene.content.generation_config or {}).get("audio", {}).get("voice_enabled") is not False:
            voice = db.query(Voice).filter(Voice.user_id == user_id, Voice.scene_id == scene.id, Voice.content_id == scene.content_id, Voice.status == "generated").order_by(Voice.updated_at.desc(), Voice.created_at.desc(), Voice.id.desc()).first()
            if voice:
                path = _stored_path(voice.audio_path)
                if not path or not path.is_file():
                    raise HTTPException(422, "A narration file is missing. Regenerate it before exporting.")
                duration = max(duration, FFmpegClient.audio_duration(str(path)))
        total += math.ceil(duration)
    return total


def billed_render(operation, **kwargs):
    db, user_id = kwargs["db"], kwargs["user_id"]
    key = kwargs.pop("request_key", None)
    scenes = scenes_for(db, user_id, kwargs)
    kind = "image" if kwargs.get("as_image") else "video"
    units = len(scenes) if kind == "image" else estimate_seconds(db, scenes, user_id)
    if "scene_ids" in kwargs:
        import hashlib
        resource = "images:" + hashlib.sha256(",".join(map(str, sorted(kwargs["scene_ids"]))).encode()).hexdigest()
    else:
        resource = (f"scene:{kwargs['scene_id']}" if "scene_id" in kwargs else f"content:{kwargs['content_id']}") + f":{kind}"
    row, replay = reserve(db, user_id, kind, units, resource, key)
    if replay:
        return row.result
    reservation_id = row.id
    try:
        result = operation(**kwargs)
        if not result or result.get("success") is False:
            raise RuntimeError("Export did not complete. No allowance was charged.")
        row = db.get(ExportUsage, reservation_id)
        row.result = jsonable_encoder(result)
        row.status, row.active_user, row.finished_at = "completed", None, now()
        db.commit()
        return result
    except Exception:
        db.rollback()
        row = db.get(ExportUsage, reservation_id)
        row.status, row.active_user, row.finished_at = "failed", None, now()
        db.commit()
        raise


def grant_plan(db, user_id, admin_id, code, note):
    note = note.strip()
    if len(note) < 5:
        raise HTTPException(422, "Enter a reason of at least five characters for this grant.")
    lock_account(db, user_id)
    sub = subscription(db, user_id)
    plan = db.get(BillingPlan, code)
    if not plan or code == "trial":
        raise HTTPException(422, "Select Creator, Pro or Agency for pilot access.")
    if db.query(ExportUsage).filter_by(active_user=user_id).first():
        raise HTTPException(409, "Wait for the user's current export to finish before changing plans.")
    if sub.plan_name != "trial" and sub.status == "active" and sub.expires_at and utc(sub.expires_at) > now():
        raise HTTPException(409, "This user already has an active pilot plan. Wait until it expires to grant another period.")
    start = now()
    sub.plan_name, sub.status, sub.starts_at, sub.expires_at = code, "active", start, start + timedelta(days=plan.period_days)
    sub.amount, sub.auto_renew, sub.payment_provider, sub.billing_cycle = 0, False, "manual_pilot", "pilot"
    db.add(PlanGrant(user_id=user_id, admin_id=admin_id, plan_code=code, starts_at=start, expires_at=sub.expires_at, note=note))
    db.commit()
    return snapshot(db, user_id)
