import os
import json
from urllib.parse import urlencode
from cryptography.fernet import InvalidToken
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user_id
from app.models.publishing import PublishingAccount, PublishJob
from app.models.schedule import Schedule
from app.services.publishing_accounts import PublishingAccounts, ProviderError, cipher
from app.services.publishing_worker import event

router = APIRouter(prefix="/api/social-connections", tags=["Social publishing"])


@router.get("/")
def list_connections(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    accounts = db.query(PublishingAccount).filter_by(user_id=user_id).order_by(PublishingAccount.id).all()
    providers = []
    for provider in PublishingAccounts.SCOPES:
        try:
            PublishingAccounts.credentials(provider)
            configured = True
        except HTTPException:
            configured = False
        providers.append({"provider": provider, "configured": configured})
    return {"accounts": [{key: getattr(row, key) for key in ("id", "provider", "remote_id", "name", "status", "expires_at", "created_at")} for row in accounts],
            "providers": providers, "worker_enabled": os.getenv("AUTO_PUBLISH_ENABLED", "true").lower() == "true"}


@router.post("/{provider}/connect")
def connect(provider: str, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    url, browser = PublishingAccounts.start(db, user_id, provider)
    # Set the binding cookie during top-level navigation on the callback host.
    # A cookie created by a localhost API request cannot reach an HTTPS tunnel.
    ticket = cipher().encrypt(json.dumps({"provider": provider, "url": url, "browser": browser}).encode()).decode()
    start_url = PublishingAccounts.redirect_uri(provider).rsplit("/", 1)[0] + "/authorize"
    response = JSONResponse({"authorization_url": start_url + "?" + urlencode({"ticket": ticket})})
    response.headers["Cache-Control"] = "no-store"
    return response


@router.get("/{provider}/authorize")
def authorize(provider: str, ticket: str):
    try:
        data = json.loads(cipher().decrypt(ticket.encode(), ttl=120))
        if data["provider"] != provider or provider not in PublishingAccounts.SCOPES:
            raise ValueError()
    except (InvalidToken, ValueError, KeyError, TypeError):
        raise HTTPException(400, "Connection link expired or is invalid. Start connecting again.") from None
    response = RedirectResponse(data["url"], status_code=303)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    browser = data["browser"]
    response.set_cookie(f"publishing_{provider}", browser, httponly=True, secure=PublishingAccounts.redirect_uri(provider).startswith("https:"), samesite="lax", max_age=600, path=f"/api/social-connections/{provider}/callback")
    return response


@router.get("/{provider}/callback")
def callback(provider: str, request: Request, code: str = "", state: str = "", error: str = "", db: Session = Depends(get_db)):
    result = "failed"
    try:
        user_id = PublishingAccounts.consume_state(db, provider, state, request.cookies.get(f"publishing_{provider}"))
        if error:
            result = "cancelled"
        elif code:
            PublishingAccounts.complete(db, user_id, provider, code)
            result = "connected"
    except (HTTPException, ProviderError, KeyError, ValueError):
        db.rollback()
    frontend = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
    response = RedirectResponse(f"{frontend}/settings?social={result}#social-accounts", status_code=303)
    response.delete_cookie(f"publishing_{provider}", path=f"/api/social-connections/{provider}/callback")
    return response


@router.delete("/{account_id:int}")
def disconnect(account_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    account = db.query(PublishingAccount).filter_by(id=account_id, user_id=user_id).with_for_update().first()
    if not account:
        raise HTTPException(404, "Connection not found.")
    # Publishing jobs cannot be interrupted safely after a platform request was sent.
    jobs = db.query(PublishJob).filter(PublishJob.account_id == account.id, PublishJob.user_id == user_id, PublishJob.status.in_(["queued", "processing", "publishing"])).all()
    if any(job.status in {"publishing", "processing"} for job in jobs):
        raise HTTPException(409, "This account is publishing a post. Wait for its result before disconnecting.")
    for job in jobs:
        changed = db.query(PublishJob).filter(PublishJob.id == job.id, PublishJob.status == "queued").update({"status": "cancelled"})
        if changed != 1:
            db.rollback()
            raise HTTPException(409, "Publishing just started. Wait for its result before disconnecting.")
        schedule = db.get(Schedule, job.schedule_id)
        if schedule:
            schedule.status = "cancelled"
        event(db, job, "cancelled", "Connection disconnected; pending publishing cancelled.")
    account.status, account.access_token, account.refresh_token = "disconnected", None, None
    db.commit()
    return {"success": True}
