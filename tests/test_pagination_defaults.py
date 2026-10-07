from backend.app.schemas.pagination import PaginationParams


def test_default_pagination_is_stable():
    params = PaginationParams()

    assert params.limit == 50
    assert params.offset == 0


def test_pagination_accepts_maximum_limit():
    params = PaginationParams(limit=100)

    assert params.limit == 100


def test_pagination_accepts_zero_offset():
    params = PaginationParams(offset=0)

    assert params.offset == 0