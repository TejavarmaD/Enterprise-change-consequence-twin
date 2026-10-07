from pydantic import BaseModel, ConfigDict


class ConsequenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    change_id: int

    consequence_category: str
    consequence_type: str
    description: str

    evidence_classification: str

    probability: float | None = None
    impact: float | None = None
    risk_score: float | None = None
    confidence: float | None = None

    evidence: str | None = None
    unknowns: str | None = None
    recommended_test: str | None = None

    approval_required: bool