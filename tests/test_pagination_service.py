import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models import Base
from backend.app.models.change import Change
from backend.app.models.consequence_assessment import ConsequenceAssessment
from backend.app.repositories.change_repository import ChangeRepository
from backend.app.repositories.consequence_repository import (
    ConsequenceRepository,
)


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


def create_change(db, change_id):
    repository = ChangeRepository(db)

    change = Change(
        change_id=change_id,
        change_type="business_rule",
        title=f"Change {change_id}",
        description="Test change.",
        target_entity_type="business_rule",
        target_entity_id=1,
    )

    return repository.create(change)


def create_consequence(db, change_id, consequence_type):
    repository = ConsequenceRepository(db)

    consequence = ConsequenceAssessment(
        change_id=change_id,
        consequence_category="business",
        consequence_type=consequence_type,
        description="Test consequence.",
        evidence_classification="PREDICTION",
    )

    return repository.create(consequence)


def test_change_repository_pagination_boundaries(db):
    create_change(db, "CHG-001")
    create_change(db, "CHG-002")
    create_change(db, "CHG-003")

    repository = ChangeRepository(db)

    assert len(repository.list_all(limit=1, offset=0)) == 1
    assert len(repository.list_all(limit=1, offset=2)) == 1
    assert len(repository.list_all(limit=1, offset=3)) == 0
    assert repository.count() == 3


def test_consequence_repository_pagination_boundaries(db):
    change = create_change(db, "CHG-004")

    create_consequence(db, change.id, "first")
    create_consequence(db, change.id, "second")
    create_consequence(db, change.id, "third")

    repository = ConsequenceRepository(db)

    assert (
        len(
            repository.list_by_change_id(
                change.id,
                limit=1,
                offset=0,
            )
        )
        == 1
    )

    assert (
        len(
            repository.list_by_change_id(
                change.id,
                limit=1,
                offset=2,
            )
        )
        == 1
    )

    assert (
        len(
            repository.list_by_change_id(
                change.id,
                limit=1,
                offset=3,
            )
        )
        == 0
    )

    assert repository.count_by_change_id(change.id) == 3