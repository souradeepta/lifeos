from datetime import datetime
from pydantic import BaseModel, ConfigDict


class GoalCreate(BaseModel):
    domain_id: int
    title: str
    description: str | None = None


class GoalUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_active: bool | None = None


class GoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    domain_id: int
    title: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
