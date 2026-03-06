import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.goal import Goal
from app.schemas.goal import GoalCreate, GoalUpdate

log = structlog.get_logger()


async def list_goals(db: AsyncSession, domain_id: int | None = None) -> list[Goal]:
    stmt = select(Goal).options(selectinload(Goal.plans)).order_by(Goal.created_at.desc())
    if domain_id is not None:
        stmt = stmt.where(Goal.domain_id == domain_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_goal(db: AsyncSession, goal_id: int) -> Goal | None:
    result = await db.execute(
        select(Goal).options(selectinload(Goal.plans)).where(Goal.id == goal_id)
    )
    return result.scalar_one_or_none()


async def create_goal(db: AsyncSession, data: GoalCreate) -> Goal:
    goal = Goal(**data.model_dump())
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    log.info("goal_created", title=data.title, domain_id=data.domain_id)
    return goal


async def update_goal(db: AsyncSession, goal_id: int, data: GoalUpdate) -> Goal | None:
    goal = await get_goal(db, goal_id)
    if not goal:
        return None
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(goal, key, val)
    await db.commit()
    await db.refresh(goal)
    return goal


async def delete_goal(db: AsyncSession, goal_id: int) -> bool:
    goal = await get_goal(db, goal_id)
    if not goal:
        return False
    await db.delete(goal)
    await db.commit()
    log.info("goal_deleted", goal_id=goal_id)
    return True
