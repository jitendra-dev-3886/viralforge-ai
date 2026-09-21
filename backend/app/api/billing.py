from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user_id
from app.api.admin import require_admin
from app.models.user import User
from app.models.billing import BillingPlan, ExportUsage, PlanGrant
from app.services.billing_service import snapshot, plan_dict, grant_plan, lock_account, now, utc

router = APIRouter(prefix="/api/billing", tags=["Plans and usage"])


@router.get("/plans")
def plans(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    return {"plans": [plan_dict(row) for row in db.query(BillingPlan).order_by(BillingPlan.price_inr).all()], "payments_enabled": False}


@router.get("/me")
def my_plan(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    return snapshot(db, user_id)


@router.get("/history")
def history(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    exports = db.query(ExportUsage).filter_by(user_id=user_id).order_by(ExportUsage.created_at.desc()).limit(100).all()
    grants = db.query(PlanGrant).filter_by(user_id=user_id).order_by(PlanGrant.starts_at.desc()).limit(30).all()
    return {"exports": [{"id": row.id, "kind": row.kind, "units": row.units, "status": row.status, "created_at": utc(row.created_at)} for row in exports], "grants": [{"plan": row.plan_code, "starts_at": utc(row.starts_at), "expires_at": utc(row.expires_at), "type": "complimentary pilot access"} for row in grants]}


class GrantInput(BaseModel):
    plan: Literal["creator", "pro", "agency"]
    note: str = Field(min_length=5, max_length=500)


@router.get("/admin/users/{user_id}")
def admin_snapshot(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return snapshot(db, user_id)


@router.post("/admin/users/{user_id}/grant")
def grant(user_id: int, request: GrantInput, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return grant_plan(db, user_id, admin.id, request.plan, request.note.strip())


@router.get("/admin/pending")
def pending(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return {"exports": [{"id": row.id, "user_id": row.user_id, "created_at": utc(row.created_at), "resource": row.resource} for row in db.query(ExportUsage).filter_by(status="reserved").order_by(ExportUsage.created_at).all()]}


class ReleaseInput(BaseModel):
    confirmed_stopped: bool


@router.post("/admin/exports/{export_id}/release")
def release(export_id: str, request: ReleaseInput, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if not request.confirmed_stopped:
        raise HTTPException(422, "Confirm the render worker has stopped before releasing this reservation.")
    row = db.get(ExportUsage, export_id)
    if not row:
        raise HTTPException(404, "Export not found.")
    lock_account(db, row.user_id)
    db.refresh(row)
    if row.status != "reserved":
        raise HTTPException(409, "This export is no longer pending.")
    row.status, row.active_user, row.finished_at = "failed", None, now()
    db.commit()
    return {"success": True}
