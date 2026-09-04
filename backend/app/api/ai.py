from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user_id

from app.schemas.ai import (
    GenerateRequest,
    GenerateResponse,
)

from app.services.ai_service import AIService

router = APIRouter(
    prefix="/api/ai",
    tags=["AI"],
)


# ==========================================================
# Generate AI Content
# ==========================================================

@router.post(
    "/generate",
    response_model=GenerateResponse,
)
def generate_ai_content(
    request: GenerateRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Generate AI content

    Flow

    Project
        ↓
    Prompt
        ↓
    AI
        ↓
    Content
        ↓
    Scene
    """

    return AIService.generate(
        request=request,
        db=db,
        user_id=user_id,
    )
