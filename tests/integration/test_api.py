"""Integration tests for LifeOS API endpoints."""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app, lifespan


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="module")
async def client():
    async with lifespan(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c


class TestPageRoutes:
    @pytest.mark.asyncio
    async def test_dashboard_loads(self, client: AsyncClient) -> None:
        r = await client.get("/")
        assert r.status_code == 200
        assert b"LifeOS" in r.content

    @pytest.mark.asyncio
    async def test_today_loads(self, client: AsyncClient) -> None:
        r = await client.get("/today")
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_upcoming_loads(self, client: AsyncClient) -> None:
        r = await client.get("/upcoming")
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_domain_detail_loads(self, client: AsyncClient) -> None:
        r = await client.get("/domains/1")
        assert r.status_code == 200


class TestGoalCRUD:
    @pytest.mark.asyncio
    async def test_create_goal(self, client: AsyncClient) -> None:
        r = await client.post("/api/goals", data={
            "domain_id": "1",
            "title": "Test Goal",
            "description": "A test goal"
        })
        assert r.status_code == 200
        assert b"Test Goal" in r.content

    @pytest.mark.asyncio
    async def test_update_goal(self, client: AsyncClient) -> None:
        r = await client.put("/api/goals/1", data={"title": "Updated Goal"})
        assert r.status_code == 200
        assert b"Updated Goal" in r.content

    @pytest.mark.asyncio
    async def test_delete_goal(self, client: AsyncClient) -> None:
        # Create a goal to delete
        await client.post("/api/goals", data={"domain_id": "2", "title": "To Delete"})
        r = await client.delete("/api/goals/2")
        assert r.status_code == 200
        assert b"To Delete" not in r.content

    @pytest.mark.asyncio
    async def test_delete_nonexistent_goal_returns_404(self, client: AsyncClient) -> None:
        r = await client.delete("/api/goals/99999")
        assert r.status_code == 404


class TestPlanCRUD:
    @pytest.mark.asyncio
    async def test_create_plan(self, client: AsyncClient) -> None:
        r = await client.post("/api/plans", data={
            "goal_id": "1",
            "title": "Test Plan",
            "plan_date": "2026-03-10"
        })
        assert r.status_code == 200
        assert b"Test Plan" in r.content

    @pytest.mark.asyncio
    async def test_update_plan(self, client: AsyncClient) -> None:
        r = await client.put("/api/plans/1", data={
            "title": "Updated Plan",
            "plan_date": "2026-03-11"
        })
        assert r.status_code == 200
        assert b"Updated Plan" in r.content


class TestTaskCRUD:
    @pytest.mark.asyncio
    async def test_create_task(self, client: AsyncClient) -> None:
        r = await client.post("/api/tasks", data={
            "plan_id": "1",
            "title": "Test Task",
            "priority": "1"
        })
        assert r.status_code == 200
        assert b"Test Task" in r.content

    @pytest.mark.asyncio
    async def test_update_task(self, client: AsyncClient) -> None:
        r = await client.put("/api/tasks/1", data={"title": "Updated Task", "priority": "2"})
        assert r.status_code == 200
        assert b"Updated Task" in r.content

    @pytest.mark.asyncio
    async def test_toggle_task_status_done(self, client: AsyncClient) -> None:
        r = await client.patch("/api/tasks/1/status", data={"status": "DONE"})
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_toggle_task_status_todo(self, client: AsyncClient) -> None:
        r = await client.patch("/api/tasks/1/status", data={"status": "TODO"})
        assert r.status_code == 200


class TestSubtaskCRUD:
    @pytest.mark.asyncio
    async def test_create_subtask(self, client: AsyncClient) -> None:
        r = await client.post("/api/tasks/1/subtasks", data={"title": "Sub item"})
        assert r.status_code == 200
        assert b"Sub item" in r.content

    @pytest.mark.asyncio
    async def test_toggle_subtask(self, client: AsyncClient) -> None:
        r = await client.patch("/api/subtasks/1/toggle")
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_subtask(self, client: AsyncClient) -> None:
        r = await client.delete("/api/subtasks/1")
        assert r.status_code == 200
