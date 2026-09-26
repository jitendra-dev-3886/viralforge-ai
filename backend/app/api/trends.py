from typing import Optional
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user_id
from app.models.project import Project
from app.services.user_ai_settings import credentials_for
from app.config.prompt_config import VISUAL_NICHE_BOUNDARIES

from app.services.trend_service import TrendService

router = APIRouter(
    prefix="/api/trends",
    tags=["Trends"]
)


@router.get("/")
def trending(niche: Optional[str] = None, limit: int = 10, project_id: Optional[int] = None,
             platform: str = "", content_type: str = "", db: Session = Depends(get_db),
             user_id: int = Depends(get_current_user_id)):
    brand = None
    if project_id:
        project = db.query(Project).filter(Project.id == project_id, Project.user_id == user_id).first()
        if not project:
            raise HTTPException(404, detail="Project not found.")
        brand = project.brand
    normalize = lambda value: re.sub(r"[^a-z0-9]", "", str(value or "").lower())
    boundary = ""
    for identity in (getattr(brand, "name", None), niche, getattr(brand, "niche", None)):
        boundary = next((scope for name, scope in VISUAL_NICHE_BOUNDARIES.items() if normalize(name) == normalize(identity)), "")
        if boundary:
            break

    return TrendService.get_trending(niche=niche, limit=limit, user_id=user_id,
                                    credentials=credentials_for(db, user_id), boundary=boundary,
                                    brand=f"{getattr(brand, 'name', '')}: {getattr(brand, 'description', '')}",
                                    platform=platform, content_type=content_type)
