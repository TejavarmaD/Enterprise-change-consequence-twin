from sqlalchemy.orm import Session

from backend.app.models.consequence_assessment import ConsequenceAssessment
from backend.app.repositories.consequence_repository import ConsequenceRepository
from backend.app.schemas.consequence import ConsequenceCreate
from backend.app.schemas.consequence_list import ConsequenceListResponse
from backend.app.services.base import BaseService


class ConsequenceService(BaseService[ConsequenceAssessment]):
    def __init__(self, db: Session):
        repository = ConsequenceRepository(db)
        super().__init__(db, repository)

    def create_consequence(
        self,
        data: ConsequenceCreate,
        change_id: int,
    ) -> ConsequenceAssessment:
        consequence = ConsequenceAssessment(
            change_id=change_id,
            **data.model_dump(),
        )

        return self.repository.create(consequence)

    def get_consequence(
        self,
        consequence_id: int,
    ) -> ConsequenceAssessment | None:
        return self.repository.get_by_id(
            ConsequenceAssessment,
            consequence_id,
        )

    def list_consequences_for_change(
        self,
        change_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> ConsequenceListResponse:
        items = self.repository.list_by_change_id(
            change_id=change_id,
            limit=limit,
            offset=offset,
        )

        return ConsequenceListResponse(
            items=items,
            total=self.repository.count_by_change_id(change_id),
            limit=limit,
            offset=offset,
        )