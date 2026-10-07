import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models import Base
from backend.app.models.consequence_assessment import ConsequenceAssessment
from backend.app.repositories.consequence_repository import (
    ConsequenceRepository,
)
from backend.app.schemas.change import ChangeCreate
from backend.app.services.change_service import ChangeService


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
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def create_change(db):
    service = ChangeService(db)

    return service.create_change(
        ChangeCreate(
            change_id="CHG-DELETE-SERVICE-001",
            change_type="business_rule",
            title="Delete test",
            description="Test service deletion.",
            target_entity_type="business_rule",
            target_entity_id=1,
        )
    )


def test_change_service_deletes_existing_change(db):
    change = create_change(db)

    service = ChangeService(db)

    result = service.delete_change(change.id)

    assert result is True

    db.commit()

    assert service.get_change(change.id) is None


def test_change_service_returns_false_for_missing_change(db):
    service = ChangeService(db)

    result = service.delete_change(99999)

    assert result is False


def test_change_service_delete_does_not_commit(db):
    change = create_change(db)

    db.commit()

    service = ChangeService(db)

    result = service.delete_change(change.id)

    assert result is True

    db.rollback()

    restored = service.get_change(change.id)

    assert restored is not None
    assert restored.change_id == "CHG-DELETE-SERVICE-001"


def test_change_service_delete_cascades_consequences(db):
    change = create_change(db)

    consequence_repository = ConsequenceRepository(db)

    consequence = consequence_repository.create(
        ConsequenceAssessment(
            change_id=change.id,
            consequence_category="business",
            consequence_type="customer_impact",
            description="Customers may be affected.",
            evidence_classification="PREDICTION",
        )
    )

    service = ChangeService(db)

    result = service.delete_change(change.id)

    assert result is True

    db.commit()

    remaining = db.scalar(
        select(ConsequenceAssessment).where(
            ConsequenceAssessment.id == consequence.id
        )
    )

    assert remaining is None