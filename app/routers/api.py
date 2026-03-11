"""JSON API routes for HTMX partial updates and CRUD."""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.goal import GoalCreate, GoalUpdate
from app.schemas.plan import PlanCreate, PlanUpdate
from app.schemas.task import TaskCreate, TaskUpdate, SubtaskCreate, SubtaskUpdate
from app.schemas.recurring import RecurringPlanCreate, RecurringPlanUpdate
from app.services import domain_service, goal_service, plan_service, task_service
from app.services import recurring_service

router = APIRouter(prefix="/api", tags=["api"])


# --- Goals ---

@router.post("/goals")
async def create_goal(
    request: Request, db: AsyncSession = Depends(get_db)
) -> "Response":
    form = await request.form()
    data = GoalCreate(
        domain_id=int(form["domain_id"]),
        title=str(form["title"]),
        description=str(form.get("description", "")) or None,
    )
    goal = await goal_service.create_goal(db, data)
    goals = await goal_service.list_goals(db, domain_id=data.domain_id)
    domain = await domain_service.get_domain(db, data.domain_id)
    return request.app.state.templates.TemplateResponse(
        "partials/goal_list.html",
        {"request": request, "goals": goals, "domain": domain},
    )


@router.put("/goals/{goal_id}")
async def update_goal(
    request: Request, goal_id: int, db: AsyncSession = Depends(get_db)
) -> "Response":
    form = await request.form()
    fields: dict = {}
    if form.get("title"):
        fields["title"] = str(form["title"])
    if form.get("description"):
        fields["description"] = str(form["description"])
    if form.get("is_active") is not None:
        fields["is_active"] = form["is_active"] != "false"
    data = GoalUpdate(**fields)
    goal = await goal_service.update_goal(db, goal_id, data)
    if not goal:
        raise HTTPException(status_code=404)
    goals = await goal_service.list_goals(db, domain_id=goal.domain_id)
    domain = await domain_service.get_domain(db, goal.domain_id)
    return request.app.state.templates.TemplateResponse(
        "partials/goal_list.html",
        {"request": request, "goals": goals, "domain": domain},
    )


@router.delete("/goals/{goal_id}")
async def delete_goal(
    request: Request, goal_id: int, db: AsyncSession = Depends(get_db)
) -> "Response":
    goal = await goal_service.get_goal(db, goal_id)
    if not goal:
        raise HTTPException(status_code=404)
    domain_id = goal.domain_id
    await goal_service.delete_goal(db, goal_id)
    goals = await goal_service.list_goals(db, domain_id=domain_id)
    domain = await domain_service.get_domain(db, domain_id)
    return request.app.state.templates.TemplateResponse(
        "partials/goal_list.html",
        {"request": request, "goals": goals, "domain": domain},
    )


# --- Plans ---

@router.post("/plans")
async def create_plan(
    request: Request, db: AsyncSession = Depends(get_db)
) -> "Response":
    form = await request.form()
    data = PlanCreate(
        goal_id=int(form["goal_id"]),
        title=str(form["title"]),
        description=str(form.get("description", "")) or None,
        plan_date=date.fromisoformat(str(form["plan_date"])),
    )
    plan = await plan_service.create_plan(db, data)
    plans = await plan_service.list_plans(db, goal_id=data.goal_id)
    return request.app.state.templates.TemplateResponse(
        "partials/plan_list.html",
        {"request": request, "plans": plans},
    )


@router.put("/plans/{plan_id}")
async def update_plan(
    request: Request, plan_id: int, db: AsyncSession = Depends(get_db)
) -> "Response":
    form = await request.form()
    fields: dict = {}
    if form.get("title"):
        fields["title"] = str(form["title"])
    if form.get("description"):
        fields["description"] = str(form["description"])
    if form.get("plan_date"):
        fields["plan_date"] = date.fromisoformat(str(form["plan_date"]))
    data = PlanUpdate(**fields)
    plan = await plan_service.update_plan(db, plan_id, data)
    if not plan:
        raise HTTPException(status_code=404)
    plans = await plan_service.list_plans(db, goal_id=plan.goal_id)
    return request.app.state.templates.TemplateResponse(
        "partials/plan_list.html",
        {"request": request, "plans": plans},
    )


@router.delete("/plans/{plan_id}")
async def delete_plan(
    request: Request, plan_id: int, db: AsyncSession = Depends(get_db)
) -> "Response":
    plan = await plan_service.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404)
    goal_id = plan.goal_id
    await plan_service.delete_plan(db, plan_id)
    plans = await plan_service.list_plans(db, goal_id=goal_id)
    return request.app.state.templates.TemplateResponse(
        "partials/plan_list.html",
        {"request": request, "plans": plans},
    )


# --- Tasks ---

@router.post("/tasks")
async def create_task(
    request: Request, db: AsyncSession = Depends(get_db)
) -> "Response":
    form = await request.form()
    data = TaskCreate(
        plan_id=int(form["plan_id"]),
        title=str(form["title"]),
        description=str(form.get("description", "")) or None,
        priority=int(form.get("priority", 0)),
    )
    task = await task_service.create_task(db, data)
    tasks = await task_service.list_tasks(db, plan_id=data.plan_id)
    return request.app.state.templates.TemplateResponse(
        "partials/task_list.html",
        {"request": request, "tasks": tasks, "plan_id": data.plan_id},
    )


@router.put("/tasks/{task_id}")
async def update_task(
    request: Request, task_id: int, db: AsyncSession = Depends(get_db)
) -> "Response":
    form = await request.form()
    fields: dict = {}
    if form.get("title"):
        fields["title"] = str(form["title"])
    if form.get("description"):
        fields["description"] = str(form["description"])
    if form.get("priority") is not None:
        fields["priority"] = int(form["priority"])
    data = TaskUpdate(**fields)
    task = await task_service.update_task(db, task_id, data)
    if not task:
        raise HTTPException(status_code=404)
    tasks = await task_service.list_tasks(db, plan_id=task.plan_id)
    return request.app.state.templates.TemplateResponse(
        "partials/task_list.html",
        {"request": request, "tasks": tasks, "plan_id": task.plan_id},
    )


@router.patch("/tasks/{task_id}/status")
async def toggle_task_status(
    request: Request, task_id: int, db: AsyncSession = Depends(get_db)
) -> "Response":
    form = await request.form()
    status_val = str(form["status"])
    data = TaskUpdate(status=status_val)
    task = await task_service.update_task(db, task_id, data)
    if not task:
        raise HTTPException(status_code=404)
    tasks = await task_service.list_tasks(db, plan_id=task.plan_id)
    return request.app.state.templates.TemplateResponse(
        "partials/task_list.html",
        {"request": request, "tasks": tasks, "plan_id": task.plan_id},
    )


@router.delete("/tasks/{task_id}")
async def delete_task(
    request: Request, task_id: int, db: AsyncSession = Depends(get_db)
) -> "Response":
    task = await task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404)
    plan_id = task.plan_id
    await task_service.delete_task(db, task_id)
    tasks = await task_service.list_tasks(db, plan_id=plan_id)
    return request.app.state.templates.TemplateResponse(
        "partials/task_list.html",
        {"request": request, "tasks": tasks, "plan_id": plan_id},
    )


# --- Subtasks ---

@router.post("/tasks/{task_id}/subtasks")
async def create_subtask(
    request: Request, task_id: int, db: AsyncSession = Depends(get_db)
) -> "Response":
    form = await request.form()
    data = SubtaskCreate(title=str(form["title"]))
    subtask = await task_service.create_subtask(db, task_id, data)
    if not subtask:
        raise HTTPException(status_code=404)
    task = await task_service.get_task(db, task_id)
    return request.app.state.templates.TemplateResponse(
        "partials/subtask_list.html",
        {"request": request, "task": task},
    )


@router.patch("/subtasks/{subtask_id}/toggle")
async def toggle_subtask(
    request: Request, subtask_id: int, db: AsyncSession = Depends(get_db)
) -> "Response":
    from sqlalchemy import select
    from app.models.task import Subtask
    result = await db.execute(select(Subtask).where(Subtask.id == subtask_id))
    subtask = result.scalar_one_or_none()
    if not subtask:
        raise HTTPException(status_code=404)
    data = SubtaskUpdate(is_done=not subtask.is_done)
    await task_service.update_subtask(db, subtask_id, data)
    task = await task_service.get_task(db, subtask.task_id)
    return request.app.state.templates.TemplateResponse(
        "partials/subtask_list.html",
        {"request": request, "task": task},
    )


# --- Recurring Plans ---

@router.post("/recurring-plans")
async def create_recurring_plan(
    request: Request, db: AsyncSession = Depends(get_db)
) -> "Response":
    form = await request.form()
    task_titles = form.getlist("task_title")
    data = RecurringPlanCreate(
        goal_id=int(form["goal_id"]),
        title=str(form["title"]),
        description=str(form.get("description", "")) or None,
        recurrence_type=str(form["recurrence_type"]),
        tasks=[{"title": t, "priority": i} for i, t in enumerate(task_titles) if t.strip()],
    )
    await recurring_service.create_recurring_plan(db, data)
    recurring_plans = await recurring_service.list_recurring_plans(db, goal_id=data.goal_id)
    return request.app.state.templates.TemplateResponse(
        "partials/recurring_plan_list.html",
        {"request": request, "recurring_plans": recurring_plans, "goal_id": data.goal_id},
    )


@router.patch("/recurring-plans/{rp_id}/toggle")
async def toggle_recurring_plan(
    request: Request, rp_id: int, db: AsyncSession = Depends(get_db)
) -> "Response":
    rp = await recurring_service.get_recurring_plan(db, rp_id)
    if not rp:
        raise HTTPException(status_code=404)
    goal_id = rp.goal_id
    data = RecurringPlanUpdate(is_active=not rp.is_active)
    await recurring_service.update_recurring_plan(db, rp_id, data)
    recurring_plans = await recurring_service.list_recurring_plans(db, goal_id=goal_id)
    return request.app.state.templates.TemplateResponse(
        "partials/recurring_plan_list.html",
        {"request": request, "recurring_plans": recurring_plans, "goal_id": goal_id},
    )


@router.delete("/recurring-plans/{rp_id}")
async def delete_recurring_plan(
    request: Request, rp_id: int, db: AsyncSession = Depends(get_db)
) -> "Response":
    rp = await recurring_service.get_recurring_plan(db, rp_id)
    if not rp:
        raise HTTPException(status_code=404)
    goal_id = rp.goal_id
    await recurring_service.delete_recurring_plan(db, rp_id)
    recurring_plans = await recurring_service.list_recurring_plans(db, goal_id=goal_id)
    return request.app.state.templates.TemplateResponse(
        "partials/recurring_plan_list.html",
        {"request": request, "recurring_plans": recurring_plans, "goal_id": goal_id},
    )


@router.delete("/subtasks/{subtask_id}")
async def delete_subtask(
    request: Request, subtask_id: int, db: AsyncSession = Depends(get_db)
) -> "Response":
    from sqlalchemy import select
    from app.models.task import Subtask
    result = await db.execute(select(Subtask).where(Subtask.id == subtask_id))
    subtask = result.scalar_one_or_none()
    if not subtask:
        raise HTTPException(status_code=404)
    task_id = subtask.task_id
    await task_service.delete_subtask(db, subtask_id)
    task = await task_service.get_task(db, task_id)
    return request.app.state.templates.TemplateResponse(
        "partials/subtask_list.html",
        {"request": request, "task": task},
    )
