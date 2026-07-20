from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Subscription(Base):

    __tablename__ = "subscriptions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    plan_name = Column(
        String(50),
        default="Free",
    )

    billing_cycle = Column(
        String(20),
        default="monthly",
    )

    amount = Column(
        Integer,
        default=0,
    )

    currency = Column(
        String(10),
        default="INR",
    )

    payment_provider = Column(
        String(50),
        nullable=True,
    )

    payment_id = Column(
        String(255),
        nullable=True,
    )

    order_id = Column(
        String(255),
        nullable=True,
    )

    subscription_id = Column(
        String(255),
        nullable=True,
    )

    status = Column(
        String(30),
        default="active",
    )

    starts_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    auto_renew = Column(
        Boolean,
        default=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # =====================================
    # Relationship
    # =====================================

    # user = relationship(
    #     "User",
    #     back_populates="subscription",
    # )