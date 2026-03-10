from contextlib import asynccontextmanager
from pathlib import Path
import socket

import structlog
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import engine, async_session, Base
from app.models import Domain, Goal, Plan, Task, Subtask  # noqa: F401 — register models
from app.routers import pages, api
from app.services.domain_service import seed_domains


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

log = structlog.get_logger()

APP_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("database_ready")

    async with async_session() as db:
        await seed_domains(db)

    log.info("startup_complete", local_ip=app.state.local_ip, port=8000)
    yield

    await engine.dispose()
    log.info("shutdown_complete")


app = FastAPI(title="LifeOS", version="0.1.0", lifespan=lifespan)
app.state.local_ip = get_local_ip()

app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
app.state.templates = Jinja2Templates(directory=APP_DIR / "templates")

app.include_router(pages.router)
app.include_router(api.router)
