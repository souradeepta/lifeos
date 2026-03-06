import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.domain import Domain, DomainType
from app.schemas.domain import DomainCreate, DomainUpdate

log = structlog.get_logger()

DEFAULT_DOMAINS = [
    {"name": "Work", "domain_type": DomainType.WORK, "color": "#3b82f6", "description": "Day job tasks and projects"},
    {"name": "Study", "domain_type": DomainType.STUDY, "color": "#8b5cf6", "description": "Learning and courses"},
    {"name": "Interview Prep", "domain_type": DomainType.INTERVIEW, "color": "#f59e0b", "description": "Interview preparation"},
    {"name": "Personal Dev", "domain_type": DomainType.PERSONAL_DEV, "color": "#10b981", "description": "Personal development"},
    {"name": "Hobbies", "domain_type": DomainType.HOBBIES, "color": "#ec4899", "description": "Fun and creative pursuits"},
    {"name": "Workouts", "domain_type": DomainType.WORKOUTS, "color": "#ef4444", "description": "Exercise and fitness"},
]


async def seed_domains(db: AsyncSession) -> None:
    result = await db.execute(select(Domain))
    if result.scalars().first() is not None:
        return
    for d in DEFAULT_DOMAINS:
        db.add(Domain(**d))
    await db.commit()
    log.info("seeded_default_domains")


async def list_domains(db: AsyncSession) -> list[Domain]:
    result = await db.execute(
        select(Domain).options(selectinload(Domain.goals)).order_by(Domain.id)
    )
    return list(result.scalars().all())


async def get_domain(db: AsyncSession, domain_id: int) -> Domain | None:
    result = await db.execute(
        select(Domain).options(selectinload(Domain.goals)).where(Domain.id == domain_id)
    )
    return result.scalar_one_or_none()


async def create_domain(db: AsyncSession, data: DomainCreate) -> Domain:
    domain = Domain(**data.model_dump())
    db.add(domain)
    await db.commit()
    await db.refresh(domain)
    log.info("domain_created", domain_type=data.domain_type)
    return domain


async def update_domain(db: AsyncSession, domain_id: int, data: DomainUpdate) -> Domain | None:
    domain = await get_domain(db, domain_id)
    if not domain:
        return None
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(domain, key, val)
    await db.commit()
    await db.refresh(domain)
    return domain
