from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session


ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(
        self,
        model: type[ModelType],
        object_id: int,
    ) -> ModelType | None:
        statement = select(model).where(model.id == object_id)
        return self.db.scalar(statement)

    def create(
        self,
        instance: ModelType,
    ) -> ModelType:
        self.db.add(instance)
        self.db.flush()
        self.db.refresh(instance)

        return instance

    def delete(
        self,
        instance: ModelType,
    ) -> None:
        self.db.delete(instance)
        self.db.flush()