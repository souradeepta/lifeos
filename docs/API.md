# LifeOS API Reference

All API routes are served by FastAPI. The app exposes two router groups:
- **Page routes** (`/`, `/today`, etc.) — return full HTML pages (Jinja2)
- **API routes** (`/api/*`) — return HTML partials for HTMX in-place swaps

> **Note:** This app uses HTML-over-the-wire (HTMX), not JSON. All `/api/*` endpoints accept `application/x-www-form-urlencoded` and return HTML fragments, not JSON. This is intentional — it keeps the stack simple and eliminates a separate API client.

---

## Base URL

```
http://<your-local-ip>:8000
```

For local development: `http://localhost:8000`

---

## Authentication

**None.** LifeOS is a single-user local network app. It is designed to run behind your home router's NAT — never exposed to the public internet. See [SECURITY.md](SECURITY.md) for network hardening recommendations.

---

## Data Hierarchy

```
Domain → Goal → Plan → Task → Subtask
```

All IDs are auto-incrementing integers.

---

## Page Routes

These routes return full HTML pages.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Dashboard (domain cards, today's plans, upcoming) |
| GET | `/today` | Today's view — all plans for today with task checkboxes |
| GET | `/upcoming` | Plans for the next 30 days grouped by date |
| GET | `/domains/{id}` | Domain detail — list of goals for that domain |
| GET | `/goals/{id}` | Goal detail — list of plans for that goal |
| GET | `/plans/{id}` | Plan detail — task list with subtask expansion |

---

## API Routes

All routes are prefixed with `/api`. Requests use `Content-Type: application/x-www-form-urlencoded`.

---

### Goals

#### Create Goal

```
POST /api/goals
```

**Form fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `domain_id` | integer | Yes | ID of the parent domain |
| `title` | string | Yes | Goal title (max 200 chars) |
| `description` | string | No | Optional description |

**Returns:** HTML partial — updated goal list for that domain

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/goals \
  -d "domain_id=1&title=Learn+System+Design&description=Complete+the+Grokking+course"
```

---

#### Update Goal

```
PUT /api/goals/{goal_id}
```

**Form fields:** (all optional — only provided fields are updated)

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | New title |
| `description` | string | New description |
| `is_active` | string | `"true"` or `"false"` |

**Returns:** HTML partial — updated goal list

---

#### Delete Goal

```
DELETE /api/goals/{goal_id}
```

Cascades to all child Plans, Tasks, and Subtasks.

**Returns:** HTML partial — updated goal list (goal removed)

---

### Plans

#### Create Plan

```
POST /api/plans
```

**Form fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `goal_id` | integer | Yes | ID of the parent goal |
| `title` | string | Yes | Plan title |
| `plan_date` | string | Yes | ISO date: `YYYY-MM-DD` |
| `description` | string | No | Optional notes |

**Returns:** HTML partial — updated plan list for that goal

**Example:**
```bash
curl -X POST http://localhost:8000/api/plans \
  -d "goal_id=1&title=Morning+Study+Session&plan_date=2026-03-07"
```

---

#### Update Plan

```
PUT /api/plans/{plan_id}
```

**Form fields:** (all optional)

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | New title |
| `plan_date` | string | New date `YYYY-MM-DD` |
| `description` | string | New description |

**Returns:** HTML partial — updated plan list

---

#### Delete Plan

```
DELETE /api/plans/{plan_id}
```

Cascades to all child Tasks and Subtasks.

**Returns:** HTML partial — updated plan list (plan removed)

---

### Tasks

#### Create Task

```
POST /api/tasks
```

**Form fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plan_id` | integer | Yes | ID of the parent plan |
| `title` | string | Yes | Task title |
| `description` | string | No | Optional details |
| `priority` | integer | No | `0` = Normal, `1` = High, `2` = Urgent (default: 0) |

**Returns:** HTML partial — updated task list

---

#### Update Task

```
PUT /api/tasks/{task_id}
```

**Form fields:** (all optional)

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | New title |
| `description` | string | New description |
| `priority` | integer | `0`, `1`, or `2` |

**Returns:** HTML partial — updated task list

---

#### Update Task Status

```
PATCH /api/tasks/{task_id}/status
```

**Form fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | Yes | One of: `TODO`, `IN_PROGRESS`, `DONE`, `SKIPPED` |

Used by the checkbox toggle in the UI — toggles between `TODO` and `DONE`.

**Returns:** HTML partial — updated task list

---

#### Delete Task

```
DELETE /api/tasks/{task_id}
```

Cascades to all child Subtasks.

**Returns:** HTML partial — updated task list (task removed)

---

### Subtasks

#### Create Subtask

```
POST /api/tasks/{task_id}/subtasks
```

**Form fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Subtask title |

**Returns:** HTML partial — updated subtask list for that task

---

#### Toggle Subtask Done

```
PATCH /api/subtasks/{subtask_id}/toggle
```

No body required. Flips `is_done` between `true` and `false`.

**Returns:** HTML partial — updated subtask list

---

#### Delete Subtask

```
DELETE /api/subtasks/{subtask_id}
```

**Returns:** HTML partial — updated subtask list (subtask removed)

---

## Error Responses

| Status | Meaning |
|--------|---------|
| 200 | Success — HTML partial returned |
| 404 | Resource not found |
| 422 | Validation error (missing required field) |
| 500 | Server error (check logs in `logs/`) |

---

## Interactive API Docs (FastAPI)

FastAPI auto-generates OpenAPI docs at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

> Note: The auto-docs describe the endpoints but since they return HTML (not JSON), the response schemas shown there are not representative of the actual output.

---

## Data Schemas

### DomainType (enum)

```
WORK | STUDY | INTERVIEW | PERSONAL_DEV | HOBBIES | WORKOUTS
```

### TaskStatus (enum)

```
TODO | IN_PROGRESS | DONE | SKIPPED
```

### Priority levels

```
0 = Normal
1 = High
2 = Urgent
```
