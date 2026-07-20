from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.ai import GenerateRequest
from app.services.ai_service import AIService
from app.database import get_db


router = APIRouter(
    prefix="/api/ai",
    tags=["AI"]
)


@router.post("/generate")
def generate(
    request: GenerateRequest,
    db: Session = Depends(get_db)
):

    return AIService.generate(
        request,
        db
    )