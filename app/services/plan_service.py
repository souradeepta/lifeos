import structlog
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.plan import Plan
from app.models.task import Task, Subtask
from app.schemas.plan import PlanCreate, PlanUpdate

log = structlog.get_logger()


async def list_plans(db: AsyncSession, goal_id: int | None = None, plan_date: date | None = None) -> list[Plan]:
    stmt = select(Plan).options(
        selectinload(Plan.tasks).selectinload(Task.subtasks)
    ).order_by(Plan.plan_date.desc())
    if goal_id is not None:
        stmt = stmt.where(Plan.goal_id == goal_id)
    if plan_date is not None:
        stmt = stmt.where(Plan.plan_date == plan_date)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def list_plans_in_range(db: AsyncSession, start_date: date, end_date: date) -> list[Plan]:
    stmt = (
        select(Plan)
        .options(selectinload(Plan.tasks).selectinload(Task.subtasks))
        .where(Plan.plan_date >= start_date, Plan.plan_date <= end_date)
        .order_by(Plan.plan_date.asc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_plan(db: AsyncSession, plan_id: int) -> Plan | None:
    result = await db.execute(
        select(Plan).options(
            selectinload(Plan.tasks).selectinload(Task.subtasks)
        ).where(Plan.id == plan_id)
    )
    return result.scalar_one_or_none()


async def create_plan(db: AsyncSession, data: PlanCreate) -> Plan:
    plan = Plan(**data.model_dump())
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    log.info("plan_created", title=data.title, date=str(data.plan_date))
    return plan


async def update_plan(db: AsyncSession, plan_id: int, data: PlanUpdate) -> Plan | None:
    plan = await get_plan(db, plan_id)
    if not plan:
        return None
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(plan, key, val)
    await db.commit()
    await db.refresh(plan)
    return plan


async def delete_plan(db: AsyncSession, plan_id: int) -> bool:
    plan = await get_plan(db, plan_id)
    if not plan:
        return False
    await db.delete(plan)
    await db.commit()
    log.info("plan_deleted", plan_id=plan_id)
    return True
