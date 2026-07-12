from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
)
from app.services.auth_service import AuthService

from app.schemas.auth import ForgotPasswordRequest

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post("/register")
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    return AuthService.register(
        db=db,
        request=request,
    )


@router.post("/login")
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