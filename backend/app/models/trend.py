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


class Trend(Base):

    __tablename__ = "trends"

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

    title = Column(
        String(500),
        nullable=False,
    )

    score = Column(
        Integer,
        default=0,
    )

    category = Column(
        String(100),
        nullable=True,
    )

    platform = Column(
        String(50),
        nullable=True,
    )

    content_type = Column(
        String(50),
        nullable=True,
    )

    source = Column(
        String(50),
        nullable=True,
    )

    language = Column(
        String(30),
        default="English",
    )

    country = Column(
        String(10),
        default="IN",
    )

    status = Column(
        String(30),
        default="active",
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
    #     back_populates="trends",
    # )