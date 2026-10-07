import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.api.dependencies import get_database_session
from backend.app.main import app
from backend.app.models import Base
from backend.app.models.consequence_assessment import ConsequenceAssessment


@pytest.fixture
def test_database():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(bind=engine)

    yield engine, SessionLocal

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(test_database):
    _, SessionLocal = test_database

    def override_database_session():
        db = SessionLocal()

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


def create_change(client):
    response = client.post(
        "/changes",
        json={
            "change_id": "CHG-CASCADE-001",
            "change_type": "business_rule",
            "title": "Cascade delete test",
            "description": "Test consequence cleanup.",
            "target_entity_type": "business_rule",
            "target_entity_id": 1,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_consequence(client, change_id):
    response = client.post(
        f"/changes/{change_id}/consequences",
        json={
            "consequence_category": "business",
            "consequence_type": "customer_impact",
            "description": "Customers may be affected.",
            "evidence_classification": "PREDICTION",
            "probability": 0.8,
            "impact": 0.7,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_deleting_change_deletes_consequences(
    client,
    test_database,
):
    _, SessionLocal = test_database

    change_id = create_change(client)

    consequence_id = create_consequence(
        client,
        change_id,
    )

    delete_response = client.delete(
        f"/changes/{change_id}"
    )

    assert delete_response.status_code == 204

    with SessionLocal() as db:
        consequence = db.scalar(
            select(ConsequenceAssessment).where(
                ConsequenceAssessment.id == consequence_id
            )
        )

        assert consequence is None