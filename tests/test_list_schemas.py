from backend.app.schemas.change_list import ChangeListResponse
from backend.app.schemas.consequence_list import ConsequenceListResponse


def test_change_list_response_requires_pagination_fields():
    payload = {
        "items": [],
        "total": 0,
        "limit": 50,
        "offset": 0,
    }

    response = ChangeListResponse.model_validate(payload)

    assert response.items == []
    assert response.total == 0
    assert response.limit == 50
    assert response.offset == 0


def test_consequence_list_response_requires_pagination_fields():
    payload = {
        "items": [],
        "total": 0,
        "limit": 50,
        "offset": 0,
    }

    response = ConsequenceListResponse.model_validate(payload)

    assert response.items == []
    assert response.total == 0
    assert response.limit == 50
    assert response.offset == 0