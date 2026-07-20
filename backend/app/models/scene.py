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

    id = Column(Integer, primary_key=True, index=True)

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

    scene_no = Column(Integer, nullable=False)

    title = Column(String(255))

    text = Column(Text, nullable=False)

    keyword = Column(String(255))

    duration = Column(Integer, default=5)

    media_type = Column(String(20), default="image")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    project = relationship("Project")

    content = relationship("Content")