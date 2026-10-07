from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_database_session
from backend.app.schemas.change import ChangeCreate
from backend.app.schemas.change_list import ChangeListResponse
from backend.app.schemas.change_response import ChangeResponse
from backend.app.schemas.change_update import ChangeUpdate
from backend.app.schemas.error import ErrorResponse
from backend.app.schemas.pagination import PaginationParams
from backend.app.services.change_service import ChangeService


router = APIRouter(
    prefix="/changes",
    tags=["changes"],
)


@router.post(
    "",
    response_model=ChangeResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def create_change(
    data: ChangeCreate,
    db: Session = Depends(get_database_session),
):
    service = ChangeService(db)

    try:
        change = service.create_change(data)
        db.commit()
        return change
    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/{change_id}",
    response_model=ChangeResponse,
    responses={
        404: {"model": ErrorResponse},
    },
)
def get_change(
    change_id: int,
    db: Session = Depends(get_database_session),
):
    service = ChangeService(db)
    change = service.get_change(change_id)

    if change is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Change not found.",
        )

    return change


@router.patch(
    "/{change_id}",
    response_model=ChangeResponse,
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def update_change(
    change_id: int,
    data: ChangeUpdate,
    db: Session = Depends(get_database_session),
):
    service = ChangeService(db)

    change = service.update_change(
        change_id,
        data,
    )

    if change is None:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Change not found.",
        )

    db.commit()

    return change


@router.delete(
    "/{change_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse},
    },
)
def delete_change(
    change_id: int,
    db: Session = Depends(get_database_session),
):
    service = ChangeService(db)

    deleted = service.delete_change(change_id)

    if not deleted:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Change not found.",
        )

    db.commit()


@router.get(
    "",
    response_model=ChangeListResponse,
)
def list_changes(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_database_session),
):
    service = ChangeService(db)

    return service.list_changes(
        limit=pagination.limit,
        offset=pagination.offset,
    )