from datetime import datetime, timedelta
from secrets import token_urlsafe
from app.core.admin_access import is_owner_email, sync_owner_access

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


class AuthService:

    # ============================================
    # Register
    # ============================================

    @staticmethod
    def register(db: Session, request: RegisterRequest):

        print("========== REGISTER ==========")
        print("STEP 1")

        existing_user = (
            db.query(User)
            .filter(User.email == request.email)
            .first()
        )

        print("STEP 2")

        if existing_user:
            return {
                "success": False,
                "message": "Email already registered."
            }

        user = User(
            name=request.name,
            email=request.email,
            hashed_password=hash_password(request.password),
            is_super_admin=is_owner_email(request.email),
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "success": True,
            "message": "Registration successful.",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "is_super_admin": user.is_super_admin,
            }
        }

    # ============================================
    # Login
    # ============================================

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
                "message": "Invalid email or password."
            }

        if not user.hashed_password or not user.hashed_password.startswith("$2") or not verify_password(
            request.password,
            user.hashed_password,
        ):
            return {
                "success": False,
                "message": "Invalid email or password."
            }

        if not user.is_active:
            return {
                "success": False,
                "message": "Account disabled."
            }

        sync_owner_access(db, user)

        access_token = create_access_token(
            {
                "user_id": user.id,
                "email": user.email,
            }
        )

        return {
            "success": True,
            "message": "Login successful.",
            "token": access_token,
            "access_token": access_token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "is_super_admin": user.is_super_admin,
            }
        }

    # ============================================
    # Logout
    # ============================================

    @staticmethod
    def logout():

        return {
            "success": True,
            "message": "Logout successful."
        }

    # ============================================
    # Forgot Password
    # ============================================

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

            # TODO
            # Send Email

        return {
            "success": True,
            "message": "If the email exists, a reset link has been sent."
        }

    # ============================================
    # Reset Password
    # ============================================

    @staticmethod
    def reset_password(
        db: Session,
        token: str,
        new_password: str,
    ):

        user = (
            db.query(User)
            .filter(User.reset_token == token)
            .first()
        )

        if not user:
            return {
                "success": False,
                "message": "Invalid reset token."
            }

        if (
            user.reset_token_expiry is None
            or user.reset_token_expiry < datetime.utcnow()
        ):
            return {
                "success": False,
                "message": "Reset token expired."
            }

        user.hashed_password = hash_password(new_password)

        user.reset_token = None
        user.reset_token_expiry = None

        db.commit()

        return {
            "success": True,
            "message": "Password reset successful."
        }

    @staticmethod
    def set_password(db: Session, user_id: int, password: str):
        if len(password) < 8:
            return {"success": False, "message": "Password must be at least 8 characters."}
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "message": "User not found."}
        user.hashed_password = hash_password(password)
        db.commit()
        return {"success": True, "message": "Password updated successfully."}
