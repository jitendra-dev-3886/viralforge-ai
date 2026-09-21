"""Shared owner-account promotion for every authentication path."""
import os


def is_owner_email(email):
    owners = {"ystechlab@gmail.com", os.getenv("SUPER_ADMIN_EMAIL", "").strip().lower()}
    return bool(email) and email.strip().lower() in owners


def sync_owner_access(db, user):
    if user and user.is_active and is_owner_email(user.email) and not user.is_super_admin:
        user.is_super_admin = True
        db.commit()
        db.refresh(user)
