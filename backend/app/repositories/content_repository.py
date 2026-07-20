from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.content import Content


class ContentRepository:

    def __init__(self, db: Session):
        self.db = db

    # -----------------------------
    # Create
    # -----------------------------

    def create(self, content: Content) -> Content:

        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)

        return content

    # -----------------------------
    # Find by ID
    # -----------------------------

    def get_by_id(
        self,
        content_id: int
    ) -> Optional[Content]:

        return (
            self.db.query(Content)
            .filter(Content.id == content_id)
            .first()
        )

    # -----------------------------
    # Get by Status
    # -----------------------------

    def get_by_status(
        self,
        status: str,
        limit: int = 20
    ) -> List[Content]:

        return (
            self.db.query(Content)
            .filter(Content.status == status)
            .order_by(Content.created_at.desc())
            .limit(limit)
            .all()
        )

    # -----------------------------
    # Get Scheduled
    # -----------------------------

    def get_scheduled(
        self,
        limit: int = 50
    ) -> List[Content]:

        return (
            self.db.query(Content)
            .filter(Content.status == "scheduled")
            .order_by(Content.scheduled_at.asc())
            .limit(limit)
            .all()
        )

    # -----------------------------
    # Update
    # -----------------------------

    def update(
        self,
        content: Content
    ) -> Content:

        self.db.commit()
        self.db.refresh(content)

        return content

    # -----------------------------
    # Approve
    # -----------------------------

    def approve(
        self,
        content: Content
    ) -> Content:

        content.is_approved = True
        content.status = "approved"

        self.db.commit()
        self.db.refresh(content)

        return content

    # -----------------------------
    # Publish
    # -----------------------------

    def publish(
        self,
        content: Content,
        response: dict | None = None
    ) -> Content:

        content.status = "published"
        content.publish_response = response

        self.db.commit()
        self.db.refresh(content)

        return content

    # -----------------------------
    # Delete
    # -----------------------------

    def delete(
        self,
        content: Content
    ):

        self.db.delete(content)
        self.db.commit()