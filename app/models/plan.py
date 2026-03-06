from datetime import date, datetime, timezone
from sqlalchemy import Integer, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    goal_id: Mapped[int] = mapped_column(ForeignKey("goals.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    plan_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    goal: Mapped["Goal"] = relationship(back_populates="plans")  # noqa: F821
    tasks: Mapped[list["Task"]] = relationship(back_populates="plan", cascade="all, delete-orphan")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Plan {self.title!r} ({self.plan_date})>"
