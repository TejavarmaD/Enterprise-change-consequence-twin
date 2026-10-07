from pydantic import BaseModel, ConfigDict


class ChangeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    change_id: str
    change_type: str
    title: str
    description: str

    target_entity_type: str
    target_entity_id: int

    current_state: str | None = None
    proposed_state: str | None = None
    affected_domain: str | None = None

    requester: str | None = None
    business_reason: str | None = None
    expected_effect: str | None = None
    constraints: str | None = None
    uncertainty: str | None = None