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


class Content(Base):

    __tablename__ = "contents"

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

    title = Column(
        String(255),
        nullable=False,
    )

    hook = Column(
        Text,
        nullable=True,
    )

    script = Column(
        Text,
        nullable=False,
    )

    caption = Column(
        Text,
        nullable=True,
    )

    hashtags = Column(
        Text,
        nullable=True,
    )

    keywords = Column(
        Text,
        nullable=True,
    )

    cta = Column(
        Text,
        nullable=True,
    )

    platform = Column(
        String(50),
        nullable=False,
    )

    content_type = Column(
        String(50),
        nullable=False,
    )

    language = Column(
        String(30),
        default="English",
    )

    ai_provider = Column(
        String(50),
        nullable=True,
    )

    ai_model = Column(
        String(100),
        nullable=True,
    )

    prompt = Column(
        Text,
        nullable=True,
    )

    status = Column(
        String(30),
        default="generated",
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

    # Many Contents -> One User
    user = relationship(
        "User",
        back_populates="contents",
    )

    # Many Contents -> One Project
    project = relationship(
        "Project",
        back_populates="contents",
    )
    scenes = relationship(
        "Scene",
        back_populates="content",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    voices = relationship(
        "Voice",
        back_populates="content",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    images = relationship(
        "Image",
        back_populates="content",
        cascade="all, delete-orphan",
        lazy="selectin",
    )