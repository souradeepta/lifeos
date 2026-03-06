import enum
from datetime import datetime, timezone
from sqlalchemy import Integer, String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class DomainType(str, enum.Enum):
    WORK = "WORK"
    STUDY = "STUDY"
    INTERVIEW = "INTERVIEW"
    PERSONAL_DEV = "PERSONAL_DEV"
    HOBBIES = "HOBBIES"
    WORKOUTS = "WORKOUTS"


class Domain(Base):
    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    domain_type: Mapped[DomainType] = mapped_column(Enum(DomainType), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    color: Mapped[str] = mapped_column(String(7), default="#6366f1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    goals: Mapped[list["Goal"]] = relationship(back_populates="domain", cascade="all, delete-orphan")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Domain {self.domain_type.value}>"
