from sqlalchemy.orm import Session

from secrets import token_urlsafe
from datetime import datetime, timedelta

from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


class AuthService:

    @staticmethod
    def register(db: Session, request: RegisterRequest):

        existing_user = (
            db.query(User)
            .filter(User.email == request.email)
            .first()
        )

        if existing_user:
            return {
                "success": False,
                "message": "Email already exists.",
            }

        user = User(
            name=request.name,
            email=request.email,
            password=hash_password(request.password),
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "success": True,
            "message": "Registration successful.",
            "user": user,
        }

    @staticmethod
    def login(db: Session, request: LoginRequest):

        user = (
            db.query(User)
            .filter(User.email == request.email)
            .first()
        )

        if not user:
            return {
                "success": False,
                "message": "Invalid email or password.",
            }

        if not verify_password(
            request.password,
            user.password,
        ):
            return {
                "success": False,
                "message": "Invalid email or password.",
            }

        token = create_access_token(
            {
                "user_id": user.id,
                "email": user.email,
            }
        )

        return {
            "success": True,
            "message": "Login successful.",
            "token": token,
            "user": user,
        }

    @staticmethod
    def logout():

        return {
            "success": True,
            "message": "Logout successful."
        }

    @staticmethod
    def forgot_password(db: Session, email: str):

        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if user:

            token = token_urlsafe(32)

            user.reset_token = token

            user.reset_token_expiry = (
                datetime.utcnow() + timedelta(hours=1)
            )

            db.commit()

            # TODO:
            # Send reset email here

        return {
            "success": True,
            "message": "If the email exists, a password reset link has been sent."
        }