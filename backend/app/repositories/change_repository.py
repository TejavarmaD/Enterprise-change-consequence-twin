from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.change import Change


class ChangeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, change: Change) -> Change:
        self.db.add(change)
        self.db.flush()
        self.db.refresh(change)
        return change

    def get_by_id(self, change_id: int) -> Change | None:
        statement = select(Change).where(Change.id == change_id)
        return self.db.scalar(statement)

    def get_by_change_id(self, change_id: str) -> Change | None:
        statement = select(Change).where(Change.change_id == change_id)
        return self.db.scalar(statement)

    def list_all(self) -> list[Change]:
        statement = select(Change).order_by(Change.id)
        return list(self.db.scalars(statement).all())