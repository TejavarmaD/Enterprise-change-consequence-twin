from sqlalchemy import inspect

from backend.app.core.database import engine
from backend.app.models import Base


def test_orm_matches_database_schema():
    orm_tables = set(Base.metadata.tables.keys())
    database_tables = set(inspect(engine).get_table_names()) - {"alembic_version"}

    assert orm_tables == database_tables