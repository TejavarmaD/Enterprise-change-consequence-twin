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


def valid_change_payload():
    return {
        "change_id": "CHG-VALIDATION-001",
        "change_type": "business_rule",
        "title": "Update eligibility",
        "description": "Increase the minimum eligible age.",
        "target_entity_type": "business_rule",
        "target_entity_id": 1,
    }


def test_change_rejects_empty_change_id(client):
    payload = valid_change_payload()
    payload["change_id"] = ""

    response = client.post(
        "/changes",
        json=payload,
    )

    assert response.status_code == 422


def test_change_rejects_empty_title(client):
    payload = valid_change_payload()
    payload["title"] = ""

    response = client.post(
        "/changes",
        json=payload,
    )

    assert response.status_code == 422


def test_change_rejects_empty_description(client):
    payload = valid_change_payload()
    payload["description"] = ""

    response = client.post(
        "/changes",
        json=payload,
    )

    assert response.status_code == 422


def test_change_rejects_zero_target_entity_id(client):
    payload = valid_change_payload()
    payload["target_entity_id"] = 0

    response = client.post(
        "/changes",
        json=payload,
    )

    assert response.status_code == 422


def test_change_rejects_negative_target_entity_id(client):
    payload = valid_change_payload()
    payload["target_entity_id"] = -1

    response = client.post(
        "/changes",
        json=payload,
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field",
    [
        "change_id",
        "change_type",
        "title",
        "description",
        "target_entity_type",
    ],
)
def test_change_rejects_missing_required_field(client, field):
    payload = valid_change_payload()
    del payload[field]

    response = client.post(
        "/changes",
        json=payload,
    )

    assert response.status_code == 422


def test_change_accepts_optional_fields_as_omitted(client):
    response = client.post(
        "/changes",
        json=valid_change_payload(),
    )

    assert response.status_code == 201

    body = response.json()

    assert body["current_state"] is None
    assert body["proposed_state"] is None
    assert body["affected_domain"] is None
    assert body["requester"] is None
    assert body["business_reason"] is None
    assert body["expected_effect"] is None
    assert body["constraints"] is None
    assert body["uncertainty"] is None