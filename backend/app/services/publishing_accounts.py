"""Publishing authorization is independent of signing in to ViralForge."""
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import requests
from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException

from app.core.private_secrets import private_secret
from app.models.publishing import PublishingAccount, PublishingOAuthState
from app.models.user import User


def now():
    return datetime.now(timezone.utc)


def aware(value):
    return value.replace(tzinfo=timezone.utc) if value and value.tzinfo is None else value


def cipher():
    return Fernet(private_secret("publishing.key", "PUBLISHING_ENCRYPTION_KEY"))


def encrypt(value):
    return cipher().encrypt(value.encode()).decode() if value else None


def decrypt(value):
    try:
        return cipher().decrypt(value.encode()).decode() if value else None
    except (InvalidToken, ValueError):
        raise HTTPException(409, "Connection credentials are unavailable. Reconnect this account.") from None


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


class ProviderError(Exception):
    def __init__(self, message, uncertain=False, reconnect=False):
        super().__init__(message)
        self.uncertain = uncertain
        self.reconnect = reconnect


def request(method, url, **kwargs):
    """Never include provider bodies, URLs with tokens, or secrets in errors."""
    try:
        response = requests.request(method, url, timeout=(15, 60), allow_redirects=False, **kwargs)
    except requests.RequestException:
        raise ProviderError("The platform connection was interrupted. Check the platform before posting again.", uncertain=True) from None
    if response.status_code >= 400:
        code = None
        try:
            error = response.json().get("error", {})
            code = error.get("code") if isinstance(error, dict) else error
        except ValueError:
            pass
        reconnect = response.status_code == 401 or code in (190, "invalid_grant")
        message = "Reconnect this account to renew publishing permission." if reconnect else f"Platform rejected the request (HTTP {response.status_code}). Check permissions, media requirements and quota."
        raise ProviderError(message, uncertain=response.status_code >= 500, reconnect=reconnect)
    if 300 <= response.status_code < 400:
        raise ProviderError("The platform returned an unexpected redirect.", uncertain=True)
    return response


def api(method, url, **kwargs):
    response = request(method, url, **kwargs)
    try:
        result = response.json()
        if not isinstance(result, dict) or result.get("error"):
            raise ValueError()
        return result
    except ValueError:
        raise ProviderError("The platform returned an unreadable response. Check the platform before retrying.", uncertain=True) from None


class PublishingAccounts:
    SCOPES = {
        "instagram": "instagram_business_basic,instagram_business_content_publish",
        "facebook": "pages_show_list,pages_read_engagement,pages_manage_posts",
        "youtube": "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly",
    }

    @staticmethod
    def graph(provider):
        return f"https://graph.{provider}.com/{os.getenv('META_GRAPH_VERSION', 'v23.0')}"

    @staticmethod
    def credentials(provider):
        if provider not in PublishingAccounts.SCOPES:
            raise HTTPException(404, "Unsupported publishing platform.")
        prefix = "GOOGLE" if provider == "youtube" else provider.upper()
        values = os.getenv(f"{prefix}_CLIENT_ID"), os.getenv(f"{prefix}_CLIENT_SECRET")
        if not all(values):
            raise HTTPException(503, f"{provider.title()} publishing is not configured. Ask the administrator to configure its app credentials.")
        return values

    @staticmethod
    def redirect_uri(provider):
        return f"{os.getenv('BACKEND_URL', 'http://localhost:8000').rstrip('/')}/api/social-connections/{provider}/callback"

    @classmethod
    def start(cls, db, user_id, provider):
        client_id, _ = cls.credentials(provider)
        state, browser = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        db.query(PublishingOAuthState).filter(PublishingOAuthState.expires_at < now()).delete()
        db.add(PublishingOAuthState(state_hash=digest(state), browser_hash=digest(browser), user_id=user_id,
                                    provider=provider, expires_at=now() + timedelta(minutes=10)))
        db.commit()
        params = {"client_id": client_id, "redirect_uri": cls.redirect_uri(provider), "response_type": "code",
                  "state": state, "scope": cls.SCOPES[provider]}
        if provider == "youtube":
            params.update(access_type="offline", prompt="consent select_account", include_granted_scopes="true")
            base = "https://accounts.google.com/o/oauth2/v2/auth"
        elif provider == "facebook":
            base = f"https://www.facebook.com/{os.getenv('META_GRAPH_VERSION', 'v23.0')}/dialog/oauth"
        else:
            params.update(enable_fb_login="0", force_authentication="1")
            base = "https://www.instagram.com/oauth/authorize"
        return base + "?" + urlencode(params), browser

    @staticmethod
    def consume_state(db, provider, state, browser):
        row = db.query(PublishingOAuthState).filter_by(state_hash=digest(state or ""), provider=provider).first()
        if not row or aware(row.expires_at) <= now() or not secrets.compare_digest(row.browser_hash, digest(browser or "")):
            raise HTTPException(400, "Connection expired or belongs to another browser. Start connecting again.")
        user_id = row.user_id
        consumed = db.query(PublishingOAuthState).filter_by(state_hash=row.state_hash).delete()
        db.commit()
        if consumed != 1 or not db.query(User.id).filter_by(id=user_id, is_active=True).first():
            raise HTTPException(400, "This connection request is no longer valid.")
        return user_id

    @classmethod
    def complete(cls, db, user_id, provider, code):
        client_id, secret = cls.credentials(provider)
        base = {"client_id": client_id, "client_secret": secret, "code": code, "redirect_uri": cls.redirect_uri(provider)}
        records = []
        if provider == "youtube":
            token = api("POST", "https://oauth2.googleapis.com/token", data={**base, "grant_type": "authorization_code"})
            channels = api("GET", "https://www.googleapis.com/youtube/v3/channels", headers={"Authorization": f"Bearer {token['access_token']}"}, params={"part": "snippet", "mine": "true"}).get("items", [])
            if len(channels) > 1:
                raise HTTPException(400, "Choose a single YouTube channel during Google authorization, then connect again.")
            if token.get("scope") and "https://www.googleapis.com/auth/youtube.upload" not in token["scope"].split():
                raise HTTPException(400, "YouTube upload permission was not granted. Connect again and allow publishing.")
            records = [(item["id"], item["snippet"]["title"], token) for item in channels]
        elif provider == "facebook":
            token = api("GET", cls.graph(provider) + "/oauth/access_token", params=base)
            token = api("GET", cls.graph(provider) + "/oauth/access_token", params={"grant_type": "fb_exchange_token", "client_id": client_id, "client_secret": secret, "fb_exchange_token": token["access_token"]})
            cursor = None
            for _ in range(20):
                page = api("GET", cls.graph(provider) + "/me/accounts", headers={"Authorization": f"Bearer {token['access_token']}"}, params={"fields": "id,name,access_token,tasks", "limit": 100, **({"after": cursor} if cursor else {})})
                records.extend((item["id"], item["name"], {"access_token": item["access_token"]}) for item in page.get("data", []) if item.get("access_token") and set(item.get("tasks", [])) & {"CREATE_CONTENT", "MANAGE", "PROFILE_PLUS_CREATE_CONTENT"})
                cursor = page.get("paging", {}).get("cursors", {}).get("after")
                if not page.get("paging", {}).get("next") or not cursor:
                    break
        else:
            token = api("POST", "https://api.instagram.com/oauth/access_token", data={**base, "grant_type": "authorization_code"})
            token = api("GET", "https://graph.instagram.com/access_token", params={"grant_type": "ig_exchange_token", "client_secret": secret, "access_token": token["access_token"]})
            profile = api("GET", cls.graph(provider) + "/me", headers={"Authorization": f"Bearer {token['access_token']}"}, params={"fields": "user_id,username"})
            records = [(str(profile.get("user_id") or profile["id"]), profile["username"], token)]
        if not records:
            raise HTTPException(400, "No eligible channel or Page found. Use an Instagram professional account, a managed Facebook Page, or a YouTube channel.")
        for remote_id, name, token in records:
            row = db.query(PublishingAccount).filter_by(user_id=user_id, provider=provider, remote_id=remote_id).first()
            if not row:
                row = PublishingAccount(user_id=user_id, provider=provider, remote_id=remote_id, name=name)
                db.add(row)
            row.name, row.status = name[:255], "connected"
            row.access_token = encrypt(token["access_token"])
            if token.get("refresh_token"):
                row.refresh_token = encrypt(token["refresh_token"])
            row.expires_at = now() + timedelta(seconds=int(token["expires_in"])) if token.get("expires_in") else None
            row.scopes = token.get("scope") or cls.SCOPES[provider]
            if provider == "youtube" and not row.refresh_token:
                raise HTTPException(400, "Google did not grant offline access. Revoke this app in Google account permissions, then connect again.")
        db.commit()

    @classmethod
    def token(cls, db, account):
        if account.status != "connected" or not account.access_token:
            raise ProviderError("Reconnect this account before publishing.", reconnect=True)
        expires = aware(account.expires_at)
        threshold = timedelta(days=7) if account.provider == "instagram" else timedelta(minutes=5)
        if expires and expires <= now() + threshold:
            if account.provider == "youtube" and account.refresh_token:
                client_id, secret = cls.credentials("youtube")
                value = api("POST", "https://oauth2.googleapis.com/token", data={"grant_type": "refresh_token", "client_id": client_id, "client_secret": secret, "refresh_token": decrypt(account.refresh_token)})
            elif account.provider == "instagram" and expires > now():
                value = api("GET", "https://graph.instagram.com/refresh_access_token", params={"grant_type": "ig_refresh_token", "access_token": decrypt(account.access_token)})
            else:
                raise ProviderError("Publishing permission expired. Reconnect this account.", reconnect=True)
            account.access_token = encrypt(value["access_token"])
            account.expires_at = now() + timedelta(seconds=int(value["expires_in"]))
            db.commit()
        return decrypt(account.access_token)
