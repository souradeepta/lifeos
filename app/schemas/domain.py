from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.domain import DomainType


class DomainCreate(BaseModel):
    name: str
    domain_type: DomainType
    description: str | None = None
    color: str = "#6366f1"


class DomainUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None


class DomainRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    domain_type: DomainType
    description: str | None
    color: str
    created_at: datetime
