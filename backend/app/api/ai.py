from fastapi import APIRouter

from app.schemas.ai import GenerateContentRequest
from app.services.ai_service import AIService

router = APIRouter(
    prefix="/api/ai",
    tags=["AI"]
)


@router.post("/generate")
def generate(request: GenerateContentRequest):

    return AIService.generate(request)