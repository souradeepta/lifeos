# LifeOS — Personal Life Management App

## What this is

Local-network personal productivity app. Single user, no auth needed.
SQLite at db/lifeos.db. Runs on 0.0.0.0:8000 for local WiFi access.

## Stack

- Python 3.11+, FastAPI, SQLAlchemy async + aiosqlite
- Alembic for migrations (always create migration after model changes)
- Jinja2 + HTMX frontend (no JS build step, no npm)
- structlog for all logging — never use print()

## Life Domains (enum: DomainType)

WORK | STUDY | INTERVIEW | PERSONAL_DEV | HOBBIES | WORKOUTS

## Data hierarchy

Domain → Goal → Plan (date-scoped) → Task → Subtask

## Coding rules

- Type hints on every function
- Pydantic v2 schemas for all API I/O
- Business logic in services/ only — routers call services
- All DB via async SQLAlchemy sessions using Depends()
- Use pathlib.Path, never hardcoded string paths
- UTC timestamps everywhere

## Sub-Agent Routing Rules

**Parallel:** 3+ unrelated tasks, no shared files, independent domains
**Sequential:** Task B needs output from Task A, shared state, unclear scope
**Use agents for:** db schema work, test writing, frontend templates, code review

## Running

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

## Testing

pytest tests/ -v — use in-memory SQLite for all tests

```

---

## Part 3: Understanding Agents — The Real Education

### What an Agent Actually Is

Subagents are specialized AI assistants that handle specific types of tasks. Each subagent runs in its own context window with a custom system prompt, specific tool access, and independent permissions. When Claude encounters a task matching a subagent's description, it delegates to that subagent, which works independently and returns results.

Think of it this way — without agents, you have one Claude juggling everything in one conversation. Context fills up fast. With agents:
```

You (main session)
├── delegates to → db-architect agent (designs schema)
├── delegates to → test-writer agent (writes pytest tests)
└── delegates to → code-reviewer agent (reviews before commit)
