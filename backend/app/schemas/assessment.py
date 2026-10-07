from pydantic import BaseModel, Field


class AssessmentCreate(BaseModel):
    change_id: int = Field(gt=0)

    consequences: list[int] = Field(
        min_length=1,
    )