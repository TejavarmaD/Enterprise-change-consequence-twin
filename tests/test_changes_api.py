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


def create_change(client, change_id="CHG-001"):
    payload = {
        "change_id": change_id,
        "change_type": "business_rule",
        "title": "Update customer eligibility",
        "description": "Increase the minimum eligible customer age.",
        "target_entity_type": "business_rule",
        "target_entity_id": 1,
        "current_state": "Minimum age is 18.",
        "proposed_state": "Minimum age is 21.",
        "affected_domain": "business",
    }

    response = client.post("/changes", json=payload)

    assert response.status_code == 201

    return response.json()


def test_create_and_get_change(client):
    created_change = create_change(client)

    assert created_change["change_id"] == "CHG-001"
    assert created_change["title"] == "Update customer eligibility"
    assert isinstance(created_change["id"], int)

    get_response = client.get(
        f"/changes/{created_change['id']}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["change_id"] == "CHG-001"


def test_duplicate_change_id_returns_conflict(client):
    create_change(client, "CHG-DUPLICATE")

    payload = {
        "change_id": "CHG-DUPLICATE",
        "change_type": "schema",
        "title": "Duplicate change",
        "description": "This change should be rejected.",
        "target_entity_type": "data_asset",
        "target_entity_id": 1,
    }

    response = client.post("/changes", json=payload)

    assert response.status_code == 409


def test_get_missing_change_returns_not_found(client):
    response = client.get("/changes/99999")

    assert response.status_code == 404


def test_list_changes_returns_paginated_response(client):
    create_change(client, "CHG-LIST-001")
    create_change(client, "CHG-LIST-002")
    create_change(client, "CHG-LIST-003")

    response = client.get(
        "/changes",
        params={
            "limit": 2,
            "offset": 0,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 3
    assert len(body["items"]) == 2
    assert body["items"][0]["change_id"] == "CHG-LIST-001"
    assert body["items"][1]["change_id"] == "CHG-LIST-002"


def test_list_changes_respects_offset(client):
    create_change(client, "CHG-OFFSET-001")
    create_change(client, "CHG-OFFSET-002")
    create_change(client, "CHG-OFFSET-003")

    response = client.get(
        "/changes",
        params={
            "limit": 1,
            "offset": 1,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 3
    assert len(body["items"]) == 1
    assert body["items"][0]["change_id"] == "CHG-OFFSET-002"