from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.database import get_db
from app.models.content import Content
from app.models.media import Media
from app.models.project import Project
from app.models.scene import Scene

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/")
def project_analytics(
    project_id: int | None = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    project_query = db.query(Project).filter(Project.user_id == user_id)
    content_query = db.query(Content).filter(Content.user_id == user_id)
    scene_query = db.query(Scene).filter(Scene.user_id == user_id)
    media_query = db.query(Media).filter(Media.user_id == user_id)
    if project_id is not None:
        project_query = project_query.filter(Project.id == project_id)
        content_query = content_query.filter(Content.project_id == project_id)
        scene_query = scene_query.filter(Scene.project_id == project_id)
        media_query = media_query.filter(Media.project_id == project_id)
    by_platform = content_query.with_entities(Content.platform, func.count(Content.id)).group_by(Content.platform).all()
    by_type = content_query.with_entities(Content.content_type, func.count(Content.id)).group_by(Content.content_type).all()
    return {
        "success": True,
        "project_id": project_id,
        "totals": {
            "projects": project_query.count(),
            "contents": content_query.count(),
            "scenes": scene_query.count(),
            "media": media_query.count(),
            "ready_media": media_query.filter(Media.status == "ready").count(),
            "final_renders": media_query.filter(Media.media_type == "final").count(),
        },
        "by_platform": [{"name": name, "count": count} for name, count in by_platform],
        "by_content_type": [{"name": name, "count": count} for name, count in by_type],
    }
