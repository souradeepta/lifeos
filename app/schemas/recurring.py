from pydantic import BaseModel
from app.models.recurring import RecurrenceType


class RecurringTaskCreate(BaseModel):
    title: str
    priority: int = 0


class RecurringPlanCreate(BaseModel):
    goal_id: int
    title: str
    description: str | None = None
    recurrence_type: RecurrenceType
    tasks: list[RecurringTaskCreate] = []


class RecurringPlanUpdate(BaseModel):
    is_active: bool | None = None
    title: str | None = None
    description: str | None = None
