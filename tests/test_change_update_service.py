import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models import Base
from backend.app.schemas.change import ChangeCreate
from backend.app.schemas.change_update import ChangeUpdate
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
            change_id="CHG-UPDATE-SERVICE-001",
            change_type="business_rule",
            title="Original title",
            description="Original description.",
            target_entity_type="business_rule",
            target_entity_id=1,
            current_state="Minimum age is 18.",
            proposed_state="Minimum age is 21.",
        )
    )


def test_change_service_updates_change(db):
    change = create_change(db)

    service = ChangeService(db)

    updated = service.update_change(
        change.id,
        ChangeUpdate(
            title="Updated title",
            proposed_state="Minimum age is 25.",
        ),
    )

    assert updated is not None
    assert updated.id == change.id
    assert updated.change_id == "CHG-UPDATE-SERVICE-001"
    assert updated.title == "Updated title"
    assert updated.proposed_state == "Minimum age is 25."
    assert updated.description == "Original description."


def test_change_service_returns_none_for_missing_change(db):
    service = ChangeService(db)

    result = service.update_change(
        99999,
        ChangeUpdate(
            title="Updated title",
        ),
    )

    assert result is None


def test_change_service_preserves_external_change_id(db):
    change = create_change(db)

    service = ChangeService(db)

    updated = service.update_change(
        change.id,
        ChangeUpdate(
            title="Updated title",
        ),
    )

    assert updated is not None
    assert updated.change_id == "CHG-UPDATE-SERVICE-001"


def test_change_service_supports_single_field_update(db):
    change = create_change(db)

    service = ChangeService(db)

    updated = service.update_change(
        change.id,
        ChangeUpdate(
            affected_domain="business",
        ),
    )

    assert updated is not None
    assert updated.affected_domain == "business"
    assert updated.title == "Original title"


def test_change_service_does_not_commit_update(db):
    change = create_change(db)

    db.commit()

    service = ChangeService(db)

    service.update_change(
        change.id,
        ChangeUpdate(title="Uncommitted title"),
    )

    db.rollback()

    result = service.get_change(change.id)

    assert result is not None
    assert result.title == "Original title"