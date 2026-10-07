from pydantic import BaseModel, Field

from backend.app.schemas.consequence_response import ConsequenceResponse


class ConsequenceListResponse(BaseModel):
    items: list[ConsequenceResponse]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)