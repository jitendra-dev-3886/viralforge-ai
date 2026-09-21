import os
from datetime import datetime, timezone
from urllib.parse import urlencode

import requests
from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.security import ALGORITHM, SECRET_KEY, create_access_token
from app.models.social_account import SocialAccount
from app.models.user import User
from app.core.admin_access import sync_owner_access


class OAuthService:
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
    PROVIDERS = {"google", "youtube", "facebook", "instagram"}

    @classmethod
    def _credentials(cls, provider: str):
        prefix = "GOOGLE" if provider in {"google", "youtube"} else provider.upper()
        client_id = os.getenv(f"{prefix}_CLIENT_ID")
        client_secret = os.getenv(f"{prefix}_CLIENT_SECRET")
        if not client_id or not client_secret:
            raise HTTPException(status_code=503, detail=f"{provider.title()} login is not configured.")
        return client_id, client_secret

    @classmethod
    def _redirect_uri(cls, provider: str):
        return f"{cls.BACKEND_URL}/api/auth/oauth/{provider}/callback"

    @classmethod
    def authorization_url(cls, provider: str):
        if provider not in cls.PROVIDERS:
            raise HTTPException(status_code=404, detail="Unsupported login provider.")
        client_id, _ = cls._credentials(provider)
        state = jwt.encode({"provider": provider, "exp": int(datetime.now(timezone.utc).timestamp()) + 600}, SECRET_KEY, algorithm=ALGORITHM)
        common = {"client_id": client_id, "redirect_uri": cls._redirect_uri(provider), "response_type": "code", "state": state}
        if provider in {"google", "youtube"}:
            scopes = ["openid", "email", "profile"]
            if provider == "youtube": scopes.append("https://www.googleapis.com/auth/youtube.readonly")
            common.update({"scope": " ".join(scopes), "access_type": "offline", "prompt": "select_account", "include_granted_scopes": "true"})
            return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(common)}"
        if provider == "facebook":
            common["scope"] = "email,public_profile"
            return f"https://www.facebook.com/{os.getenv('META_GRAPH_VERSION', 'v23.0')}/dialog/oauth?{urlencode(common)}"
        common.update({"scope": "instagram_business_basic", "enable_fb_login": "0", "force_authentication": "1"})
        return f"https://www.instagram.com/oauth/authorize?{urlencode(common)}"

    @classmethod
    def _validate_state(cls, provider: str, state_token: str):
        try:
            payload = jwt.decode(state_token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("provider") != provider: raise ValueError("provider mismatch")
        except (JWTError, ValueError, TypeError) as exc:
            raise HTTPException(status_code=400, detail="Invalid or expired OAuth state.") from exc

    @classmethod
    def _request_json(cls, method: str, url: str, **kwargs):
        try:
            response = requests.request(method, url, timeout=15, **kwargs)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            detail = getattr(getattr(exc, "response", None), "text", "")
            raise HTTPException(status_code=502, detail=f"Provider request failed. {detail[:200]}") from exc

    @classmethod
    def fetch_profile(cls, provider: str, code: str, state_token: str):
        cls._validate_state(provider, state_token)
        client_id, client_secret = cls._credentials(provider)
        redirect_uri = cls._redirect_uri(provider)
        if provider in {"google", "youtube"}:
            token = cls._request_json("POST", "https://oauth2.googleapis.com/token", data={"code": code, "client_id": client_id, "client_secret": client_secret, "redirect_uri": redirect_uri, "grant_type": "authorization_code"})
            headers = {"Authorization": f"Bearer {token['access_token']}"}
            profile = cls._request_json("GET", "https://openidconnect.googleapis.com/v1/userinfo", headers=headers)
            provider_data = {"locale": profile.get("locale"), "email_verified": profile.get("email_verified")}
            if provider == "youtube":
                channels = cls._request_json("GET", "https://www.googleapis.com/youtube/v3/channels", headers=headers, params={"part": "snippet,statistics", "mine": "true"}).get("items", [])
                provider_data["channels"] = channels
            return {"id": profile["sub"], "email": profile.get("email"), "name": profile.get("name"), "username": profile.get("email"), "avatar": profile.get("picture"), "data": provider_data}
        if provider == "facebook":
            version = os.getenv("META_GRAPH_VERSION", "v23.0")
            token = cls._request_json("GET", f"https://graph.facebook.com/{version}/oauth/access_token", params={"client_id": client_id, "client_secret": client_secret, "redirect_uri": redirect_uri, "code": code})
            profile = cls._request_json("GET", f"https://graph.facebook.com/{version}/me", params={"fields": "id,name,email,picture.type(large)", "access_token": token["access_token"]})
            return {"id": profile["id"], "email": profile.get("email"), "name": profile.get("name"), "username": None, "avatar": profile.get("picture", {}).get("data", {}).get("url"), "data": {}}
        token = cls._request_json("POST", "https://api.instagram.com/oauth/access_token", data={"client_id": client_id, "client_secret": client_secret, "grant_type": "authorization_code", "redirect_uri": redirect_uri, "code": code})
        access_token = token["access_token"]
        profile = cls._request_json("GET", "https://graph.instagram.com/me", params={"fields": "id,user_id,username,name,profile_picture_url,account_type", "access_token": access_token})
        provider_id = str(profile.get("user_id") or profile["id"])
        return {"id": provider_id, "email": None, "name": profile.get("name") or profile.get("username") or "Instagram creator", "username": profile.get("username"), "avatar": profile.get("profile_picture_url"), "data": {"account_type": profile.get("account_type")}}

    @classmethod
    def login(cls, db: Session, provider: str, profile: dict):
        account = db.query(SocialAccount).filter(SocialAccount.provider == provider, SocialAccount.provider_user_id == profile["id"]).first()
        if account:
            user = account.user
        else:
            email = (profile.get("email") or f"{profile['id']}@{provider}.oauth.viralforge.ai").lower()
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(name=profile.get("name") or provider.title() + " user", email=email, hashed_password="!social-only", is_verified=bool(profile.get("email")))
                db.add(user); db.flush()
            account = SocialAccount(user_id=user.id, provider=provider, provider_user_id=profile["id"])
            db.add(account)
        if not user.is_active: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled.")
        account.username = profile.get("username"); account.avatar_url = profile.get("avatar"); account.profile_data = profile.get("data") or {}; account.last_login_at = datetime.now(timezone.utc)
        db.commit(); db.refresh(user)
        sync_owner_access(db, user)
        return user, create_access_token({"user_id": user.id, "email": user.email})
