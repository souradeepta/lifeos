import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task import Task, Subtask, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, SubtaskCreate, SubtaskUpdate

log = structlog.get_logger()


async def list_tasks(db: AsyncSession, plan_id: int) -> list[Task]:
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.subtasks))
        .where(Task.plan_id == plan_id)
        .order_by(Task.sort_order, Task.created_at)
    )
    return list(result.scalars().all())


async def get_task(db: AsyncSession, task_id: int) -> Task | None:
    result = await db.execute(
        select(Task).options(selectinload(Task.subtasks)).where(Task.id == task_id)
    )
    return result.scalar_one_or_none()


async def create_task(db: AsyncSession, data: TaskCreate) -> Task:
    task = Task(**data.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    log.info("task_created", title=data.title, plan_id=data.plan_id)
    return task


async def update_task(db: AsyncSession, task_id: int, data: TaskUpdate) -> Task | None:
    task = await get_task(db, task_id)
    if not task:
        return None
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(task, key, val)
    await db.commit()
    await db.refresh(task)
    log.info("task_updated", task_id=task_id, status=task.status)
    return task


async def delete_task(db: AsyncSession, task_id: int) -> bool:
    task = await get_task(db, task_id)
    if not task:
        return False
    await db.delete(task)
    await db.commit()
    log.info("task_deleted", task_id=task_id)
    return True


# --- Subtasks ---

async def create_subtask(db: AsyncSession, task_id: int, data: SubtaskCreate) -> Subtask | None:
    task = await get_task(db, task_id)
    if not task:
        return None
    subtask = Subtask(task_id=task_id, **data.model_dump())
    db.add(subtask)
    await db.commit()
    await db.refresh(subtask)
    log.info("subtask_created", title=data.title, task_id=task_id)
    return subtask


async def update_subtask(db: AsyncSession, subtask_id: int, data: SubtaskUpdate) -> Subtask | None:
    result = await db.execute(select(Subtask).where(Subtask.id == subtask_id))
    subtask = result.scalar_one_or_none()
    if not subtask:
        return None
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(subtask, key, val)
    await db.commit()
    await db.refresh(subtask)
    return subtask


async def delete_subtask(db: AsyncSession, subtask_id: int) -> bool:
    result = await db.execute(select(Subtask).where(Subtask.id == subtask_id))
    subtask = result.scalar_one_or_none()
    if not subtask:
        return False
    await db.delete(subtask)
    await db.commit()
    log.info("subtask_deleted", subtask_id=subtask_id)
    return True
