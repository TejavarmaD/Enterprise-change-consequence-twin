from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_database_session
from backend.app.schemas.consequence import ConsequenceCreate
from backend.app.schemas.consequence_list import ConsequenceListResponse
from backend.app.schemas.consequence_response import ConsequenceResponse
from backend.app.schemas.error import ErrorResponse
from backend.app.schemas.pagination import PaginationParams
from backend.app.services.change_service import ChangeService
from backend.app.services.consequence_service import ConsequenceService


router = APIRouter(
    prefix="/changes/{change_id}/consequences",
    tags=["consequences"],
)


@router.post(
    "",
    response_model=ConsequenceResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": ErrorResponse},
    },
)
def create_consequence(
    change_id: int,
    data: ConsequenceCreate,
    db: Session = Depends(get_database_session),
):
    change_service = ChangeService(db)

    if change_service.get_change(change_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Change not found.",
        )

    service = ConsequenceService(db)
    consequence = service.create_consequence(data, change_id)

    db.commit()

    return consequence


@router.get(
    "",
    response_model=ConsequenceListResponse,
    responses={
        404: {"model": ErrorResponse},
    },
)
def list_consequences(
    change_id: int,
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_database_session),
):
    change_service = ChangeService(db)

    if change_service.get_change(change_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Change not found.",
        )

    service = ConsequenceService(db)

    return service.list_consequences_for_change(
        change_id=change_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )


@router.get(
    "/{consequence_id}",
    response_model=ConsequenceResponse,
    responses={
        404: {"model": ErrorResponse},
    },
)
def get_consequence(
    change_id: int,
    consequence_id: int,
    db: Session = Depends(get_database_session),
):
    change_service = ChangeService(db)

    if change_service.get_change(change_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Change not found.",
        )

    service = ConsequenceService(db)
    consequence = service.get_consequence(consequence_id)

    if consequence is None or consequence.change_id != change_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consequence not found.",
        )

    return consequence