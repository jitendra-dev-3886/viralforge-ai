import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.database import get_db
from app.models.user import User
from app.models.brand import Brand
from app.models.project import Project
from app.models.content import Content
from app.models.media import Media
from app.models.niche import Niche

router = APIRouter(prefix="/api/admin", tags=["Super Admin"])


def require_admin(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    configured_email = os.getenv("SUPER_ADMIN_EMAIL", "").strip().lower()
    if user and configured_email and user.email.lower() == configured_email and not user.is_super_admin:
        user.is_super_admin = True
        db.commit(); db.refresh(user)
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
    return {"success": True, "users": [{"id": u.id, "name": u.name, "email": u.email, "is_active": u.is_active, "is_verified": u.is_verified, "is_super_admin": u.is_super_admin, "created_at": u.created_at} for u in rows]}


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
