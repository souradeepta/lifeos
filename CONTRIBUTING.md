# Contributing to LifeOS

This is a personal project, but contributions are welcome. This document explains the architecture, conventions, and development workflow.

---

## Architecture Overview

LifeOS follows a strict layered architecture:

```
HTTP Request
    └── Router (app/routers/)       ← parse form/query params only
            └── Service (app/services/)  ← all business logic
                    └── SQLAlchemy ORM (app/models/)
                            └── SQLite (db/lifeos.db)
```

**Rules:**
- Routers must never contain business logic — only parse input, call services, return responses
- Services must never return HTTP responses or raise HTTP exceptions
- All DB access goes through async SQLAlchemy sessions injected via `Depends(get_db)`
- Every function must have type hints
- Never use `print()` — use `structlog`

---

## Data Model

```
Domain (6 fixed types: WORK | STUDY | INTERVIEW | PERSONAL_DEV | HOBBIES | WORKOUTS)
  └── Goal (many per domain, can be active/inactive)
        └── Plan (date-scoped, one or more per goal per day)
              └── Task (ordered, with status: TODO | IN_PROGRESS | DONE | SKIPPED)
                    └── Subtask (simple checkbox items)
```

---

## Setup

```bash
git clone https://github.com/souradeepta/lifeos.git
cd lifeos
python -m venv myenv
source myenv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Coding Conventions

### Python

- Python 3.11+ required
- Type hints on every function signature
- Pydantic v2 schemas for all API I/O (`model_config = ConfigDict(from_attributes=True)`)
- Use `pathlib.Path` instead of string paths
- UTC timestamps everywhere (`datetime.now(timezone.utc)`)
- `structlog` for logging — configure once in `main.py`

```python
# Good
async def get_plan(db: AsyncSession, plan_id: int) -> Plan | None:
    ...

# Bad — missing types
async def get_plan(db, plan_id):
    ...
```

### Database

- Always create an Alembic migration after changing a model:
  ```bash
  alembic revision --autogenerate -m "describe the change"
  alembic upgrade head
  ```
- Use `selectinload()` for related entities — never lazy loading
- Use `expire_on_commit=False` on session factory (already configured)

### Frontend

- No JavaScript frameworks — HTMX only
- All dynamic updates use `hx-target` + `hx-swap="innerHTML"` targeting specific `id` containers
- Partial templates live in `app/templates/partials/`
- Icons are Lucide via CDN static font (`class="lucide lucide-{name}"`)
- CSS variables only — never hardcode colors

---

## Adding a New Feature

### Example: Adding "Notes" to a Goal

**1. Add the model field**
```python
# app/models/goal.py
notes: Mapped[str | None] = mapped_column(Text, nullable=True)
```

**2. Create migration**
```bash
alembic revision --autogenerate -m "add notes to goals"
alembic upgrade head
```

**3. Update schemas**
```python
# app/schemas/goal.py
class GoalCreate(BaseModel):
    ...
    notes: str | None = None

class GoalUpdate(BaseModel):
    ...
    notes: str | None = None
```

**4. Update service** — `goal_service.py` should handle it automatically via `model_dump(exclude_unset=True)`

**5. Update template** — Add the field to the goal form in `domain_detail.html` and display in `partials/goal_list.html`

---

## Testing

Tests use in-memory SQLite — never touch the real DB.

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run only unit tests
pytest tests/unit/ -v
```

### Test structure

```
tests/
├── unit/
│   ├── test_services.py     # Service layer tests (mocked DB)
│   └── test_schemas.py      # Pydantic schema validation tests
└── integration/
    ├── test_pages.py         # Page routes return 200
    └── test_api.py           # CRUD API full lifecycle tests
```

### Example test

```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app, lifespan

@pytest.fixture
async def client():
    async with lifespan(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c

@pytest.mark.asyncio
async def test_dashboard_loads(client):
    r = await client.get("/")
    assert r.status_code == 200
```

---

## Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short description>

[optional body]
```

| Type | Use for |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code change that isn't a fix or feature |
| `docs` | Documentation only |
| `test` | Adding or updating tests |
| `chore` | Build, config, dependency updates |
| `style` | Formatting, CSS changes |

**Examples:**
```
feat(tasks): add priority levels (normal/high/urgent)
fix(api): prevent null is_active on goal update
docs(api): add full endpoint reference with examples
chore: add alembic initial migration
```

---

## Pull Request Checklist

- [ ] Type hints on all new functions
- [ ] No `print()` statements — use `structlog`
- [ ] Alembic migration created for any model changes
- [ ] Tests added for new service/router behavior
- [ ] No hardcoded strings, colors, or paths
- [ ] `pytest tests/ -v` passes locally
