from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class PublishingAccount(Base):
    __tablename__ = "publishing_accounts"
    __table_args__ = (UniqueConstraint("user_id", "provider", "remote_id", name="uq_publishing_account"),)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(20), nullable=False)
    remote_id = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=True)  # Encrypted at rest; never serialized.
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    scopes = Column(Text, nullable=True)
    status = Column(String(30), nullable=False, default="connected")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PublishingOAuthState(Base):
    __tablename__ = "publishing_oauth_states"
    state_hash = Column(String(64), primary_key=True)
    browser_hash = Column(String(64), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(20), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)


class PublishJob(Base):
    __tablename__ = "publish_jobs"
    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False, unique=True)
    request_key = Column(String(36), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("publishing_accounts.id"), nullable=False)
    status = Column(String(30), nullable=False, default="queued", index=True)
    payload = Column(JSON, nullable=False)  # Immutable approved copy and explicit media selection.
    provider_state = Column(JSON, nullable=False, default=dict)
    remote_post_id = Column(String(255), nullable=True)
    next_attempt_at = Column(DateTime(timezone=True), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    attempts = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PublishEvent(Base):
    __tablename__ = "publish_events"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("publish_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(30), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
