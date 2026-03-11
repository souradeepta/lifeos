import enum
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, ForeignKey, DateTime, Enum as SAEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class RecurrenceType(str, enum.Enum):
    DAILY = "DAILY"
    WEEKDAYS = "WEEKDAYS"
    WEEKLY = "WEEKLY"


class RecurringPlan(Base):
    __tablename__ = "recurring_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    goal_id: Mapped[int] = mapped_column(ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    recurrence_type: Mapped[RecurrenceType] = mapped_column(SAEnum(RecurrenceType), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    goal: Mapped["Goal"] = relationship(back_populates="recurring_plans")  # noqa: F821
    recurring_tasks: Mapped[list["RecurringTask"]] = relationship(
        back_populates="recurring_plan", cascade="all, delete-orphan"
    )
    materialized_plans: Mapped[list["Plan"]] = relationship(  # noqa: F821
        back_populates="recurring_plan", foreign_keys="Plan.recurring_plan_id"
    )

    def __repr__(self) -> str:
        return f"<RecurringPlan {self.title!r} ({self.recurrence_type})>"


class RecurringTask(Base):
    __tablename__ = "recurring_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recurring_plan_id: Mapped[int] = mapped_column(
        ForeignKey("recurring_plans.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    recurring_plan: Mapped["RecurringPlan"] = relationship(back_populates="recurring_tasks")

    def __repr__(self) -> str:
        return f"<RecurringTask {self.title!r}>"
