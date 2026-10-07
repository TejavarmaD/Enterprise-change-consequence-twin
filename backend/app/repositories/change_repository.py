from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.change import Change
from backend.app.repositories.base import BaseRepository


class ChangeRepository(BaseRepository[Change]):
    def __init__(self, db: Session):
        super().__init__(db)

    def get_by_change_id(
        self,
        change_id: str,
    ) -> Change | None:
        statement = select(Change).where(
            Change.change_id == change_id
        )

        return self.db.scalar(statement)

    def list_all(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Change]:
        statement = (
            select(Change)
            .order_by(Change.id)
            .limit(limit)
            .offset(offset)
        )

        return list(self.db.scalars(statement).all())

    def count(self) -> int:
        statement = select(func.count()).select_from(Change)

        return self.db.scalar(statement) or 0

    def update(
        self,
        change: Change,
        values: dict,
    ) -> Change:
        for field, value in values.items():
            setattr(change, field, value)

        self.db.flush()
        self.db.refresh(change)

        return change