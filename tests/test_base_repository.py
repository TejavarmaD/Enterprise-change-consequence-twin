import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models import Base
from backend.app.models.change import Change
from backend.app.repositories.base import BaseRepository


@pytest.fixture
def db():
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

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_base_repository_creates_instance(db):
    repository = BaseRepository[Change](db)

    change = Change(
        change_id="CHG-BASE-001",
        change_type="api",
        title="Test change",
        description="Test repository creation.",
        target_entity_type="api",
        target_entity_id=1,
    )

    result = repository.create(change)

    assert result.id is not None
    assert result.change_id == "CHG-BASE-001"


def test_base_repository_gets_instance_by_id(db):
    repository = BaseRepository[Change](db)

    change = Change(
        change_id="CHG-BASE-002",
        change_type="schema",
        title="Test retrieval",
        description="Test repository retrieval.",
        target_entity_type="data_asset",
        target_entity_id=1,
    )

    created = repository.create(change)

    result = repository.get_by_id(
        Change,
        created.id,
    )

    assert result is not None
    assert result.id == created.id
    assert result.change_id == "CHG-BASE-002"


def test_base_repository_returns_none_for_missing_id(db):
    repository = BaseRepository[Change](db)

    result = repository.get_by_id(
        Change,
        99999,
    )

    assert result is None