from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from urllib.parse import quote
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RegisterResponse,
    LoginResponse,
    ForgotPasswordRequest,
    SetPasswordRequest,
)
from app.services.auth_service import AuthService
from app.services.oauth_service import OAuthService
from app.core.security import get_current_user_id
from app.models.user import User
from app.core.admin_access import sync_owner_access

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=RegisterResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    return AuthService.register(
        db=db,
        request=request,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    response_model_exclude_none=True,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    return AuthService.login(
        db=db,
        request=request,
    )

@router.post("/logout")
def logout():
    return AuthService.logout() 

@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):

    return AuthService.forgot_password(
        db,
        request.email,
    )   


@router.get("/oauth/{provider}")
def oauth_start(provider: str):
    return RedirectResponse(OAuthService.authorization_url(provider), status_code=302)


@router.get("/oauth/{provider}/callback")
def oauth_callback(provider: str, code: str = "", state: str = "", error: str = "", db: Session = Depends(get_db)):
    frontend = OAuthService.FRONTEND_URL
    if error:
        return RedirectResponse(f"{frontend}/auth/callback?error={quote(error)}", status_code=302)
    try:
        profile = OAuthService.fetch_profile(provider, code, state)
        _, token = OAuthService.login(db, provider, profile)
        return RedirectResponse(f"{frontend}/auth/callback#token={quote(token)}", status_code=302)
    except HTTPException as exc:
        return RedirectResponse(f"{frontend}/auth/callback?error={quote(str(exc.detail))}", status_code=302)


@router.get("/me")
def current_user(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    sync_owner_access(db, user)
    has_password = bool(user.hashed_password and user.hashed_password.startswith("$2"))
    return {"success": True, "user": {"id": user.id, "name": user.name, "email": user.email, "is_active": user.is_active, "is_verified": user.is_verified, "is_super_admin": user.is_super_admin, "has_password": has_password}}


@router.post("/set-password")
def set_password(request: SetPasswordRequest, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return AuthService.set_password(db, user_id, request.password)
