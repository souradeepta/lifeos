from datetime import datetime, timezone
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    domain: Mapped["Domain"] = relationship(back_populates="goals")  # noqa: F821
    plans: Mapped[list["Plan"]] = relationship(back_populates="goal", cascade="all, delete-orphan")  # noqa: F821
    recurring_plans: Mapped[list["RecurringPlan"]] = relationship(back_populates="goal", cascade="all, delete-orphan")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Goal {self.title!r}>"
