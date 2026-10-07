from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models import Base


if TYPE_CHECKING:
    from backend.app.models.change import Change


class ConsequenceAssessment(Base):
    __tablename__ = "consequence_assessments"

    id: Mapped[int] = mapped_column(primary_key=True)

    change_id: Mapped[int] = mapped_column(
        ForeignKey("changes.id"),
        nullable=False,
    )

    consequence_category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    consequence_type: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    evidence_classification: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    probability: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    impact: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    risk_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    evidence: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    unknowns: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    recommended_test: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    approval_required: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    change: Mapped["Change"] = relationship(
        back_populates="consequence_assessments",
    )