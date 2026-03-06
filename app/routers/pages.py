"""HTML page routes — serves Jinja2 templates for the HTMX frontend."""
from datetime import date, timedelta
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import domain_service, goal_service, plan_service, task_service

router = APIRouter(tags=["pages"])


@router.get("/")
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)) -> "Response":
    domains = await domain_service.list_domains(db)
    today = date.today()
    today_plans = await plan_service.list_plans(db, plan_date=today)
    upcoming_plans = await plan_service.list_plans_in_range(
        db, start_date=today + timedelta(days=1), end_date=today + timedelta(days=7)
    )
    return request.app.state.templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "domains": domains,
            "today_plans": today_plans,
            "upcoming_plans": upcoming_plans,
            "today": today,
        },
    )


@router.get("/domains/{domain_id}")
async def domain_detail(request: Request, domain_id: int, db: AsyncSession = Depends(get_db)) -> "Response":
    domains = await domain_service.list_domains(db)
    domain = await domain_service.get_domain(db, domain_id)
    goals = await goal_service.list_goals(db, domain_id=domain_id)
    return request.app.state.templates.TemplateResponse(
        "domain_detail.html",
        {"request": request, "domains": domains, "domain": domain, "goals": goals},
    )


@router.get("/goals/{goal_id}")
async def goal_detail(request: Request, goal_id: int, db: AsyncSession = Depends(get_db)) -> "Response":
    goal = await goal_service.get_goal(db, goal_id)
    plans = await plan_service.list_plans(db, goal_id=goal_id)
    domains = await domain_service.list_domains(db)
    return request.app.state.templates.TemplateResponse(
        "goal_detail.html",
        {"request": request, "goal": goal, "plans": plans, "domains": domains, "today": date.today()},
    )


@router.get("/plans/{plan_id}")
async def plan_detail(request: Request, plan_id: int, db: AsyncSession = Depends(get_db)) -> "Response":
    plan = await plan_service.get_plan(db, plan_id)
    tasks = await task_service.list_tasks(db, plan_id=plan_id)
    domains = await domain_service.list_domains(db)
    return request.app.state.templates.TemplateResponse(
        "plan_detail.html",
        {"request": request, "plan": plan, "tasks": tasks, "domains": domains},
    )


@router.get("/today")
async def today_view(request: Request, db: AsyncSession = Depends(get_db)) -> "Response":
    today = date.today()
    plans = await plan_service.list_plans(db, plan_date=today)
    domains = await domain_service.list_domains(db)
    return request.app.state.templates.TemplateResponse(
        "today.html",
        {"request": request, "plans": plans, "domains": domains, "today": today},
    )


@router.get("/upcoming")
async def upcoming_view(request: Request, db: AsyncSession = Depends(get_db)) -> "Response":
    today = date.today()
    domains = await domain_service.list_domains(db)
    plans = await plan_service.list_plans_in_range(
        db, start_date=today, end_date=today + timedelta(days=30)
    )
    return request.app.state.templates.TemplateResponse(
        "upcoming.html",
        {"request": request, "plans": plans, "domains": domains, "today": today},
    )
