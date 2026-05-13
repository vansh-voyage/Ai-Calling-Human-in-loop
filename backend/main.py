"""
FastAPI application factory.

Responsibilities:
- Create the app and configure CORS
- Lifespan: init DB, seed knowledge base, start APScheduler
- Mount all API routers
- Expose GET /health
"""

import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.router import api_router
from backend.config import settings
from backend.database import AsyncSessionFactory, init_db
from backend.jobs.timeout_job import mark_timed_out_requests
from backend.seed import seed_knowledge_base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────────
    logger.info("Starting Frontdesk AI backend...")

    await init_db()
    logger.info("Database tables ready.")

    async with AsyncSessionFactory() as session:
        await seed_knowledge_base(session)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        mark_timed_out_requests,
        trigger=IntervalTrigger(hours=1),
        id="timeout_reaper",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("APScheduler started (timeout reaper: every 1 hour).")

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────────
    scheduler.shutdown(wait=False)
    logger.info("Frontdesk AI backend shut down.")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Frontdesk AI — Human-in-the-Loop Supervisor",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.get("/health", tags=["health"])
    async def health():
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
