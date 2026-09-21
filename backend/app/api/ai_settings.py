import json
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, SecretStr
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user_id
from app.models.api_setting import ApiSetting
from app.services.user_ai_settings import settings_for, public_setting, cipher, credentials_for

router = APIRouter(prefix="/api/ai-settings", tags=["My AI providers"])
Provider = Literal["gemini", "groq", "cerebras", "openrouter", "mistral", "cloudflare", "huggingface"]


class SettingInput(BaseModel):
    model: str = Field(min_length=1, max_length=160, pattern=r"^[a-zA-Z0-9_./:@-]+$")
    api_key: SecretStr | None = None
    is_active: bool = True
    account_id: str | None = Field(None, pattern=r"^[a-fA-F0-9]{32}$")


@router.get("/")
def read_settings(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    return {"providers": [public_setting(row) for row in settings_for(db, user_id)]}


@router.put("/{provider}")
def save_setting(provider: Provider, request: SettingInput, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    row = db.query(ApiSetting).filter(ApiSetting.user_id == user_id, ApiSetting.provider == provider).first()
    account_id = request.account_id or (public_setting(row)["account_id"] if row else "")
    if provider == "cloudflare" and not account_id:
        raise HTTPException(422, detail="Cloudflare requires your 32-character Account ID.")
    key = request.api_key.get_secret_value().strip() if request.api_key else ""
    if key.startswith(('"', "'")) and key.endswith(key[0]):
        key = key[1:-1].strip()
    if key.lower().startswith("bearer "):
        key = key[7:].strip()
    if key and (not key.isascii() or "*" in key or key.startswith("enc:v1:")):
        raise HTTPException(422, detail="Paste the original provider API key, not a masked or encrypted value.")
    if key and (len(key) > 512 or any(c.isspace() for c in key)):
        raise HTTPException(422, detail="Enter a valid API key without spaces (maximum 512 characters).")
    if not key and (not row or not public_setting(row)["has_key"]):
        raise HTTPException(422, detail="An API key is required for this provider.")
    if row is None:
        row = ApiSetting(user_id=user_id, provider=provider)
        db.add(row)
    if key:
        row.api_key = "enc:v1:" + cipher().encrypt(key.encode()).decode()
    row.api_secret = json.dumps({"model": request.model, **({"account_id": account_id} if provider == "cloudflare" else {})})
    row.is_active = request.is_active
    db.commit()
    return public_setting(row)


@router.delete("/{provider}")
def delete_setting(provider: Provider, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    db.query(ApiSetting).filter(ApiSetting.user_id == user_id, ApiSetting.provider == provider).delete()
    db.commit()
    return {"success": True}


@router.post("/{provider}/test")
def test_setting(provider: Provider, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    from app.core.user_ai_client import generate_user_content
    from app.services.ai_service import AIService
    credentials = credentials_for(db, user_id, [provider])[provider]
    try:
        text, model = generate_user_content(provider, 'Return only this JSON object: {"ok":true}', credentials, max_tokens=512)
        AIService._parse_json_response(text)
    except Exception as error:
        raise AIService._provider_failure([(provider, error)]) from None
    return {"success": True, "provider": provider, "model": model, "message": "Saved key and model successfully returned JSON. Content generation uses these same credentials."}
