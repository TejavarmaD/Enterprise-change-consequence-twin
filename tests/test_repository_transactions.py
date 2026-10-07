import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.models import Base
from backend.app.models.change import Change
from backend.app.repositories.change_repository import ChangeRepository


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
    return Change(
        change_id=change_id,
        change_type="api",
        title="Update API",
        description="Update API contract.",
        target_entity_type="api",
        target_entity_id=1,
    )


def test_repository_create_does_not_commit(db):
    repository = ChangeRepository(db)

    repository.create(
        build_change("CHG-REPOSITORY-TX-001")
    )

    db.rollback()

    result = db.scalar(
        select(Change).where(
            Change.change_id == "CHG-REPOSITORY-TX-001"
        )
    )

    assert result is None


def test_repository_create_is_visible_before_commit(db):
    repository = ChangeRepository(db)

    change = repository.create(
        build_change("CHG-REPOSITORY-TX-002")
    )

    result = db.scalar(
        select(Change).where(
            Change.change_id == "CHG-REPOSITORY-TX-002"
        )
    )

    assert result is not None
    assert result.id == change.id


def test_repository_create_persists_after_explicit_commit(db):
    repository = ChangeRepository(db)

    change = repository.create(
        build_change("CHG-REPOSITORY-TX-003")
    )

    db.commit()

    result = db.scalar(
        select(Change).where(
            Change.change_id == "CHG-REPOSITORY-TX-003"
        )
    )

    assert result is not None
    assert result.id == change.id