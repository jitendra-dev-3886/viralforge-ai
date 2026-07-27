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


class Image(Base):

    __tablename__ = "images"

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

    scene_id = Column(
        Integer,
        ForeignKey("scenes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # =====================================================
    # AI
    # =====================================================

    provider = Column(
        String(50),
        default="pollinations",
    )

    model = Column(
        String(100),
        nullable=True,
    )

    prompt = Column(
        Text,
        nullable=False,
    )

    negative_prompt = Column(
        Text,
        nullable=True,
    )

    # =====================================================
    # Generated Image
    # =====================================================

    image_name = Column(
        String(255),
        nullable=True,
    )

    image_path = Column(
        String(1000),
        nullable=True,
    )

    image_url = Column(
        String(1000),
        nullable=True,
    )

    width = Column(
        Integer,
        default=1024,
    )

    height = Column(
        Integer,
        default=1024,
    )

    file_size = Column(
        Integer,
        nullable=True,
    )

    # =====================================================
    # Status
    # =====================================================

    status = Column(
        String(30),
        default="pending",
    )

    error_message = Column(
        Text,
        nullable=True,
    )

    # =====================================================
    # Timestamp
    # =====================================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # =====================================================
    # Relationships
    # =====================================================

    user = relationship(
        "User",
        back_populates="images",
    )

    project = relationship(
        "Project",
        back_populates="images",
    )

    content = relationship(
        "Content",
        back_populates="images",
    )

    scene = relationship(
        "Scene",
        back_populates="images",
    )