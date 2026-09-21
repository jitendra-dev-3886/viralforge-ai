from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, UniqueConstraint
from app.database import Base


class BillingPlan(Base):
    __tablename__ = "billing_plans"
    code = Column(String(30), primary_key=True)
    name = Column(String(60), nullable=False)
    price_inr = Column(Integer, nullable=False)
    period_days = Column(Integer, nullable=False)
    brands = Column(Integer, nullable=False)
    video_seconds = Column(Integer, nullable=True)
    video_exports = Column(Integer, nullable=True)
    image_exports = Column(Integer, nullable=False)


class ExportUsage(Base):
    __tablename__ = "export_usage"
    __table_args__ = (UniqueConstraint("user_id", "request_key", name="uq_export_request"),)
    id = Column(String(36), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    request_key = Column(String(128), nullable=False)
    resource = Column(String(100), nullable=False)
    kind = Column(String(20), nullable=False)
    units = Column(Integer, nullable=False)
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    # One render per account at a time also prevents same-output-file races.
    active_user = Column(Integer, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    result = Column(JSON, nullable=True)


class PlanGrant(Base):
    __tablename__ = "plan_grants"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_code = Column(String(30), nullable=False)
    starts_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    note = Column(String(500), nullable=False)
