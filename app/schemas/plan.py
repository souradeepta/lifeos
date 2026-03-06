from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class PlanCreate(BaseModel):
    goal_id: int
    title: str
    description: str | None = None
    plan_date: date


class PlanUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    plan_date: date | None = None


class PlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    goal_id: int
    title: str
    description: str | None
    plan_date: date
    created_at: datetime
