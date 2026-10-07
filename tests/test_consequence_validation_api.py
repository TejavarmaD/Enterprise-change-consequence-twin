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
            "change_id": "CHG-CONSEQUENCE-VALIDATION-001",
            "change_type": "business_rule",
            "title": "Update eligibility",
            "description": "Increase the minimum eligible age.",
            "target_entity_type": "business_rule",
            "target_entity_id": 1,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def valid_consequence_payload():
    return {
        "consequence_category": "business",
        "consequence_type": "customer_eligibility",
        "description": "Some customers may become ineligible.",
        "evidence_classification": "PREDICTION",
        "probability": 0.8,
        "impact": 0.7,
        "risk_score": 0.56,
        "confidence": 0.9,
    }


@pytest.mark.parametrize(
    "field",
    [
        "consequence_category",
        "consequence_type",
        "description",
        "evidence_classification",
    ],
)
def test_consequence_rejects_missing_required_field(client, field):
    change_id = create_change(client)

    payload = valid_consequence_payload()
    del payload[field]

    response = client.post(
        f"/changes/{change_id}/consequences",
        json=payload,
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field",
    [
        "probability",
        "impact",
        "risk_score",
        "confidence",
    ],
)
def test_consequence_rejects_value_above_one(client, field):
    change_id = create_change(client)

    payload = valid_consequence_payload()
    payload[field] = 1.01

    response = client.post(
        f"/changes/{change_id}/consequences",
        json=payload,
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "field",
    [
        "probability",
        "impact",
        "risk_score",
        "confidence",
    ],
)
def test_consequence_rejects_negative_value(client, field):
    change_id = create_change(client)

    payload = valid_consequence_payload()
    payload[field] = -0.01

    response = client.post(
        f"/changes/{change_id}/consequences",
        json=payload,
    )

    assert response.status_code == 422


def test_consequence_accepts_optional_risk_fields_as_omitted(client):
    change_id = create_change(client)

    payload = {
        "consequence_category": "technical",
        "consequence_type": "api_validation",
        "description": "API validation may require an update.",
        "evidence_classification": "INFERENCE",
    }

    response = client.post(
        f"/changes/{change_id}/consequences",
        json=payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["probability"] is None
    assert body["impact"] is None
    assert body["risk_score"] is None
    assert body["confidence"] is None
    assert body["approval_required"] is False