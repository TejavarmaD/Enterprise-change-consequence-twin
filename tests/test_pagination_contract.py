from backend.app.schemas.change_list import ChangeListResponse
from backend.app.schemas.consequence_list import ConsequenceListResponse
from backend.app.schemas.pagination import PaginationParams


def test_pagination_contract_defaults():
    params = PaginationParams()

    assert params.limit == 50
    assert params.offset == 0


def test_change_list_contract_uses_items_total_and_pagination():
    response = ChangeListResponse(
        items=[],
        total=0,
        limit=50,
        offset=0,
    )

    assert response.model_dump() == {
        "items": [],
        "total": 0,
        "limit": 50,
        "offset": 0,
    }


def test_consequence_list_contract_uses_items_total_and_pagination():
    response = ConsequenceListResponse(
        items=[],
        total=0,
        limit=50,
        offset=0,
    )

    assert response.model_dump() == {
        "items": [],
        "total": 0,
        "limit": 50,
        "offset": 0,
    }