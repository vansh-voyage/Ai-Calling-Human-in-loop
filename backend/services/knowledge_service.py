"""
Knowledge service: the algorithmic heart of the system.

normalize_question  — converts any raw question to a stable lookup key
lookup_answer       — finds an answer (exact then fuzzy), increments lookup_count
save_answer         — upserts a knowledge entry (called after supervisor resolves)
"""

import re
import string
from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.knowledge_entry import KnowledgeEntry


def normalize_question(raw: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace → stable lookup key."""
    text = raw.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text


async def lookup_answer(session: AsyncSession, question: str) -> KnowledgeEntry | None:
    """
    1. Normalize the question.
    2. Try exact match on question_normalized.
    3. If no exact match, try keyword-based LIKE on the top 3 content words.
    4. On hit, increment lookup_count and return the entry.
    """
    normalized = normalize_question(question)

    # Exact match
    result = await session.execute(
        select(KnowledgeEntry).where(KnowledgeEntry.question_normalized == normalized)
    )
    entry = result.scalar_one_or_none()

    if entry is None:
        # Keyword fallback: pick words longer than 3 chars, take up to 3
        keywords = [w for w in normalized.split() if len(w) > 3][:3]
        if keywords:
            stmt = select(KnowledgeEntry)
            for kw in keywords:
                stmt = stmt.where(KnowledgeEntry.question_normalized.like(f"%{kw}%"))
            stmt = stmt.order_by(KnowledgeEntry.lookup_count.desc()).limit(1)
            result = await session.execute(stmt)
            entry = result.scalar_one_or_none()

    if entry is not None:
        await session.execute(
            update(KnowledgeEntry)
            .where(KnowledgeEntry.id == entry.id)
            .values(lookup_count=KnowledgeEntry.lookup_count + 1)
        )
        await session.commit()
        await session.refresh(entry)

    return entry


async def save_answer(
    session: AsyncSession,
    question: str,
    answer: str,
    help_request_id: int | None = None,
    source: str = "supervisor",
) -> KnowledgeEntry:
    """
    Upsert a knowledge entry by question_normalized.
    If an entry already exists for this question, update its answer and updated_at.
    Called automatically when a supervisor resolves a help request.
    """
    normalized = normalize_question(question)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    result = await session.execute(
        select(KnowledgeEntry).where(KnowledgeEntry.question_normalized == normalized)
    )
    entry = result.scalar_one_or_none()

    if entry is None:
        entry = KnowledgeEntry(
            question_normalized=normalized,
            question_display=question,
            answer=answer,
            source=source,
            help_request_id=help_request_id,
            created_at=now,
            updated_at=now,
        )
        session.add(entry)
    else:
        entry.answer = answer
        entry.updated_at = now
        if help_request_id is not None:
            entry.help_request_id = help_request_id

    await session.commit()
    await session.refresh(entry)
    return entry


async def list_entries(
    session: AsyncSession,
    limit: int = 50,
    offset: int = 0,
    source: str | None = None,
) -> tuple[list[KnowledgeEntry], int]:
    stmt = select(KnowledgeEntry)
    count_stmt = select(func.count()).select_from(KnowledgeEntry)

    if source:
        stmt = stmt.where(KnowledgeEntry.source == source)
        count_stmt = count_stmt.where(KnowledgeEntry.source == source)

    stmt = stmt.order_by(KnowledgeEntry.lookup_count.desc()).limit(limit).offset(offset)

    total_result = await session.execute(count_stmt)
    total = total_result.scalar_one()

    result = await session.execute(stmt)
    entries = list(result.scalars().all())

    return entries, total
