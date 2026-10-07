from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from backend.app.repositories.base import BaseRepository


ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    def __init__(
        self,
        db: Session,
        repository: BaseRepository[ModelType],
    ):
        self.db = db
        self.repository = repository