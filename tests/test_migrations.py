from alembic import command
from alembic.config import Config


def test_alembic_current_is_head():
    config = Config("alembic.ini")
    command.check(config)