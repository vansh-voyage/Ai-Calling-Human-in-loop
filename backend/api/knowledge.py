"""
Knowledge Base API

GET    /knowledge             — list all entries
GET    /knowledge/lookup?q=   — agent lookup (returns {found, answer})
POST   /knowledge             — manually seed an entry
PUT    /knowledge/{id}        — edit an entry's answer
DELETE /knowledge/{id}        — remove an entry
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session
from backend.models.knowledge_entry import KnowledgeEntry
from backend.schemas.knowledge_entry import (
    KnowledgeEntryCreate,
    KnowledgeEntryListResponse,
    KnowledgeEntryResponse,
    KnowledgeEntryUpdate,
    KnowledgeLookupResponse,
)
from backend.services import knowledge_service

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/lookup", response_model=KnowledgeLookupResponse)
async def lookup(
    q: str = Query(..., min_length=1, description="Raw question from agent"),
    session: AsyncSession = Depends(get_session),
):
    entry = await knowledge_service.lookup_answer(session, q)
    if entry is None:
        return KnowledgeLookupResponse(found=False)
    return KnowledgeLookupResponse(found=True, answer=entry.answer, entry_id=entry.id)


@router.get("", response_model=KnowledgeEntryListResponse)
async def list_entries(
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    source: str | None = Query(None),
):
    entries, total = await knowledge_service.list_entries(
        session, limit=limit, offset=offset, source=source
    )
    return KnowledgeEntryListResponse(items=entries, total=total, limit=limit, offset=offset)


@router.post("", response_model=KnowledgeEntryResponse, status_code=201)
async def seed_entry(
    body: KnowledgeEntryCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    entry = await knowledge_service.save_answer(
        session=session,
        question=body.question,
        answer=body.answer,
        source=body.source,
    )
    return entry


@router.put("/{entry_id}", response_model=KnowledgeEntryResponse)
async def update_entry(
    entry_id: int,
    body: KnowledgeEntryUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    entry = await session.get(KnowledgeEntry, entry_id)
    if entry is None:
        raise HTTPException(404, f"No knowledge entry with id={entry_id}")

    from datetime import datetime, timezone

    entry.answer = body.answer
    entry.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await session.commit()
    await session.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=204)
async def delete_entry(
    entry_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    entry = await session.get(KnowledgeEntry, entry_id)
    if entry is None:
        raise HTTPException(404, f"No knowledge entry with id={entry_id}")
    await session.delete(entry)
    await session.commit()
