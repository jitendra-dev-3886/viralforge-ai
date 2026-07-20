from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    BigInteger,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Media(Base):

    __tablename__ = "media"

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

    media_type = Column(
        String(30),
        nullable=False,
    )

    provider = Column(
        String(50),
        nullable=True,
    )

    title = Column(
        String(255),
        nullable=True,
    )

    file_name = Column(
        String(255),
        nullable=False,
    )

    file_path = Column(
        String(1000),
        nullable=False,
    )

    file_url = Column(
        String(1000),
        nullable=True,
    )

    mime_type = Column(
        String(100),
        nullable=True,
    )

    extension = Column(
        String(20),
        nullable=True,
    )

    duration = Column(
        Integer,
        nullable=True,
    )

    width = Column(
        Integer,
        nullable=True,
    )

    height = Column(
        Integer,
        nullable=True,
    )

    file_size = Column(
        BigInteger,
        nullable=True,
    )

    status = Column(
        String(30),
        default="ready",
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

    user = relationship(
        "User",
        back_populates="media",
    )

    project = relationship(
        "Project",
        back_populates="media",
    )