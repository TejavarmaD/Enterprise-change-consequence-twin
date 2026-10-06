from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.models import Base


class System(Base):
    __tablename__ = "systems"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)