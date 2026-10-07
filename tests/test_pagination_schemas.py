import pytest
from pydantic import ValidationError

from backend.app.schemas.pagination import PaginationParams


def test_pagination_defaults():
    pagination = PaginationParams()

    assert pagination.limit == 50
    assert pagination.offset == 0


def test_pagination_accepts_valid_values():
    pagination = PaginationParams(
        limit=25,
        offset=50,
    )

    assert pagination.limit == 25
    assert pagination.offset == 50


@pytest.mark.parametrize(
    "limit",
    [0, -1, 101],
)
def test_pagination_rejects_invalid_limit(limit):
    with pytest.raises(ValidationError):
        PaginationParams(limit=limit)


@pytest.mark.parametrize(
    "offset",
    [-1, -10],
)
def test_pagination_rejects_negative_offset(offset):
    with pytest.raises(ValidationError):
        PaginationParams(offset=offset)