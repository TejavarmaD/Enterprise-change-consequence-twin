import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.api.dependencies import get_database_session
from backend.app.main import app
from backend.app.models import Base


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
            "change_id": "CHG-PERSISTENCE-001",
            "change_type": "business_rule",
            "title": "Original title",
            "description": "Original description.",
            "target_entity_type": "business_rule",
            "target_entity_id": 1,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_updated_change_survives_fresh_session(
    client,
    test_database,
):
    _, SessionLocal = test_database

    change = create_change(client)

    response = client.patch(
        f"/changes/{change['id']}",
        json={
            "title": "Persisted updated title",
        },
    )

    assert response.status_code == 200

    with SessionLocal() as db:
        from backend.app.models.change import Change

        persisted = db.get(
            Change,
            change["id"],
        )

        assert persisted is not None
        assert persisted.title == "Persisted updated title"
        assert persisted.change_id == "CHG-PERSISTENCE-001"