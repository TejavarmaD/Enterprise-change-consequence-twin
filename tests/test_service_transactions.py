import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models import Base
from backend.app.models.change import Change
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


def build_change(change_id):
    return ChangeCreate(
        change_id=change_id,
        change_type="business_rule",
        title="Update eligibility",
        description="Increase the minimum eligible age.",
        target_entity_type="business_rule",
        target_entity_id=1,
    )


def test_service_create_does_not_commit_transaction(db):
    service = ChangeService(db)

    change = service.create_change(
        build_change("CHG-TRANSACTION-001")
    )

    assert change.id is not None

    db.rollback()

    result = db.scalar(
        select(Change).where(
            Change.change_id == "CHG-TRANSACTION-001"
        )
    )

    assert result is None


def test_service_create_is_persisted_after_explicit_commit(db):
    service = ChangeService(db)

    change = service.create_change(
        build_change("CHG-TRANSACTION-002")
    )

    db.commit()

    result = db.scalar(
        select(Change).where(
            Change.change_id == "CHG-TRANSACTION-002"
        )
    )

    assert result is not None
    assert result.id == change.id