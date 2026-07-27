from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    email = Column(
        String(150),
        unique=True,
        index=True,
        nullable=False,
    )

    # Store only hashed password
    hashed_password = Column(
        String(255),
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
        server_default="1",
    )

    is_verified = Column(
        Boolean,
        default=False,
        server_default="0",
    )

    reset_token = Column(
        String(255),
        nullable=True,
    )

    reset_token_expiry = Column(
        DateTime(timezone=True),
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

    # =====================================================
    # Relationships
    # =====================================================

    # One User -> Many Brands
    brands = relationship(
        "Brand",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # One User -> Many Projects
    projects = relationship(
        "Project",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # One User -> Many Contents
    contents = relationship(
        "Content",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # One User -> One Subscription
    # subscription = relationship(
    #     "Subscription",
    #     back_populates="user",
    #     uselist=False,
    #     cascade="all, delete-orphan",
    #     lazy="selectin",
    # )

    # One User -> Many Usage Records
    usage = relationship(
        "Usage",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # One User -> Many API Settings
    api_settings = relationship(
        "ApiSetting",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # One User -> Many Schedules (optional)
    # schedules = relationship(
    #     "Schedule",
    #     back_populates="user",
    #     cascade="all, delete-orphan",
    #     lazy="selectin",
    # )

    # One User -> Many Trends (saved/generated trends)
    # trends = relationship(
    #     "Trend",
    #     back_populates="user",
    #     cascade="all, delete-orphan",
    #     lazy="selectin",
    # )

    media = relationship(
        "Media",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )   
    scenes = relationship(
        "Scene",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    images = relationship(
        "Image",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )