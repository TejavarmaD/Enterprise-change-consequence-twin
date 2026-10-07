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


def test_missing_change_error_contract(client):
    response = client.get("/changes/99999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Change not found.",
    }


def test_missing_change_for_consequence_error_contract(client):
    response = client.get(
        "/changes/99999/consequences"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Change not found.",
    }


def test_missing_consequence_error_contract(client):
    change_response = client.post(
        "/changes",
        json={
            "change_id": "CHG-ERROR-001",
            "change_type": "api",
            "title": "Test change",
            "description": "Test missing consequence.",
            "target_entity_type": "api",
            "target_entity_id": 1,
        },
    )

    assert change_response.status_code == 201

    change_id = change_response.json()["id"]

    response = client.get(
        f"/changes/{change_id}/consequences/99999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Consequence not found.",
    }


def test_duplicate_change_error_contract(client):
    payload = {
        "change_id": "CHG-ERROR-DUPLICATE",
        "change_type": "schema",
        "title": "Duplicate change",
        "description": "Duplicate identifier test.",
        "target_entity_type": "data_asset",
        "target_entity_id": 1,
    }

    first_response = client.post(
        "/changes",
        json=payload,
    )

    second_response = client.post(
        "/changes",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": (
            "Change with change_id "
            "'CHG-ERROR-DUPLICATE' already exists."
        ),
    }