from typing import Optional

from fastapi import APIRouter

from app.services.trend_service import TrendService

router = APIRouter(
    prefix="/api/trends",
    tags=["Trends"]
)


@router.get("/")
def trending(niche: Optional[str] = None):

    return TrendService.get_trending(niche=niche)