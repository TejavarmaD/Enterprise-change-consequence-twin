from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models import Base


if TYPE_CHECKING:
    from backend.app.models.consequence_assessment import ConsequenceAssessment


class Change(Base):
    __tablename__ = "changes"

    id: Mapped[int] = mapped_column(primary_key=True)

    change_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    change_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    target_entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    target_entity_id: Mapped[int] = mapped_column(
        nullable=False,
    )

    current_state: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    proposed_state: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    affected_domain: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    requester: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    business_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    expected_effect: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    constraints: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    uncertainty: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    consequence_assessments: Mapped[list["ConsequenceAssessment"]] = relationship(
        back_populates="change",
        cascade="all, delete-orphan",
    )