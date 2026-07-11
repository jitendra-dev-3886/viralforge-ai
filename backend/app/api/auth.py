from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
)
from app.services.auth_service import AuthService

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