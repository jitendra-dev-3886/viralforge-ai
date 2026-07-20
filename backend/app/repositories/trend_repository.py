from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.trend import Trend


class TrendRepository:

    def __init__(self, db: Session):
        self.db = db

    # -----------------------------
    # Create
    # -----------------------------

    def create(self, trend: Trend) -> Trend:
        self.db.add(trend)
        self.db.commit()
        self.db.refresh(trend)
        return trend

    # -----------------------------
    # Bulk Insert
    # -----------------------------

    def bulk_create(self, trends: List[Trend]) -> List[Trend]:

        self.db.add_all(trends)
        self.db.commit()

        for trend in trends:
            self.db.refresh(trend)

        return trends

    # -----------------------------
    # Find by ID
    # -----------------------------

    def get_by_id(self, trend_id: int) -> Optional[Trend]:

        return (
            self.db.query(Trend)
            .filter(Trend.id == trend_id)
            .first()
        )

    # -----------------------------
    # Find by Title
    # -----------------------------

    def get_by_title(self, title: str) -> Optional[Trend]:

        return (
            self.db.query(Trend)
            .filter(Trend.title == title)
            .first()
        )

    # -----------------------------
    # Latest Trends
    # -----------------------------

    def get_latest(
        self,
        limit: int = 20
    ) -> List[Trend]:

        return (
            self.db.query(Trend)
            .order_by(Trend.created_at.desc())
            .limit(limit)
            .all()
        )

    # -----------------------------
    # Top Trending
    # -----------------------------

    def get_top_trends(
        self,
        limit: int = 20
    ) -> List[Trend]:

        return (
            self.db.query(Trend)
            .order_by(Trend.trend_score.desc())
            .limit(limit)
            .all()
        )

    # -----------------------------
    # Unprocessed
    # -----------------------------

    def get_unprocessed(
        self,
        limit: int = 100
    ) -> List[Trend]:

        return (
            self.db.query(Trend)
            .filter(
                Trend.is_processed == False
            )
            .order_by(
                Trend.trend_score.desc()
            )
            .limit(limit)
            .all()
        )

    # -----------------------------
    # Mark Processed
    # -----------------------------

    def mark_processed(
        self,
        trend: Trend
    ) -> Trend:

        trend.is_processed = True
        trend.status = "processed"

        self.db.commit()
        self.db.refresh(trend)

        return trend

    # -----------------------------
    # Delete
    # -----------------------------

    def delete(
        self,
        trend: Trend
    ):

        self.db.delete(trend)
        self.db.commit()