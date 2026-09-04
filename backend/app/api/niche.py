from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.database import get_db
from app.models.niche import Niche
from app.schemas.niche import NicheCreate, NicheUpdate


router = APIRouter(prefix="/api/niches", tags=["Niches"])

DEFAULT_NICHES = [
    ("Morning Spiritual", "Mindfulness, wisdom and inner peace", "🌅", "amber"),
    ("Financial Freedom", "Money, investing and wealth mindset", "💰", "emerald"),
    ("Cosmic Knowledge", "Space, universe and cosmic mysteries", "🌌", "indigo"),
    ("Psychology", "Human behavior and the mind", "🧠", "violet"),
    ("Love & Romance", "Love, attraction and relationships", "❤️", "rose"),
    ("AI & Technology", "AI, coding, web and future technology", "🤖", "blue"),
]


def serialize(niche: Niche):
    return {key: getattr(niche, key) for key in (
        "id", "name", "description", "icon", "color", "is_active", "created_at", "updated_at"
    )}


@router.get("/")
def list_niches(include_inactive: bool = False, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    if db.query(Niche).filter(Niche.user_id == user_id).count() == 0:
        db.add_all([Niche(user_id=user_id, name=n, description=d, icon=i, color=c) for n, d, i, c in DEFAULT_NICHES])
        db.commit()
    query = db.query(Niche).filter(Niche.user_id == user_id)
    if not include_inactive:
        query = query.filter(Niche.is_active.is_(True))
    niches = query.order_by(Niche.name.asc()).all()
    return {"success": True, "niches": [serialize(item) for item in niches]}


@router.post("/")
def create_niche(request: NicheCreate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    name = request.name.strip()
    if db.query(Niche).filter(Niche.user_id == user_id, func.lower(Niche.name) == name.lower()).first():
        raise HTTPException(status_code=409, detail="This niche already exists.")
    niche = Niche(user_id=user_id, **request.model_dump(), name=name)
    db.add(niche); db.commit(); db.refresh(niche)
    return {"success": True, "niche": serialize(niche)}


@router.put("/{niche_id}")
def update_niche(niche_id: int, request: NicheUpdate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    niche = db.query(Niche).filter(Niche.id == niche_id, Niche.user_id == user_id).first()
    if not niche:
        raise HTTPException(status_code=404, detail="Niche not found.")
    data = request.model_dump(exclude_unset=True)
    if "name" in data:
        data["name"] = data["name"].strip()
        duplicate = db.query(Niche).filter(Niche.user_id == user_id, Niche.id != niche_id, func.lower(Niche.name) == data["name"].lower()).first()
        if duplicate:
            raise HTTPException(status_code=409, detail="This niche already exists.")
    for key, value in data.items(): setattr(niche, key, value)
    db.commit(); db.refresh(niche)
    return {"success": True, "niche": serialize(niche)}


@router.delete("/{niche_id}")
def delete_niche(niche_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    niche = db.query(Niche).filter(Niche.id == niche_id, Niche.user_id == user_id).first()
    if not niche:
        raise HTTPException(status_code=404, detail="Niche not found.")
    db.delete(niche); db.commit()
    return {"success": True}
