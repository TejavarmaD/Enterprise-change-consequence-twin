import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models import Base
from backend.app.schemas.change import ChangeCreate
from backend.app.schemas.consequence import ConsequenceCreate
from backend.app.services.change_service import ChangeService
from backend.app.services.consequence_service import ConsequenceService


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


def create_change(db, change_id="CHG-SERVICE-001"):
    service = ChangeService(db)

    data = ChangeCreate(
        change_id=change_id,
        change_type="business_rule",
        title="Update customer eligibility",
        description="Increase the minimum eligible customer age.",
        target_entity_type="business_rule",
        target_entity_id=1,
    )

    return service.create_change(data)


def test_change_service_creates_change(db):
    change = create_change(db)

    assert change.id is not None
    assert change.change_id == "CHG-SERVICE-001"


def test_change_service_gets_change_by_id(db):
    change = create_change(db)

    service = ChangeService(db)
    result = service.get_change(change.id)

    assert result is not None
    assert result.change_id == "CHG-SERVICE-001"


def test_change_service_gets_change_by_external_id(db):
    create_change(db)

    service = ChangeService(db)
    result = service.get_change_by_external_id(
        "CHG-SERVICE-001"
    )

    assert result is not None
    assert result.title == "Update customer eligibility"


def test_change_service_lists_changes_with_pagination(db):
    create_change(db, "CHG-SERVICE-001")
    create_change(db, "CHG-SERVICE-002")
    create_change(db, "CHG-SERVICE-003")

    service = ChangeService(db)

    result = service.list_changes(
        limit=2,
        offset=0,
    )

    assert result.total == 3
    assert len(result.items) == 2
    assert result.items[0].change_id == "CHG-SERVICE-001"
    assert result.items[1].change_id == "CHG-SERVICE-002"


def test_change_service_lists_changes_with_offset(db):
    create_change(db, "CHG-SERVICE-001")
    create_change(db, "CHG-SERVICE-002")
    create_change(db, "CHG-SERVICE-003")

    service = ChangeService(db)

    result = service.list_changes(
        limit=1,
        offset=1,
    )

    assert result.total == 3
    assert len(result.items) == 1
    assert result.items[0].change_id == "CHG-SERVICE-002"


def test_change_service_returns_empty_page_after_last_item(db):
    create_change(db)

    service = ChangeService(db)

    result = service.list_changes(
        limit=10,
        offset=1,
    )

    assert result.total == 1
    assert result.items == []


def test_change_service_rejects_duplicate_external_id(db):
    create_change(db)

    service = ChangeService(db)

    data = ChangeCreate(
        change_id="CHG-SERVICE-001",
        change_type="api",
        title="Duplicate change",
        description="This change should be rejected.",
        target_entity_type="api",
        target_entity_id=1,
    )

    with pytest.raises(ValueError):
        service.create_change(data)


def test_consequence_service_creates_consequence(db):
    change = create_change(db)

    service = ConsequenceService(db)

    data = ConsequenceCreate(
        consequence_category="business",
        consequence_type="customer_eligibility",
        description="Some customers may become ineligible.",
        evidence_classification="PREDICTION",
        probability=0.8,
        impact=0.7,
        risk_score=0.56,
        confidence=0.9,
    )

    consequence = service.create_consequence(
        data,
        change.id,
    )

    assert consequence.id is not None
    assert consequence.change_id == change.id
    assert consequence.consequence_type == "customer_eligibility"


def test_consequence_service_gets_consequence(db):
    change = create_change(db)

    service = ConsequenceService(db)

    data = ConsequenceCreate(
        consequence_category="technical",
        consequence_type="api_validation",
        description="API validation may need updating.",
        evidence_classification="INFERENCE",
    )

    consequence = service.create_consequence(
        data,
        change.id,
    )

    result = service.get_consequence(consequence.id)

    assert result is not None
    assert result.id == consequence.id


def test_consequence_service_lists_with_pagination(db):
    change = create_change(db)

    service = ConsequenceService(db)

    first = ConsequenceCreate(
        consequence_category="technical",
        consequence_type="api_validation",
        description="API validation may need updating.",
        evidence_classification="INFERENCE",
    )

    second = ConsequenceCreate(
        consequence_category="business",
        consequence_type="customer_impact",
        description="Some customers may become ineligible.",
        evidence_classification="PREDICTION",
    )

    third = ConsequenceCreate(
        consequence_category="semantic",
        consequence_type="definition_change",
        description="Eligibility definition changes.",
        evidence_classification="FACT",
    )

    service.create_consequence(first, change.id)
    service.create_consequence(second, change.id)
    service.create_consequence(third, change.id)

    result = service.list_consequences_for_change(
        change_id=change.id,
        limit=2,
        offset=0,
    )

    assert result.total == 3
    assert len(result.items) == 2
    assert result.items[0].consequence_type == "api_validation"
    assert result.items[1].consequence_type == "customer_impact"


def test_consequence_service_returns_empty_page_after_last_item(db):
    change = create_change(db)

    service = ConsequenceService(db)

    data = ConsequenceCreate(
        consequence_category="technical",
        consequence_type="api_validation",
        description="API validation may need updating.",
        evidence_classification="INFERENCE",
    )

    service.create_consequence(data, change.id)

    result = service.list_consequences_for_change(
        change_id=change.id,
        limit=10,
        offset=1,
    )

    assert result.total == 1
    assert result.items == []