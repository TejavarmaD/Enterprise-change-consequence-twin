from sqlalchemy.orm import Session

from backend.app.models.change import Change
from backend.app.repositories.change_repository import ChangeRepository
from backend.app.schemas.change import ChangeCreate
from backend.app.schemas.change_list import ChangeListResponse
from backend.app.schemas.change_update import ChangeUpdate
from backend.app.services.base import BaseService


class ChangeService(BaseService[Change]):
    def __init__(self, db: Session):
        repository = ChangeRepository(db)
        super().__init__(db, repository)

    def create_change(self, data: ChangeCreate) -> Change:
        existing_change = self.repository.get_by_change_id(
            data.change_id
        )

        if existing_change is not None:
            raise ValueError(
                f"Change with change_id '{data.change_id}' already exists."
            )

        change = Change(**data.model_dump())

        return self.repository.create(change)

    def get_change(self, change_id: int) -> Change | None:
        return self.repository.get_by_id(
            Change,
            change_id,
        )

    def get_change_by_external_id(
        self,
        change_id: str,
    ) -> Change | None:
        return self.repository.get_by_change_id(change_id)

    def update_change(
        self,
        change_id: int,
        data: ChangeUpdate,
    ) -> Change | None:
        change = self.repository.get_by_id(
            Change,
            change_id,
        )

        if change is None:
            return None

        values = data.model_dump(
            exclude_unset=True,
        )

        return self.repository.update(
            change,
            values,
        )

    def delete_change(
        self,
        change_id: int,
    ) -> bool:
        change = self.repository.get_by_id(
            Change,
            change_id,
        )

        if change is None:
            return False

        self.repository.delete(change)

        return True

    def list_changes(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> ChangeListResponse:
        items = self.repository.list_all(
            limit=limit,
            offset=offset,
        )

        return ChangeListResponse(
            items=items,
            total=self.repository.count(),
            limit=limit,
            offset=offset,
        )