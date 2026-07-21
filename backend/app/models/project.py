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


class Project(Base):

    __tablename__ = "projects"

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

    brand_id = Column(
        Integer,
        ForeignKey("brands.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    topic = Column(
        String(500),
        nullable=False,
    )

    niche = Column(
        String(100),
        nullable=True,
    )

    category = Column(
        String(100),
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

    status = Column(
        String(30),
        default="draft",
    )

    ai_provider = Column(
        String(50),
        nullable=True,
    )

    prompt = Column(
        Text,
        nullable=True,
    )

    folder = Column(
        String(255),
        nullable=False,
    )

    path = Column(
        String(500),
        nullable=False,
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

    # ==================================================
    # Relationships
    # ==================================================

    # Many Projects -> One User
    user = relationship(
        "User",
        back_populates="projects",
    )

    # Many Projects -> One Brand
    brand = relationship(
        "Brand",
        back_populates="projects",
    )

    # One Project -> Many Contents
    contents = relationship(
        "Content",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # One Project -> Many Media Files
    media = relationship(
        "Media",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # One Project -> Many Scheduled Posts
    schedules = relationship(
        "Schedule",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    scenes = relationship(
        "Scene",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
