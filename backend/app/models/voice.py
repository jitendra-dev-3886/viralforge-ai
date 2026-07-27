from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    Float,
    DateTime,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Voice(Base):

    __tablename__ = "voices"

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
    # Voice Settings
    # =====================================================

    provider = Column(
        String(50),
        default="edge-tts",
    )

    voice = Column(
        String(100),
        nullable=False,
    )

    gender = Column(
        String(20),
        nullable=True,
    )

    language = Column(
        String(30),
        default="English",
    )

    speed = Column(
        String(20),
        default="+0%",
    )

    pitch = Column(
        String(20),
        default="+0Hz",
    )

    # =====================================================
    # Voice Content
    # =====================================================

    text = Column(
        Text,
        nullable=False,
    )

    # =====================================================
    # Generated Audio
    # =====================================================

    audio_name = Column(
        String(255),
        nullable=True,
    )

    audio_path = Column(
        String(1000),
        nullable=True,
    )

    audio_url = Column(
        String(1000),
        nullable=True,
    )

    duration = Column(
        Float,
        default=0,
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
        back_populates="voices",
    )

    project = relationship(
        "Project",
        back_populates="voices",
    )

    content = relationship(
        "Content",
        back_populates="voices",
    )

    scene = relationship(
        "Scene",
        back_populates="voices",
    )