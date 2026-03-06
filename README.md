# LifeOS

A personal life management app for focused, distraction-free planning. Runs on your local network — no cloud, no subscriptions, no data leaving your home.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![SQLite](https://img.shields.io/badge/SQLite-local-orange)
![HTMX](https://img.shields.io/badge/HTMX-2.0-purple)

---

## What it does

LifeOS helps you organize your life across six domains, break goals into day-scoped plans, and track tasks down to subtasks — all in a clean, fast, dark-themed UI accessible from any device on your home network.

```
Domain → Goal → Plan (day-scoped) → Task → Subtask
```

### Life Domains

| Domain | Purpose |
|--------|---------|
| Work | Day job tasks, projects, meetings |
| Study | Courses, books, skills to learn |
| Interview Prep | Job hunt, coding practice, mock interviews |
| Personal Dev | Habits, side projects, self-improvement |
| Hobbies | Creative pursuits, gaming, reading |
| Workouts | Exercise plans, fitness tracking |

---

## Quick Start

### Prerequisites
- Python 3.11+
- pip

### 1. Clone and install

```bash
git clone https://github.com/souradeepta/lifeos.git
cd lifeos
python -m venv myenv
source myenv/bin/activate        # Windows: myenv\Scripts\activate
pip install -e ".[dev]"
```

### 2. Run database migrations

```bash
alembic upgrade head
```

### 3. Start the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://localhost:8000` in your browser. On your local network, use your machine's IP instead of `localhost` (e.g. `http://192.168.1.10:8000`).

> The app seeds six default domains automatically on first run.

---

## Features

- **Dashboard** — Overview of all domains + today's plans + 7-day upcoming preview
- **Today view** — Single-page focus on what to do right now, with one-click task completion
- **Upcoming view** — Next 30 days of plans grouped by date
- **Inline editing** — Edit goals, plans, and tasks in-place without page reloads
- **Task breakdown** — Tasks with subtask checklists, priority levels (Normal / High / Urgent)
- **Progress tracking** — Per-plan progress bars showing tasks completed
- **HTMX-powered** — All interactions update in-place, no page reloads, no JS framework
- **Responsive** — Works on mobile, tablet, and desktop

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, SQLAlchemy (async) |
| Database | SQLite via aiosqlite |
| Migrations | Alembic |
| Frontend | Jinja2 templates + HTMX |
| Styling | Custom CSS (dark theme, no framework) |
| Icons | Lucide (static font) |
| Logging | structlog |

---

## Project Structure

```
lifeos/
├── app/
│   ├── main.py              # FastAPI app entry point, lifespan, seeding
│   ├── database.py          # Async engine, session factory, Base
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── domain.py        # Domain + DomainType enum
│   │   ├── goal.py          # Goal model
│   │   ├── plan.py          # Plan model (date-scoped)
│   │   └── task.py          # Task + Subtask models
│   ├── schemas/             # Pydantic v2 request/response schemas
│   ├── services/            # Business logic (no DB logic in routers)
│   ├── routers/
│   │   ├── pages.py         # HTML page routes
│   │   └── api.py           # HTMX API routes (form posts, partials)
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── base.html        # Sidebar layout
│   │   ├── dashboard.html
│   │   ├── today.html
│   │   ├── upcoming.html
│   │   ├── domain_detail.html
│   │   ├── goal_detail.html
│   │   ├── plan_detail.html
│   │   └── partials/        # HTMX swap targets
│   └── static/
│       └── style.css
├── db/
│   └── migrations/          # Alembic migration scripts
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
│   ├── API.md               # Full API reference
│   ├── SECURITY.md          # Security model and hardening guide
│   └── USER_GUIDE.md        # End-user guide
├── pyproject.toml
├── alembic.ini
└── README.md
```

---

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full developer workflow.

```bash
# Run tests
pytest tests/ -v

# Format code
black app/ tests/

# Type check
mypy app/
```

---

## Documentation

- [User Guide](docs/USER_GUIDE.md) — How to use LifeOS day-to-day
- [API Reference](docs/API.md) — All endpoints, request/response formats
- [Security Guide](docs/SECURITY.md) — Security model, network hardening, recommendations
- [Contributing](CONTRIBUTING.md) — Dev setup, architecture decisions, conventions

---

## License

MIT License — personal use encouraged. See [LICENSE](LICENSE).
