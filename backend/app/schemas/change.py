from pydantic import BaseModel, Field


class ChangeCreate(BaseModel):
    change_id: str = Field(min_length=1, max_length=100)
    change_type: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)

    target_entity_type: str = Field(min_length=1, max_length=100)
    target_entity_id: int = Field(gt=0)

    current_state: str | None = None
    proposed_state: str | None = None
    affected_domain: str | None = Field(default=None, max_length=100)

    requester: str | None = Field(default=None, max_length=255)
    business_reason: str | None = None
    expected_effect: str | None = None
    constraints: str | None = None
    uncertainty: str | None = None