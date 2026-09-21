import json
from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException
from app.core.private_secrets import private_secret
from app.models.api_setting import ApiSetting

PROVIDERS = ("gemini", "groq", "cerebras", "openrouter", "mistral", "cloudflare", "huggingface")


def cipher():
    return Fernet(private_secret("api-keys.key", "API_CREDENTIAL_ENCRYPTION_KEY"))


def settings_for(db, user_id):
    return db.query(ApiSetting).filter(ApiSetting.user_id == user_id, ApiSetting.provider.in_(PROVIDERS)).order_by(ApiSetting.id).all()


def public_setting(row):
    try:
        metadata = json.loads(row.api_secret or "{}")
    except (ValueError, TypeError):
        metadata = {}
    if not isinstance(metadata, dict):
        metadata = {}
    return {"provider": row.provider, "model": metadata.get("model", ""), "account_id": metadata.get("account_id", "") if row.provider == "cloudflare" else "", "is_active": row.is_active, "has_key": bool(row.api_key and row.api_key.startswith("enc:v1:"))}


def credentials_for(db, user_id, requested=None):
    result = {}
    for row in settings_for(db, user_id):
        info = public_setting(row)
        if not row.is_active or not info["has_key"] or not info["model"]:
            continue
        if row.provider == "cloudflare" and not info["account_id"]:
            continue
        if requested and row.provider not in requested:
            continue
        try:
            key = cipher().decrypt(row.api_key[7:].encode()).decode()
        except InvalidToken:
            raise HTTPException(503, detail="Your saved API key could not be unlocked. Re-enter it in Settings → AI providers.")
        result[row.provider] = {"api_key": key, "model": info["model"]}
        if row.provider == "cloudflare":
            result[row.provider]["account_id"] = info["account_id"]
    if not result or (requested and any(p not in result for p in requested)):
        raise HTTPException(400, detail={"code": "user_ai_configuration_required", "message": "Add and enable your own API key and model in Settings → AI providers before generating content. Server API keys and local models are not shared with user accounts."})
    return result
