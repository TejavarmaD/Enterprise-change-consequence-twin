import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.parametrize(
    "path",
    [
        "/changes/not-an-integer",
        "/changes/abc/consequences",
        "/changes/abc/consequences/1",
        "/changes/1/consequences/not-an-integer",
    ],
)
def test_invalid_path_ids_return_validation_error(client, path):
    response = client.get(path)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "path",
    [
        "/changes/-1",
        "/changes/0",
        "/changes/1/consequences/-1",
        "/changes/1/consequences/0",
    ],
)
def test_non_positive_path_ids_are_rejected(client, path):
    response = client.get(path)

    assert response.status_code in {404, 422}