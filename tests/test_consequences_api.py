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


def create_test_change(client):
    payload = {
        "change_id": "CHG-CONSEQUENCE-001",
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

    return response.json()["id"]


def create_consequence(client, change_id, consequence_type):
    payload = {
        "consequence_category": "business",
        "consequence_type": consequence_type,
        "description": "Some customers may become affected.",
        "evidence_classification": "PREDICTION",
        "probability": 0.8,
        "impact": 0.7,
        "risk_score": 0.56,
        "confidence": 0.9,
    }

    response = client.post(
        f"/changes/{change_id}/consequences",
        json=payload,
    )

    assert response.status_code == 201

    return response.json()


def test_create_consequence(client):
    change_id = create_test_change(client)

    consequence = create_consequence(
        client,
        change_id,
        "customer_eligibility",
    )

    assert consequence["change_id"] == change_id
    assert consequence["consequence_category"] == "business"
    assert consequence["risk_score"] == 0.56
    assert consequence["approval_required"] is False


def test_list_consequences_returns_paginated_response(client):
    change_id = create_test_change(client)

    create_consequence(client, change_id, "customer_eligibility")
    create_consequence(client, change_id, "customer_segmentation")
    create_consequence(client, change_id, "kpi_impact")

    response = client.get(
        f"/changes/{change_id}/consequences",
        params={
            "limit": 2,
            "offset": 0,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 3
    assert len(body["items"]) == 2
    assert body["items"][0]["consequence_type"] == (
        "customer_eligibility"
    )
    assert body["items"][1]["consequence_type"] == (
        "customer_segmentation"
    )


def test_list_consequences_respects_offset(client):
    change_id = create_test_change(client)

    create_consequence(client, change_id, "first")
    create_consequence(client, change_id, "second")
    create_consequence(client, change_id, "third")

    response = client.get(
        f"/changes/{change_id}/consequences",
        params={
            "limit": 1,
            "offset": 1,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 3
    assert len(body["items"]) == 1
    assert body["items"][0]["consequence_type"] == "second"


def test_get_consequence(client):
    change_id = create_test_change(client)

    consequence = create_consequence(
        client,
        change_id,
        "definition_change",
    )

    response = client.get(
        f"/changes/{change_id}/consequences/{consequence['id']}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == consequence["id"]


def test_missing_change_returns_not_found(client):
    payload = {
        "consequence_category": "technical",
        "consequence_type": "dependency_failure",
        "description": "The affected change does not exist.",
        "evidence_classification": "UNKNOWN",
    }

    response = client.post(
        "/changes/99999/consequences",
        json=payload,
    )

    assert response.status_code == 404


def test_missing_consequence_returns_not_found(client):
    change_id = create_test_change(client)

    response = client.get(
        f"/changes/{change_id}/consequences/99999"
    )

    assert response.status_code == 404