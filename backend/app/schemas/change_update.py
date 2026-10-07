from pydantic import BaseModel, ConfigDict, Field, model_validator


class ChangeUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    change_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        min_length=1,
    )

    target_entity_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    target_entity_id: int | None = Field(
        default=None,
        gt=0,
    )

    current_state: str | None = None
    proposed_state: str | None = None

    affected_domain: str | None = Field(
        default=None,
        max_length=100,
    )

    requester: str | None = Field(
        default=None,
        max_length=255,
    )

    business_reason: str | None = None
    expected_effect: str | None = None
    constraints: str | None = None
    uncertainty: str | None = None

    @model_validator(mode="after")
    def validate_at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError(
                "At least one field must be provided for an update."
            )

        for field_name in self.model_fields_set:
            if getattr(self, field_name) is None:
                raise ValueError(
                    f"Field '{field_name}' cannot be null."
                )

        return self