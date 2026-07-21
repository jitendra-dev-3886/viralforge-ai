from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Scene(Base):

    __tablename__ = "scenes"

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

    content_id = Column(
        Integer,
        ForeignKey("contents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    scene_number = Column(
        Integer,
        nullable=False,
    )

    text = Column(
        Text,
        nullable=False,
    )

    keyword = Column(
        String(255),
        nullable=True,
    )

    media_type = Column(
        String(30),
        default="image",
    )

    duration = Column(
        Integer,
        default=5,
    )

    media_id = Column(
        Integer,
        ForeignKey("media.id", ondelete="SET NULL"),
        nullable=True,
    )

    status = Column(
        String(30),
        default="pending",
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

    # ======================================================
    # Relationships
    # ======================================================

    user = relationship(
        "User",
        back_populates="scenes",
    )

    project = relationship(
        "Project",
        back_populates="scenes",
    )

    content = relationship(
        "Content",
        back_populates="scenes",
    )

    media = relationship(
        "Media",
        back_populates="scenes",
    )