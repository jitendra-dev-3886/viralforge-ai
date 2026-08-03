from typing import Optional

from fastapi import APIRouter

from app.services.trend_service import TrendService

router = APIRouter(
    prefix="/api/trends",
    tags=["Trends"]
)


@router.get("/")
def trending(niche: Optional[str] = None, limit: int = 24):

    return TrendService.get_trending(niche=niche, limit=limit)
