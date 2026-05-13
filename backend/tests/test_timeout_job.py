from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.database import Base, get_session_context
from backend.jobs.timeout_job import mark_timed_out_requests
from backend.models.help_request import HelpRequest
from backend.services.knowledge_service import normalize_question


def _make_request(caller_id: str, question: str, hours_ago: float) -> HelpRequest:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    created = now - timedelta(hours=hours_ago)
    timeout = created + timedelta(hours=1)
    return HelpRequest(
        caller_id=caller_id,
        question=question,
        question_normalized=normalize_question(question),
        created_at=created,
        timeout_at=timeout,
    )


@pytest_asyncio.fixture(autouse=True)
async def patch_session(monkeypatch):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    from backend import database

    original = database.get_session_context

    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def patched():
        async with factory() as s:
            yield s

    monkeypatch.setattr(database, "get_session_context", patched)
    monkeypatch.setattr("backend.jobs.timeout_job.get_session_context", patched)

    yield factory

    await engine.dispose()


@pytest.mark.asyncio
async def test_pending_past_timeout_marked_unresolved(patch_session):
    factory = patch_session
    async with factory() as session:
        hr = _make_request("+15550200", "Timed out question?", hours_ago=2.0)
        session.add(hr)
        await session.commit()
        request_id = hr.id

    count = await mark_timed_out_requests()
    assert count == 1

    async with factory() as session:
        result = await session.get(HelpRequest, request_id)
        assert result.status == "unresolved"


@pytest.mark.asyncio
async def test_pending_not_yet_timed_out_left_unchanged(patch_session):
    factory = patch_session
    async with factory() as session:
        hr = _make_request("+15550201", "Future question?", hours_ago=0.1)
        session.add(hr)
        await session.commit()
        request_id = hr.id

    count = await mark_timed_out_requests()
    assert count == 0

    async with factory() as session:
        result = await session.get(HelpRequest, request_id)
        assert result.status == "pending"


@pytest.mark.asyncio
async def test_resolved_not_touched_by_timeout_job(patch_session):
    factory = patch_session
    async with factory() as session:
        hr = _make_request("+15550202", "Already resolved?", hours_ago=2.0)
        hr.status = "resolved"
        session.add(hr)
        await session.commit()
        request_id = hr.id

    count = await mark_timed_out_requests()
    assert count == 0

    async with factory() as session:
        result = await session.get(HelpRequest, request_id)
        assert result.status == "resolved"
