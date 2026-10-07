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


def create_change(db, change_id="CHG-REPOSITORY-001"):
    change = Change(
        change_id=change_id,
        change_type="business_rule",
        title="Update customer eligibility",
        description="Increase the minimum eligible customer age.",
        target_entity_type="business_rule",
        target_entity_id=1,
    )

    repository = ChangeRepository(db)

    return repository.create(change)


def test_change_repository_creates_change(db):
    change = create_change(db)

    assert change.id is not None
    assert change.change_id == "CHG-REPOSITORY-001"


def test_change_repository_gets_change_by_id(db):
    change = create_change(db)

    repository = ChangeRepository(db)
    result = repository.get_by_id(
        Change,
        change.id,
    )

    assert result is not None
    assert result.id == change.id


def test_change_repository_gets_change_by_external_id(db):
    create_change(db)

    repository = ChangeRepository(db)
    result = repository.get_by_change_id(
        "CHG-REPOSITORY-001"
    )

    assert result is not None
    assert result.change_id == "CHG-REPOSITORY-001"


def test_change_repository_returns_none_for_missing_change(db):
    repository = ChangeRepository(db)

    result = repository.get_by_id(
        Change,
        99999,
    )

    assert result is None


def test_change_repository_lists_with_pagination(db):
    create_change(db, "CHG-REPOSITORY-001")
    create_change(db, "CHG-REPOSITORY-002")
    create_change(db, "CHG-REPOSITORY-003")

    repository = ChangeRepository(db)

    results = repository.list_all(
        limit=2,
        offset=0,
    )

    assert len(results) == 2
    assert results[0].change_id == "CHG-REPOSITORY-001"
    assert results[1].change_id == "CHG-REPOSITORY-002"


def test_change_repository_counts_changes(db):
    create_change(db, "CHG-REPOSITORY-001")
    create_change(db, "CHG-REPOSITORY-002")
    create_change(db, "CHG-REPOSITORY-003")

    repository = ChangeRepository(db)

    assert repository.count() == 3


def test_consequence_repository_creates_consequence(db):
    change = create_change(db)

    consequence = ConsequenceAssessment(
        change_id=change.id,
        consequence_category="business",
        consequence_type="customer_eligibility",
        description="Some customers may become ineligible.",
        evidence_classification="PREDICTION",
        probability=0.8,
        impact=0.7,
        risk_score=0.56,
        confidence=0.9,
        approval_required=True,
    )

    repository = ConsequenceRepository(db)
    result = repository.create(consequence)

    assert result.id is not None
    assert result.change_id == change.id


def test_consequence_repository_gets_consequence(db):
    change = create_change(db)

    consequence = ConsequenceAssessment(
        change_id=change.id,
        consequence_category="technical",
        consequence_type="api_validation",
        description="API validation may need updating.",
        evidence_classification="INFERENCE",
    )

    repository = ConsequenceRepository(db)
    created = repository.create(consequence)

    result = repository.get_by_id(
        ConsequenceAssessment,
        created.id,
    )

    assert result is not None
    assert result.id == created.id


def test_consequence_repository_returns_none_for_missing_consequence(
    db,
):
    repository = ConsequenceRepository(db)

    result = repository.get_by_id(
        ConsequenceAssessment,
        99999,
    )

    assert result is None


def test_consequence_repository_lists_with_pagination(db):
    change = create_change(db)

    repository = ConsequenceRepository(db)

    first = ConsequenceAssessment(
        change_id=change.id,
        consequence_category="technical",
        consequence_type="api_validation",
        description="API validation may need updating.",
        evidence_classification="INFERENCE",
    )

    second = ConsequenceAssessment(
        change_id=change.id,
        consequence_category="business",
        consequence_type="customer_impact",
        description="Some customers may become ineligible.",
        evidence_classification="PREDICTION",
    )

    third = ConsequenceAssessment(
        change_id=change.id,
        consequence_category="semantic",
        consequence_type="definition_change",
        description="Eligibility definition changes.",
        evidence_classification="FACT",
    )

    repository.create(first)
    repository.create(second)
    repository.create(third)

    results = repository.list_by_change_id(
        change.id,
        limit=2,
        offset=0,
    )

    assert len(results) == 2
    assert results[0].consequence_type == "api_validation"
    assert results[1].consequence_type == "customer_impact"


def test_consequence_repository_counts_by_change_id(db):
    change = create_change(db)

    repository = ConsequenceRepository(db)

    repository.create(
        ConsequenceAssessment(
            change_id=change.id,
            consequence_category="technical",
            consequence_type="api_validation",
            description="API validation may need updating.",
            evidence_classification="INFERENCE",
        )
    )

    repository.create(
        ConsequenceAssessment(
            change_id=change.id,
            consequence_category="business",
            consequence_type="customer_impact",
            description="Some customers may become ineligible.",
            evidence_classification="PREDICTION",
        )
    )

    assert repository.count_by_change_id(change.id) == 2