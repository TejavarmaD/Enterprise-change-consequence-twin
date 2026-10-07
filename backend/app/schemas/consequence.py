from pydantic import BaseModel, Field


class ConsequenceCreate(BaseModel):
    consequence_category: str = Field(min_length=1, max_length=100)
    consequence_type: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1)

    evidence_classification: str = Field(
        min_length=1,
        max_length=50,
    )

    probability: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    impact: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    risk_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    evidence: str | None = None
    unknowns: str | None = None
    recommended_test: str | None = None
    approval_required: bool = False