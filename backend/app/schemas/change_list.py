from pydantic import BaseModel, Field

from backend.app.schemas.change_response import ChangeResponse


class ChangeListResponse(BaseModel):
    items: list[ChangeResponse]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)