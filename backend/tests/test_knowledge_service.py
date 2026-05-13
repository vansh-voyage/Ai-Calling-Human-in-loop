import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.database import Base
from backend.services.knowledge_service import (
    lookup_answer,
    normalize_question,
    save_answer,
)


@pytest.fixture(scope="module")
def event_loop_policy():
    import asyncio
    return asyncio.DefaultEventLoopPolicy()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as s:
        yield s
    await engine.dispose()


# ── normalize_question ────────────────────────────────────────────────────────

def test_normalize_lowercases():
    assert normalize_question("What Are YOUR Hours?") == "what are your hours"


def test_normalize_strips_punctuation():
    assert normalize_question("Do you have gift cards??") == "do you have gift cards"


def test_normalize_collapses_whitespace():
    assert normalize_question("  where   are  you  ") == "where are you"


# ── lookup_answer ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_lookup_exact_match(session: AsyncSession):
    await save_answer(session, "What are your hours", "9 AM to 7 PM", source="seed")
    entry = await lookup_answer(session, "What are your hours?")
    assert entry is not None
    assert "9 AM" in entry.answer


@pytest.mark.asyncio
async def test_lookup_increments_count(session: AsyncSession):
    await save_answer(session, "Do you accept walk-ins", "Yes, walk-ins welcome", source="seed")
    entry1 = await lookup_answer(session, "Do you accept walk-ins?")
    count_after_first = entry1.lookup_count
    entry2 = await lookup_answer(session, "Do you accept walk-ins?")
    assert entry2.lookup_count > count_after_first


@pytest.mark.asyncio
async def test_lookup_no_match_returns_none(session: AsyncSession):
    result = await lookup_answer(session, "Do you offer skydiving lessons?")
    assert result is None


# ── save_answer ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_save_creates_entry(session: AsyncSession):
    entry = await save_answer(session, "How much does a pedicure cost", "$45 for a basic pedicure")
    assert entry.id is not None
    assert entry.question_normalized == "how much does a pedicure cost"


@pytest.mark.asyncio
async def test_save_upserts_on_duplicate(session: AsyncSession):
    await save_answer(session, "Is there parking", "Yes, free parking behind the building")
    updated = await save_answer(session, "Is there parking?", "Yes, free parking on Maple Street")
    assert "Maple Street" in updated.answer
