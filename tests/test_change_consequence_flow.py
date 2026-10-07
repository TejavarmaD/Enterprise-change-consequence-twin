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


def test_change_can_have_multiple_consequences(client):
    change_payload = {
        "change_id": "CHG-FLOW-001",
        "change_type": "business_rule",
        "title": "Increase eligibility age",
        "description": "Increase the minimum customer age.",
        "target_entity_type": "business_rule",
        "target_entity_id": 1,
        "current_state": "Minimum age is 18.",
        "proposed_state": "Minimum age is 21.",
        "affected_domain": "business",
    }

    change_response = client.post(
        "/changes",
        json=change_payload,
    )

    assert change_response.status_code == 201

    change_id = change_response.json()["id"]

    first_consequence = {
        "consequence_category": "technical",
        "consequence_type": "api_validation",
        "description": "API validation logic must change.",
        "evidence_classification": "INFERENCE",
        "probability": 0.8,
        "impact": 0.6,
        "confidence": 0.9,
    }

    second_consequence = {
        "consequence_category": "business",
        "consequence_type": "customer_eligibility",
        "description": "Customers aged 18 to 20 may become ineligible.",
        "evidence_classification": "PREDICTION",
        "probability": 0.7,
        "impact": 0.9,
        "confidence": 0.85,
    }

    first_response = client.post(
        f"/changes/{change_id}/consequences",
        json=first_consequence,
    )

    second_response = client.post(
        f"/changes/{change_id}/consequences",
        json=second_consequence,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    list_response = client.get(
        f"/changes/{change_id}/consequences"
    )

    assert list_response.status_code == 200

    body = list_response.json()

    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert body["items"][0]["change_id"] == change_id
    assert body["items"][1]["change_id"] == change_id
    assert body["items"][0]["consequence_category"] == "technical"
    assert body["items"][1]["consequence_category"] == "business"


def test_consequence_cannot_be_retrieved_under_wrong_change(
    client,
):
    change_one = client.post(
        "/changes",
        json={
            "change_id": "CHG-FLOW-002",
            "change_type": "api",
            "title": "Change one",
            "description": "First change.",
            "target_entity_type": "api",
            "target_entity_id": 1,
        },
    ).json()["id"]

    change_two = client.post(
        "/changes",
        json={
            "change_id": "CHG-FLOW-003",
            "change_type": "api",
            "title": "Change two",
            "description": "Second change.",
            "target_entity_type": "api",
            "target_entity_id": 2,
        },
    ).json()["id"]

    consequence_response = client.post(
        f"/changes/{change_one}/consequences",
        json={
            "consequence_category": "technical",
            "consequence_type": "api_validation",
            "description": "Validation impact.",
            "evidence_classification": "INFERENCE",
        },
    )

    assert consequence_response.status_code == 201

    consequence_id = consequence_response.json()["id"]

    wrong_change_response = client.get(
        f"/changes/{change_two}/consequences/{consequence_id}"
    )

    assert wrong_change_response.status_code == 404