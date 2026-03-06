from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.task import TaskStatus


class SubtaskCreate(BaseModel):
    title: str


class SubtaskUpdate(BaseModel):
    title: str | None = None
    is_done: bool | None = None


class SubtaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    title: str
    is_done: bool
    sort_order: int
    created_at: datetime


class TaskCreate(BaseModel):
    plan_id: int
    title: str
    description: str | None = None
    priority: int = 0


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: int | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    plan_id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: int
    sort_order: int
    created_at: datetime
    updated_at: datetime
    subtasks: list[SubtaskRead] = []
