from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Schedule(Base):

    __tablename__ = "schedules"

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

    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content_id = Column(Integer, ForeignKey("contents.id", ondelete="CASCADE"), nullable=True, index=True)

    platform = Column(
        String(50),
        nullable=False,
    )

    account_name = Column(
        String(100),
        nullable=True,
    )

    scheduled_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    timezone = Column(
        String(100),
        default="Asia/Kolkata",
    )

    status = Column(
        String(30),
        default="pending",
    )

    published_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    post_url = Column(
        String(500),
        nullable=True,
    )

    error_message = Column(
        Text,
        nullable=True,
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
    # Relationships
    # =====================================

    # user = relationship(
    #     "User",
    #     back_populates="schedules",
    # )

    project = relationship(
        "Project",
        back_populates="schedules",
    )
