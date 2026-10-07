from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.consequence_assessment import ConsequenceAssessment
from backend.app.repositories.base import BaseRepository


class ConsequenceRepository(BaseRepository[ConsequenceAssessment]):
    def __init__(self, db: Session):
        super().__init__(db)

    def list_by_change_id(
        self,
        change_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ConsequenceAssessment]:
        statement = (
            select(ConsequenceAssessment)
            .where(ConsequenceAssessment.change_id == change_id)
            .order_by(ConsequenceAssessment.id)
            .limit(limit)
            .offset(offset)
        )

        return list(self.db.scalars(statement).all())

    def count_by_change_id(self, change_id: int) -> int:
        statement = (
            select(func.count())
            .select_from(ConsequenceAssessment)
            .where(ConsequenceAssessment.change_id == change_id)
        )

        return self.db.scalar(statement) or 0