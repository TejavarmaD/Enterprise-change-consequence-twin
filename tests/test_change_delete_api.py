import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.api.dependencies import get_database_session
from backend.app.main import app
from backend.app.models import Base


@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_database_session():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_database_session] = (
        override_database_session
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


def create_change(client):
    response = client.post(
        "/changes",
        json={
            "change_id": "CHG-DELETE-001",
            "change_type": "business_rule",
            "title": "Delete test change",
            "description": "Change created for deletion testing.",
            "target_entity_type": "business_rule",
            "target_entity_id": 1,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_delete_change(client):
    change = create_change(client)

    response = client.delete(
        f"/changes/{change['id']}"
    )

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(
        f"/changes/{change['id']}"
    )

    assert get_response.status_code == 404


def test_delete_missing_change_returns_not_found(client):
    response = client.delete(
        "/changes/99999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Change not found.",
    }


def test_deleted_change_is_removed_from_list(client):
    change = create_change(client)

    response = client.delete(
        f"/changes/{change['id']}"
    )

    assert response.status_code == 204

    list_response = client.get("/changes")

    assert list_response.status_code == 200

    body = list_response.json()

    assert body["total"] == 0
    assert body["items"] == []