from fastapi import APIRouter

from app.schemas.ai import GenerateRequest
from app.services.ai_service import AIService

router = APIRouter(
    prefix="/api/ai",
    tags=["AI"]
)


@router.post("/generate")
def generate(request: GenerateRequest):
    return AIService.generate(request)