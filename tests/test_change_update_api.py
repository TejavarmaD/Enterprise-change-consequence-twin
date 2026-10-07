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
            "change_id": "CHG-UPDATE-001",
            "change_type": "business_rule",
            "title": "Original title",
            "description": "Original description.",
            "target_entity_type": "business_rule",
            "target_entity_id": 1,
            "current_state": "Minimum age is 18.",
            "proposed_state": "Minimum age is 21.",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_update_change(client):
    change = create_change(client)

    response = client.patch(
        f"/changes/{change['id']}",
        json={
            "title": "Updated title",
            "description": "Updated description.",
            "proposed_state": "Minimum age is 25.",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == change["id"]
    assert body["change_id"] == "CHG-UPDATE-001"
    assert body["title"] == "Updated title"
    assert body["description"] == "Updated description."
    assert body["proposed_state"] == "Minimum age is 25."
    assert body["current_state"] == "Minimum age is 18."


def test_update_change_supports_partial_updates(client):
    change = create_change(client)

    response = client.patch(
        f"/changes/{change['id']}",
        json={
            "affected_domain": "business",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["affected_domain"] == "business"
    assert body["title"] == "Original title"
    assert body["description"] == "Original description."


def test_update_change_id_is_rejected(client):
    change = create_change(client)

    response = client.patch(
        f"/changes/{change['id']}",
        json={
            "change_id": "CHG-MODIFIED",
        },
    )

    assert response.status_code == 422

    response = client.get(
        f"/changes/{change['id']}",
    )

    assert response.status_code == 200
    assert response.json()["change_id"] == change["change_id"]


def test_update_missing_change_returns_not_found(client):
    response = client.patch(
        "/changes/99999",
        json={
            "title": "Updated title",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Change not found.",
    }


def test_update_change_rejects_invalid_target_entity_id(client):
    change = create_change(client)

    response = client.patch(
        f"/changes/{change['id']}",
        json={
            "target_entity_id": 0,
        },
    )

    assert response.status_code == 422


def test_update_change_rejects_empty_payload(client):
    change = create_change(client)

    response = client.patch(
        f"/changes/{change['id']}",
        json={},
    )

    assert response.status_code == 422