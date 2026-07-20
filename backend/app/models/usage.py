from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Usage(Base):

    __tablename__ = "usage"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    feature = Column(
        String(100),
        nullable=False,
    )

    provider = Column(
        String(50),
        nullable=True,
    )

    model = Column(
        String(100),
        nullable=True,
    )

    credits_used = Column(
        Integer,
        default=0,
    )

    requests = Column(
        Integer,
        default=1,
    )

    tokens = Column(
        Integer,
        default=0,
    )

    status = Column(
        String(20),
        default="success",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # =====================================
    # Relationship
    # =====================================

    user = relationship(
        "User",
        back_populates="usage",
    )