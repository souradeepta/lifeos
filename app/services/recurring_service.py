"""Business logic for recurring plans: creation, toggling, deletion, and materialization."""
from datetime import date, datetime, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.plan import Plan
from app.models.task import Task
from app.models.recurring import RecurringPlan, RecurringTask, RecurrenceType
from app.schemas.recurring import RecurringPlanCreate, RecurringPlanUpdate

log = structlog.get_logger()


async def create_recurring_plan(
    db: AsyncSession, data: RecurringPlanCreate
) -> RecurringPlan:
    plan = RecurringPlan(
        goal_id=data.goal_id,
        title=data.title,
        description=data.description,
        recurrence_type=data.recurrence_type,
        is_active=True,
    )
    db.add(plan)
    await db.flush()  # get plan.id

    for t in data.tasks:
        db.add(RecurringTask(recurring_plan_id=plan.id, title=t.title, priority=t.priority))

    await db.commit()
    await db.refresh(plan)
    log.info("recurring_plan_created", id=plan.id, title=plan.title)
    return plan


async def list_recurring_plans(db: AsyncSession, goal_id: int) -> list[RecurringPlan]:
    result = await db.execute(
        select(RecurringPlan)
        .where(RecurringPlan.goal_id == goal_id)
        .options(selectinload(RecurringPlan.recurring_tasks))
        .order_by(RecurringPlan.created_at)
    )
    return list(result.scalars().all())


async def get_recurring_plan(db: AsyncSession, rp_id: int) -> RecurringPlan | None:
    result = await db.execute(
        select(RecurringPlan)
        .where(RecurringPlan.id == rp_id)
        .options(selectinload(RecurringPlan.recurring_tasks))
    )
    return result.scalar_one_or_none()


async def update_recurring_plan(
    db: AsyncSession, rp_id: int, data: RecurringPlanUpdate
) -> RecurringPlan | None:
    rp = await get_recurring_plan(db, rp_id)
    if not rp:
        return None
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(rp, field, value)
    await db.commit()
    await db.refresh(rp)
    return rp


async def delete_recurring_plan(db: AsyncSession, rp_id: int) -> bool:
    rp = await get_recurring_plan(db, rp_id)
    if not rp:
        return False
    await db.delete(rp)
    await db.commit()
    log.info("recurring_plan_deleted", id=rp_id)
    return True


def _should_run_today(recurrence_type: RecurrenceType, target_date: date) -> bool:
    """Return True if a recurring plan with this type should produce a plan on target_date."""
    if recurrence_type == RecurrenceType.DAILY:
        return True
    if recurrence_type == RecurrenceType.WEEKDAYS:
        return target_date.weekday() < 5  # Mon=0 … Fri=4
    if recurrence_type == RecurrenceType.WEEKLY:
        return target_date.weekday() == 0  # Mondays only
    return False


async def materialize_for_date(db: AsyncSession, target_date: date) -> None:
    """Idempotently create Plan+Tasks for all active recurring plans on target_date."""
    result = await db.execute(
        select(RecurringPlan)
        .where(RecurringPlan.is_active == True)  # noqa: E712
        .options(selectinload(RecurringPlan.recurring_tasks))
    )
    recurring_plans = list(result.scalars().all())

    for rp in recurring_plans:
        if not _should_run_today(rp.recurrence_type, target_date):
            continue

        # Idempotency check — skip if already materialized for this date
        existing = await db.execute(
            select(Plan).where(
                Plan.recurring_plan_id == rp.id,
                Plan.plan_date == target_date,
            )
        )
        if existing.scalar_one_or_none():
            continue

        plan = Plan(
            goal_id=rp.goal_id,
            title=rp.title,
            description=rp.description,
            plan_date=target_date,
            recurring_plan_id=rp.id,
        )
        db.add(plan)
        await db.flush()

        for rt in rp.recurring_tasks:
            db.add(Task(
                plan_id=plan.id,
                title=rt.title,
                priority=rt.priority,
            ))

        log.info("recurring_plan_materialized", rp_id=rp.id, date=str(target_date))

    await db.commit()
