from app.core.admin_access import is_owner_email, sync_owner_access
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.database import get_db
from app.models.user import User
from app.models.brand import Brand
from app.models.project import Project
from app.models.content import Content
from app.models.media import Media
from app.models.niche import Niche
from app.models import Schedule, Image, Voice, Scene, Subscription, Usage, ApiSetting, SocialAccount, Trend
from app.models.billing import ExportUsage, PlanGrant

router = APIRouter(prefix="/api/admin", tags=["Super Admin"])


def require_admin(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    sync_owner_access(db, user)
    if not user or not user.is_active or not user.is_super_admin:
        raise HTTPException(status_code=403, detail="Super-admin access required.")
    return user


class UserAdminUpdate(BaseModel):
    is_active: bool | None = None
    is_verified: bool | None = None
    is_super_admin: bool | None = None


@router.get("/overview")
def overview(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return {"success": True, "counts": {
        "users": db.query(func.count(User.id)).scalar(), "brands": db.query(func.count(Brand.id)).scalar(),
        "projects": db.query(func.count(Project.id)).scalar(), "contents": db.query(func.count(Content.id)).scalar(),
        "media": db.query(func.count(Media.id)).scalar(), "niches": db.query(func.count(Niche.id)).scalar(),
    }}


@router.get("/users")
def users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    rows = db.query(User).order_by(User.created_at.desc()).all()
    return {"success": True, "users": [{"id": u.id, "name": u.name, "email": u.email, "is_active": u.is_active, "is_verified": u.is_verified, "is_super_admin": u.is_super_admin, "created_at": u.created_at, "delete_blocked_reason": delete_blocked_reason(u, admin)} for u in rows]}


def delete_blocked_reason(target: User, admin: User) -> str | None:
    if target.id == admin.id:
        return "You cannot delete your own account."
    if is_owner_email(target.email):
        return "Owner accounts cannot be deleted."
    if target.is_super_admin:
        return "Demote this admin to a user before deleting the account."
    return None


@router.delete("/users/{target_id}")
def delete_user(target_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    target = db.query(User).filter(User.id == target_id).with_for_update().first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found.")
    reason = delete_blocked_reason(target, admin)
    if reason:
        raise HTTPException(status_code=400, detail=reason)
    if db.query(PlanGrant.id).filter(PlanGrant.admin_id == target_id).first():
        raise HTTPException(status_code=409, detail="This account has issued plan grants. Disable it instead to preserve the grant history.")
    if db.query(ExportUsage.id).filter(ExportUsage.user_id == target_id, ExportUsage.status == "reserved").first():
        raise HTTPException(status_code=409, detail="This user has an export in progress. Wait for it to finish before deleting the account.")
    try:
        # Delete children first, including records without User ORM relationships.
        # Core deletes avoid ORM attempts to null non-nullable ownership columns.
        # Stored files are retained, matching the existing project deletion policy.
        for model in (Schedule, Image, Voice, Scene, Media, Content, Project, Brand,
                      ExportUsage, PlanGrant, Subscription, Usage, ApiSetting,
                      SocialAccount, Trend, Niche):
            table = model.__table__
            db.execute(table.delete().where(table.c.user_id == target_id))
        db.execute(User.__table__.delete().where(User.id == target_id))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Linked records prevent deletion. No changes were saved; disable the account instead.")
    return {"success": True, "message": "User and linked database records deleted."}


@router.put("/users/{target_id}")
def update_user(target_id: int, request: UserAdminUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    target = db.query(User).filter(User.id == target_id).first()
    if not target: raise HTTPException(status_code=404, detail="User not found.")
    data = request.model_dump(exclude_unset=True)
    if target.id == admin.id and (data.get("is_active") is False or data.get("is_super_admin") is False):
        raise HTTPException(status_code=400, detail="You cannot disable or demote your own admin account.")
    for key, value in data.items(): setattr(target, key, value)
    db.commit(); db.refresh(target)
    return {"success": True}


@router.get("/resources")
def resources(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return {"success": True,
        "brands": [{"id": x.id, "name": x.name, "user_id": x.user_id, "niche": x.niche} for x in db.query(Brand).order_by(Brand.created_at.desc()).limit(100)],
        "projects": [{"id": x.id, "title": x.title, "user_id": x.user_id, "status": x.status} for x in db.query(Project).order_by(Project.created_at.desc()).limit(100)],
        "contents": [{"id": x.id, "title": x.title, "user_id": x.user_id, "content_type": x.content_type, "status": x.status} for x in db.query(Content).order_by(Content.created_at.desc()).limit(100)]}
