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


def create_change(client, change_id):
    payload = {
        "change_id": change_id,
        "change_type": "business_rule",
        "title": f"Change {change_id}",
        "description": "Test change.",
        "target_entity_type": "business_rule",
        "target_entity_id": 1,
    }

    response = client.post(
        "/changes",
        json=payload,
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_consequence(
    client,
    change_id,
    consequence_type,
):
    payload = {
        "consequence_category": "business",
        "consequence_type": consequence_type,
        "description": "Test consequence.",
        "evidence_classification": "PREDICTION",
    }

    response = client.post(
        f"/changes/{change_id}/consequences",
        json=payload,
    )

    assert response.status_code == 201


def test_change_limit_validation(client):
    response = client.get(
        "/changes",
        params={"limit": 0},
    )

    assert response.status_code == 422


def test_change_limit_upper_bound_validation(client):
    response = client.get(
        "/changes",
        params={"limit": 101},
    )

    assert response.status_code == 422


def test_change_offset_validation(client):
    response = client.get(
        "/changes",
        params={"offset": -1},
    )

    assert response.status_code == 422


def test_consequence_limit_validation(client):
    change_id = create_change(
        client,
        "CHG-PAGINATION-001",
    )

    response = client.get(
        f"/changes/{change_id}/consequences",
        params={"limit": 0},
    )

    assert response.status_code == 422


def test_consequence_offset_validation(client):
    change_id = create_change(
        client,
        "CHG-PAGINATION-002",
    )

    response = client.get(
        f"/changes/{change_id}/consequences",
        params={"offset": -1},
    )

    assert response.status_code == 422


def test_change_pagination_defaults(client):
    create_change(client, "CHG-PAGINATION-003")
    create_change(client, "CHG-PAGINATION-004")

    response = client.get("/changes")

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert body["limit"] == 50
    assert body["offset"] == 0


def test_consequence_pagination_defaults(client):
    change_id = create_change(
        client,
        "CHG-PAGINATION-005",
    )

    create_consequence(
        client,
        change_id,
        "first",
    )
    create_consequence(
        client,
        change_id,
        "second",
    )

    response = client.get(
        f"/changes/{change_id}/consequences"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert body["limit"] == 50
    assert body["offset"] == 0